# Load Warp 
description="""
Python input script for a Warp simulation of 
the MSU UEM experiment using input photoemission data. 

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
parser.add_argument('--3D_simulation',  
                    dest="sym_type", action="store_const", const="w3d",
                    help='Specify the use of "w3d" aka the 3 dimensional simulation.  ' +
                    'Default is the "wrz" aka rz simulation.', default="wrz")
parser.add_argument('-e','--extraction_field',  
                    dest="extraction_field", type=float,
                    help='Specifies the extraction electric field gradient in MV.', 
                    default=1.)
parser.add_argument('-m','--electrons_per_macroparticle', 
                    dest="electrons_per_macroparticle", type=float, 
                    help='The number of electrons per macroparticle for the ' +
                    'simulation.  The defaults to 100', default=100.)
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


args = parser.parse_args()

print "Argument dictionary: " 
print "\t" + "\n\t".join([k + " = " + str(v) for k, v in vars(args).iteritems()])

from config.my_config import MyConfigParser, parse_key_as_numpy_array
from config.simulation_type import get_mesh_symmetry_factor, get_solver
from config.elements import load_elements
from diagnostics.diagnostic_classes import DiagnosticsByTimes, DumpBySteps
from diagnostics.phase_volume import dump_phase_volume
from diagnostics.steves_uem_diagnostics import steves_plots, electric_potential_plots
from discrete_fourspace.mesh import get_supremum_index
from injectors.injector_classes import ElectronInjector
from injectors.steves_uem_injection import steves_injectelectrons
from class_and_config_conversion import set_attributes_with_config_section
from warp import *
#from histplot import *

# Invoke setup routine: needed to created a cgm file for plots
setup()

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

# Simulation grid specification and load of conductors on the grid. 
#  * Load conductors on left and right z-grid boundary. Mesh boundary can 
#    be coincident with conductors, but conductors must have finite axial 
#    thickness in specification (value irrelevant). No padding space needed.
#  * bound0 and boundnz are not needed for end grid boundary conditions 
#    since end mesh points are loaded as conductors. 
#  * boundxy might be best set as neumann in terms of symmetry, 
#    but this may be less efficient than using dirichlet and taking large 
#    enough not to matter.  
# Specify conducting structures for parallel plate capacitor geometry 
#     * Cathode will be set at z = 0 at v_cathode bias 
#       (calculated) needed to achieve specified gradient. 
#     * An anode conductor will be placed at z = mesh_max at v_anode bias 
#       (calculated) needed to achieve specified gradient.
#     * Assume potential 0 (ground) at physical anode at z = d_plates to 
#       specify reference potential   
#
conductor_elements = load_elements(config,"Conductor elements")

# --- specify conducting plates to place on mesh 
#     * plate_cathode => emitter plate at z = 0  
#     * plate_anode   => artificial anode plate placed on abbreviated mesh window
#                        at bias needed to achieve specified diode gradient 
#     * plates will be loaded after field solver employed is registered (necessary) 

conductor_elements.cathode.voltage = -grad*conductor_elements.cathode.voltage  # Cathode bias [V]
conductor_elements.anode.voltage = -grad*conductor_elements.anode.voltage  # Cathode bias [V]

for conductor_element in conductor_elements:
   installconductor(conductor_element)  # install conductors after field solver registered

# Create the electron beam species 
momentum_unit_conversion = jperev*1.*MV/clight #Input is in MeV/c and we want si units.
electron_injector = ElectronInjector(steves_injectelectrons,top, args.input_file,
                      top.echarge/top.emass, args.electrons_per_macroparticle, 
                      flags={"adjust_position": args.adjust_position,
                             "adjust_velocity": args.adjust_velocity},
                      momentum_conversion=momentum_unit_conversion/args.electrons_per_macroparticle)
installuserinjection(electron_injector.callFunction)  # install injection function in timestep 

#Diagnostics
diagnostics = DiagnosticsByTimes(steves_plots,top,top,diagnostic_times)
installafterstep(diagnostics.callFunction) # install function myplots() to be called after each timestep

if args.iterative_dump is not None: #Install the phase volume dump.
  dump_steps = range(args.iterative_dump,int(steps_tot),args.iterative_dump) #Every iterative_dump step.
  phase_volume_dump = DumpBySteps(dump_phase_volume,electron_injector.getElectronContainer(),
        args.electrons_per_macroparticle*top.emass,top,dump_steps)
  installafterstep(phase_volume_dump.callFunction)
"""
 Generate the PIC code
   * 3D code "w3d" is always used here: 3d mover is same and 
       field solver setup different for rz and 3d code. 
   * DO NOT use package("wrz"). This uses old r-z code by 
       Debbie Callahan that has not been maintained.  
   * Initial field solve will be carried out on generate() call 
   * Since no particles are present till timesteps are taken, 
       the initial field will not include emitted electrons.  
   * If the field_solver_off option has been set to true,
     this initial field is the only one used in the simulation.
"""
package("w3d") 
generate() 
if args.field_solver_off:
  solver.ldosolve = False

# Generate initial plots
ix_cen = get_supremum_index(w3d.xmesh,0)
iy_cen = get_supremum_index(w3d.ymesh,0)
electric_potential_plots(ix_cen,iy_cen)

# Advance simulation through each step interval set  
for ii in range(len(adv_steps)):
  top.dt = adv_dt[ii]
  step(adv_steps[ii])  

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
