import sys
sys.path.append("/home/pi/code/g2sphere")

from spherecam import G2SphereCam
from matplotlib import pyplot as plt

s = G2SphereCam(470, 514, 330, 30)
s.plot_edges()

plt.show()
