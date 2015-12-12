"""
Python input script for a Warp simulation of 
the MSU UEM experiment using input photoemission data. 

For help and/or additional information contact:

     Steve Lund     lund@frib.msu.edu    (517) 908-7291

For documentation see the Warp web-site:

     https://warp.lbl.gov

All code inputs are mks except where noted.  

To run this Warp script:
  Interactive (return to interpreter after executing):

    % python -i uem.py 

  Non-interactive (exit interpreter after executing):

    % python uem.py
"""

# Load Warp 
from warp import *
#from histplot import *

# Set four-character run id, comment lines, user's name.
top.pline2   = "3D Warp Simulation of MSU UEM"
top.pline1   = "Photoinjector Input, 100e per Macroparticle"
top.runmaker = "Steven Lund, Brandon Zerbe, Dave Grote"

# Invoke setup routine: needed to created a cgm file for plots
setup()

# Specify simulation type 
#simtype = "w3d"   # 3D full 3d 
simtype = "wrz"   # rz axisymmetric 

# Specify conducting structures for parallel plate capacitor geometry 
#     * Cathode will be set at z = 0 at v_cathode bias 
#       (calculated) needed to achieve specified gradient. 
#     * An anode conductor will be placed at z = mesh_max at v_anode bias 
#       (calculated) needed to achieve specified gradient.
#     * Assume potential 0 (ground) at physical anode at z = d_plates to 
#       specify reference potential   
#
grad      = 1.*MV    # Electric field gradient [V/m] 
d_plates  = 5.*mm    # Plate seperation [m]
r_plate   = 1.0      # Radius plate (take large) [m]
t_plate   = 1.*mm    # Thickness plate (take large) [m] 

# Numerical time advance parameters 
fs = 1.e-15  # femto-sec specification 

adv_steps = array([100,100,100,100,220])                 # interval steps 
adv_dt    = array([1.27*fs,5.*fs,15.*fs,80.*fs,0.5*ps])  # interval dt 

steps_tot = sum(adv_steps)         # Total steps to take [1]
t_final   = sum(adv_steps*adv_dt)  # Total time advance [s] 

# --- make array of times at step number for 
#     later use in diagnostic calls at set times (use to calculate steps at set times)
t_step      = zeros(steps_tot) 
t_intervals = len(adv_steps)
istep = 0 
t0    = 0.
for ii in arange(t_intervals):
  t_step[istep:istep+adv_steps[ii]] = t0 + (1.+arange(adv_steps[ii]))*adv_dt[ii]
  istep += adv_steps[ii] 
  t0 = t_step[istep-1]
 

top.dt       = adv_dt[0]     # Specify initial dt advance for generate etc 
top.lrelativ = True          # use relativity in particle advance 
top.ibpush   = 0             # specify no B-field advance for efficiency:
                             #   change to 1 (fast) or 2 (accurate) if B-focus 
                             #   fields or B-self fields (EM or other) later added  

# Simulation grid specification and load of conductors on the grid. 
#  * Load conductors on left and right z-grid boundary. Mesh boundary can 
#    be coincident with conductors, but conductors must have finite axial 
#    thickness in specification (value irrelevant). No padding space needed.
#  * bound0 and boundnz are not needed for end grid boundary conditions 
#    since end mesh points are loaded as conductors. 
#  * boundxy might be best set as neumann in terms of symmetry, 
#    but this may be less efficient than using dirichlet and taking large 
#    enough not to matter.  

# --- specify mesh does not move
top.vbeamfrm = 0.  

# --- mesh size in x and z 
dx = 5.*um 
dz = dx 

# --- mesh extents 
xmax = 0.7*mm 
zmin = 0. 
zmax = 2. *mm 

w3d.xmmin = -xmax
w3d.xmmax =  xmax
w3d.ymmin = -xmax
w3d.ymmax =  xmax 
w3d.zmmin =  zmin
w3d.zmmax =  zmax 

# --- mesh symmetry and boundary conditions 
w3d.l4symtry = True      # use 4-fold perp symmetry in 3D fieldsolve  
w3d.bound0   = dirichlet # probably does not matter since conductor on left 
w3d.boundnz  = dirichlet # probably does not matter since conductor on right  
w3d.boundxy  = neumann   # Probably better neumann but less efficient

