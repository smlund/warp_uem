import numpy as np

def get_supremum_index(numpy_array,value):
  """
  Returns the index of the point in the component 
  mesh that has the smallest value greater than
  or equal to the supplied value.
  Args:
    numpy_array: A numpy array
    value: The value for which we are seraching
  Return value:
    index: The index with the smallest value greater than 
      or equal to the supplied value.
  """
  return np.sum(np.where(numpy_array <= value,1,0))-1

def get_index_of_point(numpy_array,stepsize):
  """
  Returns a numpy array of the indices associted with
  the numpy array given the stepsize.
  Args:
    numpy_array: The entire array of points that will
      fit a single dimension of a grid.
    stepsize: The discrete distance between steps in
      that dimension.
  Return value:
    numpy_indices: A numpy array with the indices.
  """
  output = np.around( ( numpy_array-numpy_array.min() )/stepsize ) 
  return np.array([int(o) for o in output])

def r_mesh_to_xy_mesh(r_array,scale=2.0,**kwargs):
  """
  Returns a square mesh describing the circle represented by  r_array (assuming
  invariance by rotation) using the stepsize for x,y of dr/scale.
  Args:
    r_array: A numpy array.
    scale: The amount by which we will divide the stepsize in r to get the
      stepsizes for x and y.
  Return value:
    Two numpy arrays, x and y, and their stepsizes, dx and dy.
  """
  #Extract r stats to be used.
  rmin = 0
  rmax = r_array.max()
  dr = np.average( np.diff( np.unique(r_array) ) )
  
  #Derive important stats for x and y.
  dx = dr/scale
  xmin = -rmax
  nmax = np.ceil(rmax/dx) #Box has x = rmax.
  n = int(2*nmax)+1
  
  #Create and fill the x y arrays
  x = np.zeros(n**2)
  y = np.zeros(n**2)
  for i in range(n):
    val = xmin + i*dx
    xslice = range(i,n**2,n) #Every nth element starting with the ith element.
    yslice = slice(i*n,(i+1)*n) #The ith block of n consequetive elements.
    x[xslice] = val
    y[yslice] = val
  return (x, y, dx, dx, n-1, n-1)

def linear_field_projection_from_r_to_xy(r_array, fr, fz, x_array, y_array):
  """
  Uses a linear interpolation on x y points that fall within
  rmin to rmax and a linear extrapolation on the points that
  fall outside of this interval.
  Args:
    r_array: A numpy array of radial values.
    fr: A numpy array of the tangent field in the r direction at 
      at each r point in the r numpy array.
    fz: A numpy array of the tangent field in the z direction at 
      at each r point in the r numpy array.
    x_array: The x points onto which we plan on projecting.
    y_array: The y points onto which we plan on projection.
  Return value:
    fx_out: A numpy array of the tangent field in the x direction at 
      at each x outer_product y point.
    fy_out: A numpy array of the tangent field in the y direction at 
      at each x outer_product y point.
    fz_out: A numpy array of the tangent field in the z direction at 
      at each x outer_product y point.
  """
  #Extract r stats to be used.
  rmin = 0
  rmax = r_array.max()
  dr = np.average( np.diff( np.unique(r_array) ) )

  #Initialize and fill tangent field elements.
  fx_out = np.zeros(x_array.size)
  fy_out = np.zeros(x_array.size)
  fz_out = np.zeros(x_array.size)
  for i in range(x_array.size):
    x = x_array[i]
    y = y_array[i]
    r_xy = np.sqrt( x**2 + y**2 )
    if r_xy == 0:
      fx_out[i] = fr[0]
      fy_out[i] = fr[0]
      fz_out[i] = fz[0]
      continue
    elif r_xy == rmin: #Just the first element
      fr_to_use = fr[0]
      fz_to_use = fz[0]
    elif r_xy == rmax: #Just the last element
      fr_to_use = fr[-1]
      fz_to_use = fz[-1]
    elif r_xy < rmin: #extrapolation from the first element.
      fr_slope = (fr[1]-fr[0])/dr
      dfr = fr_slope * (rmin-r_xy)
      fz_slope = (fz[1]-fz[0])/dr
      dfz = fz_slope * (rmin-r_xy)
      fr_to_use = (fr[0]-dfr)
      fz_to_use = (fz[0]-dfz)
    elif r_xy > rmax: #extrapolation from the last element.
      fr_slope = (fr[-1]-fr[-2])/dr
      dfr = fr_slope * (r_xy-rmax)
      fz_slope = (fz[-1]-fz[-2])/dr
      dfz = fz_slope * (r_xy-rmax)
      fr_to_use = (fr[-1]+dfr)
      fz_to_use = (fz[-1]+dfz)
    else:
      supremum_index = get_supremum_index(r_array,r_xy)
      r_lower = r_array[supremum_index]
      r_upper = r_array[supremum_index+1]
      fr_lower = fr[supremum_index]
      fr_upper = fr[supremum_index+1]
      fz_lower = fz[supremum_index]
      fz_upper = fz[supremum_index+1]
      fr_to_use = fr_lower*(r_xy-r_lower)/dr + fr_upper*(r_upper-r_xy)/dr #Linear interpolation
      fz_to_use = fz_lower*(r_xy-r_lower)/dr + fz_upper*(r_upper-r_xy)/dr #Linear interpolation
    fx_out[i] = fr_to_use*x/r_xy
    fy_out[i] = fr_to_use*y/r_xy
    fz_out[i] = fz_to_use
  return (fx_out, fy_out, fz_out)
