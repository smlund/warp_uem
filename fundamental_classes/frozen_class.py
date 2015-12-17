class FrozenClass(object):
  """
  A class that prevents changing or adding attribues once
  they are set.
  """
  __isfrozen = False
  def __setattr__(self, key, value):
    if self.__isfrozen:
      raise TypeError( "%r is a frozen class" % self )
    object.__setattr__(self, key, value)

  def _freeze(self):
    self.__isfrozen = True

class PartiallyFrozenClass(object):
  """
  A class that prevents adding attribues once
  they are set.  Changing attributes is still
  allowed
  """
  __ispartiallyfrozen = False
  def __setattr__(self, key, value):
    if self.__ispartiallyfrozen and not hasattr(self, key):
      raise TypeError( "%r is a partially frozen class, so attributes cannot be set." % self )
    object.__setattr__(self, key, value)

  def _partially_freeze(self):
    self.__ispartiallyfrozen = True
