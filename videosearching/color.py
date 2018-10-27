from tkinter import *
import math
import numpy as np
from PIL import Image
import _pickle as cPickle
import cv2
from math import log10, floor

import glob

IMG_WIDTH = 352
IMG_HEIGHT = 288
NUM_DOM = 5
DB_LEN = 600
QUERY_LEN = 150
NORM = 44220 #half of a diagonal on a 255x255x255 cube is ~220 and taking into consideration the weighting of the error (65-(2*i)**2) we have 220*(10+8+6+4+2) = 6600
MAX_ERR = 444 #444 #length of the diagonal of a 255x255x255 cube, aka the farthest two points could be from each other


cache_path = './static/data/cache/color'

database_path = './static/data/database'

# dbFiles = ["C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/flowers/flowers","C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/interview/interview", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/movie/movie", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/musicvideo/musicvideo", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/sports/sports", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/starcraft/starcraft", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/traffic/traffic"]
dbPklFile = sorted(["flower.pkl", "interview.pkl", "movie.pkl", "musicvideo.pkl", "sports.pkl", "starcraft.pkl", "traffic.pkl"])

# queryFiles = ["C:/Users/Alex Grieco/Desktop/CS576_final/query_vids/first/first"]
queryPklFile = ["query.pkl"]


IMAGES = []

#construct the array representation of the pixels of the image
def read_img(path):
	#open the file and fill the temp array
	with open(path, 'rb') as f:
		res = f.read()

    #create individual r,g,b buffers and combine them in an rgb array
	r = np.zeros((IMG_HEIGHT, IMG_WIDTH))
	g = np.zeros((IMG_HEIGHT, IMG_WIDTH))
	b = np.zeros((IMG_HEIGHT, IMG_WIDTH))
	rgb = np.stack([r,g,b], 2)

	#fill the rgb array from the filled temporary array
	for k in range(3):
		for i in range(IMG_HEIGHT):
			for j in range(IMG_WIDTH):
				rgb[i][j][k] = ((res[k*IMG_WIDTH*IMG_HEIGHT + i*IMG_WIDTH + j]))
             

	rgb = rgb.astype('uint8')

	return rgb

def round_sig(x, sig=3):
	if(x == 0):
		return round(x, sig-1)
	else:
		return round(x, sig-int(floor(log10(abs(x))))-1)

#returns num most dominant RGB values in the image img
def get_dominant_colors(img, num):
	#returns tuples of RGB values and their frequencies
	pixels = img.getcolors(IMG_WIDTH*IMG_HEIGHT)
	pixels.sort(reverse = True)

	freq =[]
	rgb_vals=[]
	for key,val in pixels[:num]:
		freq.append(val)
		rgb_vals.append(round_sig(key/float(IMG_WIDTH*IMG_HEIGHT)))
	return [rgb_vals, freq]

#read dominate colors for each .rgb file into a file
def colors_to_file(inFile, outFile, num=NUM_DOM, frameNum=QUERY_LEN):
	pixel_doms =[]
	print(inFile)
	query_path = sorted(glob.glob(inFile + "/*.rgb"))
	# print(query_path)
	for path in query_path:
		temp = read_img(path)
		img = Image.fromarray(temp, "RGB")
		IMAGES.append(temp)
		saved_path = '.' + path.split('.')[1] + '.jpg'
		print(saved_path, "saved_path")
		img.save(saved_path)
		pixel_doms.append(get_dominant_colors(img, num))
		# print(inFile, i+1)

	# for i in range(frameNum):
	# 	temp = read_img(inFile+"%03d.rgb"%(i+1))
	# 	img = Image.fromarray(temp, "RGB")
	# 	IMAGES.append(temp)
	# 	img.save(inFile+"%03d"%(i+1)+".jpg")
	# 	pixel_doms.append(get_dominant_colors(img, num))
	# 	print(inFile, i+1)
	
	# use cPickle to encode the array so it is easy to open as an array later
	cPickle.dump(pixel_doms, open(outFile, "wb")) 
	
def return_doms(file):
	return cPickle.load(open(file, "rb"))

def compare_images(testPic, dbPic, num=NUM_DOM):
	err = 0
	lenTest = len(testPic[1])
	lenDB = len(dbPic[1])

	minLen = min(lenTest,lenDB)
	last = num - minLen

	for i in range(minLen):
		a = np.asarray(dbPic[1][i])
		b = np.asarray(testPic[1][i])

		#I've weighted the error calc to give more error for the more dominant colors
		err+= (65 - (2*i)**2)*np.linalg.norm(a - b)

	
	if last != 0:
		for i in range(num-last+1,num-last+abs(lenTest - lenDB)):
			err+=(65 - (2*i)**2)*MAX_ERR
	

	sim = 1 - err/NORM
	if sim < 0:
		sim = 0

	return sim

