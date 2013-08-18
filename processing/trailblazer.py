#modules to request server stuff
from urllib.request import urlopen
from urllib.parse import urlencode

import matplotlib.pyplot as plot
import json, random, math, os, sys

#be able to call commands
import subprocess as cmd

#import matrix repr
from numpy import mat

#import numpy for errors
import numpy as numpy

#import UTM coordinate transformation
from utm import from_latlon as toUTM

#import deep array copy for functions
from copy import deepcopy as deep

#used for saving files
testName = 'No Name'

#file location
testRoot = 'C:'

#save location
testSave = 'C:'

#Python 2 command
pyRoot = 'python27'

#set Python 2 command
def setPythonTwo(loc):
	global pyRoot
	pyRoot = loc
	
#get Python 2 command
def getPythonTwo():
	global pyRoot
	return pyRoot

#get directory of this
def getMyDirectory():
	path = os.path.abspath(__file__)
	return os.path.dirname(path)
	
#set the global name
def setTestName(name):
	global testName
	testName = name

#set file location
def setTestRoot(loc):
	global testRoot
	testRoot = loc
	
#get our test name
def getTestName():
	global testName
	return testName

#get file location
def getTestRoot():
	global testRoot #folder of all tests
	return testRoot + '/' + getTestName()

#set file save dir
def setTestSave():
	#get global save
	global testSave
	
	number = 1 #keep track of what folders we have already used for data
	while os.path.isdir(getTestRoot() + '/' + str(number)): number += 1
	
	os.makedirs(getTestRoot() + '/' + str(number)) #create directory
	testSave = getTestRoot() + '/' + str(number) #return minimum number

#get file save dir
def getTestSave():
	global testSave
	return testSave
	
#get heat map file	
def getHeatSave():
	global testSave #get save location
	return testSave + '/' + 'gray.png'
	
def fakeData(data):
	#store each session
	#in this dictionary
	sessions = {}
	
	for idx in range(len(data)):
		#instantiate array
		sessions[idx] = []
		
		for tup in data[idx]:
			if tup[0] == 'r':
				#relative footfall event
				sessions[idx].append({
					'type' : 'relative',
					'x' : tup[1],
					'y' : tup[2],
					'stride' : 0.74,
					'time' : tup[3]
				})
				
			elif tup[0] == 'a':
				sessions[idx].append({
					'type' : 'absolute',
					'x' : tup[1],
					'y' : tup[2],
					'stride' : 0.74,
					'time' : tup[3],
					'north' : tup[5],
					'east' : tup[4],
					'zone' : 'Z',
					'accuracy' : tup[6]
				})

		#auto-generate a fake label for start
		sessions[idx][0]['label'] = 'Start'
			
	#output fakes
	return sessions

#function to download JSON data
#as a dictionary of session IDs
#and their associated events
def downloadData():
	file = open('query.sql', 'r')
	query = file.read()
	post = urlencode({'query' : query}).encode('ascii')

	url = 'http://www.skalon.com/trailblazer/retrieve.php'
	response = urlopen(url, post)
	data = json.loads(str(response.read().decode('utf-8')))
	
	sessions = {}

	for event in data:
		if event['session'] not in sessions:
			sessions[event['session']] = [event]
		else:
			sessions[event['session']].append(event)
			
	#return sessions array and count
	return sessions, len(sessions)

#helper function
#sort events by time
def timeSort(dic):
	return dic['time']

