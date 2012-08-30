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
				print m
				modName = os.path.splitext(m)[0]
				try:
					module = __import__(modName)
				except (ImportError, NotImplementedError):
					print 'help!'
					continue
				for cls in dir(module):
					cls = getattr(module, cls)
					if (inspect.isclass(cls) and \
				    	inspect.getmodule(cls) == module and \
				    	issubclass(cls, met.IrodsMetric)):
						classList.append(cls)
	return classList

# setup logging - want to change this later to append to date stamped
# log files and clean up logs older that N days
# 
cfg = ConfigParser.ConfigParser()
cfg.read('./GuinanConfig.ini')

# need to do some good error checking for values read from config
#if not isinstance(log_level, int):
#	raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(filename=cfg.get('logs', 'filename'),
	level=cfg.get('logs', 'log_level'),
	format='%(asctime)s %(message)s')

logging.info('Started Guinan')

metricsFolderName = './metrics'

# set up search path for metrics modules
metricsFolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split( \
			     inspect.getfile(inspect.currentframe()))[0], \
			     metricsFolderName)))
if metricsFolder not in sys.path:
	sys.path.insert(0, metricsFolder)

# load metrics modules
metrics = loadMetrics(metricsFolderName)
for metric in metrics:
	m = metric()
	if m.runMeEvery > 0:
		logging.info('Running %s metrics. runMeEvery=%d' % \
			     (m.__class__.__name__, m.runMeEvery))
		m.runMetrics()
	
logging.info('Exiting Guinan - status=0')
sys.exit(0)