# def max_sim_block(i, jstep = 25, kstep=5, maxSim=0):
# 	jmax = 0
# 	jmax2 = 0
# 	for j in range(0, DB_LEN-QUERY_LEN,jstep):
# 		sim = 0
# 		for k in range(0,QUERY_LEN,kstep):
# 			sim+=compare_images(return_doms(queryPklFile[0])[k], return_doms(cache_path + '/' + dbPklFile[i])[j+k])
# 		if sim > maxSim:
# 			maxSim = sim
# 			jmax2 = jmax
# 			jmax = j
# 	return jmax, jmax2
def max_sim_block(i, testFile, dbFile, jstep = 25, kstep=5, maxSim=0):
	jmax = 0
	jmax2 = 0
	for j in range(0, DB_LEN-QUERY_LEN,jstep):
		sim = 0
		for k in range(0,QUERY_LEN,kstep):
			sim+=compare_images(testFile[k], dbFile[j+k])
		if sim > maxSim:
			maxSim = sim
			jmax2 = jmax
			jmax = j
	return jmax, jmax2

# def max_sim(i, jstart, jstep=25, kstep=5, maxSim=0):
# 	max_loc = 0
# 	for j in range(jstart, jstart+jstep):
# 		sim= 0
# 		for k in range(0, QUERY_LEN, kstep):
# 			sim+=compare_images(return_doms(queryPklFile[0])[k], return_doms(cache_path + '/' + dbPklFile[i])[j+k])
# 		if sim > maxSim:
# 			maxSim = sim
# 			max_loc = j

# 	return maxSim, max_loc

def max_sim(i, jstart, testFile, dbFile, jstep=25, kstep=5, maxSim=0):
	max_loc = 0
	for j in range(jstart, jstart+jstep):
		sim= 0
		for k in range(0, QUERY_LEN, kstep):
			sim+=compare_images(testFile[k], dbFile[j+k])
		if sim > maxSim:
			maxSim = sim
			max_loc = j

	return maxSim, max_loc

# def setArray(i, maxLoc):
# 	arr = [0]*DB_LEN
# 	for j in range(150):
# 		arr[j+maxLoc]=round_sig(compare_images(return_doms(queryPklFile[0])[j], return_doms(cache_path + '/' + dbPklFile[i])[j+maxLoc]))

# 	return arr

def setArray(i, maxLoc, testFile, dbFile):
	arr = [0]*DB_LEN
	for j in range(150):
		arr[j+maxLoc]=round_sig(compare_images(testFile[j], dbFile[j+maxLoc]))

	return arr



# def movie_err(i):
# 	maxLoc, maxLoc2 = max_sim_block(i)
# 	maxSim, maxLoc=max_sim(i, maxLoc)
# 	maxSim2, maxLoc2=max_sim(i, maxLoc2, maxSim=maxSim)

# 	if maxSim2 > maxSim:
# 		maxLoc = maxLoc2
# 		maxSim = maxSim2

# 	maxSim = round_sig(maxSim/30)
# 	# arr = setArray(i, maxLoc)#range(maxLoc, maxLoc+150)#
# 	arr = setArray(i, maxLoc)

# 	return maxSim, arr

def movie_err(i, testFile):
	dbFile = return_doms(cache_path + '/' + dbPklFile[i])
	maxLoc, maxLoc2 = max_sim_block(i, testFile, dbFile)
	maxSim, maxLoc=max_sim(i, maxLoc, testFile, dbFile)
	maxSim2, maxLoc2=max_sim(i, maxLoc2, testFile, dbFile, maxSim=maxSim)

	if maxSim2 > maxSim:
		maxLoc = maxLoc2
		maxSim = maxSim2

	maxSim = round_sig(maxSim/30)
	arr = setArray(i, maxLoc, testFile, dbFile)#range(maxLoc, maxLoc+150)#

	return maxSim, arr

def return_info(queryLoc):
	colors_to_file(queryLoc, queryPklFile[0])
	
	# subprocess.call('ffmpeg.exe -y -r 30 -f image2 -i "' + queryLoc + '%03d.jpg" -i "' + queryLoc + '.wav" -c:v libx264 -c:a aac -b:a 192k queryVid.mp4', shell = False)
	"""
	ffmpeg -r 30 -f image2 -i "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/traffic/traffic%03d.jpg" -i "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/traffic/traffic.wav" -c:v libx264 -c:a aac -b:a 192k trafficVid.mp4
	dbFiles = ["C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/flowers/flowers","C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/interview/interview", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/movie/movie", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/musicvideo/musicvideo", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/sports/sports", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/starcraft/starcraft", "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/traffic/traffic"]
	"""
	testFile = return_doms(queryPklFile[0])
	final_arr = []
	for i in range(len(dbPklFile)):
		# sim, arr = movie_err(i)
		sim, arr = movie_err(i, testFile)
		final_arr.append((i, sim, arr))

	# final_arr.sort(key=lambda x: x[1], reverse=True)
	final_arr.sort(key=lambda x: x[0])
	return final_arr
	
if __name__ == '__main__':
	print('test')
	# dbFiles = sorted(glob.glob(database_path + '/*'))
	# for i in range(len(dbFiles)):
	# 	colors_to_file(dbFiles[i], cache_path + '/' + dbPklFile[i], frameNum=600)


"""
arr = return_info(queryFiles[0])

for line in arr:
	print(line)

"""

#If we need to encode the database files again
"""
for i in range(len(dbPklFile)):
	colors_to_file(dbFiles[i], dbPklFile[i], frameNum=600)
"""

