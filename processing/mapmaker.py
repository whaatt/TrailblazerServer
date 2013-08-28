#OpenCV Lib
import cv2

#access args
import sys

#get numpy for arrays
import numpy as np

#import deep array copy for functions
from copy import deepcopy as deep

#get distance between
#two XY coordinates
def distance(first, second):
	xsq = (second[0] - first[0])**2
	ysq = (second[1] - first[1])**2
	return (xsq + ysq)**(1/2)

#set whether generated plots are shown
if sys.argv[3] == 'n': visible = False
else: visible = True

#set whether generated plots are saved
if sys.argv[4] == 'n': save = False
else: save = True
	
#set whether we draw plot extensions
if sys.argv[7] == 'n': exts = False
else: exts = True
	
#set TIPS parameters and smoothing
boxWidth = int(sys.argv[5])
smoothThresh = int(sys.argv[6])

#get file save locaions
saveDir = sys.argv[1]
saveFile = sys.argv[2]

#load images and create drawing canvases
image = cv2.imread(saveDir + '/' + saveFile)
drawing = np.zeros(image.shape, np.uint8)
drawings = np.zeros(image.shape, np.uint8)
drawingo = np.zeros(image.shape, np.uint8)

#get width and height of image
imageLength = image.shape[1]
imageWidth = image.shape[0]

#calculate size of iteration
chunkSize = 2 * boxWidth + 2

paths = []
corns = []