#strip unnececessary JSON parameters
#associate labels and GPS with footfalls
def cleanData(data):
	#create copy of data
	data = deep(data)
	
	#store data with
	#labels and GPS
	newData = {}
	
	for key, session in data.items():
		session = sorted(session, key = timeSort) #sort events by time
		newData[key] = []
		
		#first relative
		relIdx = 0
		
		while session[relIdx]['type'] != 'relative':
			relIdx += 1 #loop through until found
			
		xValue = session[relIdx]['absX']
		yValue = session[relIdx]['absY']
		stride = session[relIdx]['stride']
		time = session[relIdx]['time']
		label = session[relIdx]['start'] 
				
		newData[key].append({
			'type' : 'relative',
			'x' : xValue,
			'y' : yValue,
			'stride' : stride,
			'label' : label,
			'time' : time
		})
		
		for idx in range(1, len(session)):
			if idx == relIdx:
				continue
			
			if session[idx]['type'] == 'label':
				if len(newData) > 1: #don't overwrite start location
					newData[key][-1]['label'] = session[idx]['content']
			
			elif session[idx]['type'] == 'absolute':
				#change type as an identifier
				newData[key][-1]['type'] = 'absolute'
				
				latitude = session[idx]['latitude']
				longitude = session[idx]['longitude']
				northing, easting, zone = toUTM(latitude, longitude)
				
				newData[key][-1]['north'] = northing #cartesian y-axis
				newData[key][-1]['east'] = easting #cartesian x-axis
				newData[key][-1]['zone'] = zone #UTM validity zone
				newData[key][-1]['accuracy'] = session[idx]['accuracy']
				
			elif session[idx]['type'] == 'relative':
				xValue = session[idx]['absX']
				yValue = session[idx]['absY']
				stride = session[idx]['stride']
				time = session[idx]['time'] 
						
				newData[key].append({
					'type' : 'relative',
					'x' : xValue,
					'y' : yValue,
					'stride' : stride,
					'time' : time
				})
	
	#output organized
	return newData

#get distance between
#two XY coordinates
def distance(first, second):
	xsq = (second[0] - first[0])**2
	ysq = (second[1] - first[1])**2
	return (xsq + ysq)**(1/2)

#take a sequence of
#footfalls and transform
#them to fit GPS points
def transform(steps):
	#create copy of data
	steps = deep(steps)
	
	#coordinate frame
	origin = steps[0]
	originIdx = 0

	#get origin rel and abs XY-coordinates
	originRel = (origin['x'], origin['y'])
	originAbs = (origin['east'], origin['north'])
	originZone = origin['zone'] #zone check
	
	#set current accuracy
	currentAcc = origin['accuracy']
	
	#transform relative to absolute
	for idx in range(len(steps)):
		steps[idx]['x'] += originAbs[0] - originRel[0]
		steps[idx]['y'] += originAbs[1] - originRel[1]
	
	for idx in range(1, len(steps)):
		if steps[idx]['type'] == 'absolute':
			reading = (steps[idx]['east'], steps[idx]['north'])
			footfall = (steps[idx]['x'], steps[idx]['y'])
			
			#get new reading accuracy
			newAcc = steps[idx]['accuracy']
			
			#discard if reading overlaps with previous reading
			if (distance(originAbs, reading) <= currentAcc + newAcc):
				continue
			
			#same thing, but with footfall and its corresponding GPS
			if (distance(footfall, reading) <= currentAcc + newAcc):
				continue
			
			#check if zones match, or continue
			if originZone != steps[idx]['zone']:
				continue
			
			#calculate linear matrix transformation for footfalls
			initialPoints = mat([list(originAbs), list(footfall)]).T
			finalPoints = mat([list(originAbs), list(reading)]).T
			
			try:
				#see if we can find a transformation matrix
				transform = finalPoints * initialPoints.I
				
			#this fires if initialPoints is singular
			except numpy.linalg.linalg.LinAlgError:
				#we could not
				continue
			
			#apply transformation to each point
			#that is located between readings
			for pos in range(originIdx, idx + 1):
				oldPt = (steps[pos]['x'], steps[pos]['y'])
				oldVec = mat([[oldPt[0], oldPt[1]]]).T
				newVec = transform * oldVec
				
				newPt = newVec.ravel().tolist()[0]
				(steps[pos]['x'], steps[pos]['y']) = newPt
			
			#calculate translation vector for reading
			footfallVec = mat([list(footfall)]).T
			readingVec = mat([list(reading)]).T
			translate = readingVec - footfallVec
			
			#apply translation to each point
			#that is subsequent to new reading
			for pos in range(idx + 1, len(steps)):
				oldPt = (steps[pos]['x'], steps[pos]['y'])
				oldVec = mat([[oldPt[0], oldPt[1]]]).T
				newVec = oldVec + translate
				
				newPt = newVec.ravel().tolist()[0]
				(steps[pos]['x'], steps[pos]['y']) = newPt
			
			#all of the stuff we did at the beginning
			#since the first point was the first origin anchor
			
			origin = steps[idx]
			originIdx = idx
			
			originRel = (origin['x'], origin['y'])
			originAbs = (origin['east'], origin['north'])
			
			#see discussion for why this changes
			currentAcc = origin['accuracy']
			
	#return all but
	#first origin point
	return steps[1:]
	
