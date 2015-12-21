from config.my_config import MyConfigParser
from class_and_config_conversion import import_classes_from_config_file
class Elements(object):
  """
  Currently just a class to hold elements.
  """

  def __init__(self):
    """
    Initializes the dict in which the elements will be stored.
    Args:
      self:  Standard python object notation for the instance.
    Return value:
      The instance.
    """
    self.container = {}

  def addElement(self,element_name,element):
    """
    Adds an element to the container.
    Args:
      self:  Standard python object notation for the instance.
      element_name: The name by which the element will be known.
      element: The element to be added.
    Return value:
       None --- although the container dict is altered.
    """
    self.container[element_name] = element

  def getElement(self,element_name):
    """
    Adds an element to the container.
    Args:
      self:  Standard python object notation for the instance.
      element_name: The name by which the element will be known.
    Return value.
      element: The element with the give element name.
    """
    return self.container[element_name]

  def __getattr__(self,attr_name):
    """
    Captures the __get_attr__ method and inserts 
    getElement before the typical __getattr__.
    Args:
      self:  Standard python object notation for the instance.
      attr_name: The name of an element or a standard attribute.
    Return value:
      The element or attribure or error.
    """
    try:
      return self.getElement(attr_name)
    except:
      return object.__getattr__(self,attr_name)

  def __iter__(self):
    """
    Captures the iteration over the elements.
    Args:
      self:  Standard python object notation for the instance.
    Yields:
      The elements.
    """
    for element_name, element in self.container.iteritems():
      yield element

  def __contains__(self, element):
    """
    Captures the "in" command. 
    Args:
      self:  Standard python object notation for the instance.
    Return value:
      True/false if the element in container.
    """
    return element in self.container.values()

  def getMaxAttr(self,attr):
    """
    Returns the max value of the provided attribute (assuming
    the attr is a real or integer) across all elements.
    Args:
      self:  Standard python object notation for the instance.
      attr:  Attribute name for which the max will be found.
    Return value:
      Max of all of the elements attributes.
    """
    value = None
    for element in self:
      current_value = getattr(self,attr)
      try:
        if value < current_value:
          value = current_value
      except TypeError:
        value = current_value
    return value

  def getMinAttr(self,attr):
    """
    Returns the min value of the provided attribute (assuming
    the attr is a real or integer) across all elements.
    Args:
      self:  Standard python object notation for the instance.
      attr:  Attribute name for which the max will be found.
    Return value:
      Min of all of the elements attributes.
    """
    value = None
    for element in self:
      current_value = getattr(self,attr)
      try:
        if value > current_value:
          value = current_value
      except TypeError:
        value = current_value
    return value

def load_elements(config,section_name):
  """
  Loads up all of the classes from config object 
  into a single dictionary using config2class.
  Args:
    config: A config object.
    section_name: The name of the section where the element
      config files are stored.
  Return value:
    elements: A dictionary containing the class instances keyed by
      the section names in the elements config file.
  """ 
  elements=Elements()
  for option in config.options(section_name):
    elements_file = config.get(section_name,option)
    try:
      loaded_elements = import_classes_from_config_file(elements_file, config_parser_class=MyConfigParser, 
                          key_overwrite=option)
    except KeyError:
      loaded_elements = import_classes_from_config_file(elements_file, config_parser_class=MyConfigParser)
    for k, v in loaded_elements.iteritems():  
      elements.addElement(k,v)
  return elements
