import time
import os

import picamera
import picamera.array

import cv2
import cv2.cv as cv

import numpy as np
from matplotlib import pyplot as plt

DEBUG = True

class G2Cam(object):
    def __init__(self, exposure_time_ms = 100000, **kwargs):
        super(G2Cam, self).__init__(**kwargs)

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
                print ""

            with picamera.array.PiRGBArray(camera) as stream:
                if DEBUG: print "Capturing image..."
                camera.capture(stream, format='bgr')
                # TODO: don't hardcode these numbers
                self.image = stream.array #[50:1035, 600:1600]


class G2EdgeCam(G2Cam):
    def __init__(self, edge_par_1 = 80, edge_par_2 = 180, **kwargs):
        super(G2EdgeCam, self).__init__(**kwargs)

        if DEBUG: print "Creating grayscale copy of image..."
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        if DEBUG:
            print "Identifying edges in grayscale image..."
            print "Canny Edge Parameter 1:", edge_par_1
            print "Canny Edge Parameter 2:", edge_par_2
        self.gray_edges = cv2.Canny(self.gray_image, edge_par_1, edge_par_2)

    def write_edge_image(self, filepath):
        return

    def _collect_edges(self, x_0, y_0):

        if DEBUG: print "Collecting edge pixel coordinates..."

        self.xs = []
        self.ys = []

        it = np.nditer(self.gray_edges_cleaned, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if (it[0] == 255):
                x = it.multi_index[1] - x_0
                y = it.multi_index[0] - y_0
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

    def plot_edges(self):

        if DEBUG: "Plotting edge images..."

        plt.figure()

        plt.subplot(121),plt.imshow(self.gray_image,cmap = 'gray')
        plt.subplot(122),plt.imshow(self.gray_edges,cmap = 'gray')
        plt.gcf().canvas.set_window_title("Grayscale Edges")

        plt.show()

    def save_edge_image(self, filename):
        cv2.imwrite(filename, self.gray_edges)

class G2SphereCam(G2EdgeCam):
    def __init__(self, **kwargs):
         super(G2SphereCam, self).__init__(**kwargs)

    def _clean_edges(self, center_guess_x, center_guess_y, radius_guess, radius_tolerance):
        if DEBUG: print "Cleaning extraneous detected edges outside/inside of sphere radius..."
        self.gray_edges_cleaned = np.copy(self.gray_edges)
        it = np.nditer(self.gray_edges_cleaned, flags=['multi_index'], op_flags=['readwrite'])

        while not it.finished:
            if it[0] == 0:
                it.iternext()
            else:
                x = (it.multi_index[1] - center_guess_x)
                y = (it.multi_index[0] - center_guess_y)
                r = np.sqrt(x**2 + y**2)

                if (r < radius_guess - radius_tolerance or r > radius_guess + radius_tolerance):
                    it[0] = 0

                if self.xs.size > 10000:
                    print "ERROR: Too many edge pixels (", self.xs.size, ") found!"
                    return -1

                it.iternext()

        if self.xs.size < 100:
            print "ERROR: Too few edge pixels (", self.xs.size, ") found!"
            return -1

    def plot_edge_overlay(self):

        if DEBUG: print "Preparing and plotting edge overlay image..."
        self.gray_edges_color = cv2.cvtColor(self.gray_edges, cv2.COLOR_GRAY2BGR)

        # TODO: use numpy indexing here instead (faster)
        b,g,r = cv2.split(self.gray_edges_color)
        g = g * 0
        b = b * 0
        self.gray_edges_color = cv2.merge((r,g,b))

        plt.figure()
        plt.imshow(cv2.addWeighted(self.image, 0.3, self.gray_edges_color, 0.7, 0))