#preprocess footfalls with GPS coordinates
#rotate x and y coords in absolute frame
def preprocess(data):
	#create copy of data
	data = deep(data)
	
	#store origin indices
	origins = {}
	
	for key, session in data.items():
		#no GPS found yet
		originIdx = None
		best = float('inf')
		
		#get GPS with lowest accuracy
		for idx in range(len(session)):
			if session[idx]['type'] == 'absolute':
				accuracy = session[idx]['accuracy']
				if originIdx is None or accuracy < best:
					best = accuracy
					originIdx = idx
		
		if originIdx is not None:
			left = transform(session[:originIdx+1][::-1])
			right = transform(session[originIdx:])
			
			session[originIdx]['x'] = session[originIdx]['east']
			session[originIdx]['y'] = session[originIdx]['north']
			
			#reassemble original session with fixes
			session = left[::-1] + [session[originIdx]] + right
		
			for idx in range(len(session)):
				#get rid of absolute type parameters
				if session[idx]['type'] == 'absolute':
					del session[idx]['north']
					del session[idx]['east']
					del session[idx]['zone']
					del session[idx]['accuracy']
					
				#get rid of parameters
				#that are now unnecessary
				del session[idx]['type']
				del session[idx]['time']
				
		#put session back in place
		data[key] = session
		
		#store origin index
		origins[key] = originIdx
	
	#output fixed
	return data, origins

#plot GPS-improved data and raw data together
#for transformation comparison purposes
#origins stores origin indices as zero points
#bound here serves the same purpose as below
#show determines whether we actually plot stuff
def plotCompare(oldData, newData, origins, bound, show):
	#create copy of data
	oldData = deep(oldData)
	newData = deep(newData)
	origins = deep(origins)
	
	#GPS data by old and new coords
	gpsData, gpsDataNew = {}, {}
	
	#rescale old data to origin
	for key, session in oldData.items():
		x = oldData[key][origins[key]]['x']
		y = oldData[key][origins[key]]['y']
				
		#dictionary with GPS XY points
		gpsData[key] = {'x' : [], 'y' : []}
		
		for idx in range(len(session)):
			oldData[key][idx]['x'] -= x
			oldData[key][idx]['y'] -= y
			
			if oldData[key][idx]['type'] == 'absolute':
				gpsData[key]['x'].append(oldData[key][idx]['x'])
				gpsData[key]['y'].append(oldData[key][idx]['y'])	
				
		#pre-compute arrays of X and Y to avoid wasteful looping
		oldData[key][0]['x'] = [i['x'] for i in oldData[key]]
		oldData[key][0]['y'] = [i['y'] for i in oldData[key]]

	#rescale new data to origin
	for key, session in newData.items():
		x = newData[key][origins[key]]['x']
		y = newData[key][origins[key]]['y']
				
		#dictionary with GPS XY points
		gpsDataNew[key] = {'x' : [], 'y' : []}
		
		for idx in range(len(session)):
			newData[key][idx]['x'] -= x
			newData[key][idx]['y'] -= y
			
			if oldData[key][idx]['type'] == 'absolute':
				gpsDataNew[key]['x'].append(newData[key][idx]['x'])
				gpsDataNew[key]['y'].append(newData[key][idx]['y'])	
			
		#pre-compute arrays of X and Y to avoid wasteful looping
		newData[key][0]['x'] = [i['x'] for i in newData[key]]
		newData[key][0]['y'] = [i['y'] for i in newData[key]]
		
	#draw plots for every session
	for key, session in oldData.items():
		#instantiate two different subplots that share the XY axes
		f, (new, old) = plot.subplots(2, sharex = True, sharey = True)
		
		old.plot(oldData[key][0]['x'], oldData[key][0]['y'], 'bo')
		new.plot(newData[key][0]['x'], newData[key][0]['y'], 'go')
		old.plot(gpsData[key]['x'], gpsData[key]['y'], 'yo')
		new.plot(gpsDataNew[key]['x'], gpsDataNew[key]['y'], 'ro')
		old.plot(gpsDataNew[key]['x'], gpsDataNew[key]['y'], 'ro')
		
		#these are temporary arrays used for axis scaling
		x = oldData[key][0]['x'] + newData[key][0]['x']
		y = oldData[key][0]['y'] + newData[key][0]['y']
		
		#find max point values for X and Y
		rawMaxX = max([i for i in x])
		rawMaxY = max([i for i in y])
		
		#find max point values for X and Y
		rawMinX = min([i for i in x])
		rawMinY = min([i for i in y])
		
		#find scaled X and Y to define plotting ranges
		maxX = bound * math.ceil(rawMaxX / bound)
		maxY = bound * math.ceil(rawMaxY / bound)
		
		if maxX == 0:
			maxX += bound

		if maxY == 0:
			maxY += bound
		
		maxX += bound/2
		maxY += bound/2
		
		#scale minima based on maxima margin
		minX = rawMinX - (maxX - rawMaxX)
		minY = rawMinY - (maxY - rawMaxY)
		
		#set up gridlines with color and appropriate width
		old.grid(color = '#9932cc', linestyle = ':', linewidth = 1)
		new.grid(color = '#9932cc', linestyle = ':', linewidth = 1)
		
		#define axes for both old and new
		old.axis([minX, maxX, minY, maxY])
		new.axis([minX, maxX, minY, maxY])
	
	if show: plot.show()
	plot.close() #done
	
