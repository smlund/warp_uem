import csv
from warp import *
from fields.standard import count_lines, convert_list_of_dicts_to_dict_of_numpy_arrays

def read_dat_file_as_numpy_arrays(dat_file):
  """
  Wraps the read_dat_file function so that the "data"
  output field is now a dictionary of numpy arrays instead of 
  a list of dicts.
  Args:
    dat_file: File with the .dat extension taken from the output
      of Poisson (I think)
  Return value:
    output: Dictionary with the keys metadata and data.
      metadata: Additional data stored in the first couple
        lines of the dat file (e.g. ZMin)
      fieldnames: The keys of the dictionary in the order they
        appear in the file.
      data: A dictionary of numpy arrays keyed by the fieldnames.
  """
  output = read_dat_file(dat_file)
  output["data"] = convert_list_of_dicts_to_dict_of_numpy_arrays(output["data"])
  return output

def read_dat_file(dat_file):
  """
  Reads a dat field file (as given to me by Chung-Yu Ruan)
  returning an object with elements data and metadata.  The
  data will be returned a list of dicts with the header
  fieldnames as keys.  All fieldnames will be in lower case only.
  Args:
    dat_file: File with the .dat extension taken from the output
      of Poisson (I think)
  Return value:
    output: Dictionary with the keys metadata and data.
      metadata: Additional data stored in the first couple
        lines of the dat file (e.g. ZMin)
      fieldnames: The keys of the dictionary in the order they
        appear in the file.
      data: A table (rows of dicts) keyed by whatever is in
        the header.
  """
  output = {}
  #Get header and meta data and check consistency.
  with open(dat_file,"r") as f:
    line = f.readline() #Skip first line
    output["metadata"] = {} #Adds metadata taken from line.
    for i in range(3):
      line = f.readline().strip()
      metadata = get_metadata_from_dat_line(line)
      output["metadata"].update(metadata) #Adds metadata taken from line.
    output["fieldnames"] = f.readline().strip().lower().split()
    line = f.readline().strip()
    if not line.startswith("==="):
      raise Exception("Check format of " + dat_file + "." +
        "It appears as if the sixth line is not \"===...\".")
    table = []
    for line in f:
      line = line.strip()
      pieces = line.split()
      pieces = [float(p) for p in pieces]
      table.append(dict(zip(output["fieldnames"],pieces)))
    output["data"] = table
  return output
   
    
def get_metadata_from_dat_line(line):
  """
  Extract the metadata that is stored in a line from the header 
  of a dat file.
  Args:
    line: A line taken from the header of a data file.
  Return values:
    A dictionary of terms taken from the line.
  """
  output = {}
  pieces = line.split()
  if len(pieces) % 2 != 0:
    raise Exception("The dat metadata line must have an even number of " + 
                    "elements (i.e. keys AND values).  The following " + 
                    "line is problematic: \n\t" + line)
  number_of_variables = len(pieces)/2
  for i in range(number_of_variables):
    key = pieces[2*i].rstrip(":").rstrip("=").lower()
    value = float(pieces[2*i+1])
    output[key] = value
  return output
    
    
  
