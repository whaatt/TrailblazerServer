#import our module of stuff
from trailblazer import *

#set parameters for saving our test results in an organized folder
if len(sys.argv) > 1: setTestName(sys.argv[1]) #make sure arg exists
setTestRoot('C:/Users/Sanjay/Documents/Programming/Trailblazer/tests')
setTestSave() #using the test root and test name, get save location

#download data and omit any trials deemed problematic from figures
savedData, cnt = downloadData([6, 23]) #remove trials with faults
raw = cleanData(savedData, True) #clean up any unneeded parameters

#preprocess and superimpose sessions
nice, origins = preprocess(raw, False) #GPS
steps, package = superimpose(nice, 'None', 1)

#generate the heat maps with steps, pixel, alpha, function, frame
map, uw, labels = makeHeatMap(package, steps, .4, 0.5, linear, 30)

#generate the product binary heat map for saving
product = simpleThresholdMap(uw, 0, 5, 0, cnt)

#compare preprocessed data to original data
plotCompare(raw, nice, origins, 5, False)

#plot label-superimposed steps
plotSuper(steps, 5, False, True)

#plot heat map with color
#then plot grayscale version
plotHeatMap(map, 'hot', False, False, True, False, 5)
plotHeatMap(product, 'gray', True, False, True, False, 5)

#set Python 2.7 location
setPythonTwo('python27')

#parameters are mapmaker location, save directory, file name, visibility, save, box width, smoothing thresh, extns
cmd.call([getPythonTwo(), getMyDirectory() + '/mapmaker.py', getTestSave(), 'gray.png', 'n', 'y', '15', '30', 'n'])