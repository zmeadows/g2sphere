import sys
sys.path.append("/home/pi/code/g2sphere")

from spherecam import G2EdgeCam

s = G2EdgeCam()

s.save_edge_image(sys.argv[1])

s.plot_edges()

