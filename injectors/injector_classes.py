from fundamental_classes.user_event import UserEvent
from injectors.io import phase_volume_pickle_loader
from warp import * #Need for species
class ElectronInjector(UserEvent):
  """
  A class to provide the interface with the the injector
  set up in warp.  This is a little more 
  transparent then using UserEvent by itself.
  """

  def __init__(self, callback, top, filepath,
               chage_mass_ratio, weight, flags={},**kwargs):
    """
    The init method captures what happens when instance = ElectronInjector()
    is called.  This passes the callback function and the 
    arguments for this callback function, namely top, phase_volume, electrons,
    and flags, to the UserEvent.__init__ method.
    Args:
      self: The ElectronInjector object --- standard notation
        for object oriented python.
      callback: The function to that will be called when
        injection is called.
      top: The top object from warp.  This is passed so that it is accessible
        by the callback function for electron injecton.
      phase_volume: A timed phase volume object containing the injection time 
        and the x, y, z an px, py, pz coordinates of the N particles.  A phase
        volume can be found in my coordinates package.
      flags: A dictionary of additional terms that can be passed to
        the callback function.  This is meant to hold True/False flags.
    """
    self.callback = callback
    t, x, y, z, px, py, pz = phase_volume_pickle_loader(filepath,**kwargs)
    electrons = Species(type=Electron,weight=weight,name="Electron")
    args=[top, t, x, y, z, px, py, pz, chage_mass_ratio, electrons, flags]
    UserEvent.__init__(self,callback,args) #This partially freezes the attributes

  #def callFunction(self): This method is inherited from UserEvent

  def getElectronContainer(self):
    """
    An interface to return the electrons that were originally created.
    Args:
      self: The ElectronInjector object --- standard notation
        for object oriented python.
    Return value:
      electrons: The container with the electrons in it.
    """
    return self.args[9]