# --- mesh size symmetry factor 
sym = 1 
if simtype == "w3d":
  sym = 2
  if w3d.l4symtry: sym = 1
elif simtype == "wrz":
  sym = 1 
else:
  raise Exception("Error: simtype not defined")

# --- mesh size consistent with symmetries  
w3d.nx = sym*int(xmax/dx)
w3d.ny = sym*int(xmax/dx)
w3d.nz = int(zmax/dz)

# --- particle absorbing conditions on mesh 
top.pbound0  = absorb  # left  z-mesh: absorb particles impinging on 
top.pboundnz = absorb  # right z-mesh: absorb particles impinging on 
top.pboundxy = absorb  # radial mesh:  absorb particles impinging on 

top.prwall = xmax  # cylinder radius to absorb particles if 
                   #   radius = sqrt(x**2 + y**2) exceeds

# --- specify conducting plates to place on mesh 
#     * plate_cathode => emitter plate at z = 0  
#     * plate_anode   => artificial anode plate placed on abbreviated mesh window
#                        at bias needed to achieve specified diode gradient 
#     * plates will be loaded after field solver employed is registered (necessary) 

v_cathode = -grad*d_plates                # Cathode bias [V]
v_anode   = -grad*(d_plates-(zmax-zmin))  # Anode   bias [V] 

plate_cathode = ZCylinder(r_plate,t_plate,zcent=zmin-t_plate/2.,voltage=v_cathode) 
plate_anode   = ZCylinder(r_plate,t_plate,zcent=zmax+t_plate/2.,voltage=v_anode  ) 

plates = plate_cathode + plate_anode 

# Specifiy muliti-grid field ES field solver 
#     for 3D and rz versions. Can add mesh refinement versions and EM versions 
#     later.
  
if simtype == "w3d":
  # --- 3D ES
  solver = MultiGrid3D()
elif simtype == "wrz":
  # r-z ES
  w3d.solvergeom = w3d.RZgeom
  solver = MultiGrid2D()
else:
  raise Exception("Error: simtype not defined")

# --- register field solver
registersolver(solver)
installconductor(plates)  # install conductors after field solver registered

# Create the electron beam species 

weight = 100. # number of real particles per macro-particle 
electrons = Species(type=Electron,weight=weight,name="Electron")

# Read in electrons to inject from external file generated by a photemission simulation 
#  * Data read in as an array of *macro* particles.  
#  * Each entry has dictionary giving by name:
#     t  = time birth [sec] consistent with simulation starting at t = 0.  
#     x  = x-coordinate [m] at birth 
#     px = x-momentum [MeV/c] at birth of macroparticle (divide by weight for physical particle px)  
#     + analogous entries for y,py and z,pz 
#  * No order or size of data file is assumed.  

# --- read in data 
ff = open('InitCond_10000x100e_dict.pckl', 'r')
dd = cPickle.load(ff)
ff.close() 

# --- create ..._inj arrays to store data  
n_inj  = len(dd)
t_inj  = zeros(n_inj)  
x_inj  = zeros(n_inj) 
y_inj  = zeros(n_inj) 
z_inj  = zeros(n_inj) 
px_inj = zeros(n_inj) 
py_inj = zeros(n_inj) 
pz_inj = zeros(n_inj) 

# --- place data in ..._inj arrays.  Convert units of px,py,pz to MKS units  
convert = jperev*1.*MV/clight
for ii in range(n_inj):
  p_data = dd[ii] 
  #
  t_inj[ii] = p_data['t'] 
  #
  x_inj[ii] = p_data['x'] 
  y_inj[ii] = p_data['y'] 
  z_inj[ii] = p_data['z'] 
  # 
  px_inj[ii] = p_data['px']*convert/weight 
  py_inj[ii] = p_data['py']*convert/weight
  pz_inj[ii] = p_data['pz']*convert/weight  

# Define function to inject electrons macroparticles each time step.
#  * Installed in particle advance loop by user defined function injectelectrons() defined below. 
#  * Function placed in time advance cycle by installuserinjection(user_function) used below.  
#  * Present version assumes nonrelativisit dynamics for all injected electrons.  After injection, 
#    electrons can be advanced relativisitically or not depending on setting of top.lrelativ .  
#  * Works by finding all birthed particles between present time (top.time) and next time step 
#    (top.time + top.dt) and injecting those particles.   
#  * If flag adj_inject = True/False, then injected particle coordinates are/are not 
#    adjusted to account for difference of birth time and time at end of timestep. This just 
#    adjusts positions in a free-streaming NR sense. If adj_inject_p = True/False the momenta/velocities 
#    are also NR adjusted with the self-consistent EM-field data using the Lorentz force eqn.  
#  * In the above correction of momenta/velocities the magnetic field will only be nonzero if the 
#    simulation is electromagnetic.

