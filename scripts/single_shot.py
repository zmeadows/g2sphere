import sys
sys.path.append("/home/pi/code/g2sphere")

from spherecam import G2EdgeCam
from matplotlib import pyplot as plt

s = G2EdgeCam()
s.plot_edges()

plt.show()
