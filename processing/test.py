#import our module of stuff
from trailblazer import *

#set parameters for saving our test results in an organized folder
if len(sys.argv) > 1: setTestName(sys.argv[1]) #make sure arg exists
setTestRoot('C:/Users/Sanjay/Documents/Programming/Trailblazer/tests')
setTestSave() #using the test root and test name, get save location

#download data and clean it up
savedData, cnt = downloadData()
raw = cleanData(savedData)

#preprocess and superimpose sessions
nice, origins = preprocess(raw, False) #GPS
steps, package = superimpose(nice, 'walk', 1)

#generate the heat maps with steps, pixel, alpha, function, frame
map, uw, labels = makeHeatMap(package, steps, .1, 0.5, square, 30)

#generate the product binary heat map for saving
product = simpleThresholdMap(uw, 0, 5, 0.1, cnt)

#compare preprocessed data to original data
plotCompare(raw, nice, origins, 5, True)

#plot label-superimposed steps
plotSuper(steps, 5, False, True)

#plot heat map with color
#then plot grayscale version
plotHeatMap(map, 'hot', False, False, True)
plotHeatMap(product, 'gray', True, False, True)

#set Python 2.7 location
setPythonTwo('python27')

#parameters are mapmaker location, save directory, file name, visibility, save, box width, smoothing thresh, exts
cmd.call([getPythonTwo(), getMyDirectory() + '/mapmaker.py', getTestSave(), 'gray.png', 'n', 'y', '50', '2', 'n'])