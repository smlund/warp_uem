import re
import numpy as np
from ConfigParser import *

class MyConfigParser(ConfigParser):
  """
  Extends config parser to do some post processing.
  """

  def get(self,section,key):
    """
    Translates the markup in the config file.  Specifically, 
    returns a dictionary if both ',' and ':' are present,
    returns a list if only ',' is present,
    and returns a variable if neither ',' nor ':' is present.
    Args:
      self: The MyConfigParser object.
      section: The string specifying the section of in
        the config from which to retrieve the key.
      key: The key within the section to retrieve the value.
    Return value:  
      value: The translated value in the form of a dict, list, or
        normal variable depending on encoding in the config string.
    """
    value = ConfigParser.get(self,section,key)
    if value.startswith('"') or value.startswith("'"):
      return value
    if re.search(r":",value):
      out_dict = {}
      pieces = valuesplit(",")
      for piece in pieces:
        key,v = piece.split(":")
        out_dict[key] = translate(v)
      return out_dict
    elif re.search(",",value):
       values = value.split(",")
       return [translate(v) for v in values]
    return translate(value)
      
  
  def safe_get(self,section,key,default_value=None):
    """
    Return either the value of the parameter or the default value if there is an exception.
    Args:
      self: The MyConfigParser object.
      section: The string specifying the section of in
        the config from which to retrieve the key.
      key: The key within the section to retrieve the value.
    Return value:
      value: Either the value form the get function or the default value if an exception
        is thrown.  
    """
    try:
      return self.get(section,key)
    except:
      return default_value

def translate(value):
  """
  A hook to replace specific words with python special values.
  Args:
    value: A string.
  Return value:
    value: Either a string or a special word in python.
  """
  if re.match(r"true",value,re.IGNORECASE) or re.match(r"t",value,re.IGNORECASE):
    return True
  if re.match(r"false",value,re.IGNORECASE) or re.match(r"f",value,re.IGNORECASE):
    return False
  if re.match(r"none",value,re.IGNORECASE):
    return None
  try:
    return int(value)
  except:
    pass
  try:
    return float(value)
  except:
    pass
  return value

def parse_key_as_numpy_array(obj, string, key, value):
  """
  Function to be used with set_attributes_with_config_section.
  Parses the key (config option) with the string to add
  numpy arrayed attributes to the obj.
  Arg:
    obj: The object to be edited.
    string: The string to use to split the key.
    key: The option taken from the section portion
      of the key.
    value: The value to set the attribute to.
  Return value: 
    The parsed key. 
  """
  match_string = "r"+'"'+string+'"'
  pieces = key.split(string)
  if len(pieces) > 1:
    attr = pieces.pop(0)
    if not hasattr(obj,attr):
      raise Exception("Cannot add a numpy array, only edit.")
    current_attribute = getattr(obj,attr)
    if not isinstance(current_attribute, np.ndarray):
      raise Exception("The atribute " + key + " of the object " + 
        obj.__name__ + " must be a numpy array a priori." )
    full_dim = []
    for i in range(len(pieces)):
      dim = pieces[i]
      dim_pieces = dim.split("-")
      if dim == "-":
        dim_len = current_attribute.shape[i]
        dim = slice(0,dim_len)
      elif len(dim_pieces) == 2:
        start, stop = dim.split("-")
        dim = slice(int(start),int(stop))
      full_dim.append(dim)
    current_attribute[full_dim] = value
    return full_dim
  return key

def handle_rz_1D_mesh_refinements(config,solver,elements,rmax,**kwargs):
  """
  Goes through the elements array and implements any refinement 
  assoiciated with the element that is stored in the config file.
  Args:
    config:  The configuration file where refinements may be defined
      in a section named "'element key' refinement'. 
    solver:  The solver object from warp.
    elements:  Elements being added to the simulation off
      which the refinement will be based.
  Return value:
    solver: A possibly editted solver object from warp.
  """
  for k, element in elements.container.iteritems():
    section_name = k + " refinement"
    print("Adding "+section_name)
    handle_section_named_refinement(config,solver,section_name,rmax,**kwargs)

