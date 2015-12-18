from coordinates.coordinate_vector_3d import Cartesian3DVector
from warp import *

def steves_injectelectrons(top, phase_volume, electrons, flags={}):
  """
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
      phase_volume: A timed phase volume object containing the injection time 
        and the x, y, z an px, py, pz coordinates of the N particles.  A phase
        volume can be found in my coordinates package.
      electrons: A container holding the elctrons.
      flags: A dictionary of true/false flags.
    Return value:
      None --- although the electrons container is modified in place.
  """

  # Find macroparticles  between t and t + dt to inject 
  phase_volume_to_inject = phase_volume.getTimeSlice(top.time, top.time + top.dt)
  # add small number to insure z coordinate just to right of conductor 
  phase_volume_to_inject = phase_volume_to_inject.translate(Cartesian3DVector(0,0,top.smallpos))

  # Adjust particle coordinates (Nonrelativistic formulas) to inject 
  if "advance_position" in flags:
    if flags["advance_position"]:
      advance_position_over_remaining_time(phase_volume_to_inject,top.time+top.dt)
 
  #Get the position in the form necessary for warp, i.e. numpy.array.
  xinj = array(phase_volume_to_inject.getListFromFieldname("x"))
  yinj = array(phase_volume_to_inject.getListFromFieldname("y"))
  zinj = array(phase_volume_to_inject.getListFromFieldname("z"))

  # velocity correction using both E- and B-fields: B-field only 
  #   nonzero for EM fieldsolve 
  if "advance_velocity" in flags:
    if flags["advance_velocity"]:
      advance_position_over_remaining_time(phase_volume_to_inject,top.time+top.dt)

  #Get the velocity in the form necessary for warp, i.e. numpy.array.
  vxinj = array(phase_volume_to_inject.getListFromFieldname("vx"))
  vyinj = array(phase_volume_to_inject.getListFromFieldname("vy"))
  vzinj = array(phase_volume_to_inject.getListFromFieldname("vz"))
  
  #Get gammas:
  ginj = []
  for particle in phase_volume_to_inject:
    ginj.append(particle.calcLorentzGammaFromVelocity("z"))
  ginj = array(ginj)
  
  electrons.addparticles(x=xinj,y=yinj,z=zinj,vx=vxinj,vy=vyinj,vz=vzinj,gi=ginj)


def advance_position_over_remaining_time(phase_volume,goal_time):
  """
  Advances the particle from its attribute time to the goal time
  assuming 0 acceleration.
    Args:
      phase_volume: A timed phase volume object containing the injection time 
        and the x, y, z an px, py, pz coordinates of the N particles.  A phase
        volume can be found in my coordinates package.
      goal_time: The time to which we want our particle to progress.
    Return value:
      None --- although the particles objects are modified in place.
  """
  for particle in phase_volume:
    time = particle.getValueFromFieldname("time")
    particle.advancePosition(goal_time - time)

def advance_velocity_over_remaining_time(phase_volume,goal_time):
  """
  Advances the particle from its attribute time to the goal time
  assuming.
    Args:
      phase_volume: A timed phase volume object containing the injection time 
        and the x, y, z an px, py, pz coordinates of the N particles.  A phase
        volume can be found in my coordinates package.
      goal_time: The time to which we want our particle to progress.
    Return value:
      None --- although the particle objects are modified in place.
  """
  ex = zeros(ninj); ey = zeros(ninj); ez = zeros(ninj) 
  bx = zeros(ninj); by = zeros(ninj); bz = zeros(ninj)
  fetche3dfrompositions(electrons.sid,1,len(phase_volume_to_inject),xinj,yinj,zinj,ex,ey,ez,bx,by,bz)
  for i in range(len(phase_volume)):
    particle = phase_volume_to_inject.particles[i]
    time = particle.getValueFromFieldname("time")
    evector = Cartesian3DVector(ex,ey,ez)
    bvector = Cartesian3DVector(ex,ey,ez)
    acceleration = -(top.echarge/particle.mass)*(evector + particle.getVelocity().__cross_product__(bvector))
    particle.advanceVelocity(goal_time - time,acceleration)
