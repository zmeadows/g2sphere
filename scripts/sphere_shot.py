import sys
sys.path.append("/home/pi/code/g2sphere")

from spherecam import G2SphereCam, query_yes_no
from matplotlib import pyplot as plt

s = G2SphereCam(exposure_time_ms = 200000,
                edge_par_1 = 105,
                edge_par_2 = 180,
                x_cut_1 = 598,
                x_cut_2 = 1517,
                y_cut_1 = 12,
                y_cut_2 = 932)

s.clean_edges(460,460, 360, 23)
s.plot_edges()

if query_yes_no("Write edge coordinates to file?"):
    s.collect
    s.write_edges_to_file()

plt.show()
