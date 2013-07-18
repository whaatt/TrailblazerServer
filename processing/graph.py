from urllib.request import urlopen
from urllib.parse import urlencode
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg
import json, random, math

file = open('query.sql', 'r')
query = file.read()
post = urlencode({'query' : query}).encode('ascii')

url = 'http://www.skalon.com/trailblazer/retrieve.php'
response = urlopen(url, post)
data = json.loads(str(response.read().decode('utf-8')))

lastX, lastY = 0, 0
maxX, maxY = 0, 0
sessions = {}

for event in data:
	if event['session'] not in sessions:
		sessions[event['session']] = [event]
	else:
		sessions[event['session']].append(event)

use = [i for i in 'bymgc']
colors = [i for i in 'bymgc']

xParam = 'absX'
yParam = 'absY'

x, y = [], []
labels = []

for session in sessions.values():
	x.append(0);
	y.append(0);
	
	for step in session:
		if xParam in step:
			x.append(step[xParam])
			lastX = step[xParam]
			if abs(lastX) > maxX:
				maxX = abs(lastX)
		if yParam in step:
			y.append(step[yParam])
			lastY = step[yParam]
			if abs(lastY) > maxY:
				maxY = abs(lastY)
		if 'type' in step and step['type'] == 'label':
			labels.append([step['content'], (lastX, lastY)])

	if len(use) > 0:
		color = use[0]
		del use[0]

	else:
		color = random.choice(colors)
			
	plt.plot(x, y, color)
	x, y = [], []

for label in labels:
	plt.annotate(label[0], xy = label[1])

maxX = 10 * math.ceil(maxX / 10)
maxY = 10 * math.ceil(maxY / 10)
	
if maxX == 0:
	maxX += 10

if maxY == 0:
	maxY += 10
	
plt.grid(color = 'r', linestyle = ':', linewidth = 1)
plt.axis([-maxX, maxX, -maxY, maxY])

plt.show()