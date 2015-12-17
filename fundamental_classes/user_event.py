from fundamental_classes.frozen_class import PartiallyFrozenClass
class UserEvent(FrozenClass):
  """
  A class to provide the interface to allow passing
  arguments to functions that are called by warp's
  decoraters.  Attributes cannot be added or changed after
  initialization due to the inheritance of the
  frozen class.
  """

  def __init__(self,callback,args=[],additional_attributes={}):
    """
    The init method captures what happens when instance = UserEvent()
    is called.  Specifically, this allows us to store and then
    pass the arguments we set here.
    Args:
      self: The UserEvent object --- standard notation
        for object oriented python.
      callback: The function to that will be called when
        UserEvent.callFunction is called.
      arg: An ordered list of argument in the order they
        should be passed to the callback function.
      additional_attributes: A dict containing the names (string)
        and values of additional attributes to be set.  These
        attributes will not be passed to the callback.  Instead,
        this provides a hook to providing logic during 
        a captured callFunction method.
    """
    self.callback = callback
    self.args = args
    for key, value in additional_attributes.iteritems():
      setattr(self,key,value)
    self._freeze()

  def callFunction(self):
    """
    The method that is passed to the decorator,
    i.e. installafterstep(self.callFunction) 
    This method essentially just calls the callback with
    the args. 
    Args:
      self: The DiagnosticsBySteps object --- standard notation
        for object oriented python.
    """
    self.callback(*self.args)#Star unpacks
