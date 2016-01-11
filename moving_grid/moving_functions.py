import numpy as np
def sync_grid_to_com(top,particles):
  """
  Sets the velocity of the grid to average velocity of the particles.
  Args:
    top: object from warp.
    particles: A species object from warp.
  Return value:
    None --- but alters the velocity of the grid.
  """
  if particles.getn() == 0:
    top.vbeamfrm = 0
  else:
    top.vbeamfrm = np.mean(particles.getvz())