#iterate through our entire image
#working by steps of value chunkSize
for y in range(0, imageWidth, boxWidth + 1):
	for x in range(0, imageLength, boxWidth + 1):
		#boolean values for each of our quadrants
		I, II, III, IV = False, False, False, False
		bI, bII, bIII, bIV = False, False, False, False
		gU, gL, gR, gD = True, True, True, True
		
		#grid halfway point
		halfway = boxWidth
		
		#get TIPS edge type
		def getEdges(type):
			if type == 'XXs' : return []
			if type == 'LUi' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y - 1)]
			if type == 'RUi' : return [(x + chunkSize - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y - 1)]
			if type == 'LDi' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'RDi' : return [(x + chunkSize - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'LUe' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y - 1)]
			if type == 'RUe' : return [(x + chunkSize - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y - 1)]
			if type == 'LDe' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'RDe' : return [(x + chunkSize - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'LRs' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + chunkSize - 1, y + halfway)]
			if type == 'UDs' : return [(x + halfway, y - 1), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'LUs' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y - 1)]
			if type == 'RUs' : return [(x + chunkSize - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y - 1)]
			if type == 'LDs' : return [(x - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'RDs' : return [(x + chunkSize - 1, y + halfway), (x + halfway, y + halfway), (x + halfway, y + chunkSize - 1)]
			if type == 'MUt' : return [(x + halfway, y + halfway), (x + halfway, y + halfway - 1), (x + halfway, y - 1)]
			if type == 'MLt' : return [(x - 1, y + halfway), (x, y + halfway), (x + halfway, y + halfway)]
			if type == 'MRt' : return [(x + chunkSize - 1, y + halfway), (x + chunkSize - 2, y + halfway), (x + halfway, y + halfway)]
			if type == 'MDt' : return [(x + halfway, y + halfway), (x + halfway, y + halfway + 1), (x + halfway, y + chunkSize - 1)]
		
		#see if quadrant II is colored
		for i in range(y, y + boxWidth):
			for j in range(x, x + boxWidth):
				if i > imageWidth - 1 or j > imageLength - 1:
					continue
				if [255, 255, 255] == image[i][j].tolist():
					II, bII = True, True
					break
			if bII: break
		
		#see if quadrant I is colored		
		for i in range(y, y + boxWidth):
			for j in range(x + boxWidth + 1, x + chunkSize - 1):
				if i > imageWidth - 1 or j > imageLength - 1:
					continue
				if [255, 255, 255] == image[i][j].tolist():
					I, bI = True, True
					break
			if bI: break
			
		#see if quadrant III is colored
		for i in range(y + boxWidth + 1, y + chunkSize - 1):
			for j in range(x, x + boxWidth):
				if i > imageWidth - 1 or j > imageLength - 1:
					continue
				if [255, 255, 255] == image[i][j].tolist():
					III, bIII = True, True
					break
			if bIII: break
		
		#see if quadrant IV is colored		
		for i in range(y + boxWidth + 1, y + chunkSize - 1):
			for j in range(x + boxWidth + 1, x + chunkSize - 1):
				if i > imageWidth - 1 or j > imageLength - 1:
					continue
				if [255, 255, 255] == image[i][j].tolist():
					IV, bIV = True, True
					break
			if bIV: break
		
		#trigger for Type Four blocks
		#draw thin-obstacle type lines
		if I and II and III and IV:
			#decide if to set upper gridline
			for i in range(y - 1, y + boxWidth):
				if [255, 255, 255] == image[i][x + boxWidth - 1].tolist():
					gU = False
					
			#decide if to set lower gridline		
			for i in range(y + boxWidth - 1, y + chunkSize):
				if [255, 255, 255] == image[i][x + boxWidth - 1].tolist():
					gD = False
					
			#decide if to set left gridline
			for i in range(x - 1, x + boxWidth):
				if [255, 255, 255] == image[y + boxWidth - 1][i].tolist():
					gL = False
			
			#decide if to set right gridline
			for i in range(x + boxWidth - 1, x + chunkSize):
				if [255, 255, 255] == image[y + boxWidth - 1][i].tolist():
					gR = False
					
		#combos contain all of the combinatorial
		#types as specified in TIPS presentation
		
		combos = [
			[True, not (I or II or III or IV), ['XXs']], #class 0
			[I, not (II or III or IV), ['RUe']], #class 1
			[II, not (I or III or IV), ['LUe']],
			[III, not (I or II or IV), ['LDe']],
			[IV, not (I or II or III), ['RDe']],
			[I and II, not (III or IV), ['LRs']], #class 2A
			[I and IV, not (II or III), ['UDs']],
			[II and III, not (I or IV), ['UDs']],
			[III and IV, not (I or II), ['LRs']],
			[I and III, not (II or IV), ['LDe', 'RUe']], #class 2B
			[II and IV, not (I or III), ['LUe', 'RDe']],
			[II and III and IV, not I, ['RUi']], #class 3
			[I and III and IV, not II, ['LUi']],
			[I and II and IV, not III, ['LDi']],
			[I and II and III, not IV, ['RDi']],
			[I and II and III and IV, not (gU or gD or gL or gR), ['XXs']], #class 4
			[I and II and III and IV, gU and not (gD or gL or gR), ['MUt']],
			[I and II and III and IV, gD and not (gU or gL or gR), ['MDt']],
			[I and II and III and IV, gL and not (gU or gD or gR), ['MLt']],
			[I and II and III and IV, gR and not (gU or gD or gL), ['MRt']],
			[I and II and III and IV, (gU and gL) and not (gD or gR), ['LUs']],
			[I and II and III and IV, (gU and gR) and not (gD or gL), ['RUs']],
			[I and II and III and IV, (gU and gD) and not (gL or gR), ['UDs']],
			[I and II and III and IV, (gR and gL) and not (gU or gD), ['LRs']],
			[I and II and III and IV, (gR and gD) and not (gU or gL), ['RDs']],
			[I and II and III and IV, (gL and gD) and not (gU or gR), ['LDs']],
			[I and II and III and IV, (gU and gR and gL) and not gD, ['LUs', 'MRt']],
			[I and II and III and IV, (gU and gR and gD) and not gL, ['UDs', 'MRt']],
			[I and II and III and IV, (gU and gL and gD) and not gR, ['UDs', 'MLt']],
			[I and II and III and IV, (gD and gR and gL) and not gU, ['LDs', 'MRt']],
			[I and II and III and IV, gU and gR and gL and gD, ['LDs', 'RUs']]
		]
		
		#generate, and find the array value in combos satisfying conditions
		types = [i[2] for i in combos if (i[0], i[1]) == (True, True)][0]
		
		#placeholder null type
		if types == ['XXs']:
			pass
		
		else:
			#put corresponding edges in a list
			edges = [getEdges(i) for i in types]
			
			#iterate and classify points
			for i in range(len(edges)):
				sub = types[i][-1]
				
				#identify points as corner types or not
				if sub == 'e': corr = ['s', 'e', 's']
				elif sub == 's': corr = ['s', 's', 's']
				elif sub == 'i': corr = ['s', 'i', 's']
				elif sub == 't': corr = ['t', 't', 't']
				
				#if we are drawing a filled type edge with no exts
				if I and II and III and IV and not exts: continue
				
				paths.append(edges[i])
				corns.append(corr)

#copy paths and corners
orgPaths = deep(paths)
orgCorns = deep(corns)	
	
idx = 0	#fake for loop
while idx < len(orgPaths):

	found = True #init
	while found == True:
		found = False
		lastlen = 0
		
		#try to stitch the point groups together
		for i in range(len(orgPaths)-1, idx, -1):
			#needs the algo extension
			if orgCorns[i][0] == 't':
			
				if orgPaths[idx][0] == orgPaths[i][0]:
					orgPaths[idx] = orgPaths[i][1:][::-1] + orgPaths[idx]
					orgCorns[idx] = orgCorns[i][1:][::-1] + orgCorns[idx]
					found = True
					del orgPaths[i], orgCorns[i]
					
				elif orgPaths[idx][-1] == orgPaths[i][0]:
					orgPaths[idx] = orgPaths[idx] + orgPaths[i][1:]
					orgCorns[idx] = orgCorns[idx] + orgCorns[i][1:]
					found = True
					del orgPaths[i], orgCorns[i]
					
				elif orgPaths[idx][0] == orgPaths[i][2]:
					orgPaths[idx] = orgPaths[i][:2] + orgPaths[idx]
					orgCorns[idx] = orgCorns[i][:2] + orgCorns[idx]
					found = True
					del orgPaths[i], orgCorns[i]
					
				elif orgPaths[idx][-1] == orgPaths[i][2]:
					orgPaths[idx] = orgPaths[idx] + orgPaths[i][:2][::-1]
					orgCorns[idx] = orgCorns[idx] + orgCorns[i][:2][::-1]
					found = True
					del orgPaths[i], orgCorns[i]
		
			elif orgPaths[idx][:2] == orgPaths[i][:2]:
				orgPaths[idx] = [orgPaths[i][2]] + orgPaths[idx]
				orgCorns[idx] = [orgCorns[i][2]] + orgCorns[idx]
				orgCorns[idx][1] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][:2] == orgPaths[i][-2:]:
				orgPaths[idx] = [orgPaths[i][0]] + orgPaths[idx]
				orgCorns[idx] = [orgCorns[i][0]] + orgCorns[idx]
				orgCorns[idx][1] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][-2:] == orgPaths[i][0:2]:
				orgPaths[idx] = orgPaths[idx] + [orgPaths[i][2]]
				orgCorns[idx] = orgCorns[idx] + [orgCorns[i][2]]
				orgCorns[idx][-2] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][-2:] == orgPaths[i][-2:]:
				orgPaths[idx] = orgPaths[idx] + [orgPaths[i][0]]
				orgCorns[idx] = orgCorns[idx] + [orgCorns[i][0]]
				orgCorns[idx][-2] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][:2] == orgPaths[i][::-1][:2]:
				orgPaths[idx] = [orgPaths[i][0]] + orgPaths[idx]
				orgCorns[idx] = [orgCorns[i][0]] + orgCorns[idx]
				orgCorns[idx][1] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][:2] == orgPaths[i][::-1][-2:]:
				orgPaths[idx] = [orgPaths[i][2]] + orgPaths[idx]
				orgCorns[idx] = [orgCorns[i][2]] + orgCorns[idx]
				orgCorns[idx][1] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][-2:] == orgPaths[i][::-1][0:2]:
				orgPaths[idx] = orgPaths[idx] + [orgPaths[i][0]]
				orgCorns[idx] = orgCorns[idx] + [orgCorns[i][0]]
				orgCorns[idx][-2] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
			elif orgPaths[idx][-2:] == orgPaths[i][::-1][-2:]:
				orgPaths[idx] = orgPaths[idx] + [orgPaths[i][2]]
				orgCorns[idx] = orgCorns[idx] + [orgCorns[i][2]]
				orgCorns[idx][-2] = orgCorns[i][1]
				found = True
				del orgPaths[i], orgCorns[i]
				
	#increase
	idx += 1

