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
from fields.time_dependent_functions import sine_at_com_distance
from warp import *

class FieldLoader(object):
  """
  An object to load preprocessed field and their 
  config files.
  """

  def __init__(self,config_filepath=None,config=None,section="field parameters",
               time_dependent_function=None, scale=1.0, **kwargs):
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
      current_position: The position of the center of mass of the pulse
        to be used if a distance needs to be calculated.
      time_dependent_function: An option function callback (function is a function of top.time)
        that can add time dependence to the field.  Default is no such function.
      scale: An option that provides a hook to scale the field(s) being loaded.
    """
    if config_filepath is None and config is None:
      raise Exception("Either the config_filepath needs to be specified or a config parser object " + 
                      "needs to be passed to the init function.")
    if config is None:
      config = ConfigParser()
      config.read(config_filepath)
    self.config = config
    self.section = section
    
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
          self.fields[field_type][component] = scale*np.array(self.fields[field_type][component],order="FORTRAN")
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

  def installFields(self,top):
    """
    Installs the fields within the top object.
    Args:
      self: Standard python object oriented notation. 
      top: The forthon top object generally loaded in warp applications.
    Return value:
      None --- although field id is written.
    """
    args_dict = self.getArgs()
    for field_type in args_dict:
      if "id" in self.fields[field_type].keys():
        raise KeyError("Field has already been installed.")
      if field_type == "electric":
        self.fields[field_type]["id"] = addnewegrd(*args_dict[field_type]["args"],**args_dict[field_type]["kwargs"])
      elif field_type == "magnetic":
        self.fields[field_type]["id"] = addnewbgrd(*args_dict[field_type]["args"],**args_dict[field_type]["kwargs"])

  def diagnosticPlots(self,top,**kwargs):
    """
    Plots the fields that have been installed.
    Args:
      self: Standard python object oriented notation. 
      top: The forthon top object generally loaded in warp applications.
    Return value:
      None
    """
    for field_type in self.fields.keys():
      if "id" in self.fields[field_type]: #Field has been installed.
        plot_field_diagnostics(top, field_type, self.fields[field_type]["id"], self.number_of_steps, "x", "x",**kwargs)
        plot_field_diagnostics(top, field_type, self.fields[field_type]["id"], self.number_of_steps, "x", "z",**kwargs)
        plot_field_diagnostics(top, field_type, self.fields[field_type]["id"], self.number_of_steps, "y", "y",**kwargs)
        plot_field_diagnostics(top, field_type, self.fields[field_type]["id"], self.number_of_steps, "y", "z",**kwargs)
        plot_field_diagnostics(top, field_type, self.fields[field_type]["id"], self.number_of_steps, "z", "x",**kwargs)
        plot_field_diagnostics(top, field_type, self.fields[field_type]["id"], self.number_of_steps, "z", "z",**kwargs)

def plot_field_diagnostics(top, field_type, grd_id, steps_dict, field_component, independent_variable,loops=True,**kwargs):
  """
  Standard plot for a single field component and independent variable.
  Args:
    top: The forthon top object generally loaded in warp applications.
    field_type: The type of field to be plotted.  Either "electric" or "magnetic" currently.
    grd_id: The grid id to plot.
    steps_dict: A dictionary with the number of steps in the x, y, and z direction.
    field_component: The component of the field desired to be plotted.
    independent_variable: The variable, x, y, or z, that will appear on the x-axis.  The other
      two variables will be plot-summed over.
  Return value:
    None - but writes to the cgm file.
  """
  if field_type == "electric":
    plot_func = plotegrd
  if field_type == "magnetic":
    plot_func = plotbgrd

  #Get the coordinates that are not the independent variable
  all_coordinates = set(steps_dict.keys())
  remaining_coordinates = list(all_coordinates.difference(set([independent_variable])))
  c1 = remaining_coordinates[0]
  ic1 = "i"+c1
  c2 = remaining_coordinates[1]
  ic2 = "i"+c2

  #Plot over all non-independent variable components.
  if loops:
    for i1 in range(steps_dict[c1]+1):
      temp_step_dict = { ic1:i1 }
      for i2 in range(steps_dict[c2]+1):
        temp_step_dict[ic2] = i2
        plot_func(grd_id[0],component=field_component,**temp_step_dict)
  else:
    temp_step_dict = { ic1:0, ic2:0 }
    plot_func(grd_id[0],component=field_component,**temp_step_dict)
  fma()
