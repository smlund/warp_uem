import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.description = "Generate a sample of a Gaussian distibution in the spatial extent.  Outputs x y z 0 0 0"
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('R', type=float, 
                    help='The radial standard extent of the cylinder ' +
                    'from which the starting position will be drawn.')
parser.add_argument('L', type=float,
                    help="The length of the cylinder.")
parser.add_argument('N', type=int, 
                    help='The number of macroparticles to draw ' +
                    'from the Gaussian distribution.')
args = parser.parse_args()

phi = 2*np.pi*np.random.uniform(size=args.N)
u = np.random.uniform(size=args.N)
r = args.R*np.sqrt(u)
x = r*np.cos(phi)
y = r*np.sin(phi)
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
