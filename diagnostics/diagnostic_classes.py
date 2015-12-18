from fundamental_classes.user_event import UserEvent
class DiagnosticsByTimes(UserEvent):
  """
  A class to provide the interface with the the diagnostics
  set up in warp so that the diagnositcs function runs
  at the specified times.  This is a little more 
  transparent then using UserEvent.
  """

  def __init__(self,callback,top,times):
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
      top: The top object from warp
      times:  A list of approximate times at which the diagnostics
        will be launched.  The program will launch the diagnostic
        at the first time that is equal or greater than the
        provided time.
    """
    args = [top]
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

class DiagnosticsBySteps(UserEvent):
  """
  A class to provide the interface with the the diagnostics
  set up in warp so that the diagnositcs function runs
  at the specified steps.  This is a little more 
  transparent then using UserEvent.
  """

  def __init__(self,callback,top,steps):
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
      top: The top object from warp
      steps:  A list of steps (iterations) at which the diagnostics
        will be launched.
    """
    args = [top]
    additional_attr = {"top": top, "steps": list(steps)}
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
    UserEvent.callFunction(self,*args,**kwargs)