def handle_section_named_refinement(config,solver,section_name,rmax=None,zmax=None,**kwargs):
  if config.has_section(section_name):
    reference_point = config.get(section_name,"reference_point")
    specified_mins = config.has_option(section_name,"grid_refinement_z_locations_mins")
    specified_maxs = config.has_option(section_name,"grid_refinement_z_locations_maxs")
    if not specified_mins and not specified_maxs:
      raise Exception("Refinement not provided mins or maxs.")
    if specified_mins:
      temp_mins = np.asarray(config.get(section_name,"grid_refinement_z_locations_mins"))
      mins = reference_point*np.ones(temp_mins.size) - temp_mins
    if specified_maxs:
      temp_maxs = np.asarray(config.get(section_name,"grid_refinement_z_locations_maxs"))
      maxs = reference_point*np.ones(temp_maxs.size) + temp_maxs
    if not specified_mins:
      mins = (reference_point)*np.ones(maxs.size)
    if not specified_maxs:
      maxs = (reference_point)*np.ones(maxs.size)
    if mins.size != maxs.size:
      raise Exception("Problem with mesh refinement.  The specified grid refinement bounds are of different sizes.")
    if rmax is not None:
      add_rz_z_1D_mesh_refinement(solver,mins,maxs,rmax,**kwargs)
    elif zmax is not None:
      add_rz_r_1D_mesh_refinement(solver,mins,maxs,zmax,**kwargs)
    else:
      add_rz_symmetric_1D_mesh_refinement(solver,mins,maxs,**kwargs)

def add_rz_z_1D_mesh_refinement(solver,mins,maxs,rmax,refinement_factor=2,**kwargs):
  """
  Adds mesh recursive refinement in the region demarcated by
  grid_refinement_z_locations_mins and grid_refinement_z_locations_maxs.
  If neither of these parameters is defined, skips this step.
  If only 1 is defined, the other is set to zcent +/- 0.5*length.
  Args:
    solver:  The solver object from warp.
    unspecified:  Optional argument telling the function whether to
      add (plus) or substract (minus) the length from zcent.
    mins: a list of all the mins for refinement
    maxs: a list of all the maxs for refinement
    refinement_factor = Specifies the extra number of grid points
      in the refined patch.
  Return value:
    solver: A possibly editted solver object from warp.
  """
  prev_refinement = solver
  for i in range(mins.size):
    current_min = mins[i]
    current_max = maxs[i]
    current_refinement = prev_refinement.addchild(mins=[0,0,current_min],maxs=[rmax,rmax,current_max],refinement=[1,1,refinement_factor])
    prev_refinement = current_refinement
  return solver

def add_rz_r_1D_mesh_refinement(solver,mins,maxs,zmax,refinement_factor=2,**kwargs):
  """
  Adds mesh recursive refinement in the region demarcated by
  grid_refinement_z_locations_mins and grid_refinement_z_locations_maxs.
  If neither of these parameters is defined, skips this step.
  If only 1 is defined, the other is set to zcent +/- 0.5*length.
  Args:
    solver:  The solver object from warp.
    unspecified:  Optional argument telling the function whether to
      add (plus) or substract (minus) the length from zcent.
    mins: a list of all the mins for refinement
    maxs: a list of all the maxs for refinement
    refinement_factor = Specifies the extra number of grid points
      in the refined patch.
  Return value:
    solver: A possibly editted solver object from warp.
  """
  prev_refinement = solver
  for i in range(mins.size):
    current_min = mins[i]
    current_max = maxs[i]
    current_refinement = prev_refinement.addchild(mins=[current_min,current_min,0],maxs=[current_max,current_max,zmax],refinement=[refinement_factor,refinement_factor,1])
    prev_refinement = current_refinement
  return solver

def add_rz_symmetric_1D_mesh_refinement(solver,mins,maxs,refinement_factor=2,**kwargs):
  """
  Adds mesh recursive refinement in the region demarcated by
  grid_refinement_z_locations_mins and grid_refinement_z_locations_maxs.
  If neither of these parameters is defined, skips this step.
  If only 1 is defined, the other is set to zcent +/- 0.5*length.
  Args:
    solver:  The solver object from warp.
    unspecified:  Optional argument telling the function whether to
      add (plus) or substract (minus) the length from zcent.
    mins: a list of all the mins for refinement
    maxs: a list of all the maxs for refinement
    refinement_factor = Specifies the extra number of grid points
      in the refined patch.
  Return value:
    solver: A possibly editted solver object from warp.
  """
  prev_refinement = solver
  for i in range(mins.size):
    current_min = mins[i]
    current_max = maxs[i]
    current_refinement = prev_refinement.addchild(mins=[current_min,current_min,current_min],maxs=[current_max,current_max,current_max],refinement=[refinement_factor,refinement_factor,refinement_factor])
    prev_refinement = current_refinement
  return solver