#store smooth paths
smoothPaths = []

#iterate through our contours
for i in range(len(orgCorns)):
	smoothPaths.append([])
	
	fi = None
	si = None
	j = 0
	ec = 0
	
	#fake for loop through
	while j < len(orgCorns[i]):
	
		#does it point internally
		#toward accessible space
		if orgCorns[i][j] == 'i':
			if fi is None:
				smoothPaths[i] += deep(orgPaths[i][:j+1])
				fi = j #set first appearance location
				
			elif ec != 1:
				smoothPaths[i] += deep(orgPaths[i][fi:j+1])
				fi = j #set first appearance location
				
			elif si is None:
				si = j #set first appearance location
				
				#see if the distance between two internals is less than thresh
				if distance(orgPaths[i][fi], orgPaths[i][si]) < smoothThresh:
					smoothPaths[i] += deep([orgPaths[i][si]])
					j = si #set loop iteration counter forward
				
				fi = si
				si = None
			
			#reset
			ec = 0
			
		#does it point externally
		#toward inaccessible space
		elif orgCorns[i][j] == 'e':
			#count external corners
			ec = ec + 1 #increment
			
		#increment
		j = j + 1
	
	if fi is None:
		#no internals, so just keep all
		smoothPaths[i] = deep(orgPaths[i])
	
	else:
		#stitch on stuff after an unpaired corner
		smoothPaths[i] += deep(orgPaths[i][fi+1:])

