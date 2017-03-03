import csv
from warp import *
from fields.standard import count_lines, convert_list_of_dicts_to_dict_of_numpy_arrays

def read_dat_file_as_numpy_arrays(dat_file,**kwargs):
  """
  Wraps the read_dat_file function so that the "data"
  output field is now a dictionary of numpy arrays instead of 
  a list of dicts.
  Args:
    dat_file: File with the .dat extension taken from the output
      of Poisson (I think)
  Return value:
    output: Dictionary with the keys
      fieldnames: The keys of the dictionary in the order they
        appear in the file.
      data: A dictionary of numpy arrays keyed by the fieldnames.
  """
  output = read_dat_file(dat_file,**kwargs)
  output["data"] = convert_list_of_dicts_to_dict_of_numpy_arrays(output["data"])
  return output

def read_dat_file(dat_file,scale=1,**kwargs):
  """
  Reads a dat field file (as given to me by Chung-Yu Ruan)
  returning an object with elements data.  The
  data will be returned a list of dicts with the header
  fieldnames as keys.  All fieldnames will be in lower case only.
  Args:
    dat_file: File with the .dat extension taken from the output
      of Poisson (I think)
  Return value:
    output: Dictionary with the keys
      fieldnames: The keys of the dictionary in the order they
        appear in the file.
      data: A table (rows of dicts) keyed by whatever is in
        the header.
  """
  output = {}
  with open(dat_file,"r") as f:
    for i in range(4): #Skip first 4 lines
      line = f.readline()
    #Get fieldnames (keys from header)
    output["fieldnames"] = f.readline().strip().lower().split()
    #Skip next line and check to make sure it has correct format.
    line = f.readline().strip()
    if not line.startswith("==="):
      raise Exception("Check format of " + dat_file + "." +
        "It appears as if the sixth line is not \"===...\".")
    #Load data as floats.
    table = []
    for line in f:
      line = line.strip()
      pieces = line.split()
      pieces = [float(p) for p in pieces]
      row = dict(zip(output["fieldnames"],pieces))
      for fieldname in output["fieldnames"]:
        if fieldname in ["x","y","z","r"]:
          row[fieldname] = row[fieldname]/1000 #Fix units
        if fieldname.startswith("E") or fieldname.startswith("B"):
          row[fieldname] = row[fieldname]/float(scale)
      table.append(row)
    output["data"] = table
  return output
   
    
def get_metadata_from_dat_line(line):
  """
  I'm not using the metadata anymore.  I'm just deriving it since
  I found errors in the file I had.
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
    
    
  
