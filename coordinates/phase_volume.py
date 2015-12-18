import argparse
import math
import pickle
from scipy import constants
from coordinates.coordinate_vector import CoordinateException
from coordinates.coordinate_vector_3d import Cartesian3DVector
from coordinates.my_covariance_matrix import MyCovarianceMatrix
from coordinates.particle_coordinates import ParticlePhaseCoordinates, TimedParticlePhaseCoordinates

class Phase6DVolume():
  """
  An ensemble of 3D position and 3D momentum vectors.
  """

  def __init__(self,particle_type=ParticlePhaseCoordinates):
    """
    Initializes the phase volume to an empty list and sets the
    attribute type.  Type will determine what type of particles
    to include.
    """
    self.particles = []
    particle_type_options = [ParticlePhaseCoordinates, TimedParticlePhaseCoordinates]
    if particle_type not in particle_type_options:
      raise CoordinateException("The only particle options for Phase6DVolume are: " + " ".join(particle_type_options))
    self.particle_type = particle_type

  def __len__(self):
    return len(self.particles)

  def addParticle(self,mass,*args,**kwargs):
    """
    If x is a particle, then it is added, otherwise, a new particle 
    is initialized with the cartesian coordinates x and p.
    """
    if isinstance(mass,self.particle_type): #Mass is actually the particle here.
      self.particles.append(mass)
    else:
      particle = self.particle_type(mass,*args,**kwargs)
      self.particles.append(particle)

  def translate(self,translation_vector):
    """
    Translates the phase volume to a new coordinate systems
    and returns the translated phase volume.
    """
    new_phase_volume = self.__class__()
    for particle in self:
      new_phase_volume.addParticle(particle.translate(translation_vector))
    return new_phase_volume

  def __iter__(self):
    """
    Allows the ability to iterate over the particles in
    phase space without referencing the particels themselves.
    """
    for particle in self.particles:
      yield particle

  def __str__(self):
    """
    Wraps the str function so that the entire phase space may be printed.
    """
    output = []
    for particle in self:
      output.append(str(particle))
    return "\n".join(output)

  def injectFile(self,filepath,mass=1,header=False,fieldnames=["x","y","z","px","py","pz"],delimiter=" "):
    """
    Reads in the file from filepath and extracts the phasespace according to
    the split on the delimiter.  Fieldnames are only used if header is false, otherwise
    they are derived from the header.  If no fieldname called "mass" is used, the mass of
    the particle is set to mass.
    """
    with open(filepath,'r') as f:
      for line in f:
        line = line.rstrip()
        line = line.lstrip(" ")
        if header == True:
          header = False
          fieldnames = line.split(delimiter)
          continue
        pieces = line.split(delimiter)
        pieces = [p for p in pieces if p != '']
        if len(pieces) != len(fieldnames):
          print pieces
          print fieldnames
          raise Exception("The format of " + filepath + " is inconsistent.")
        row = dict(zip(fieldnames,pieces))
        position = Cartesian3DVector(row["x"],row["y"],row["z"])
        momentum = Cartesian3DVector(row["px"],row["py"],row["pz"])
        self.addParticle(mass,x=position,p=momentum)
        
  def getMean(self,fieldnames):
    """
    Checks to see if the mean has already been caclulated.  If so, return
    the previously identified mean.  Otherwise, calculate the mean and store
    if for later retrieval and returning.
    """
    if not hasattr(self,"means"):
      self.means = {}
    sortedfieldnames = sorted(fieldnames)
    fieldname_key = ",".join(sortedfieldnames)
    if fieldname_key not in self.means:
      self.means[fieldname_key] = self.calcMean(fieldnames)
    return self.means[fieldname_key]

  def calcMean(self,fieldnames):
    """
    This finds the mean of the product of the fieldnames across the ensemble
    of particles.  The mean is calculated with 1/N where N is the number of particles.
    I thought about this, but I think correcting to 1/(N-len(fieldnames)) is not
    appropriate in this instance.
    """
    total = 0
    for particle in self:
      product = 1.
      for fieldname in fieldnames:
        product *= particle.getValueFromFieldname(fieldname)
      total += product
    return total/len(self)

  def getCovarianceMatrix(self,recalculate=False):
    """
    Wraps the calculation of the covariance matrix.  If it has previously been
    calculated, then skip the calculation.  Returns the 7 x 7 matrix.
    """
    if recalculate or not hasattr(self,"cov_matrix"):
      self.cov_matrix = MyCovarianceMatrix(self)
    return self.cov_matrix

  def getListFromFieldname(self, fieldname):
    """
    Returns a list of all of the fieldname values of the particles.
    """
    output = []
    for particle in self:
      output.append(particle.getValueFromFieldname(fieldname))
    return output

