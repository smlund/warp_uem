import os
try:
  import cPickle as pickle
except ImportError:
  import pickle
import numpy as np
from ConfigParser import SafeConfigParser as ConfigParser
from Forthon import fzeros
from discrete_fourspace.mesh import get_index_of_point, r_mesh_to_xy_mesh
from discrete_fourspace.mesh import linear_field_projection_from_r_to_xy
from fields.dat import read_dat_file_as_numpy_arrays
from fields.rf_asci import read_rf_ascii_file_as_numpy_arrays

class FieldPreProcessor(object):
  """
  A class to keep track of data needed for
  adding fields in an automated fashion.
  """

  def __init__(self,filepath,**kwargs):
    """
    Reads the filepath into the objects attributes. 
    Attributes:
      input_order: The fieldnames from the imported file header in the
        order they appear in the file.
      fields: A dict first pointing to the type of field (i.e. electric 
        or magnetic) then pointing to components of the field.
      coordinates: A dict containing the coordinates keyed by x, y, z, or r.
      stepsize: A dict containing the stepsize of each of the coordinates key
        by the coordinate.
      number_of_steps: A dict containing the number of steps of each of the coordinates key
        by the coordinate.
      xmin: The minimum value of the z coordinate in the filepath.
      ymin: The minimum value of the z coordinate in the filepath.
      zmin: The minimum value of the z coordinate in the filepath.
      zmax: The max z in the field.
      zlen: The length over which the field is applied.
    """
    self.filepath = filepath
    file_content = read_file_as_dict_of_numpy_arrays(filepath,**kwargs)
    self.input_order = file_content["fieldnames"]

    self.parseData(file_content["data"])
    self.fillDerivedData()
    self.correctZCoordinate()
    self.ravelForFortran(**kwargs)

  def parseData(self, data):
    """
    Splits up the data coming in from the file reader and
    puts it into the appropriate container.
    Args:
      self: Standard python object oriented notation. 
      data: A dictionary containing np_arrays.
    Return value:
      None --- but adds numpy arrays to coordinates and
        fields attributes.
    """
    if not hasattr(self,"fields"):
      self.fields = {}
    if not hasattr(self,"coordinates"):
      self.coordinates = {}
    for key, np_array in data.iteritems():
      if key in ["x","y","z", "r"]:
        self.coordinates[key] = np_array
        continue
      if key.startswith("e"):
        direction = key.replace("e","")
        try:
          self.fields["electric"][direction] = np_array
        except KeyError:
          self.fields["electric"] = {}
          self.fields["electric"][direction] = np_array
      if key.startswith("b"):
        direction = key.replace("b","")
        try:
          self.fields["magnetic"][direction] = np_array
        except KeyError:
          self.fields["magnetic"] = {}
          self.fields["magnetic"][direction] = np_array
    
  def fillDerivedData(self):
    """
    Derive the necessary attributes from the input data.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      None --- but adds values to stepsize, number_of_steps,
        zmin, zmax, and zlen.
    """
    if not hasattr(self,"stepsize"):
      self.stepsize = {}
    if not hasattr(self,"number_of_steps"):
      self.number_of_steps = {}

    if self.isRZ():
      self.xmin = -1.*self.coordinates["r"].max()
      self.ymin = -1.*self.coordinates["r"].max()
    else:
      self.xmin = self.coordinates["x"].min()
      self.ymin = self.coordinates["y"].min()
    self.zmin = self.coordinates["z"].min()
    self.zmax = self.coordinates["z"].max()
    self.zlen = self.zmax - self.zmin
    for key, np_array in self.coordinates.iteritems():
      self.stepsize[key] = np.average(np.diff(np.unique(np_array)))
      self.number_of_steps[key] = np.around( ( np_array.max()-np_array.min() )/self.stepsize[key] )
    return
    
  def correctZCoordinate(self):
    """
    Moves the z coordinate to 0 which is necessary
    for warp.
    Args:
      self: Standard python object oriented notation. 
    Return value:
       Nothing --- z values are modified in place. 
    """
    self.coordinates["z"] -= self.coordinates["z"].min()
    return

  def ravelForFortran(self,**kwargs):
    """
    Ravels the fields into a convenient format for working
    with fortran.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      None --- but rewrites the field numpy arrays.
    """
    if self.isRZ():
      self.interpolateRToXY(**kwargs)
    self.ravelXYZForFortran()
    return

  def ravelXYZForFortran(self):
    """
    Ravels the XYZ fields into a convenient format for working
    with fortran.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      None --- but rewrites the field numpy arrays.
    """
    for field_type, field in self.fields.iteritems():
      fx = fzeros((self.number_of_steps["x"]+1,
                   self.number_of_steps["y"]+1,
                   self.number_of_steps["z"]+1) ) 
      fy = fzeros((self.number_of_steps["x"]+1,
                   self.number_of_steps["y"]+1,
                   self.number_of_steps["z"]+1) ) 
      fz = fzeros((self.number_of_steps["x"]+1,
                   self.number_of_steps["y"]+1,
                   self.number_of_steps["z"]+1) ) 

      ix = get_index_of_point(self.coordinates["x"],self.stepsize["x"])
      iy = get_index_of_point(self.coordinates["y"],self.stepsize["y"])
      iz = get_index_of_point(self.coordinates["z"],self.stepsize["z"])

      ii = ix + int(self.number_of_steps["x"]+1)*iy + \
           int(self.number_of_steps["x"]+1)*int(self.number_of_steps["y"]+1)*iz 

      fx.ravel(order='F').put(ii,field["x"]) 
      fy.ravel(order='F').put(ii,field["y"]) 
      fz.ravel(order='F').put(ii,field["z"]) 
      
      self.fields[field_type]["x"] = fx
      self.fields[field_type]["y"] = fy
      self.fields[field_type]["z"] = fz

  def ravelRZForFortran(self):
    """
    This function is no longer in use
    Ravels the RZ fields into a convenient format for working
    with fortran.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      None --- but rewrites the field numpy arrays.
    """
    for field_type, field in self.fields.iteritems():
      fr = fzeros((self.number_of_steps["r"]+1,
                   self.number_of_steps["z"]+1) ) 
      fz = fzeros((self.number_of_steps["r"]+1,
                   self.number_of_steps["z"]+1) ) 

      ir = get_index_of_point(self.coordinates["r"],self.stepsize["r"])
      iz = get_index_of_point(self.coordinates["z"],self.stepsize["z"])

      ii = ir + int(self.number_of_steps["r"]+1)*iz  

      fr.ravel(order='F').put(ii,field["r"]) 
      fz.ravel(order='F').put(ii,field["z"]) 
      
      self.fields[field_type]["r"] = fr
      self.fields[field_type]["z"] = fz

  def archive(self, pickle_file_front=None, config=None, config_file_front=None, section="field parameters"):
    """
    Saves the fields to pickle file(s) and the relevant
    other attributes to a config file.
    Args:
      self: Standard python object oriented notation. 
      pickle_file: Path to where the pickle file(s) will be written
        with the additional _electric or _magnetic.
        Default is to the original filepath without its extension.
      config: A config parser object.  If this is not defined, then one
        will be created.
      config_file_front:  Path to where the config file will be written.
        Default is to the original filepath without its extension.  If
        this is not provided, the config is written only if the config object
        is NOT provided.
    Return value:
      config: The config parser object --- but writes to the field files
        no matter what.
    """
    
    pickle_filepath = {}
    for field_type, field in self.fields.iteritems():
      if pickle_file_front is None:
        pickle_file_front, file_extension = os.path.splitext(self.filepath)
      pickle_filepath[field_type] = pickle_file_front + "_" + field_type + ".pckl"
      pickle.dump(field,open(pickle_filepath[field_type],"wb"))
 
    config_write = False
    if config is None:
      config = ConfigParser()
      config_write = True
    config.add_section(section)
    for field_type, filepath in pickle_filepath.iteritems():
      config.set(section,field_type+"_pickled_field", filepath)
    config.set(section,"xmin", str(self.xmin))
    config.set(section,"ymin", str(self.ymin))
    config.set(section,"zmin", str(self.zmin))
    config.set(section,"zmax", str(self.zmax))
    config.set(section,"zlen", str(self.zlen))
    for coordinate in self.coordinates.keys():
      config.set(section, "n"+coordinate, str(int(self.number_of_steps[coordinate])))
      config.set(section, "d"+coordinate, str(self.stepsize[coordinate]))
    if config_file_front is None:
      config_file_front, file_extension = os.path.splitext(self.filepath)
      config_filepath = config_file_front + ".cfg"
    else:
      config_filepath = config_file_front + ".cfg"
      config_write = True
    if config_write:
      config.write(open(config_filepath,'w'))
    return config

  def isRZ(self):
    """
    Returns true or false depending if the coordinates are RZ or XYZ.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      True or false
    """
    return set(self.coordinates) == set(["r","z"])

  def interpolateRToXY(self,r_to_xy_interpolation_function=linear_field_projection_from_r_to_xy,**kwargs):
    """
    Passes slices of the rz field grid to the r_to_xy_interpolation function
    and assigns the output to an xyz field grid.
    Args:
      self: Standard python object oriented notation. 
      r_to_zy_interpolation_function: The function to be used to do the
      x y interpolation.  Input must be the numpy arrays (r,fr,fz, x, y) and
      output must be a numpy arrays (fx, fy, fz).
    Return value:
      None: But unsets all "r" components, adds "x" and "y" components, 
        and reassigns both coordinates and fields to the new sized arrays.  
    """
    dr = self.stepsize["r"] #Just for ease of coding.

    #This algorithm assumes that each unique_z is matched up with each 
    #unique r (that is, the total dimensions of the grid are unique_z x unique_r
    #in the normal way).
    unique_z = np.unique(self.coordinates["z"])
    unique_r = np.unique(self.coordinates["r"])
    unique_x, unique_y, dx, dy, nx, ny = r_mesh_to_xy_mesh(unique_r)
    #Dicts to keep track of the output of the function
    fx = {}
    fy = {}
    fz = {}

    for z in np.nditer(unique_z):
      indices = np.where(self.coordinates["z"] == z)
      for field_type, field in self.fields.iteritems():
        #Get the constant z slice of each element we need.
        current_fr = field["r"][indices]
        current_fz = field["z"][indices]
        #Pass control to the interpolation function
        fx_piece, fy_piece, fz_piece = \
            r_to_xy_interpolation_function(unique_r, current_fr, current_fz, unique_x, unique_y)
        #Add the piece just calculated to object that keeps track of it.
        try:
          fx[field_type].append(fx_piece)
          fy[field_type].append(fy_piece)
          fz[field_type].append(fz_piece)
        except KeyError:
          fx[field_type]=[fx_piece]
          fy[field_type]=[fy_piece]
          fz[field_type]=[fz_piece]

    #Overwrite the elements with the new numpy arrays and values
    self.coordinates["x"] = np.tile(unique_x,unique_z.size)
    self.coordinates["y"] = np.tile(unique_y,unique_z.size)
    self.coordinates["z"] = np.repeat(unique_z,unique_x.size)
    self.stepsize["x"] = dx
    self.stepsize["y"] = dy
    self.number_of_steps["x"] = nx
    self.number_of_steps["y"] = ny


    #Concatenate the arrays into single array and save.
    for field_type in self.fields.keys():
      self.fields[field_type]["x"] = np.hstack(fx[field_type])
      self.fields[field_type]["y"] = np.hstack(fy[field_type])
      self.fields[field_type]["z"] = np.hstack(fz[field_type])

    #Delete the unnecesary r components
    del self.coordinates["r"]
    del self.stepsize["r"]
    del self.number_of_steps["r"]
    for field_type, field in self.fields.iteritems():
      del self.fields[field_type]["r"]
        

def read_file_as_dict_of_numpy_arrays(filepath,formattype="",**kwargs):

  """
  Takes a filepath and returns a dict of numpy arrays.
  Args:
    filepath: The full path to the file we want to load.
    formattype: Optional argument telling us what is the format
      type.  Right now, only supports Poisson and RF ascii.  If None, uses
      the file extension to determine the file loader.
  Return value:
    A dictionary of data from the file.
      fieldnames: The keys of the dictionary in the order they
        appear in the file.
      data: A dictionary of numpy arrays keyed by the fieldnames.
  """
  filepath_no_extension, file_extension = os.path.splitext(filepath)
  if formattype == "Poisson" or file_extension == ".dat":
    return read_dat_file_as_numpy_arrays(filepath,**kwargs)
  if formattype == "RF ascii":
    return read_rf_ascii_file_as_numpy_arrays(filepath,**kwargs)
  raise Exception("The formattype and file_extension is not supported.")

