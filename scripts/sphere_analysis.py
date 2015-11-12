import sys
sys.path.append("/home/pi/code/g2sphere")

from g2sphere import G2FileSphericity
from matplotlib import pyplot as plt

h = G2FileSphericity(sys.argv[1])
h.plot_r_t()
