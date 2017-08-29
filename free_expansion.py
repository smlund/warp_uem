# Load Warp 
description="""
Python input script for a Warp simulation of 
the free expansion of electrons experiment. 

For help and/or additional information contact:

     Steve Lund     lund@frib.msu.edu    (517) 908-7291

For documentation see the Warp web-site:

     https://warp.lbl.gov

All code inputs are mks except where noted.  

To run this Warp script:
  Interactive (return to interpreter after executing):

    % python -i uem.py [options] input_file 

  Non-interactive (exit interpreter after executing):

    % python uem.py [options] input_file

To see a list and desciption of options:
   
    % python uem.py -h
    % python uem.py --help
    % python uem.py
"""
import os
from warpoptions import *
#Handle command line arguments and default values with argparse.
parser.description = description
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('input_file', type=str, 
                    help='The path to the file containing the intial ' +
                    'conditions pickled dictionary - specified with the ' +
                    'keys time, x, y, z, px, py, and pz.')
parser.add_argument('config_file', type=str, 
                    help='The config file.  Contains a bunch of parameters ' +
                    'and references to other config files.')
parser.add_argument('--input_format', dest="input_format", type=str, 
                    help='Describes the format of the input file. ' +
                     'Default as is "xp".',default=None)
parser.add_argument('--3D_simulation',  
                    dest="sym_type", action="store_const", const="w3d",
                    help='Specify the use of "w3d" aka the 3 dimensional simulation.  ' +
                    'Default is the "wrz" aka rz simulation.', default="wrz")
parser.add_argument('--2D_simulation',  
                    dest="sym_type", action="store_const", const="wxy",
                    help='Specify the 2 dimensional simulation.  ' +
                    'Default is three dimensional.', default="wrz")
parser.add_argument('--partially_periodic', dest='partially_periodic',
                    action='store_true', help='Turns on particle exchange at z boundary.' +
                    'Default has no periodicity.',
                    default=False)
parser.add_argument('-m','--electrons_per_macroparticle', 
                    dest="electrons_per_macroparticle", type=float, 
                    help='The number of electrons per macroparticle for the ' +
                    'simulation.  The default is 100', default=100.)
parser.add_argument('--turn_off_field_solver', dest='field_solver_off',
                    action='store_true', help='Turn off field solver (for runs ' +
                    'with applied field but no self fields).  Default has the fieldsolver ' + 
                    'on.',default=False)
parser.add_argument('--turn_off_adjust_position', dest='adjust_position',
                    action = "store_false", help="Turn off the adjustment done to " +
                    "the position when the electrons are injected due to differences " +
                    "betweeen the timestep and the particle's time.  Default has the " + 
                    "adjustment on.", default=True)
parser.add_argument('--turn_off_adjust_velocity', dest='adjust_velocity',
                    action = "store_false", help="Turn off the adjustment done to " +
                    "the velocity when the electrons are injected due to differences " +
                    "betweeen the timestep and the particle's time.  Default has the " + 
                    "adjustment on.", default=True)
parser.add_argument('--iterative_phase_space_dump', dest="iterative_dump", type=int,
                    help='Tells the program to print the x, y, z, px, py, pz coordinates ' +
                    'of all the macroparticles at every iterative_dump steps.  Default is ' + 
                    'to skip this step.', default=None)
parser.add_argument('--phase_space_dump_step_list', dest="dump_list", type=str,
                    help='Tells the program to print the x, y, z, px, py, pz coordinates ' +
                    'of all the macroparticles at the listed steps separated by a comma.  ' + 
                    'For example, 35,46,72 will tell the program to dump the  coordinats after ' + 
                    'the 35th, 46th, and 72nd steps.  Default is ' + 
                    'to skip this step.', default=None)
parser.add_argument('--phase_space_locations_dump', dest="locations_dump", type=str,
                    help='Tells the program to print the x, y, z, px, py, pz coordinates ' +
                    'of all the macroparticles at the listed locations (determined by center of beam).' + 
                    'The value of this parameters should be a dictionary of form ' + 
                    'key1:value1,key2:value2,etc. Key1 will be used for the output name ' +
                    'and value1 will be the z compared to the center of the beam.  Default is ' + 
                    'to skip this step.', default=None)



