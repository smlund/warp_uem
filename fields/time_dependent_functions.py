import types
from functools import wraps
import numpy as np
"""
Functions that return functions dependent on time that can 
be used to decorate time dependent function for use in
time dependent field elements.
"""

def sine_at_com_onset(amplitude,speed,distance,current_time,
                      field_length,phase_shift=0,
                      number_of_oscillations=1):
  """
  Defines and decorates a sine function field variation good for
  RF cavities.
  Args:
    amplitude:  The amplitude of the sine wave.  Used to scale the 
      field.
    speed: Speed of the COM of the pulse.  Used to calculate
      field frequency for the number of oscillations desired 
      as well as the time of pulse arrival at the onset of the
      field.
    distance: Distance from the COM of the pulse to the onset
      of the pulse.  Used to calculate the time of pulse arrival
      at the onset of the field.
    current_time: Used to calculate the absolute time of pulse arrival
      at the onset of the field.
    field_length: Used to calculate the duration of time in which
      the COM remains inside the field.  This is then used to determine
      the frequency.
    phase_shift: Specifies to what degree the sinusoidal should be shifted
      when the COM enters the field.  Default is no shift --- that is
      when the field is zero everywhere and is about to increase toward
      the positive.
    number_of_oscillations: The number of oscillations of the field while
      the COM is inside the field.  Used to determine the frequency.
      The number of oscillations needs to be an integer for this code to
      work.
  Return value:
   A sine function that will accept the argument time that can be used
   to add time dependence to fields. 
  """
  assert types.type(number_of_oscillations) is types.IntType, \
             "Number of oscillations is not an integer: %r" % number_of_oscillations
  pi = 3.1415926535897932384626433832795028841971693993751
  arrival_time = distance/speed + current_time

  duration = field_length/speed
  frequency = number_of_oscillations/duration
  omega = 2*pi*frequency

  def sine_function(time, amplitude=amplitude, arrival_time=arrival_time, 
                    omega=omega, phase_shift=phase_shift):
    """
    A local sine function decorated with the variables set up in sine_at_com_onset.
    Args:
      time: The time that will be supplied when this function is called.
      amplitude:  The amplitude of the sine wave.  Used to scale the 
        field.
      arrival_time: The time at which we are setting the 0 time.
      omega: The angular frequency.
      phase_shift: The phase value at the 0 time.
    Return value:
      The value of the sine function at the provided time.
    """
    return amplitude*np.sin(omega*(time-arrival_time) + phase_shift)

  return sine_function

def sine_at_com_distance(coordinate_array_dict,rf_onset,rf_length,amplitude,
                         current_time,frequency,jitter=0):
  """
  Defines and decorates a sine function field variation good for
  RF cavities where the sine functions value is set to zero when
  the pulse crosses the cavity mid-point.  This means that
  the number of oscillations can be any real number and the
  field length can remain unknown, but the frequency
  must be supplied.
  Args:
    coordinate_array_dict: A dictionary with at least the keys
      z, px, py, pz with values for the corresponding numpy arrays. 
    rf_onset:  The location where the rf_cavity begins.
    rf_legth:  The length of the rf_cavity.
    amplitude:  The amplitude of the sine wave.  Used to scale the 
      field.
    current_time: Used to calculate the absolute time of pulse arrival
      at the onset of the field.
    frequency:  Frequency of the sine wave. 
    field_length: Used to calculate the duration of time in which
      the COM remains inside the field.  This is then used to determine
      the frequency.
    jitter: Specifies to what degree the sinusoidal should be shifted
      when the COM enters the field.  Default is no jitter --- that is
      when the field is zero everywhere and is about to increase toward
      the positive.
  Return value:
   A sine function that will accept the argument time that can be used
   to add time dependence to fields. 
  """
  pi = 3.1415926535897932384626433832795028841971693993751
  clight = 299792458

  mean_z = np.mean(coordinate_array_dict["z"])
  distance = rf_onset - mean_z

  speed = np.mean(coordinate_array_dict["vz"])
  onset_time = distance/speed + current_time
  omega = 2*pi*frequency
  crossing_time = get_crossing_time(speed,rf_length,amplitude*omega)
  arrival_time = onset_time + 0.5*crossing_time

  print "speed = " + str(speed)
  print "distance = " + str(distance)
  print "amplitude = " + str(amplitude)
  print "crossing_time = " + str(crossing_time)
  print "arrival_time = " + str(arrival_time)
  print "omega = " + str(omega)
  print "jitter = " + str(jitter)

  def sine_function(time, amplitude=amplitude, arrival_time=arrival_time, 
                    omega=omega, jitter=jitter):
    """
    A local sine function decorated with the variables set up in sine_at_com_onset.
    Args:
      time: The time that will be supplied when this function is called.
      amplitude:  The amplitude of the sine wave.  Used to scale the 
        field.
      arrival_time: The time at which we are setting the 0 time.
      omega: The angular frequency.
      phase_shift: The phase value at the 0 time.
    Return value:
      The value of the sine function at the provided time.
    """
    value = amplitude*np.sin(omega*(time-arrival_time + jitter))
    return value
  
  return sine_function

def constant_scalor(scale):
  """
  Defines and decorates a constant function that returns the constant 
  scalor only.  There is no time dependence.  I'm using this to 
  simply scale my input field so that I need not need to create a 
  field file for each field I introduce.
  Args:
      scale:  A constant used to scale the field.
  """
  
  def constant_function(time,scale=scale):
    """
    A local function that has implicit dependence on time;
    however time only appears as an argument.  This allows us to 
    hijack the scaling of the field.
    Args:
      time: The time that will be supplied when this function is called.
      scale: A constant used to scale the field.
    """
    return scale

  return constant_function
    
def get_crossing_time(velocity,rf_length,jerk):
  """
  Returns the time it takes the center (no velocity change from
  before to after the rf_cavity) to propogate across the rf
  cavity assuming the jerk is constant.  The solution is the root 
  of the cubic polynomial that is is closest to the solution when 
  jerk = 0.
  """
  polynomial_coefficients = [ jerk/12., 0., -velocity, rf_length ]
  roots = np.roots(polynomial_coefficients)
  best_solution = None
  difference = None
  for root in roots:
    if np.isreal(root):
      if best_solution is None:
        best_solution = root
        difference = abs(root - rf_length/velocity)
        continue
      current_difference = abs(root - rf_length/velocity)
      if current_difference < difference:
        best_solution = root
        difference = abs(root - rf_length/velocity)
  return np.real(best_solution)
