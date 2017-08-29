import numpy as np
from collections import deque
from fundamental_classes.user_event import UserEvent
from diagnostics.phase_volume import dump_phase_volume
class DiagnosticsByTimes(UserEvent):
  """
  A class to provide the interface with the the diagnostics
  set up in warp so that the diagnositcs function runs
  at the specified times.  This is a little more 
  transparent then using UserEvent.
  """

  def __init__(self,callback,obj,top,times):
    """
    The init method captures what happens when instance = DiagnosticsBySteps()
    is called.  This passes the callback function and the 
    arguments for this callback function, namely top
    and steps, to the UserEvent.__init__ method.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
      callback: The function to that will be called when
        DiagnosticsBySteps.callFunction is called.
      obj: to be passed to function
      top: The top object from warp
      times:  A list of approximate times at which the diagnostics
        will be launched.  The program will launch the diagnostic
        at the first time that is equal or greater than the
        provided time.
    """
    args = [obj]
    additional_attr = {"top": top, "times": list(times)}
    UserEvent.__init__(self,callback,args,additional_attr) #This partially freezes the attributes

  def callFunction(self,*args,**kwargs):
    """
    The method that is passed to the decorator,
    i.e. installafterstep(self.callFunction) 
    This function adds the logic of checking the
    current iteration time against the times at which we'd 
    like to evaluate the callback function and passes
    the appropriate arguments to the callback.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
    """
    if len(self.times) == 0: #If no desired times are left, skip.
      return
    #Call the function at the first time greater than or equal to
    #the desired time then remove that desired time from list.
    if self.top.time >= self.times[0]: 
      self.removeFirstTime()
      UserEvent.callFunction(self,*args,**kwargs)
    return

  def removeFirstTime(self):
    """
    Removes the first time from the times attribute.
    """
    self.times.pop(0)

class DumpBySteps(UserEvent):
  """
  A class to provide the interface with the the dump
  set up in warp so that the dump function runs
  at the specified steps.  This is a little more 
  transparent then using UserEvent.
  """

  def __init__(self,callback,obj,mass,top,steps,**kwargs):
    """
    The init method captures what happens when instance = DiagnosticsBySteps()
    is called.  This passes the callback function and the 
    arguments for this callback function, namely top
    and steps, to the UserEvent.__init__ method.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
      callback: The function to that will be called when
        DiagnosticsBySteps.callFunction is called.
      obj: to be passed to function
      mass: The mass of the macroparticle used to do momentum conversion.
      top: The top object from warp
      steps:  A list of steps (iterations) at which the diagnostics
        will be launched.
    """
    args = [obj,mass]
    additional_attr = {"top": top, "steps": list(steps)}
    self.keywordargs = kwargs
    UserEvent.__init__(self,callback,args,additional_attr) #This partially freezes the attributes

  def callFunction(self,*args,**kwargs):
    """
    The method that is passed to the decorator,
    i.e. installafterstep(self.callFunction) 
    This function adds the logic of checking the
    current iteration against the steps at which we'd 
    like to evaluate the callback function and passes
    the appropriate arguments to the callback.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
    """
    if self.top.it not in self.steps:
      return #Only calls callback when current iteration is in the steps list.
    self.callback(self.top.it,*self.args,**self.keywordargs)#Star unpacks

class DumpAtLocations(UserEvent):
  """
  A class to provide the interface with the the dump
  set up in warp so that the dump function runs
  at specified positions.  This is a little more 
  transparent then using UserEvent.
  """

  def __init__(self,callback,obj,mass,location_keys,location_values):
    """
    The init method captures what happens when instance = DiagnosticsBySteps()
    is called.  This passes the callback function and the 
    arguments for this callback function, namely top
    and steps, to the UserEvent.__init__ method.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
      callback: The function to that will be called when
        DiagnosticsBySteps.callFunction is called.
      obj: to be passed to function and which contains z data
      mass: The mass of the macroparticle used to do momentum conversion.
      locations:  A dictionary of locations (z-position) at which the diagnostics
        will be launched.  The key will be used for saving the data.
    """
    args = [obj,mass]
    additional_attr = {"obj": obj, "file_prenames": deque(location_keys), "locations": deque(location_values)}
    UserEvent.__init__(self,callback,args,additional_attr) #This partially freezes the attributes

  def callFunction(self,*args,**kwargs):
    """
    The method that is passed to the decorator,
    i.e. installafterstep(self.callFunction) 
    This function adds the logic of checking the
    current iteration against the steps at which we'd 
    like to evaluate the callback function and passes
    the appropriate arguments to the callback.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
    """
    if len(self.locations) == 0:
      return
    if np.mean(self.obj.getz()) >= self.locations[0]:
      self.callback(self.file_prenames[0],*self.args)#Star unpacks
      self.locations.popleft()
      self.file_prenames.popleft()

class RecordTransitionTime(UserEvent):
  """
  A class to allow the recording of statistics
  for the electron ensemble as it
  enteres and leaves a region.  This is a little more 
  transparent then using UserEvent.
  """

  def __init__(self,dt,filepath,onset,offset,n,electrons):
    """
    The init method captures what happens when instance = DiagnosticsBySteps()
    is called.  This passes the callback function and the 
    arguments for this callback function, namely top
    and steps, to the UserEvent.__init__ method.
    Args:
      self: The RecordTransitionTime object --- standard notation
        for object oriented python.
      onset: The begining of the region
      offset: the ending of the region
    """
    self.complete = False
    self.states = []
    self.time_in =[]
    self.time_out = []
    for i in range(0,n):
      self.states.append("before")
      self.time_in.append(0)
      self.time_out.append(0)
    self.states = np.array(self.states)
    #self.time_in = np.array(self.time_in)
    #self.time_out = np.array(self.time_out)
    self.onset = onset
    self.offset = offset
    self.electrons = electrons
    self.time = [0,dt]
    self.filepath = filepath
    args = []
    additional_attr = {}
    UserEvent.__init__(self,None,args,additional_attr) #This partially freezes the attributes

  def callFunction(self,*args,**kwargs):
    """
    The method that is passed to the decorator,
    i.e. installafterstep(self.callFunction) 
    This function adds the logic of checking the
    current iteration against the 
    region and records any transition.
    Args:
      self: The RecordTransitionTime object --- standard notation
        for object oriented python.
    """
    self.time[0] += self.time[1]
    if not self.complete:
       z = self.electrons.getz()
       for i in range(0,self.electrons.getn()):
         if self.states[i] == "before" and z[i] >= self.onset:
           self.states[i] = "inside"
           self.time_in[i] = self.time[0]
         if self.states[i] == "inside" and z[i] >= self.offset:
           self.states[i] = "after"
           self.time_out[i] = self.time[0]
       self.complete = np.all(self.states == "after")
       if self.complete:
         dump_phase_volume("post_cavity",self.electrons,9.11e-31)
         with open(self.filepath,'w') as f:
           header = ["z","t_in","t_out","delta_t"]
           f.write(",".join(header))
           for i in range(0,self.electrons.getn()):
             output = []
             output.append(z[i])
             output.append(self.time_in[i])
             output.append(self.time_out[i])
             output.append(self.time_out[i]-self.time_in[i])
             f.write("\n")
             f.write(",".join(['{:.7E}'.format(o) for o in output]))
    return

