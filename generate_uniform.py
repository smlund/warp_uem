import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.description = "Generate a sample of a Gaussian distibution in the spatial extent.  Outputs x y z 0 0 0"
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('R', type=float, 
                    help='The radius of the uniform distribution' +
                    'from which the starting position will be drawn.')
parser.add_argument('N', type=int, 
                    help='The number of macroparticles to draw ' +
                    'from the Gaussian distribution.')
parser.add_argument('--distribution', dest="distribution", type=str, 
                    help='Describes the symmetry of the distribution. Options are spherical or cylindrical.' +
                     'Default is spherical.',default="spherical")
args = parser.parse_args()

if args.distribution == "spherical":
  costheta = 2*np.random.uniform(size=args.N) - 1
  theta = np.arccos(costheta)
  phi = 2*np.pi*np.random.uniform(size=args.N)
  u = np.random.uniform(size=args.N)
  r = args.R*np.cbrt(u)
  x = r*np.cos(phi)*np.sin(theta)
  y = r*np.sin(phi)*np.sin(theta)
  z = r*costheta
elif args.distribution == "cylindrical":
  phi = 2*np.pi*np.random.uniform(size=args.N)
  u = np.random.uniform(size=args.N)
  r = args.R*np.sqrt(u)
  x = r*np.cos(phi)
  y = r*np.sin(phi)
  z = np.zeros(x.size)
else:
  raise Exception("That distribution type is unsupported.")
px = np.zeros(x.size)
py = np.zeros(y.size)
pz = np.zeros(z.size)
for i in range(x.size):
  line = []
  line.append(x[i])
  line.append(y[i])
  line.append(z[i])
  line.append(px[i])
  line.append(py[i])
  line.append(pz[i])
  print " ".join([str(element) for element in line])
