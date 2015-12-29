from warpoptions import *
description="""
Preprocesses the fields so that they are in standard fortran
order and stores them in a pickle dictionary.  A config file is 
save alongside the pickle dictionary.  These files are then
to be used with the FieldLoader class.
"""
#Handle command line arguments and default values with argparse.
parser.description = description
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('config_file', type=str, 
                    help='The path to the field config file produced by prepocessing.')
parser.add_argument('-o','--output_prefix',  
                    dest="prefix", 
                    help='Specifies the prefix to be used for the output file.  ' + 
                    'Deault will use the config file name without config.', 
                    default=None)
args = parser.parse_args()
from fields.field_loader import FieldLoader
from warp import *

print "Argument dictionary: " 
print "\t" + "\n\t".join([k + " = " + str(v) for k, v in vars(args).iteritems()])

#Handle the output path and setup of the plots.
if args.prefix is None:
  prefix, ext = os.path.splitext(args.config_file)
else:
  prefix = args.prefix
setup(prefix=prefix,cgmlog=0)
plots = {}
field_loader = FieldLoader(args.config_file)
nx = field_loader.number_of_steps["x"]
nz = field_loader.number_of_steps["z"]
args_dict = field_loader.getArgs()
for field_type in args_dict:
  if field_type == "electric":
    ie = addnewegrd(*args_dict[field_type]["args"],**args_dict[field_type]["kwargs"])
    plots["electric"] = True
  elif field_type == "magnetic":
    ib = addnewbgrd(*args_dict[field_type]["args"],**args_dict[field_type]["kwargs"])
    print ib
    plots["magnetic"] = True

if "electric" in plots:
  plotegrd(ie[0],component="z",iy=0,iz=0)
  fma()
  plotegrd(ie[0],component="z",ix=0,iy=0)
  fma()
  plotegrd(ie[0],component="x",iy=0,iz=0)
  fma()
  plotegrd(ie[0],component="x",ix=0,iy=0)
  fma()
if "magnetic" in plots:
  plotbgrd(ib[0],component="z",iy=0,iz=0)
  fma()
  plotbgrd(ib[0],component="z",ix=0,iy=0)
  fma()
  plotbgrd(ib[0],component="x",iy=0,iz=0)
  fma()
  plotbgrd(ib[0],component="x",ix=0,iy=0)
  fma()