args = parser.parse_args()

print "Argument dictionary: " 
print "\t" + "\n\t".join([k + " = " + str(v) for k, v in vars(args).iteritems()])

from config.my_config import MyConfigParser as ConfigParser
from config.my_config import parse_key_as_numpy_array, handle_section_named_refinement
from config.simulation_type import get_mesh_symmetry_factor, get_solver
from config.elements import load_elements
from diagnostics.diagnostic_classes import DiagnosticsByTimes, DumpBySteps
from diagnostics.diagnostic_classes import DumpAtLocations, RecordTransitionTime
from diagnostics.phase_volume import dump_phase_volume, dump_phase_volume_with_zlimits
from diagnostics.steves_uem_diagnostics import steves_plots, electric_potential_plots, just_vz_vs_z
from discrete_fourspace.mesh import get_supremum_index
from injectors.injector_classes import SingleElectronInjector
from injectors.steves_uem_injection import continue_injectelectrons
from injectors.io import get_pulse_velocity_from_momentum, get_distribution_average
from class_and_config_conversion import set_attributes_with_config_section
from fields.field_loader import FieldLoader
from fields.time_dependent_functions import sine_at_com_distance
from moving_grid.moving_classes import SyncToCOM
from warp import *
#from histplot import *

# Invoke setup routine: needed to created a cgm file for plots
setup()

#Load the config file and parameters from config file.
config = ConfigParser()
config.read(args.config_file)

adv_dt = array(config.get("Simulation parameters", "adv_dt"))# Numpy array of dts
if not isinstance(adv_dt,ndarray):
  adv_dt = array([adv_dt])
adv_steps = array(config.get("Simulation parameters", "adv_steps")) #Number of steps for each dt 
if not isinstance(adv_steps,ndarray):
  adv_steps = array([adv_steps])
#Mesh size
dx = config.get("Simulation parameters","dx")
dz = config.get("Simulation parameters","dz")
xmax = config.get("Simulation parameters","xmax")
zmin = config.get("Simulation parameters","zmin")
zmax = config.get("Simulation parameters","zmax")
z_extent = zmax-zmin
#When to do diagnostics
diagnostic_time_interval = config.get("Simulation parameters","diagnostic_time_interval")
try:
  dump_time_interval = config.get("Simulation parameters","dump_time_interval")
except:
  dump_time_interval = None

#Load the parameters for the w3d and top objects from the config.
set_attributes_with_config_section(top, config, "top parameters", {",":parse_key_as_numpy_array})
set_attributes_with_config_section(w3d, config, "w3d parameters")
set_attributes_with_config_section(f3d, config, "f3d parameters")

# Create the electron beam species 
#momentum_unit_conversion = jperev*1.*MV/clight #Input is in MeV/c and we want si units.
zavg = (zmax-zmin)*0.5

clight = 299792458

#Derived parameters
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
if args.sym_type == "xy":
  w3d.nz = 1
  w3d.zmmin =  0
  w3d.zmmax =  0
elif args.partially_periodic:
  w3d.nz = int((zmax-zmin)/dz)
  w3d.zmmin =  -zmin
  w3d.zmmax =  zmax
else: 
  w3d.nz = sym_factor*int(xmax/dx)
  w3d.zmmin =  -xmax
  w3d.zmmax =  xmax
w3d.xmmin = -xmax
w3d.xmmax =  xmax
w3d.ymmin = -xmax
w3d.ymmax =  xmax 
    #w3d.dz = (w3d.zmmax - w3d.zmmin)/w3d.nz
    #w3d.dx = (w3d.xmmax - w3d.xmmin)/w3d.nx

print "Setting up components"
solver = get_solver(args.sym_type, top, w3d)
registersolver(solver)

electron_injector = SingleElectronInjector(continue_injectelectrons, top, args.input_file,
                      args.electrons_per_macroparticle,input_format=args.input_format, w3d=w3d)
