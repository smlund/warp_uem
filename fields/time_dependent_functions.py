import types
import numpy as np
"""
Functions that return functions dependent on time that can 
be used to add time dependence to field elements.
"""

def sine_at_com_onset(speed,distance,current_time,
                                      field_length,phase_shift=0,
                                      number_of_oscillations=1):
  """
  Defines and decorates a sine function field variation good for
  RF cavities.
  Args:
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
  assert types.type(number_of_oscillations) is types.IntType, 
             "Number of oscillations is not an integer: %r" % number_of_oscillations
  pi = 3.1415926535897932384626433832795028841971693993751
  arrival_time = distance/speed + current_time

  duration = field_length/speed
  frequency = number_of_oscillations/duration
  omega = 2*pi*frequency

  def sine_function(time, arrival_time=arrival_time, omega=omega, phase_shift=phase_shift):
    """
    A local sine function decorated with the variables set up in sine_at_com_onset.
    Args:
      time: The time that will be supplied when this function is called.
      arrival_time: The time at which we are setting the 0 time.
      omega: The angular frequency.
      phase_shift: The phase value at the 0 time.
    Return value:
      The value of the sine function at the provided time.
    """
    return np.sin(omega*(time-arrival_time) + phase_shift)
  
  return sine_function
