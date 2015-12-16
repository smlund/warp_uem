from numpy import *

def get_steps_by_regular_time_interval(times, stepsize, max_time=None):
  """
  Returns a list of iteration steps corrsponding to multiple of 
  the stepsize time.
  Args:
    times: A list of times corresponding to when
      a simulation step will occur.
    stepsize: A time-interval at which we chose times
      to identify their time steps
    max_time:  The max time value to evaluate.  If this
      is None, the max of times is taken.
  Return value:
    time_steps: The integer steps corresponding to the 
      least time greater than the chosen times.
  """
  if max_time is None:
    max_time = times[-1]
  chosen_times = arange(stepsize,max_time,stepsize) 
  return get_steps_by_times(times,chosen_times)

def get_steps_by_times(times,chosen_times):
  """
  Returns a list of iteration steps (think indices)
  corresponding to the first time after each of the
  sorted eval_times.
  Args:
    times: A list of times corresponding to when
      a simulation step will occur.
    chosen_times: A list of approximate times at which 
      we wish to get the time step.
  Return value:
    time_steps: The integer steps corresponding to the 
      least time greater than the chosen times.
  """

  time_steps = []
  chosen_index = 0
  for i in range(len(times)):
    if times[i] >= chosen_times[chosen_index]:
      time_steps.append(i)
      chosen_index += 1
      if chosen_index == len(chosen_times): #We're done
        return time_steps
  if chosen_index != len(chosen_times): #In case the last chosen time(s) is past the end of times. 
    time_steps.append(i)
  return time_steps
