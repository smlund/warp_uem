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
