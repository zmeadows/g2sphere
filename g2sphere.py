import numpy as np
from matplotlib import pyplot as plt
import math
import sys
from scipy.optimize import fmin
import cv2

DEBUG = True

class G2SphericityAnalysis(object):
    def __init__(self, **kwargs):
        super(G2SphericityAnalysis, self).__init__(**kwargs)

        self.xs = np.array([], dtype=np.float64)
        self.ys = np.array([], dtype=np.float64)
        self.rs = []
        self.ts = []

        self.r_avg = 0.0

    def _calculate_r_theta(self):
        for i in range(self.xs.size):
            x = self.xs[i]
            y = self.ys[i]
            self.rs.append(np.sqrt(x**2 + y**2))
            self.ts.append(np.arctan2(y,x))

        self.rs    = np.array(self.rs)
        self.ts    = np.array(self.ts) + math.pi
        self.r_avg = np.average(self.rs)
        self.r_std = np.std(self.rs)

        if DEBUG:
            print "AVERAGE RADIUS: " , self.r_avg
            print "STD (PIXELS): "   , self.r_std

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
        plt.ylim(self.r_avg - 6*self.r_std, self.r_avg + 6*self.r_std)

        plt.show()

class G2ImageSphericity(G2SphericityAnalysis):
    def __init__(self, imagepath, **kwargs):
        super(G2ImageSphericity, self).__init__(**kwargs)
        self.edge_image = cv2.imread(imagepath, flags = 0)

        if DEBUG: print "Collecting edge pixel coordinates from image..."

        self.xs = []
        self.ys = []

        it = np.nditer(self.edge_image, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if (it[0] == 255):
                x = it.multi_index[1]
                y = it.multi_index[0]
                self.xs.append(x)
                self.ys.append(y)
            it.iternext()

        self.xs = np.array(self.xs)
        self.ys = np.array(self.ys)

        if DEBUG: print "Successfully found ", self.xs.size, " edge pixels."

        self.xs = self.xs - np.average(self.xs)
        self.ys = self.ys - np.average(self.ys)

        self._optimize_center()
        self._calculate_r_theta()

class G2FileSphericity(G2SphericityAnalysis):
    def __init__(self, filename, **kwargs):
        super(G2FileSphericity, self).__init__(**kwargs)
        sphere_data = np.loadtxt(filename)
        self.xs = sphere_data[:,0] - np.average(sphere_data[:,0])
        self.ys = sphere_data[:,1] - np.average(sphere_data[:,1])

        self._optimize_center()
        self._calculate_r_theta()

    def plot_x_y(self):
        return

DARKGREY  = "#9f9f9f"
GREY      = "#D7D7D7"
LIGHTGREY = "#E8E8E8"
RED       = "#990000"
GREEN     = "#3BA03B"
BLUE      = "#5959FF"

#if (len(sys.argv) <= 1):
#    print "need a .dat file to analyze"
#else:
#    a = G2SphereAnalysis(sys.argv[1])
#    a.plot_r_t()