adj_inject   = True 
adj_inject_p = True   

def injectelectrons():
  # Find indices of injected electron macroparticle arrays between t and t + dt to inject 
  indices = where(logical_and(top.time < t_inj, t_inj <= top.time + top.dt))[0] 
  ninj = len(indices)
  # Extract macroparticle coordinates t, x,p to inject
  tinj = t_inj[indices] 
  xinj = x_inj[indices]
  yinj = y_inj[indices] 
  zinj = z_inj[indices] + smallpos  # add small no to insure z coordinate just to right of conductor  
  pxinj = px_inj[indices]
  pyinj = py_inj[indices]
  pzinj = pz_inj[indices]
  # Calculate macro particle velocities and inverse gamma factors to inject
  #ginj  = sqrt(1. + (pxinj**2 + pyinj**2 + pzinj**2)/(emass*clight)**2 )
  #giinj = 1./ginj
  giinj = ones(ninj)     # inverse gamma = 1., NR limit 
  vxinj = giinj*pxinj/emass 
  vyinj = giinj*pyinj/emass 
  vzinj = giinj*pzinj/emass 
  # Adjust particle coordinates (Nonrelativistic formulas) to inject 
  if adj_inject:
    dt = (top.time + top.dt) - tinj
    # coordinate correction 
    xinj += vxinj*dt 
    yinj += vyinj*dt 
    zinj += vzinj*dt 
    # velocity correction using both E- and B-fields: B-field only 
    #   nonzero for EM fieldsolve 
    if adj_inject_p:
      ex = zeros(ninj); ey = zeros(ninj); ez = zeros(ninj) 
      bx = zeros(ninj); by = zeros(ninj); bz = zeros(ninj)
      fetche3dfrompositions(electrons.sid,1,ninj,xinj,yinj,zinj,ex,ey,ez,bx,by,bz)
      vxinj += -(echarge/emass)*ex*dt - (echarge/emass)*(vyinj*bz-vzinj*by)*dt  
      vyinj += -(echarge/emass)*ey*dt - (echarge/emass)*(vzinj*bx-vxinj*bz)*dt 
      vzinj += -(echarge/emass)*ez*dt - (echarge/emass)*(vxinj*by-vzinj*bx)*dt 
  #
  # Inject electron macroparticles 
  electrons.addparticles(x=xinj,y=yinj,z=zinj,vx=vxinj,vy=vyinj,vz=vzinj,gi=giinj)

installuserinjection(injectelectrons)  # install injection function in timestep 

#raise Exception("To Here")  


# Diagnostics 

# --- setup lists of diagnostic times and corresponding step numbers to 
#     plot distribution properties
#         diag_times = list of times to accumlate diagnostics  
#         diag_steps = list of simulation step numbers corresponding 
#                        to entries in diag_times 
#     Note:
#       * Add entries to diag_times for diagnostics at additional times 
#       * Order of entries in diag_times does not matter.  
#       * Can use diag_times.append(new_time) to add time entry new_time 
#       * diag_steps caclulated from diag_times using t_step array 

diag_t_max  = 120.*ps 
diag_t_step =  20.*ps 
diag_times = arange(diag_t_step,diag_t_max,diag_t_step) 

diag_steps = [] 
for it in range(len(diag_times)):
  diag_steps.append(sum(where(t_step < diag_times[it], 1, 0)))

# --- Set up diagnostic windows.
#w3d.dz = (w3d.zmmax - w3d.zmmin)/w3d.nz
#w3d.dx = (w3d.xmmax - w3d.xmmin)/w3d.nx
#top.rwindows[:,1] = [0.,w3d.dx]
#top.rwindows[:,2] = [0.,w3d.xmmax]
#top.zwindows[:,1] = [0.,w3d.dz]
#top.zwindows[:,2] =  25.*um + array([-w3d.dz,w3d.dz])/2.
#top.zwindows[:,3] =  50.*um + array([-w3d.dz,w3d.dz])/2.
#top.zwindows[:,4] =  75.*um + array([-w3d.dz,w3d.dz])/2.
#top.zwindows[:,5] = 100.*um + array([-w3d.dz,w3d.dz])/2.

