import logging
import sys
import GuinanCommon
import subprocess
import re
import time
from IrodsMetricAbstract import IrodsMetric

# IrodsStatus metrics local metrics file is formatted like this:
# {
#  "IrodsStatus": [{"timestamp": 1347777777.00, "metric": {"alive": true}}]
#  "CachedStatus":[{"timestamp": 1347777777.00, "metric": {"alive": false}}]
# }

def isIrodsServerUp(irods_path):
	process_name = 'irodsServer'
	ps = subprocess.Popen("ps -eaf | grep "+process_name,
				shell=True, stdout=subprocess.PIPE)
	output = ps.stdout.read()
	ps.stdout.close
	ps.wait()

	if re.search(irods_path + '/server/bin/' + process_name, output) is None:
		return False
	else:
		return True

class IrodsStatus(IrodsMetric):

	# This attribute lets Guinan know how often this metric 
	# is collected (units are in minutes)
	# If it is missing or <=0, this metric will never be collected
	# Also note that individual metrics can never be run more 
	# frequently then Guinan is configured to run (via cron)
	# this attribute is required
	runMeEvery = 10

	# this attribute specifies when the locally saved metric gets
	# stale and should be updated in irods (units are minutes)
	# this is useful when Guinan 'blacks out' for some reason and
	# could not run at regular intervals
	expiration = 60

	# iRODS connection attribute
	conn = None

	def metricsMatch(self, live, local):

		# if there are no saved local metrics - assume
		#  there has been a change
		if local is None:
			return False

		localM = local[self.__class__.__name__][0]['metric']
		localTS = local[self.__class__.__name__][0]

		# now check to see if actual metric has changed
		if (live['alive'] != localM['alive']):
			return False

		# now check to see if metric is stale
		if (time.time() > (localTS['timestamp'] + (self.expiration*60))):
			return False

		return True

	# this function is required
	def runMetric(self):

		irodsUp = False

		logging.debug('Running %s metrics' % self.__class__.__name__)
		self.mRods = GuinanCommon.MonitoredIrods()

		# get my live metrics
		myMetric = dict() # {"alive": <True or False>}

		# find out if server is up
		irodsUp = isIrodsServerUp(self.mRods.homePath)

		# here is my metric now
		myMetric['alive'] = irodsUp

		# load the json file containing my last collected metrics
		# and compare to my live metrics (just looking at alive and
		# to see if the timestamp is too stale)
		localMetrics = self.getLocalMetrics()
		if self.metricsMatch(myMetric, localMetrics):
			# Done! Nothing else to do	
			logging.debug('Metrics match: returning None')
			myMetric =  None
		else:
			logging.debug('Metrics need to be updated')

		# Done!
		logging.info('%s: completed metric collection successfully' % self.__class__.__name__)
		return myMetric
