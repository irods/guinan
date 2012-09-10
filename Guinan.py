import logging
import sys
import os
import inspect
import ConfigParser
import IrodsMetricAbstract as met

def loadMetrics(directory):

	modList = list()
	for root, dirs, files in os.walk(directory):
		modList = [fname for fname in files if fname.endswith('.py') and \
		           not fname.startswith('__')]
		classList = list()
		if modList:
			for m in modList:
				modName = os.path.splitext(m)[0]
				try:
					module = __import__(modName)
				except (ImportError, NotImplementedError):
					continue
				for cls in dir(module):
					cls = getattr(module, cls)
					if (inspect.isclass(cls) and \
				    	inspect.getmodule(cls) == module and \
				    	issubclass(cls, met.IrodsMetric)):
						classList.append(cls)
	return classList

# write current Guinan run number to file
def setRunNumber(num):
	runFile = '.runs'
        try:
                f = open(runFile, 'w')
        except IOError as e:
                logging.error('Cannot write to runs file - cannot schedule metrics to run')
		return
	
	f.write(str(num))
	f.close()

# get current Guinan run number - returns zero if it can't find one
def getRunNumber():
	num = 0

	runFile = '.runs'
        try:
                f = open(runFile, 'r')
        except IOError as e:
                logging.warning('Cannot find runs file - creating a new one')
                f = open(runFile, 'w')
		f.write('0')
		f.close()
		return num

	strNum = f.read()
	num = int(strNum)
	f.close()
	return num

# this will save the counter for how many times Guinan
# has been run in the last 365 days. The counter will be
# reset after 365 days
def incrementRunNumber():
  	# first get run number
	num = getRunNumber()
	num += 1
	if (num > cfg.get('guinan', 'run_time_rollover')) :
		num = 0
	# now save incremented one
	setRunNumber(num)


# setup logging - want to change this later to append to date stamped
# log files and clean up logs older that N days
# 
guinanRoot = None
configFile = './GuinanConfig.ini'
logFile = None
logLevel = None

# first collect info from Guinan config file to setup logging
cfg = ConfigParser.ConfigParser()

# make sure the config file is there
if os.path.exists(configFile):
	cfg.read(configFile)
else:
	print "Cannot access GuinanConfi.ini for logging information. " + \
	      "Exiting - status=1"
	sys.exit(1)

# make sure the logging config params are there
try:
	logFile = cfg.get('logs', 'filename')
	logLevel = cfg.get('logs', 'log_level')
except:
	print "Cannot find log_level in GuinanConfi.ini for logging information. " + \
	      "Exiting - status=1"
	sys.exit(1)

# finally configure the logging
try:
	logging.basicConfig(filename=logFile, level=logLevel, \
		            format='%(asctime)s %(message)s')
except:
	print "Logging is not properly configured in GuinanConfi.ini. " + \
              "Exiting - status=1"
        sys.exit(1)

# first log!
logging.info('Started Guinan')

# get the guinan root path
try: 
	guinanRoot = cfg.get('guinan', 'root_path')
except:
	logging.warn('Cannot find Guinan root_path in %s setting to: ./' % configFile)
	guinanRoot = './'
	
# now get metrics modules path
metricsFolderName = None
try: 
	metricsFolderName = cfg.get('guinan', 'metrics_path')
except:
	logging.warn('Cannot find Guinan metrics_path in %s, setting to: %s/metrics' \
		      % (configFile, guinanRoot))
	metricsFolderName = guinanRoot + '/metrics'

# check to make sure this path exists
if (not os.path.exists(metricsFolderName)):
	logging.critical('Cannot find Guinan metrics modules path: %s, Exiting - status=1' \
			 % metricsFolderName)
	sys.exit(1)
	
# set up python search path for metrics modules
metricsFolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split( \
			     inspect.getfile(inspect.currentframe()))[0], \
			     metricsFolderName)))
if metricsFolder not in sys.path:
	sys.path.insert(1, metricsFolder)

runNumber = getRunNumber()
# load metrics modules
metrics = loadMetrics(metricsFolderName)
for metric in metrics:
	m = metric()
	if ((m.runMeEvery > 0) and (runNumber % m.runMeEvery == 0)):
		logging.info('Running %s metrics. runMeEvery=%d' % \
			     (m.__class__.__name__, m.runMeEvery))
		m.runMetrics()
	
incrementRunNumber()
logging.info('Exiting Guinan - status=0')
sys.exit(0)
