class DiagnosticsBySteps():
  """
  A class to provide the interface with the the diagnostics
  set up in warp.
  """

  def __init__(self,top,steps,callback):
    """
    The init method captures what happens when instance = DiagnosticsBySteps()
    is called.  Specifically, the steps at which the diagnostics
    callback function and the callback itself are both set.
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
      top: The top object from warp
      steps:  A list of steps (iterations) at which the diagnostics
        will be launched (my be decorated to launch steps.)
      callback: The function to that will be called when
        DiagnosticsBySteps.callFunction is called.
    """
    self.top = top
    self.steps = steps
    self.callback = callback

  def callFunction(self,*args,**kwargs):
    """
    The method that is passed to the decorator,
    e.g. installafterstep(self.callFunction) 
    Decorated variables:
      top: taken from the warp simulation setup
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
      *args: A pointer to a list of arguments to be passed to internal
        functions.  Again, standard notation.
     **kwargs: A pointer to a dict of argument ("key word arguments") to
        be passed to internal functions.  Again, standard notation.
    """
    if not(self.top.it in self.steps): return
    self.callback(self.top,*args,**kwargs)