#superimpose points into one big array based on a label
#split parameter defines how many intermediary points
def superimpose(data, label, split):
	#create copy of data
	data = deep(data)

	#list of compiled steps
	compiledData = []
	
	#dic of compiled sessions
	compiledSessions = {}
	
	for key, session in data.items():
		refX = 0 #reference x-coordinate
		refY = 0 #reference y-coordinate
		
		for idx in range(len(session)):
			if 'label' in session[idx]:
				if session[idx]['label'] == label:
					refX = session[idx]['x']
					refY = session[idx]['y']
					break #for efficiency sake
					
		for idx in range(len(session)):
			session[idx]['x'] -= refX
			session[idx]['y'] -= refY
		
		#append falls to split with first
		newSplitSession = [session[0]]
		
		#add intermediary extrapolations
		for idx in range(1, len(session)):
			dx = (session[idx]['x'] - session[idx-1]['x'])
			dy = (session[idx]['y'] - session[idx-1]['y'])
			
			#define slope
			slope = dy/dx
			
			#define split length using dx
			splitLength = dx / (split + 1)
			
			#calculate the extrapolations
			for i in range(1, split + 1):
				newSplitSession.append({
					'x' : session[idx-1]['x'] + i * splitLength,
					'y' : session[idx-1]['y'] + slope * i * splitLength,
					'stride' : session[idx]['stride'], #use old stride
				})
				
			#finally add actual step to session
			newSplitSession.append(session[idx])
			
		#add steps to compiled list of steps
		for idx in range(len(newSplitSession)):
			compiledData.append(newSplitSession[idx])
			
		#add session to compiled session list
		compiledSessions[key] = newSplitSession
			
	#our final lists of steps and sessions
	return compiledData, compiledSessions
		
#plot superimposed points and their labels
#plots only unique labels throughout
#bound is what axis bounds are rounded to
def plotSuper(data, bound, show, save):
	#create copy of data
	data = deep(data)
	
	figure = plot.figure() #get the window canvas
	figure.canvas.set_window_title('Superimposed Paths')
	
	#keep track of seen points
	#we don't want duped labels
	seenLabels, x, y = [], [], []
	
	for step in data:
		x.append(step['x'])
		y.append(step['y'])
		
		#plot point and corresponding label
		plot.plot(x[-1], y[-1], 'go')
		
		if 'label' in step:
			if step['label'] not in seenLabels:
				#store label temporarily
				label = step['label']
				
				#set style of annotation box. this should be nice but unobtrusive
				box = dict(boxstyle = 'round, pad = 0.4', fc = 'cyan', alpha = 1.0)
				plot.annotate(label, xy = (x[-1], y[-1]), bbox = box) #add label to plot
				
				#append label to seen labels
				seenLabels.append(label)

	#find max point values for X and Y
	rawMaxX = max([i for i in x])
	rawMaxY = max([i for i in y])
	
	#find max point values for X and Y
	rawMinX = min([i for i in x])
	rawMinY = min([i for i in y])
	
	#find scaled X and Y to define plotting ranges
	maxX = bound * math.ceil(rawMaxX / bound)
	maxY = bound * math.ceil(rawMaxY / bound)
	
	if maxX == 0:
		maxX += bound

	if maxY == 0:
		maxY += bound
	
	maxX += bound/2
	maxY += bound/2
	
	#scale minima based on maxima margin
	minX = rawMinX - (maxX - rawMaxX)
	minY = rawMinY - (maxY - rawMaxY)
	
	#set up gridlines with color and appropriate width
	plot.grid(color = '#9932cc', linestyle = ':', linewidth = 1)
	plot.axis([minX, maxX, minY, maxY]) #define axis
	
	if show: plot.show() #show the stuff out to the screen
	if save: plot.savefig(getTestSave() + '/' + 'super.png')
	
	#close plot
	plot.close()
			
