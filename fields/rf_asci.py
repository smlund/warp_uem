import csv
from warp import *
from fields.standard import count_lines, convert_list_of_dicts_to_dict_of_numpy_arrays

"""
Don't know what to call this fie type, so I am calling it rf ascii.
Essentially it is just 2 header lines plus the data.  The first is the
fieldnames, the second is the dimensions, and the third on is the data.
"""

def read_rf_ascii_file_as_numpy_arrays(dat_file):
  """
  Wraps the read_rf_ascii_file function so that the "data"
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
  output = read_rf_ascii_file(dat_file)
  output["data"] = convert_list_of_dicts_to_dict_of_numpy_arrays(output["data"])
  return output

def read_rf_ascii_file(dat_file):
  """
  Reads a rf ascii field file (as given to me by Chung-Yu Ruan)
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
    #Get fieldnames (keys from header)
    output["fieldnames"] = f.readline().strip().lower().split()
    #Read the next line and get the conversions.
    line = f.readline().strip()
    pieces = line.split()
    pieces = [p.replace("(","").replace(")","") for p in pieces] 
    unit_conversion = []
    for p in pieces:
      if p == "mm":
        unit_conversion.append(0.001)
      elif p == "cm":
        unit_conversion.append(0.01)
      elif p == "MV/m":
        unit_conversion.append(1000000)
      else:
        unit_conversion.append(1)
    #Load data as floats.
    table = []
    for line in f:
      line = line.strip()
      pieces = line.split()
      #End when there is no longer any data.  This file type contains a footer.
      if len(pieces) <= 1:
        break
      pieces = [float(p) for p in pieces]
      converted_pieces = [pieces[i]*unit_conversion[i] for i in range(len(pieces))]
      row = dict(zip(output["fieldnames"],pieces))
      table.append(row)
    output["data"] = table
  return output