installuserinjection(electron_injector.callFunction)  # install injection function in timestep 
#if args.partially_periodic:
#  installafterstep(electron_injector.partiallyPeriodic) # install function myplots() to be called after each timestep


print("Setting up Diagnostics")
diagnostics = DiagnosticsByTimes(just_vz_vs_z,top,top,diagnostic_times)
installafterstep(diagnostics.callFunction) # install function myplots() to be called after each timestep

if args.iterative_dump is not None: #Install the phase volume dump.
  dump_steps = range(args.iterative_dump,int(steps_tot),args.iterative_dump) #Every iterative_dump step.
  phase_volume_dump = DumpBySteps(dump_phase_volume,electron_injector.getElectronContainer(),
        args.electrons_per_macroparticle*top.emass,top,dump_steps)
  installafterstep(phase_volume_dump.callFunction)
if args.dump_list is not None: #Install the phase volume dump.
  dump_steps = [int(s) for s in args.dump_list.split(",")]
  phase_volume_dump = DumpBySteps(dump_phase_volume,electron_injector.getElectronContainer(),
        args.electrons_per_macroparticle*top.emass,top,dump_steps)
  
  installafterstep(phase_volume_dump.callFunction)
if dump_time_interval is not None:
  dump_steps = []
  current_modulus = 0
  current_step = 0
  for i in range(len(adv_steps)):
    current_number_steps = adv_steps[i]
    current_dt =  adv_dt[i]
    for j in range(current_number_steps):
      current_modulus += current_dt
      if current_modulus >= dump_time_interval:
        dump_steps.append(current_step)
        current_modulus = 0
      current_step += 1
        
  #if args.partially_periodic:
  #  phase_volume_dump = DumpBySteps(dump_phase_volume_with_zlimits,electron_injector.getElectronContainer(),
  #      args.electrons_per_macroparticle*top.emass,top,dump_steps,zmin=config.get("Simulation parameters","zmin_report"),
  #      zmax=config.get("Simulation parameters","zmax_report"))
  phase_volume_dump = DumpBySteps(dump_phase_volume,electron_injector.getElectronContainer(),
        args.electrons_per_macroparticle*top.emass,top,dump_steps)
  
  installafterstep(phase_volume_dump.callFunction)
if args.locations_dump is not None: #Install the phase volume dump.
  dump_locations_list = args.locations_dump.split(",")
  location_keys = []
  location_values = []
  for location_pair in dump_locations_list:
    key, value = location_pair.split(":")
    location_keys.append(str(key))
    location_values.append(float(value))
  phase_volume_dump = DumpAtLocations(dump_phase_volume,electron_injector.getElectronContainer(),
        args.electrons_per_macroparticle*top.emass,location_keys,location_values)
  installafterstep(phase_volume_dump.callFunction)

if args.sym_type == "wxy":
  package("wxy") 
else:
  package("w3d") 
if args.partially_periodic:
  handle_section_named_refinement(config,solver,"Center refinement",zmax=zmax)
  print("handling refinement radially.")
else:
  handle_section_named_refinement(config,solver,"Center refinement")

generate() 
if args.field_solver_off:
  solver.ldosolve = False

print "Advancing simulation through each step interval set"
for ii in range(len(adv_steps)):
  top.dt = adv_dt[ii]
  step(adv_steps[ii])  
  #top.time += top.dt

#Get statistics for beam

#Apply statistics to grid and make grid move (set top.vbeamfrm to average velocity)

#Add b_fields and second edit top with configuration file.

# Advance simulation through each step interval set  until I don't know, 10mm past anode

#Re-get statistic for beam

#Apply statistics to grid and make grid move (set top.vbeamfrm to average velocity)

#Apply statistics to sin function so that average particle enters a sin phi = 0.

# Advance simulation through elements and RF cavity



# History diagnostics
#histplot() 

# Print out timing statistics of run 
printtimers() 

# Make sure that last plot is flushed from buffer
fma() 
