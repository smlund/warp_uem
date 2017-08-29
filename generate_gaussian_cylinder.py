import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.description = "Generate a sample of a Gaussian distibution in the spatial extent.  Outputs x y z 0 0 0"
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('sigma_r', type=float, 
                    help='The radial standard deviation of the Gaussian ' +
                    'from which the srting position will be drawn.')
parser.add_argument('L', type=float,
                    help="The length of the cylinder.")
parser.add_argument('N', type=int, 
                    help='The number of macroparticles to draw ' +
                    'from the Gaussian distribution.')
args = parser.parse_args()

x, y = np.random.multivariate_normal([0,0], args.sigma_r**2*np.identity(2), args.N).T
z = np.random.uniform(0,args.L,args.N)
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
