import time
import os

import picamera
import picamera.array

import cv2
import cv2.cv as cv

import numpy as np
from matplotlib import pyplot as plt

DEBUG = True

class G2SphereCam:
    def __init__(self,
            marble_center_guess_x,
            marble_center_guess_y,
            marble_radius_guess,
            marble_radius_tolerance,
            exposure_time_ms = 100000,
            edge_par_1 = 80,
            edge_par_2 = 180):

        self.failed = False

        with picamera.PiCamera(sensor_mode = 2, framerate=1) as camera:
            camera.shutter_speed = exposure_time_ms

            # let the camera warm up for 2 seconds
            time.sleep(2)

            if DEBUG:
                print "### CAMERA SETTINGS ###"
                print "Sensor Mode: "   , camera.sensor_mode
                print "Resolution: "    , camera.resolution
                print "Framerate: "     , camera.framerate
                print "Exposure Time: " , camera.shutter_speed
                print "Canny Edge Parameter 1:", edge_par_1
                print "Canny Edge Parameter 2:", edge_par_2

            with picamera.array.PiRGBArray(camera) as stream:
                camera.capture(stream, format='bgr')
                # TODO: don't hardcode these numbers
                self.image = stream.array #[50:1035, 600:1600]

        if DEBUG: print "Identifying edges in color image..."
        self.edges      = cv2.Canny(self.image, edge_par_1, edge_par_2)

        if DEBUG: print "Creating grayscale copy of image..."
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        if DEBUG: print "Identifying edges in grayscale image..."
        self.gray_edges = cv2.Canny(self.gray_image, edge_par_1, edge_par_2)

    def _clean_edges(self):

        if DEBUG: print "Cleaning extraneous detected edges outside/inside of sphere radius..."
        self.gray_edges_cleaned = np.copy(self.gray_edges)
        it = np.nditer(self.gray_edges_cleaned, flags=['multi_index'], op_flags=['readwrite'])

        while not it.finished:
            if it[0] == 0:
                it.iternext()
            else:
                x = (it.multi_index[1] - marble_center_guess_x)
                y = (it.multi_index[0] - marble_center_guess_y)
                r = np.sqrt(x**2 + y**2)

                if (r < marble_radius_guess - marble_radius_tolerance or r > marble_radius_guess + marble_radius_tolerance):
                    it[0] = 0

                if self.xs.size > 10000:
                    print "ERROR: Too many edge pixels (", self.xs.size, ") found!"
                    return -1

                it.iternext()

        if self.xs.size < 100:
            print "ERROR: Too few edge pixels (", self.xs.size, ") found!"
            return -1

    def find_edges(self):

        if (self._clean_edges() != 0):
            self.failed = True
            return

        if DEBUG: print "Shifting center and collecting edge pixel coordinates..."

        self.xs = []
        self.ys = []

        it = np.nditer(self.gray_edges_cleaned, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if (it[0] == 255):
                x = it.multi_index[1] - marble_center_guess_x
                y = it.multi_index[0] - marble_center_guess_y
                self.xs.append(x)
                self.ys.append(y)
            it.iternext()

        self.xs = np.array(self.xs)
        self.ys = np.array(self.ys)


        if DEBUG: print "Successfully found ", self.xs.size, " edge pixels."

    def write_edges_to_file(self):

        if DEBUG: print "Writing edge coordinates to file..."

        xy_data = np.zeros((self.xs.size, 2))
        xy_data[:,0] = self.xs
        xy_data[:,1] = self.ys

        data_dir = "/home/pi/code/g2sphere/dat/" + time.strftime("%d-%m-%Y/")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        old_data_nums = [ int(f[:-4]) for f in os.listdir(data_dir)
                if os.path.isfile(os.path.join(data_dir,f)) ]

        if len(old_data_nums) == 0:
            file_path = data_dir + "1.dat"
        else:
            file_path = data_dir + str(max(old_data_nums) + 1) + ".dat"

        np.savetxt(file_path, xy_data)

        if DEBUG: print "Filepath: ", file_path

    def plot_edge_overlay(self):

        if DEBUG: print "Preparing edge overlay image..."
        self.gray_edges_color = cv2.cvtColor(self.gray_edges, cv2.COLOR_GRAY2BGR)

        # separate rgb to make white pixels red, and re-order to matplotlib imshow RGB ordering
        # TODO: use numpy indexing here instead (faster)
        b,g,r = cv2.split(self.gray_edges_color)
        g = g * 0
        b = b * 0
        self.gray_edges_color = cv2.merge((r,g,b))

    def plot_edges(self):
        plt.figure(1)

        plt.subplot(121),plt.imshow(self.gray_image,cmap = 'gray')
        plt.subplot(122),plt.imshow(self.gray_edges,cmap = 'gray')

        #plt.figure(2)

        #plt.imshow(cv2.addWeighted(self.image, 0.3, self.gray_edges_color, 0.7, 0))

        #plt.figure(3)

        #plt.imshow(self.gray_edges_cleaned, cmap = 'gray')

        plt.show()

s = G2SphereCam(470, 514, 330, 30)
s.plot_edges()
