import math
from scipy import constants
from coordinates.coordinate_vector import CoordinateException
from coordinates.coordinate_vector_3d import Cartesian3DVector

class ParticlePhaseCoordinates():
  """
  The phase coordinates for a particle in 6D.
  """

  def __init__(self,mass,x=None,p=None,v=None):
    """
    Uses the two input Cartesian3DVectors or 0,0,0 for each to define the
    attributes x and p. 
    """
    self.setPosition(x)
    self.setMass(mass)
    if p is not None and v is not None:
      raise CoordinateException("Initializing a particle can only have momentum or velocity, not both.")
    elif p is None:
      self.setVelocity(v)
      self.calcMomentumFromVelocity()
    elif v is None:
      self.setMomentum(p)
      self.calcVelocityFromMomentum()

  def setPosition(self,x):
    """
    The standard set function for position.
    """
    if x is None:
      self.x = Cartesian3DVector()
    else:
      if isinstance(x,Cartesian3DVector):
        self.x = Cartesian3DVector(x.x,x.y,x.z)
      else:
        raise CoordinateException("Initializing a particle with the incorrect position vector type.")
    
  def getPosition(self):
    """
    The standard get function for position.
    """
    return self.x

  def setMomentum(self,p):
    """
    The standard set function for momentum.
    """
    if p is None:
      self.p = Cartesian3DVector()
    else:
      if isinstance(p,Cartesian3DVector):
        self.p = Cartesian3DVector(p.x,p.y,p.z)
      else:
        raise CoordinateVector("Initializing a particle with the incorrect momentum vector type.")
  
  def getMomentum(self):
    """
    The standard get function for momentum.
    """
    return self.p

  def setMass(self,mass):
    """
    The standard set function for mass.
    """
    self.mass = mass

  def getMass(self):
    """
    The standard get function for mass.
    """
    return self.mass

  def setVelocity(self,v):
    """
    The standard set function.
    """
    if v is None:
      self.v = Cartesian3DVector()
    else:
      if isinstance(v,Cartesian3DVector):
        self.v = Cartesian3DVector(v.x,v.y,v.z)
      else:
        raise CoordinateVector("Initializing a particle with the incorrect velocity vector type.")

  def getVelocity(self):
    """
    The standard get fucntion for velocity.
    """
    return self.v

  def calcVelocityFromMomentum(self):
    """
    Calculates the cartesian 3d vector of velocity from the momentum and mass of the particle.
    """
    if self.mass is None:
      raise CoordinateVector("The particle mass needs to be specified to calculate the particle velocity from momentum.")
    values = {}
    for direction in self.p.order:
      gamma = self.calcLorentzGammaFromMomentum(direction)
      values[direction] = getattr(self.p,direction)/(gamma*self.mass)
    self.setVelocity(Cartesian3DVector(**values))
    return self.getVelocity()

  def calcMomentumFromVelocity(self):
    """
    Calculates the cartesian 3d vector of momentum from the velocity and mass of the particle.
    """
    if self.mass is None:
      raise CoordinateVector("The particle mass needs to be specified to calculate the particle momentum from velocity.")
    values = {}
    for direction in self.v.order:
      gamma = self.calcLorentzGammaFromVelocity(direction)
      values[direction] = getattr(self.v,direction)*gamma*self.mass
    self.setMomentum(Cartesian3DVector(**values))
    return self.getMomentum()

  def calcLorentzGammaFromMomentum(self,direction):
    """
    Calculates the lorenzt gamma in the provided direction from the momentum and mass of the particle.
    """
    if self.mass is None:
      raise CoordinateVector("The particle mass needs to be specified to calculate the lorentz gamma.")
    if direction not in self.x.order:   
      raise CoordinateVector("The direction, "+str(direction)+ " needs to be one of " +",".join(self.x.order) + " to calculated the lorentz gamma.")
    speed_light = constants.physical_constants["speed of light in vacuum"][0]#m/sec by default
    return math.sqrt(1 + (getattr(self.p,direction)/(self.mass*speed_light))**2)

  def calcLorentzGammaFromVelocity(self,direction):
    """
    Calculates the lorenzt gamma in the provided direction from the velocity of the particle expressed as a fraction of c.
    """
    if direction not in self.v.order:   
      raise CoordinateVector("The direction, "+str(direction)+ " needs to be one of " +",".join(self.x.order) + " to calculated the lorentz gamma.")
    speed_light = constants.physical_constants["speed of light in vacuum"][0]#m/sec by default
    return math.sqrt(1 /(1 - (getattr(self.v,direction)/speed_light)**2))

  def advancePosition(self,time):
    """
    Assuming no forces, advances the particle's position over the provided time.
    """
    velocity = self.getVelocity()
    return self.x + time*velocity

  def advanceVelocity(self,time,acceleration):
    """
    Advances the particle's momentum over the provided time.
    """
    if not isinstance(acceleration,Cartesian3DVector):
      raise CoordinateException("Advancing particle momentum with the incorrect acceleration type.")
    return self.v + time*acceleration

  def translate(self,translation_vector):
    """
    Returns a new particle with the translated position.
    """
    if not isinstance(translation_vector,Cartesian3DVector):
      raise CoordinateException("Translating a particle with the incorrect translation vector type.")
    new_particle = self.__class__(self.mass,self.x-translation_vector,self.p)
    return new_particle

  def getEnergy(self):
    """
    Wraps the calc energy method skipping it if the energy is already stored.
    """
    if not hasattr(self,"energy"):
      self.energy = self.calcEnergy()
    return self.energy

  def calcEnergy(self):
    """
    Calculates the energy of the particle in J.
    """
    speed_light = constants.physical_constants["speed of light in vacuum"][0]#m/sec by default
    if self.mass is None:
      raise CoordinateVector("The particle mass needs to be specified to calculate the energy.")
    return speed_light*math.sqrt(self.p*self.p + (self.mass*speed_light)**2)

  def getValueFromFieldname(self,fieldname):
    """
    Provides an interface between the attributes of the particle
    and special names that indicate components of Cartesian3DVectors 
    (like px and vy) and also E.
    """
    if hasattr(self,fieldname): #Standard attributes.
      value = getattr(self,fieldname)
      if not isinstance(value,Cartesian3DVector):
        return value
    if fieldname == "E": #Interprets E as energy
      return self.getEnergy()
    momentum_direction = fieldname.replace("p","")
    velocity_direction = fieldname.replace("v","")
    if fieldname.startswith("p") and momentum_direction in ["x","y","z"]:
      return getattr(self.p,momentum_direction)
    if fieldname.startswith("v") and velocity_direction in ["x","y","z"]:
      return getattr(self.v,velocity_direction)
    elif fieldname in ["x","y","z"]:
      return getattr(self.x,fieldname)
    raise Exception("The given field, "+fieldname+", is not defined for the particle.")

  def __str__(self):
    """
    Passes the string argument to the poistion and then momentum.
    """
    output = []
    output.append(str(self.x))
    output.append(str(self.p))
    return " ".join(output)

class TimedParticlePhaseCoordinates(ParticlePhaseCoordinates):
  """
  Adds the time attribute to the ParticlePhaseCoordinates
  and methods associated with tis attribute.
  """

  def __init__(self,mass,time,**kwargs):
    """
    Adds the time to the object and then passes control back to ParticlePhaseCoordinates()
    """
    self.setTime(time)
    ParticlePhaseCoordinates.__init__(self,mass,**kwargs)

  def setTime(self,time):
    """
    The standard set function for time.
    """
    self.time = time

  def getTime(self):
    """
    The standard get function for time.
    """
    return self.time
    
  def translate(self,translation_vector):
    """
    Returns a new particle with the translated position.
    """
    if isinstance(translation_vector,Cartesian3DVector):
      new_particle = self.__class__(self.mass,self.time,x=self.x-translation_vector,p=self.p)
      return new_particle
    raise CoordinateException("Translating a particle with the incorrect translation vector type.")

  def __str__(self):
    """
    Adds the time to the string argument from ParticlePhaseCoordinates.
    """
    return str(self.time)+" " + " ".join(ParticlePhaseCoordinates.__str__(self))
