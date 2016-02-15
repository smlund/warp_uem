warp_uem
Git repository of Warp simulation scripts/tools to model the UEM 
ultra-intense electron microscope experiment at 
Michigan State University. 

Professor Steven M. Lund
Physics and Astronomy Department
Facility for Rare Isotope Beams
Michigan State University
lund@frib.msu.edu
517-908-7291

Dr. Brandon Zerbe 
Physics and Astronomy Department
Michigan State University
zerbe@msu.edu 


To initialize the repository, 

   % git clone  git@github.com:smlund/warp_uem.git

This will create a directory, ./warp_uem where command was 
run with the archive files.   

To get the latest version descend into directory warp_ion_beamline and run:

  % git pull 

When modifying the repository (for those with edit privilege, please contact 
me if you want to contribute and I will add you) 

  ... edit files etc then checkin (use readme.txt as example here) using: 
  % git add readme.txt 
  % git commit -m "SML: updated readme.txt file" 
  % git push 

To run the program, add the directory where this readme.txt file is to your 
python path:

  export PYTHONPATH=$PYTHONPATH:$PWD

This will allow python to find the modules in the import statement.

Before running these scripts, the following dependency needs to be resolved:

  Download the config2class utility and put it in your src directory (or wherever 
  you keep such things):

  git clone git@github.com:billyziege/config2class.git

and then the following directories need to be added to your python path:

  export PYTHONPATH=$PYTHONPATH:/path/to/warp_uem:/path/to/config2class/src

This directory contains the scripts:

  uem.py: Runs the ultrafast electron microscopy script through warp.  Required
    arguments are:
    1. Initial conditions file containing a pickle dict of N particles with 
      t, x, y, z, px, py, and pz dict keys.
    2. Config file with a bunch of parameters and references to other config files. 
  plot_conductors.py: Loads the section "Conductor elements" from the config file and
    plots the resulting electric field after initiallizing the grid.
  preprocess_field.py: Loads the field from the external file, ravels it for use in Fortran,
    writes it to a file, and writes the relevant statistics for loading to a neighboring 
    configuration file for easy loading.
  plot_field.py:  Loads the field from the input configuration file and outputs plots
    for the field.
  continue_simulation_through_field.py:  Loads the input initial conditions in a single time
    step and applies any fields to the simulation.  This is to be used with particles after 
    they already have been injected.

To see other options for these scripts:
  % python ${script_name} -h

This repository is under version control, and previous versions requiring this additional set-up
can be access:
  
  git checkout v-0.1 --- version mainly a product of Steven Lund but with argparse partially
    incorporated.
  
  git checkout v-1.0 --- version including the code from Brandon Zerbe that modularizes the code.

  git checkout v-1.1 --- version including the new plot_conductors utility.

  git checkout v-1.1 --- version including the new field and continue simulation utilities.
