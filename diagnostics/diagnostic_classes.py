from fundamental_classes.user_event import UserEvent
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
        will be launched (my be decorated to launch steps.)
    """
    args = [top,steps]
    UserEvent.__init__(callback,args)

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
    if not(self.args[0].it in self.args[1]): #self.args[0] = top, self.args[1] = steps
      return #Only calls callback when current iteration is in the steps list.
    UserEvent.callFunction()
