import sys
sys.path.append("/home/pi/code/g2sphere")

from spherecam import G2EdgeCam
from matplotlib import pyplot as plt

s = G2EdgeCam(edge_par_1 = 100, edge_par_2 = 190, exposure_time_ms = 400000)
s.plot_edges()

plt.show()