#helper functions of x
#used in heatmapping

def log(x): return math.log(x)
def linear(x): return x
def square(x): return x**2
def cube(x): return x**3

#TODO: figure out personal comfort space
#WORKAROUND: right now we use alpha values

#TODO: eventually we need to figure out
#how we will threshold the heatmap weights

#generate heat map based on array of points
#also return array of labels and locations

#var pixel defines smallest pixel width to consider
#var alpha times stride length is personal comfort space
#var function defines pixel weight increase per occurrence
#var frame defines number of pixels to frame heatmap with
def makeHeatMap(data, steps, pixel, alpha, function, frame):
	#floor pixel to one meter
	#to avoid bugs that occur
	if pixel > 1: pixel = 1

	#create copy of data
	data = deep(data)
	steps = deep(steps)
	
	#make scaling coefficient
	coeff = round(1/pixel)
	
	minX, maxX = 0, 0
	minY, maxY = 0, 0
	
	#find min and max vals of X and Y
	#accounting for radius expansion
	for element in steps:
		#calculate the personal comfort radius
		#see TODO note above about this formula
		radius = element['stride'] * alpha * coeff
		
		if element['x'] - radius < minX: minX = element['x'] - radius
		if element['x'] + radius > maxX: maxX = element['x'] + radius
		
		if element['y'] - radius < minY: minY = element['y'] - radius
		if element['y'] + radius > maxY: maxY = element['y'] + radius
	
	#calculate XY ranges
	xRange = maxX - minX
	yRange = maxY - minY
	
	#rescale everything positive
	for key, session in data.items():
		for idx in range(len(session)):
			data[key][idx]['x'] -= minX
			data[key][idx]['y'] -= minY
	
	#then scale X and Y ranges appropriately
	xRange, yRange = xRange * coeff, yRange * coeff
	xRange, yRange = math.ceil(xRange), math.ceil(yRange)
	
	#heatmap arrays
	heatmap = []
	weighted = []
	labels = []
	
	#initialize array with zeroes
	for i in range(xRange):
		heatmap.append([])
		weighted.append([])
		labels.append([])
		for j in range(yRange):
			heatmap[-1].append(0)
			weighted[-1].append(0)
			labels[-1].append(None)
	
	for key, session in data.items():
		#track seen pixels
		seenPixels = []
		
		for step in session:
			x = step['x'] * coeff
			y = step['y'] * coeff
			
			#preserve labels
			mapX = round(x)
			mapY = round(y)
			
			#calculate personal comfort radius
			#see TODO note above about this line
			radius = step['stride'] * alpha * coeff
			
			#make bounding box to find pixels
			#used in for loop, see below
			boundMinX = math.floor(x - radius)
			boundMaxX = math.ceil(x + radius)
			boundMinY = math.floor(y - radius)
			boundMaxY = math.ceil(y + radius)
			
			#only add label to array if label not set already
			if 'label' in step and labels[mapX][mapY] is None:
				labels[mapX][mapY] = step['label']
				
			for i in range(boundMinX, boundMaxX + 1):
				for j in range(boundMinY, boundMaxY + 1):
					if distance((x, y), (i, j)) <= radius:
						if i in range(xRange) and j in range(yRange):
							#weight only if not weighted
							if (i, j) not in seenPixels:
								heatmap[i][j] += 1
								seenPixels.append((i, j))
							
							#calculate weighted function of heatmap
							weighted[i][j] = function(heatmap[i][j])
	
	#rotate array CCW so it is oriented north
	weighted = mat(weighted).T[::-1].tolist()
	heatmap = mat(heatmap).T[::-1].tolist()
	labels = mat(labels).T[::-1].tolist()
	
	#add a frame of zero-weighted pixels on the top
	vertFrame = [[0] * len(weighted[0])] * frame
	weighted = mat(vertFrame + weighted + vertFrame).T.tolist()
	
	#do the same thing for our unweighted matrix
	vertFrame = [[0] * len(heatmap[0])] * frame
	heatmap = mat(vertFrame + heatmap + vertFrame).T.tolist()
	
	#do the same thing for our matrix of labels
	vertFrame = [[None] * len(labels[0])] * frame
	
	labels = mat(vertFrame + labels + vertFrame).T.tolist()
	#add a frame of zero-weighted pixels on the side
	sideFrame = [[0] * len(weighted[0])] * frame
	weighted = mat(sideFrame + weighted + sideFrame).T.tolist()
	
	#do the same thing for our unweighted matrix
	sideFrame = [[0] * len(heatmap[0])] * frame
	heatmap = mat(sideFrame + heatmap + sideFrame).T.tolist()
	
	#do the same thing for our matrix of labels
	sideFrame = [[None] * len(labels[0])] * frame
	labels = mat(sideFrame + labels + sideFrame).T.tolist()
	
	#output weights with unweighted
	return weighted, heatmap, labels
		
