import numpy
import cPickle as pickle

def phase_volume_pickle_loader(pickle_dict_file,time_conversion=1.,
          position_conversion=1.,momentum_conversion=1.):
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
