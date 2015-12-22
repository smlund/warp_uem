import os
try:
  import cPickle as pickle
except ImportError:
  import pickle
import numpy as np
from ConfigParser import SafeConfigParser as ConfigParser
from Forthon import fzeros
from discrete_fourspace.mesh import get_index_of_point
from fields.dat import read_dat_file_as_numpy_arrays

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
    self.ravel()

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

  def ravel(self):
    """
    Ravels the fields into a convenient format for working
    with fortran.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      None --- but rewrites the field numpy arrays.
    """
    if self.isRZ():
      self.ravelRZ()
    else:
      self.ravelXYZ()
    return

  def ravelXYZ(self):
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

  def ravelRZ(self):
    """
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

#The methods below here are for a different object.
#
#  def getArgs(self):
#    """
#    Returns an unpacked list of arguments for
#    """

def read_file_as_dict_of_numpy_arrays(filepath,formattype=""):

  """
  Takes a filepath and returns a dict of numpy arrays.
  Args:
    filepath: The full path to the file we want to load.
    formattype: Optional argument telling us what is the format
      type.  Right now, only supports Poisson.  If None, uses
      the file extension to determine the file loader.
  Return value:
    A dictionary of data from the file.
      fieldnames: The keys of the dictionary in the order they
        appear in the file.
      data: A dictionary of numpy arrays keyed by the fieldnames.
  """
  filepath_no_extension, file_extension = os.path.splitext(filepath)
  if formattype == "Poisson" or file_extension == ".dat":
    return read_dat_file_as_numpy_arrays(filepath)
  raise Exception("The formattype and file_extension is not supported.")

