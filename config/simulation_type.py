from warp import *

def get_mesh_symmetry_factor(simtype,top,w3d):
  """
  Gets the symmetry factor based on the simulation type
  and the parameters stored in the w3d object.
  Args:
    simtype: The type of simulation.  Supports "w3d" and "wrz" currently.
    top: The top object from warp.
    w3d: The w3d object from warp.
  Return value:
    symmetry_factor: either 1 or 2.
  """
  if simtype == "w3d":
    if w3d.l4symtry: 
      return 1
    else:
      return 2
  elif simtype == "wrz":
    return 1 
  raise Exception("Error: simtype not defined")

def get_solver(simtype,top,w3d):
  """
  Gets the solver for the type of simulation we are running
  and sets the appropriate attribute of the w3d object.
  Args:
    simtype: The type of simulation.  Supports "w3d" and "wrz" currently.
    top: The top object from warp.
    w3d: The w3d object from warp.
  Return value:
    solver: A solver object from warp.  Also, edits w3d in place.
  """
  if simtype == "w3d":
    # --- 3D ES
    return MultiGrid3D()
  elif simtype == "wrz":
    # r-z ES
    w3d.solvergeom = w3d.RZgeom
    return MultiGrid2D()
  raise Exception("Error: simtype not defined")
