import numpy as np
from matplotlib import pyplot as plt
import math
import sys
from scipy.optimize import fmin

DEBUG = True

### CONSTANTS ###

DARKGREY  = "#9f9f9f"
GREY      = "#D7D7D7"
LIGHTGREY = "#E8E8E8"
RED       = "#990000"
GREEN     = "#3BA03B"
BLUE      = "#5959FF"

class G2SphereAnalysis:
    def __init__(self, filename):
        sphere_data = np.loadtxt(filename)
        self.xs = sphere_data[:,0] - np.average(sphere_data[:,0])
        self.ys = sphere_data[:,1] - np.average(sphere_data[:,1])

        self._optimize_center()
        self._calculate_r_theta()

    def _calculate_r_theta(self):

        self.rs = []
        self.ts = []

        for i in range(self.xs.size):
            x = self.xs[i]
            y = self.ys[i]
            self.rs.append(np.sqrt(x**2 + y**2))
            self.ts.append(np.arctan2(y,x))

        self.rs = np.array(self.rs)
        self.ts = np.array(self.ts) + math.pi

        self.r_avg = np.average(self.rs)

        print "AVERAGE: ", np.average(self.rs)
        print "STD: ", np.std(self.rs)

    def _optimize_center(self):

        def change_center(args):
            new_xs = self.xs - args[0]
            new_ys = self.ys - args[1]
            temp_rs = []
            for i in range(new_xs.size):
                x = new_xs[i]
                y = new_ys[i]
                temp_rs.append(np.sqrt(x**2 + y**2))
            return np.std(np.array(temp_rs))

        if DEBUG: print "Finding the center of the sphere..."

        pars = fmin(change_center, [0,0], xtol=1.0e-5, ftol=1.0e-5)

        self.xs = self.xs - pars[0]
        self.ys = self.ys - pars[1]

    def plot_r_t(self):
        plt.figure(facecolor=LIGHTGREY)
        plt.plot(self.ts, self.rs, color=BLUE, linestyle="None", marker=".") #markevery=20
        plt.plot(self.ts, np.zeros(self.ts.size) + self.r_avg, color=RED, linestyle="-") #markevery=20
        plt.grid()
        plt.gca().set_axis_bgcolor(GREY)
        plt.xlabel("Theta (rads)")
        plt.ylabel("Radius (pixels)")
        plt.xlim(0, 2*math.pi)
        plt.ylim(self.r_avg - 5, self.r_avg + 5)

        plt.show()

    def plot_x_y(self):
        return


if (len(sys.argv) <= 1):
    print "need a .dat file to analyze"
else:
    a = G2SphereAnalysis(sys.argv[1])
    a.plot_r_t()

