from numpy import *

def get_supremum_index(w3d,component,value):
  """
  Returns the index of the point in the component 
  mesh that has the smallest value greater than
  or equal to the supplied value.
  Args:
    w3d: The w3d object from warp.
    component: A string describing the axis
      for which we are finding the value, e.g. "x".
    value: The value for which we are seraching
  Return value:
    index: The index with the smallest value greater than 
      or equal to the supplied value.
  """
  return sum(where(getattr(w3d,component + "mesh") <= value,1,0))-1