#plot heat map on screen
#color defines color scheme
#axisOff sets axes or not
#show sets show plot or not
#save sets save file or not
def plotHeatMap(heat, color, axisOff, show, save):
	#create copy of data
	heat = deep(heat)
	
	figure = plot.figure() #get window canvas
	figure.canvas.set_window_title('Heat Map') #set title
	
	#optional parameter
	#to remove padding
	if axisOff:
		ax = plot.Axes(figure, [0., 0., 1., 1.])
		ax.set_axis_off() #remove other axes
		figure.add_axes(ax) #add new, fake axis

	#interpolation nearest makes the heat map discrete without gradient
	if axisOff: plot.imshow(mat(heat), cmap = color, interpolation = 'nearest', aspect = 'normal')
	else: plot.imshow(mat(heat), cmap = color, interpolation = 'nearest') #normal aspect setting
	
	if show: plot.show() #show the stuff out to the screen
	if save: plot.savefig(getTestSave() + '/' + color + '.png')
	
	#close plot
	plot.close()

#calculate array value
#at given percentile quantity
def percentile(list, percent):
	element = int(round(percent * len(list) + 0.5))
	return list[element - 1]
	
#thresholding function based on statistics
#Tukey's Rule where outliers are Q1 - cf * IQR
#variable uw is heatmap without function weighting
def boxThresholdMap(uw, cf):
	#create data copy
	uw = deep(uw)

	#flatten heat map array using list comprehension
	weights = [item for list in uw for item in list]
	weights = sorted([i for i in weights if i != 0])
	
	#calculate appropriate statistics
	firstQuart = percentile(weights, .25)
	thirdQuart = percentile(weights, .75)
	interRange = thirdQuart - firstQuart
	outlier = firstQuart - cf * interRange
	
	for i in range(len(uw)):
		for j in range(len(uw[i])):
			if uw[i][j] == 0: uw[i][j] == 0
			elif uw[i][j] < outlier: uw[i][j] = 0
			else: uw[i][j] = 1 #turn pixel on
			
	#output binary
	#based heatmap
	return uw
	
#thresholding function by the number of tracks
#more parametric and less automatic, but this is
#probably more robust than the box plot stats method
def simpleThresholdMap(uw, min, max, coeff, tracks):
	#create data copy
	uw = deep(uw)
	
	#calculate threshold number of tracks
	#based on original number of tracks input
	sig = tracks * coeff #significant value

	for i in range(len(uw)):
		for j in range(len(uw[i])):
			if uw[i][j] == 0: uw[i][j] == 0
			elif uw[i][j] < min: uw[i][j] = 0
			elif uw[i][j] > max: uw[i][j] = 1
			elif uw[i][j] > sig: uw[i][j] = 1
			elif uw[i][j] < sig: uw[i][j] = 0
			
	#output binary
	#based heatmap
	return uw