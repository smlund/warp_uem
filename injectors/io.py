import numpy
import cPickle as pickle

def phase_volume_pickle_loader(pickle_dict_file,time_conversion=1.,
          position_conversion=1.,momentum_conversion=1.,**kwargs):
  """
  Read in the initial conditions data that is stored in a pickled
  dict.
  Args:
    pickle_dict_file: The pickle file from which we will read.
    *_conversion: Will multiply the corresponding coordinates
      to convert them to appropriate coordinates
  Return value:
    (t,x,y,z,px,py,pz) : The phase coordinates for the N particles
      stored as single dimensioned numpy arrays. 
  """
  ff = open(pickle_dict_file, 'r')
  dd = pickle.load(ff)
  ff.close() 

  # --- create ... arrays to store data  
  n  = len(dd)
  t  = numpy.zeros(n)  
  x  = numpy.zeros(n) 
  y  = numpy.zeros(n) 
  z  = numpy.zeros(n) 
  px = numpy.zeros(n) 
  py = numpy.zeros(n) 
  pz = numpy.zeros(n) 

  # --- place data in ... arrays.   
  for ii in range(n):
    row = dd[ii]
    t[ii] = row['t']*time_conversion
    #
    x[ii] = row['x']*position_conversion
    y[ii] = row['y']*position_conversion
    z[ii] = row['z']*position_conversion
    # 
    px[ii] = row['px']*momentum_conversion 
    py[ii] = row['py']*momentum_conversion
    pz[ii] = row['pz']*momentum_conversion

  return (t,x,y,z,px,py,pz)


def get_pulse_velocity_from_momentum(coordinate_array_dict,mass,direction="z"):
  """
  Calculates the boost to the mean "particle" assuming the mean
  momentums in the other two directions are 0. 
  Args:
    coordinate_array_dict: A dictionary with at least the keys
      z, px, py, pz with values for the corresponding numpy arrays. 
    mass: Mass of the particle to rescale the momentum.
    direction: The desired direction for which the velocity will be calculated.
  Return value:
    The mean velocity in the provided direction.
  """
  clight = 299792458
  mean_p = numpy.mean(coordinate_array_dict["p"+direction])
  gamma  = numpy.sqrt(1. + (mean_p/(mass*clight))**2 )
  return mean_p/(mass*gamma)
