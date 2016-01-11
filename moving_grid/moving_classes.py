from fundamental_classes.user_event import UserEvent
from moving_grid.moving_functions import sync_grid_to_com
class SyncToCOM(UserEvent):
  """
  A class to provide the interface for providing grid syncing to
  run at every step...
  """

  def __init__(self,top,particles):
    """
    The init method captures what happens when instance = SyncToCOM()
    is called.  This passes the callback function and the 
    arguments for this callback function, namely top
    and steps, to the UserEvent.__init__ method.
    Args:
      self: The SyncToCOM object --- standard notation
        for object oriented python.
      top: The top object from warp
      particles: A species container from warp
    """
    args = [top, particles]
    UserEvent.__init__(self,sync_grid_to_com,args) #This partially freezes the attributes

