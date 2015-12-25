import os
try:
  import cPickle as pickle
except ImportError:
  import pickle
import numpy as np
from config.my_config import MyConfigParser as ConfigParser
from Forthon import fzeros
from discrete_fourspace.mesh import get_index_of_point
from fields.dat import read_dat_file_as_numpy_arrays

class FieldLoader(object):
  """
  An object to load preprocessed field and their 
  config files.
  """

  def __init__(self,config_filepath=None,config=None,section="field parameters",
               time_dependent_function=None, **kwargs):
    """
    Loads the config_filepath and puts the elements into the objects attributes.
    Also loads and saves the fields. 
    Args:
      config_filepath: filepath to the config file for the field.  Either this or the
        config object needs to be present.
      config: A config parser object.  Allows the reading of this data from an existent
        config parser object.
      section: The name of the section in the filepath with the field info.  Default
        is field parameters.
    Attributes:
      fields: A dict first pointing to the type of field (i.e. electric 
        or magnetic) then pointing to components of the field.
      stepsize: A dict containing the stepsize of each of the coordinates key
        by the coordinate.
      number_of_steps: A dict containing the number of steps of each of the coordinates key
        by the coordinate.
      zmin: The minimum value of the z coordinate in the filepath.
      zmax: The max z in the field.
      zlen: The length over which the field is applied.
      time_dependent_function: An option function callback (function is a function of top.time)
        that can add time dependence to the field.  Default is no such file.
    """
    if config_filepath is None and config is None:
      raise Exception("Either the config_filepath needs to be specified or a config parser object " + 
                      "needs to be passed to the init function.")
    if config is None:
      config = ConfigParser()
      config.read(config_filepath)
    self.config = config
    
    self.xmin = config.get(section,"xmin")
    self.ymin = config.get(section,"ymin")
    self.zmin = config.get(section,"zmin")
    self.zmax = config.get(section,"zmax")
    self.zlen = config.get(section,"zlen")

    self.stepsize = {}
    self.number_of_steps = {}
    self.fields = {}
    for option in config.options(section):
      if option.startswith("d"):
        self.stepsize[option.replace("d","")] = config.get(section,option)
      if option.startswith("n"):
        self.number_of_steps[option.replace("n","")] = config.get(section,option)
      if option.endswith("_pickled_field"):
        field_type = option.replace("_pickled_field","")
        self.fields[field_type] = pickle.load( open(config.get(section,option), "rb") )
        for component in self.fields[field_type]:
          self.fields[field_type][component] = np.array(self.fields[field_type][component],order="FORTRAN")
    self.time_dependent_function = time_dependent_function

  def isRZ(self):
    """
    Returns true or false depending if the coordinates are RZ or XYZ.
    Args:
      self: Standard python object oriented notation. 
    Return value:
      True or false
    """
    return set(self.stepsize) == set(["r","z"])


  def getArgs(self):
    """
    Returns an unpacked list of arguments and key word arguments for use in add?grd.
    Args: 
      self: Standard python object oriented notation. 
    Return value:
       Dictionary with key field_type and a second dictionary with keys args and 
       key word args for the?add grd function.
    """
    output = {}
    for field_type,field in self.fields.iteritems():
      if field_type == "electric":
        field_abrv = "e"
      if field_type == "magnetic":
        field_abrv = "b"
      args_out = [self.zmin, self.zmax]
      kwargs_out = { }
      if self.isRZ():
        kwargs_out["rz"] = True
        kwargs_out["dx"] = self.stepsize["r"]
        kwargs_out["dy"] = self.stepsize["z"]
        kwargs_out["nx"] = self.number_of_steps["r"]
        kwargs_out["ny"] = self.number_of_steps["z"]
        kwargs_out[field_abrv+"x"] = field["r"]
        kwargs_out[field_abrv+"y"] = field["z"]
      else:
        kwargs_out["xs"] = self.xmin
        kwargs_out["ys"] = self.ymin
        kwargs_out["dx"] = self.stepsize["x"]
        kwargs_out["dy"] = self.stepsize["y"]
        kwargs_out["nx"] = self.number_of_steps["x"]
        kwargs_out["ny"] = self.number_of_steps["y"]
        kwargs_out["nz"] = self.number_of_steps["z"]
        kwargs_out[field_abrv+"x"] = field["x"]
        kwargs_out[field_abrv+"y"] = field["y"]
        kwargs_out[field_abrv+"z"] = field["z"]
      kwargs_out["func"] = self.time_dependent_function
      output[field_type] = {}
      output[field_type]["args"] = args_out
      output[field_type]["kwargs"] = kwargs_out
    return output
