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

class SingleElectronInjector(UserEvent):
  """
  Wraps the single injection (the whole ensemble) of electrons into 
  the simulation.
  """

  def __init__(self, callback, top, filepath, weight, **kwargs):
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
      filepath: Contains the file with particle coordinates in it
        in ascii format.
    """
    self.callback = callback
    [x, y, z, px, py, pz, vx, vy, vz] = getdatafromtextfile(filepath,nskip=0,dims=[9,None]) 
    electrons = Species(type=Electron,weight=weight,name="Electron")
    args=[top, x, y, z, vx, vy, vz, electrons]
    self.injected = False
    UserEvent.__init__(self,callback,args) #This partially freezes the attributes

  def callFunction(self): 
    """
    Wraps the callback function so that it is only called the first time 
    the callFunction is called.
    """
    if not self.injected:
      UserEvent.callFunction(self) #Inject electrons immediately.
      self.injected = True

  def getElectronContainer(self):
    """
    An interface to return the electrons that were originally created.
    Args:
      self: The ElectronInjector object --- standard notation
        for object oriented python.
    Return value:
      electrons: The container with the electrons in it.
    """
    return self.args[7]

  def getCoordinateArray(self,coordinate_name):
    """
    An interface to return the coordinates of the electrons before injection.
    Args:
      self: The ElectronInjector object --- standard notation
        for object oriented python.
      coordinate_name: One of x, y, z, px, py, or pz.
    Return value:
      The cooresponding numpy array.
    """
    keys=["x", "y", "z", "vx", "vy", "vz"]
    return self.args[keys.index(coordinate_name) + 1]

  def getDictOfCoordinateArrays(self):
    """
    An interface to return the coordinates of the electrons before injection
    as a dict of arrays.
    Args:
      self: The ElectronInjector object --- standard notation
        for object oriented python.
    Return value:
      The cooresponding numpy array.
    """
    out_dict = {}
    keys=["x", "y", "z", "vx", "vy", "vz"]
    for key in keys:
      out_dict[key] = self.getCoordinateArray(key)
    return out_dict