class TimedPhase6DVolume(Phase6DVolume):
  """
  A class to provide the functions we'd like for the timed particles.
  """

  def __init__(self,particle_type=TimedParticlePhaseCoordinates):
    Phase6DVolume.__init__(self,particle_type)

  def getTimeSlice(self,min_time,max_time):
    """
    Returns a TimedPhase6DVolume containing all of the particles
    with time > min_time and less than or equal to max_time.
    """
    new_phase_volume = self.__class__()
    for particle in self:
      if particle.time > min_time and particle.time <= max_time:
        new_phase_volume.addParticle(particle)
    return new_phase_volume

  def injectPickleDict(self,filepath,mass,position_conversion=1.,momentum_conversion=1.):
    """
    Adds the particles in the pckl dict to the object.
    """
    data_dict = pickle.load( open( filepath, "r" ) )
    for row in data_dict:
      position = Cartesian3DVector(row["x"]*position_conversion,
                                   row["y"]*position_conversion,
                                   row["z"]*position_conversion)
      momentum = Cartesian3DVector(row["px"]*momentum_conversion,
                                   row["py"]*momentum_conversion,
                                   row["pz"]*momentum_conversion)
      self.addParticle(mass,row["t"],x=position,p=momentum)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Test functions in this package and use simple commands to get some of the straightforward methods.')
  parser.add_argument('coordinates_files', nargs='+', type=str, help='The path(s) to the phase volume files containing the phase space and therefore specifying that the injection function should be tested.')
  parser.add_argument('-c','--covariance_matrix', dest="covariance_matrix", action="store_true", help='Prints out the upper triangular form of the covariance matrix.', default=False)
  parser.add_argument('-r','--correlation_matrix', dest="correlation_matrix", action="store_true", help='Prints out the upper triangular form of the correlation matrix.', default=False)
  parser.add_argument('-e','--emittances', dest="emittances", action="store_true", help='Prints out the emittances for the phase volume.', default=False)
  parser.add_argument('--mixed_matrix', dest="mixed_matrix", action="store_true", help='Prints out the upper triangular form of the correlation matrix with variance along diagonal.', default=False)
  parser.add_argument('--sub_determinant', dest="sub_determinant", action="store_true", help='Prints the determinant of the phase space portion of the covariance matrix.', default=False)
  parser.add_argument('-m','--number_of_electrons_per_macroparticle', dest="number_of_electrons_per_macroparticle", type=int, help='The number of electrons per macroparticle for the simulation.  This defaults to 100 unless specified.', default=100)
  args = parser.parse_args()

  mass_of_electron = constants.physical_constants["electron mass energy equivalent in MeV"][0]
  mass_of_macroparticle = args.number_of_electrons_per_macroparticle*mass_of_electron

  phase_volume = Phase6DVolume()
  for path in args.coordinates_files:
    phase_volume.injectFile(path,mass=mass_of_macroparticle)

  if args.covariance_matrix:
    cov_matrix = phase_volume.getCovarianceMatrix()
    cov_matrix.printCovarianceMatrix()

  if args.correlation_matrix:
    cov_matrix = phase_volume.getCovarianceMatrix()
    cov_matrix.printCorrelationMatrix()

  if args.mixed_matrix:
    cov_matrix = phase_volume.getCovarianceMatrix()
    cov_matrix.printMixedMatrix()

  if args.sub_determinant:
    cov_matrix = phase_volume.getCovarianceMatrix()
    print cov_matrix.getSubDeterminant()
 
  if args.emittances:
    cov_matrix = phase_volume.getCovarianceMatrix()
    print "ex"
    print math.sqrt(cov_matrix.getSubDeterminant(["x","px"]))/mass_of_macroparticle
    print "ey"
    print math.sqrt(cov_matrix.getSubDeterminant(["y","py"]))/mass_of_macroparticle
    print "ez"
    print math.sqrt(cov_matrix.getSubDeterminant(["z","pz"]))/mass_of_macroparticle


