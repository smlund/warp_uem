import re
import numpy
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
    if not isinstance(current_attribute, numpy.ndarray):
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
