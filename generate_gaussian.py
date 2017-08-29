import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.description = "Generate a sample of a Gaussian distibution in the spatial extent.  Outputs x y z 0 0 0"
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('sigma_r', type=float, 
                    help='The radial standard deviation of the Gaussian ' +
                    'from which the srting position will be drawn.')
parser.add_argument('N', type=int, 
                    help='The number of macroparticles to draw ' +
                    'from the Gaussian distribution.')
parser.add_argument('--distribution', dest="distribution", type=str, 
                    help='Describes the symmetry of the distribution. Options are spherical or cylindrical.' +
                     'Default is spherical.',default="spherical")
args = parser.parse_args()

if args.distribution == "spherical":
  x, y, z = np.random.multivariate_normal([0,0,0], args.sigma_r**2*np.identity(3), args.N).T
elif args.distribution == "cylindrical":
  x, y = np.random.multivariate_normal([0,0], args.sigma_r**2*np.identity(2), args.N).T
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
