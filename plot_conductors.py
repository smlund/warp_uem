# Load Warp 
description="""
Loads and plots conductors.
"""
import os
from warpoptions import *
#Handle command line arguments and default values with argparse.
parser.description = description
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('config_file', type=str, 
                    help='The config file.  Contains a bunch of parameters ' +
                    'and references to other config files.  Once section needs to be called ' + 
                    '"Conductor elements" with paths to conductor config files.')
parser.add_argument('--3D_simulation',  
                    dest="sym_type", action="store_const", const="w3d",
                    help='Specify the use of "w3d" aka the 3 dimensional simulation.  ' +
                    'Default is the "wrz" aka rz simulation.', default="wrz")
parser.add_argument('-e','--extraction_field',  
                    dest="extraction_field", type=float,
                    help='Specifies the extraction electric field gradient in MV.', 
                    default=1.)
parser.add_argument('-o','--output_prefix',  
                    dest="prefix", 
                    help='Specifies the prefix to be used for the output file.  ' + 
                    'Deault will use the config file name without config.', 
                    default=None)
args = parser.parse_args()

print "Argument dictionary: " 
print "\t" + "\n\t".join([k + " = " + str(v) for k, v in vars(args).iteritems()])

from config.my_config import MyConfigParser, parse_key_as_numpy_array
from config.simulation_type import get_mesh_symmetry_factor, get_solver
from config.elements import load_elements
from diagnostics.steves_uem_diagnostics import electric_potential_plots
from discrete_fourspace.mesh import get_supremum_index
from injectors.steves_uem_injection import steves_injectelectrons
from class_and_config_conversion import set_attributes_with_config_section
from warp import *
#from histplot import *

# Invoke setup routine: needed to created a cgm file for plots

#Handle the output path and setup of the plots.
if args.prefix is None:
  prefix, ext = os.path.splitext(args.config_file)
else:
  prefix = args.prefix
setup(prefix=prefix,cgmlog=0)

#Load the config file and parameters from config file.
config = MyConfigParser()
config.read(args.config_file)

adv_dt = array(config.get("Simulation parameters", "adv_dt"))# Numpy array of dts
adv_steps = array(config.get("Simulation parameters", "adv_steps")) #Number of steps for each dt 
#Mesh size
dx = config.get("Simulation parameters","dx")
dz = config.get("Simulation parameters","dz")
xmax = config.get("Simulation parameters","xmax")
zmin = config.get("Simulation parameters","zmin")
zmax = config.get("Simulation parameters","zmax")
#When to do diagnostics
diagnostic_time_interval = config.get("Simulation parameters","diagnostic_time_interval")

#Load the parameters for the w3d and top objects from the config.
set_attributes_with_config_section(top, config, "top parameters", {",":parse_key_as_numpy_array})
set_attributes_with_config_section(w3d, config, "w3d parameters")


#Derived parameters
grad      = args.extraction_field*MV    # Electric field gradient [V/m] --- add units to extraction_field argument.
steps_tot = sum(adv_steps)         # Total steps to take [1]
t_final   = sum(adv_steps*adv_dt)  # Total time advance [s] 
diagnostic_times = arange(diagnostic_time_interval,t_final,diagnostic_time_interval) #List of times to run diagnostics.
sym_factor = get_mesh_symmetry_factor(args.sym_type, top,w3d)
#Derived top and w3d attribute modifications
top.dt       = adv_dt[0]     # Specify initial dt advance for generate etc 
top.prwall = xmax  # cylinder radius to absorb particles if 
                   #   radius = sqrt(x**2 + y**2) exceeds
    #top.zzplseldom[0:4] =[0.,100000.,zmax/4.,0.]
    #top.zzplalways[0:4] =[0.,100000.,zmax/4.,0.]
    # --- Set up diagnostic windows.
    #top.rwindows[:,1] = [0.,w3d.dx]
    #top.rwindows[:,2] = [0.,w3d.xmmax]
    #top.zwindows[:,1] = [0.,w3d.dz]
    #top.zwindows[:,2] =  25.*um + array([-w3d.dz,w3d.dz])/2.
    #top.zwindows[:,3] =  50.*um + array([-w3d.dz,w3d.dz])/2.
    #top.zwindows[:,4] =  75.*um + array([-w3d.dz,w3d.dz])/2.
    #top.zwindows[:,5] = 100.*um + array([-w3d.dz,w3d.dz])/2.
w3d.nx = sym_factor*int(xmax/dx)
w3d.ny = sym_factor*int(xmax/dx)
w3d.nz = int(zmax/dz)
w3d.xmmin = -xmax
w3d.xmmax =  xmax
w3d.ymmin = -xmax
w3d.ymmax =  xmax 
w3d.zmmin =  zmin
w3d.zmmax =  zmax 
    #w3d.dz = (w3d.zmmax - w3d.zmmin)/w3d.nz
    #w3d.dx = (w3d.xmmax - w3d.xmmin)/w3d.nx
solver = get_solver(args.sym_type, top, w3d)
registersolver(solver)

conductor_elements = load_elements(config,"Conductor elements")
conductor_elements.cathode.voltage = -grad*conductor_elements.cathode.voltage  # Cathode bias [V]
conductor_elements.anode.voltage = -grad*conductor_elements.anode.voltage  # Cathode bias [V]

for conductor_element in conductor_elements:
   installconductor(conductor_element)  # install conductors after field solver registered
generate() 

# Generate initial plots
ix_cen = get_supremum_index(w3d.xmesh,0)
iy_cen = get_supremum_index(w3d.ymesh,0)
electric_potential_plots(ix_cen,iy_cen)
print conductor_elements.cathode.zcent

# Make sure that last plot is flushed from buffer
fma() 
