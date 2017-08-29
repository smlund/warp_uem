from coordinates.coordinate_vector_3d import Cartesian3DVector
from warp import *

def steves_injectelectrons(top, t_inj, x_inj, y_inj, z_inj, px_inj, py_inj, pz_inj, charge_mass_ratio,
            electrons, flags={}):
  """
  I tried my own approach, but it was signifcantly slower and broken to boot (I see why, but I didn't
  fix it).  Returned to Steve's original code.
  Function to inject electrons macroparticles each time step.
    * Present version assumes nonrelativisit dynamics for all injected electrons.  After injection, 
      electrons can be advanced relativisitically or not depending on setting of top.lrelativ .  
    * Works by finding all birthed particles between present time (top.time) and next time step 
      (top.time + top.dt) and injecting those particles.   
    * If flag adj_inject = True/False, then injected particle coordinates are/are not 
      adjusted to account for difference of birth time and time at end of timestep. This just 
      adjusts positions in a free-streaming NR sense. If adj_inject_p = True/False the momenta/velocities 
      are also NR adjusted with the self-consistent EM-field data using the Lorentz force eqn.  
    * In the above correction of momenta/velocities the magnetic field will only be nonzero if the 
      simulation is electromagnetic.
    Args:
      top: The top object from warp.
      (t,x,y,z,px,py,pz)_inj: Numpy arrays with the time and phase coordinates of the particles.
      charge_mass_ratio: e/m_e
      electrons: A container holding the electrons.
      flags: A dictionary of true/false flags.
    Return value:
      None --- although the electrons container is modified in place.
  """
  # Find indices of injected electron macroparticle arrays between t and t + dt to inject 
  indices = where(logical_and(top.time < t_inj, t_inj <= top.time + top.dt))[0] 
  ninj = len(indices)
  # Extract macroparticle coordinates t, x,p to inject
  tinj = t_inj[indices] 
  xinj = x_inj[indices]
  yinj = y_inj[indices] 
  zinj = z_inj[indices] + smallpos  # add small no to insure z coordinate just to right of conductor  
  pxinj = px_inj[indices]
  pyinj = py_inj[indices]
  pzinj = pz_inj[indices]
  # Calculate macro particle velocities and inverse gamma factors to inject
  #ginj  = sqrt(1. + (pxinj**2 + pyinj**2 + pzinj**2)/(emass*clight)**2 )
  #giinj = 1./ginj
  giinj = ones(ninj)     # inverse gamma = 1., NR limit 
  vxinj = pxinj/top.emass 
  vyinj = giinj*pyinj/top.emass 
  vzinj = giinj*pzinj/top.emass 
  # Adjust particle coordinates (Nonrelativistic formulas) to inject 
  if "adjust_position" in flags.keys():
    if flags["adjust_position"]:
      xinj,yinj,zinj = advance_position_over_remaining_time(top.time+top.dt,tinj,xinj,yinj,zinj,
                         vxinj,vyinj,vzinj)
  if "adjust_velocity" in flags.keys():
    if flags["adjust_velocity"]:
      vxinj,vyinj,vzinj = advance_velocity_over_remaining_time(top.time+top.dt,tinj,xinj,yinj,zinj,
                            vxinj,vyinj,vzinj,charge_mass_ratio, electrons, top.dt)

  # Inject electron macroparticles 
  """
  print(xinj)
  print(yinj)
  print(zinj)
  print(vxinj)
  print(vyinj)
  print(vzinj)
  print(giinj)
  print(xinj.size)
  print(electrons.getn())
  """
  electrons.addparticles(x=xinj,y=yinj,z=zinj,vx=vxinj,vy=vyinj,vz=vzinj,gi=giinj)
  """print(electrons.getn())"""

def continue_injectelectrons(top, xinj, yinj, zinj, vxinj, vyinj, vzinj, electrons):
  """
  Function to inject electrons macroparticles all at once.
    Args:
      top: The top object from warp.
      (x,y,z,px,py,pz)_inj: Numpy arrays with the phase coordinates of the particles.
      electrons: A container holding the elctrons.
    Return value:
      None --- although the electrons container is modified in place.
  """
  # Calculate macro particle velocities and inverse gamma factors to inject
  giinj  = sqrt( 1.  - (vxinj**2 + vyinj**2 + vzinj**2)/(top.clight**2) )
  # Inject electron macroparticles 
  electrons.addparticles(x=xinj,y=yinj,z=zinj,vx=vxinj,vy=vyinj,vz=vzinj,gi=giinj)

def advance_position_over_remaining_time(goal_time,tinj,xinj,yinj,zinj,vxinj,vyinj,vzinj):
  """
  Advances the particle from its attribute time to the goal time
  assuming 0 acceleration.
    Args:
      goal_time: The time to which we want our particle to progress.
      (t,x,y,z,vx,vy,vz)_inj: Numpy arrays with the time, position 
        and velocity coordinates of the particles.
    Return value:
      (x,y,z)_inj: Numpy arrays with position coordinates of the particles.
  """
  dt = goal_time - tinj
  # coordinate correction 
  xinj += vxinj*dt 
  yinj += vyinj*dt 
  zinj += vzinj*dt 
  return (xinj,yinj,zinj)

def advance_velocity_over_remaining_time(goal_time,tinj,xinj,yinj,zinj,vxinj,vyinj,vzinj,charge_mass_ratio, electrons, dt):
  """
  Advances the particle from its attribute time to the goal time.
  velocity correction using both E- and B-fields: B-field only 
  nonzero for EM fieldsolve 
    Args:
      goal_time: The time to which we want our particle to progress.
      (t,x,y,z,vx,vy,vz)_inj: Numpy arrays with the time, position 
        and velocity coordinates of the particles.
    Return value:
      (vx,vy,vz)_inj: Numpy arrays with velocity coordinates of the particles.
  """
  ninj = len(xinj)
  ex = zeros(ninj) 
  ey = zeros(ninj)
  ez = zeros(ninj) 
  bx = zeros(ninj)
  by = zeros(ninj)
  bz = zeros(ninj)
  fetche3dfrompositions(electrons.sid,1,ninj,xinj,yinj,zinj,ex,ey,ez,bx,by,bz)
  vxinj += -charge_mass_ratio*ex*dt - charge_mass_ratio*(vyinj*bz-vzinj*by)*dt  
  vyinj += -charge_mass_ratio*ey*dt - charge_mass_ratio*(vzinj*bx-vxinj*bz)*dt 
  vzinj += -charge_mass_ratio*ez*dt - charge_mass_ratio*(vxinj*by-vzinj*bx)*dt 
  return (vxinj,vyinj,vzinj)
  
