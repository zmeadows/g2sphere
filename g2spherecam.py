import time
import picamera
import picamera.array
import cv2
import cv2.cv as cv
import numpy as np
from matplotlib import pyplot as plt

PLOT_EDGES_FOUND = False

MARBLE_CENTER_X = 552
MARBLE_CENTER_Y = 500
MARBLE_RADIUS   = 330
MARBLE_RADIAL_TOL = 35

def find_edges():
	with picamera.PiCamera(resolution = (2592,1944), framerate=1) as camera:
        # TODO: difference between mode 2 and 3?
        camera.shutter_speed = 100000
        time.sleep(2)
        # camera.sharpness = -100
        with picamera.array.PiRGBArray(camera) as stream:
		camera.capture(stream, format='bgr')

		image = stream.array
		image = image[500:1500, 900:1900]

		gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(image, 80, 180)
		gray_edges = cv2.Canny(gray_image, 80, 180)
		gray_edges_cp = np.copy(gray_edges)

		it = np.nditer(gray_edges, flags=['multi_index'], op_flags=['readwrite'])
		while not it.finished:
			x = (it.multi_index[1] - MARBLE_CENTER_X)
			y = (it.multi_index[0] - MARBLE_CENTER_Y)
			r = np.sqrt(x**2 + y**2)
			if (r < MARBLE_RADIUS - MARBLE_RADIAL_TOL or r > MARBLE_RADIUS + MARBLE_RADIAL_TOL):
				it[0] = 0
			it.iternext()

		if PLOT_EDGES_FOUND:
			plt.figure(1)

			plt.subplot(121),plt.imshow(gray_image,cmap = 'gray')
			plt.subplot(122),plt.imshow(gray_edges,cmap = 'gray')

			plt.figure(2)

			plt.subplot(121),plt.imshow(gray_image,cmap = 'gray')
			plt.subplot(122),plt.imshow(gray_edges_cp,cmap = 'gray')

			plt.show()

		return gray_edges

def analyze(edge_array):
	it = np.nditer(edge_array, flags=['multi_index'], op_flags=['readonly'])
	count = 0
	while not it.finished:
		if (it[0] == 255):
			count = count + 1
			x = (it.multi_index[1] - MARBLE_CENTER_X)
			y = (it.multi_index[0] - MARBLE_CENTER_Y)
			theta = np.arctan2(y,x)
			r = np.sqrt(x**2 + y**2)
			print x,y,theta,r
		it.iternext()
	print count
	return 0

analyze(find_edges())
