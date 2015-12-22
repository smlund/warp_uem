import numpy

def count_lines(filepath):
  """
  Gets the line count of a file.
  Args:
    filepath:  The path to the file we want to get
      the line count of.
  Return value:  The number of lines in the file.
  """
  with open(filepath) as f:
    for i, l in enumerate(f):
      pass
  return i + 1

def convert_list_of_dicts_to_dict_of_lists(list_of_dicts):
  """
  Accumulates the entries in a list of
  dict into a dict of lists.
  Args:
    list_of_dicts: A table like structure that is a list
      of dicts.  Typical output of csv.DictReader.
  Output:
    output: A dictionary of lists of "row" entries.
  """
  output = {}
  for row in list_of_dicts:
    for key, value in row.iteritems():
      try:
        output[key].append(value)
      except KeyError:
        output[key] = []
        output[key].append(value)
  return output

def convert_list_of_dicts_to_dict_of_numpy_arrays(list_of_dicts):
  """
  Accumulates the entries in a list of
  dict into a dict of lists.
  Args:
    list_of_dicts: A table like structure that is a list
      of dicts.  Typical output of csv.DictReader.
  Output:
    output: A dictionary of lists of "row" entries.
  """
  output = {}
  dict_of_lists = convert_list_of_dicts_to_dict_of_lists(list_of_dicts)
  for key, value_list in dict_of_lists.iteritems():
    output[key] = numpy.array(value_list)
  return output