#draw smoothing lines
for path in smoothPaths:
	for i in range(len(path)-1):
		x1, y1 = path[i][0], path[i][1]
		x2, y2 = path[i+1][0], path[i+1][1]
		
		cv2.line(image,(x1, y1), (x2, y2), (255,0,255), 1)
		cv2.line(drawing,(x1, y1), (x2, y2), (255,0,255), 1)
		cv2.line(drawings,(x1, y1), (x2, y2), (255,0,255), 1)
		
#draw the original TIPS lines
for path in range(len(orgPaths)):
	for i in range(len(orgPaths[path])-1):
		x1, y1 = orgPaths[path][i][0], orgPaths[path][i][1]
		x2, y2 = orgPaths[path][i+1][0], orgPaths[path][i+1][1]
		
		cv2.line(image,(x1, y1), (x2, y2), (255,0,0), 1)
		cv2.line(drawing,(x1, y1), (x2, y2), (255,0,0), 1)
		cv2.line(drawingo,(x1, y1), (x2, y2), (255,0,0), 1)

#show images or not
if visible == True:
	cv2.imshow('Raw Image With Smoothing Cover', image)
	cv2.imshow('Original Cover', drawingo)
	cv2.imshow('Original Cover With Smoothing', drawing)
	cv2.imshow('Smoothed Cover', drawings)

#save it or not
if save == True:
	cv2.imwrite(saveDir + '/' + 'rawCover.png', image)
	cv2.imwrite(saveDir + '/' + 'origCover.png', drawingo)
	cv2.imwrite(saveDir + '/' + 'origSmooth.png', drawing)
	cv2.imwrite(saveDir + '/' + 'smoothCover.png', drawings)

#boilerplate
cv2.waitKey()
cv2.destroyAllWindows()