# --- diagnostic plot intervals, etc.
top.nhist = 1
top.itmomnts[0:4]=[0,1000000,1,0]
#top.zzplseldom[0:4] =[0.,100000.,zmax/4.,0.]
#top.zzplalways[0:4] =[0.,100000.,zmax/4.,0.]

# Diagnostic function to make plots at particular steps 
mr = 1.e-3 # milli-radian conversion scale 
def myplots():
  if not(top.it in diag_steps): return
  # time and position info to include on plot labels  
  z_cen = top.zbar[0,0]
  t_label = "time = %10.4f ps, <z> = %6.4f mm"%(top.time/ps,z_cen/mm)
  #  x-z projection 
  ppzx(xscale=1./mm,yscale=1./mm,titles=false)
  ptitles("x-z Projection Electrons","z [mm]","x [mm]",t_label)
  fma() 
  #  x-z projection with potential superimposed 
  pfzx(     xscale=1./mm,yscale=1./mm,titles=false)
  ppzx(iw=0,xscale=1./mm,yscale=1./mm,titles=false)
  ptitles("Potential and x-z Projection Electrons","z [mm]","x [mm]",t_label)
  fma()
  # x-y projection: two ways black and white scatter plot and 
  #                 colorized with intensity scale 
  ppxy(iw=0,yscale=1./mm,xscale=1./mm,titles=false)
  ptitles("x-y projection","x [mm]","y [mm]",t_label)
  fma()  
  # 
  ppxy(iw=0,color='density',ncolor=25,
       yscale=1./mm,xscale=1./mm,titles=false)
  ptitles("x-y projection","x [mm]","y [mm]",t_label)
  fma()  
  # x-x' projection: two ways black and white scatter plot and
  #                  colorized with intensity scale and slope removed 
  ppxxp(iw=0,xscale=1./mr,yscale=1./mm,titles=false) 
  ptitles("x-x' projection","x [mm]","x' [mr]",t_label)
  fma() 
  #
  ppxxp(iw=0,slope='auto',color='density',ncolor=25,
        yscale=1./mr,xscale=1./mm,titles=false)
  ptitles("x-x' projection","x [mm]","x' [mr]",t_label)
  fma()
  # z - vz projection: two ways, black and white scatter plot and 
  #                    colorized with intensity scale 
  ppzvz(iw=0,yscale=1./mm,titles=false)
  ptitles("vz-z Projection Electrons","z [mm]","vz [m/s]",t_label)
  fma()
  # 
  ppzvz(iw=0,yscale=1./mm,titles=false,color='density',ncolor=25)
  ptitles("vz-z Projection Electrons","z [mm]","vz [m/s]",t_label)
  fma()
  # mean vz vs z
  pzvzbar(scale=1./mm,zscale=mm,titles=false)
  ptitles("Mean vz vs z","z [mm]","<vz> [m/s]",t_label)
  fma()
  # rms vz vs z 
  pzvzrms(zscale=mm,titles=false)
  ptitles("rms vz vs z","z [mm]","rms vz [m/s]",t_label)
  fma() 
  # rms x,y vs z 
  pzxrms(scale=1./mm,zscale=mm,titles=false) 
  pzyrms(scale=1./mm,zscale=mm,titles=false,color=red)
  ptitles("rms x (black) and y (red) vs z","z [mm]","rms x,y [mm]",t_label)
  fma()  
  # rms r vs z 
  pzrrms(scale=1./mm,zscale=mm,titles=false)
  ptitles("rms Transverse r vs z","z [mm]","rms r [mm]",t_label)
  fma()  
  # rms x',y' vs z 
  pzxprms(scale=1./mr,zscale=mm,titles=false)
  pzyprms(scale=1./mr,zscale=mm,titles=false,color=red) 
  ptitles("rms x' (black) and y' (red) vs z","z [mm]","rms x',y' [mr]",t_label)
  fma() 
  # (rms x)', (rms y)' vs z 
  pzenvxp(scale=1./(2.*mr),zscale=mm,titles=false)
  pzenvyp(scale=1./(2.*mr),zscale=mm,titles=false)
  ptitles("Env Angles: (rms x)' (black) and (rms y)' (red) vs z",
          "z [mm]","<xx'>/sqrt<xx>, <yy'>/sqrt(yy) [mr]",t_label)
  fma()   
  # normalized rms x-x' and y-y' emittances vs z 
  pzepsnx(scale=1./4.,zscale=mm,titles=false) 
  pzepsny(scale=1./4.,zscale=mm,titles=false,color=red)
  ptitles("Normalized rms x-x' (black) and y-y' (red) Emittance vs z",
          "z [mm]","Emittance [mm-mr]",t_label)
  fma() 
  # rms x-x' and y-y' emittances vs z 
  pzepsx(scale=1./(4.*mm*mr),zscale=mm,titles=false) 
  pzepsy(scale=1./(4.*mm*mr),zscale=mm,titles=false,color=red)
  ptitles("rms x-x' (black) and y-y' (red) Emittance vs z",
          "z [mm]","Emittance [mm-mr]",t_label)
  fma() 
  # normalized rms z-z' emittance vs z # FIX: unsure what z' units are!!! 
  #    Edge measure? Update labels and info when understood.    
  pzepsnz(scale=1.,zscale=mm,titles=false) 
  ptitles("rms z-z' Emittance vs z","z [mm]","Emittance [mm-mr]",t_label)
  fma() 
  # Current vs z
  pzcurr(scale=1./1.e-3,zscale=mm,titles=false)
  ptitles("Electron Current vs z","z [mm]","I [mA]",t_label)
  fma() 
  # Line charge vs z   
  pzlchg(scale=1./1.e-9,zscale=mm,titles=false) 
  ptitles("Electron Line Charge vs z","z [mm]","Lambda [micro C/m]",t_label)
  fma() 

