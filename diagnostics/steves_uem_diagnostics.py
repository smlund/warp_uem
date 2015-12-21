from warp import *

def steves_plots(top):
  """
  Uses the global variable top to define
  a bunch of plots.
  Args:
    top: The top object from warp.
  Return value:
    None --- although plots are added to the .cgm file.
  """
  mr = 1.e-3 # milli-radian conversion scale 
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
  # normalized rms z-z' emittance vs z 
  #    From check of code in getzmmnts routine in top.F
  #    * [epsnz] = meters 
  #    *  zc  = z - zbar 
  #       vzc = vz - vzbar 
  #       epsnz = 4.*sqrt( <zc**2><vzc**2> - <zc*vzc>**2 )/clight  
  #
  pzepsnz(scale=1./(4.*mm),zscale=mm,titles=false) 
  ptitles("Normalized rms z-z' Emittance vs z",
          "z [mm]","Emittance [mm-mr]",t_label)
  fma() 
  # Current vs z
  pzcurr(scale=1./1.e-3,zscale=mm,titles=false)
  ptitles("Electron Current vs z","z [mm]","I [mA]",t_label)
  fma() 
  # Line charge vs z   
  pzlchg(scale=1./1.e-9,zscale=mm,titles=false) 
  ptitles("Electron Line Charge vs z","z [mm]","Lambda [micro C/m]",t_label)
  fma() 

def electric_potential_plots(ix, iy):
  """
  Make initial diagnostic plots of field (for simple check of fieldsolver)  
  Args:
    ix: The index of the center of the mesh in the x direction.
    iy: The index of the center of the mesh in the y direction.
  """
# --- contour diode field 
  pcphizx(iy=iy,xscale=1./mm,yscale=1./mm,
  titlet="Initial (No Beam) ES Potenital Contours in y = 0 Plane",titleb="z [mm]",titlel="x [mm]") 
  fma() 

# --- plot on axis potential 
  phiax = getphi(ix=ix,iy=iy)
  plg(phiax/kV,w3d.zmesh/mm) 
  ptitles("Initial (No Beam) On-Axis (x=y=0) ES Potential","z [mm]","Phi [kV]")
  fma() 