installafterstep(myplots) # install function myplots() to be called after each timestep

# --- Turn on time histories of some z-momments (needed for plots) 
top.lhxrmsz  = True
top.lhyrmsz  = True
top.lhepsnxz = True
top.lhepsnyz = True
top.lhcurrz  = True


# Generate the PIC code
#   * Initial field solve will be carried out on generate() call 
#   * Since no particles are present till timesteps are taken, 
#       the initial field will not include emitted electrons.  

if simtype == "w3d": 
  package("w3d") 
elif simtype == "wrz": 
  package("wrz") 
else:
  raise Exception("Error: simtype not defined")
generate() 

# Turn off field solver (for runs with applied field but no self feilds)
#   * Comment out for normal mode with self-fields. 
#   * True turns of field solver so loading rho and the FS not done.  
#     In this case the initial field solve on generate() still remains 
#     so the particles will see the applied field from the plate biases.   
#solver.ldosolve = False

# Find indices of center coordinate of mesh for later diagnostic use 
x_cen = 0. 
y_cen = 0. 
ix_cen = sum(where(w3d.xmesh <= x_cen,1,0))-1
iy_cen = sum(where(w3d.ymesh <= y_cen,1,0))-1 


# Make initial diagnostic plots of field (for simple check of fieldsolver)  

# --- contour diode field 
pcphizx(iy=iy_cen,xscale=1./mm,yscale=1./mm,
  titlet="Initial (No Beam) ES Potenital Contours in y = 0 Plane",titleb="z [mm]",titlel="x [mm]") 
fma() 

# --- plot on axis potential 
phiax = getphi(ix=ix_cen,iy=iy_cen)
plg(phiax/kV,w3d.zmesh/mm) 
ptitles("Initial (No Beam) On-Axis (x=y=0) ES Potential","z [mm]","Phi [kV]")
fma() 

#raise Exception("Code Stopped Here")  

# Advance simulation through each step interval set  
for ii in range(len(adv_steps)):
  top.dt = adv_dt[ii]
  step(adv_steps[ii])  

# History diagnostics 
#histplot() 

# Open interactive diagnostic window 
# winon()

# Some examples of code to retrieve particle coordinates 
# See warp.lbl.gov How To's for more info including tools to 
# export simulation data: See Saving/Retrieving Data  
# 
#  getz()        # returns array of z-coordinates of macroparticles 
#  getvz()       # returns array of vz values of macroparticle velocities  

# Print out timing statistics of run 
printtimers() 

# Make sure that last plot is flushed from buffer
fma() 
