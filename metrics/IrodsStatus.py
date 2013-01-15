import logging
import sys
import GuinanCommon
import subprocess
import re
import time
from IrodsMetricAbstract import IrodsMetric

# IrodsStatus local metrics file is formatted like this:
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
	# is collected (units are in minutes).
	# If it is missing or <=0, this metric will never be collected.
	# Also note that individual metrics can never be run more 
	# frequently then Guinan is configured to run (via cron).
	# This attribute is required.
	runMeEvery = 10

	# This attribute specifies when the locally saved metric gets
	# stale and should be updated in iRODS (units are minutes).
	# This is useful when Guinan 'blacks out' for some reason and
	# could not run at regular intervals.
	expiration = 60

	# Compares 'alive' status and then timestamp staleness.
	def metricsMatch(self, live, local):

		# No saved local metrics, therefore cannot match.
		if local is None:
			return False

		localM = local[self.__class__.__name__][0]['metric']
		localTS = local[self.__class__.__name__][0]

		# Check to see if actual metric has changed
		if (live['alive'] != localM['alive']):
			return False

		# Check to see if metric is stale
		if (time.time() > (localTS['timestamp'] + (self.expiration*60))):
			return False

		return True

	# This function is required.
	def runMetric(self):

		# Setup
		logging.debug('Metric begin: %s' % self.__class__.__name__)
		myMetric = dict() # {"alive": <True or False>}

		# Find out if server is up
		irodsUp = False
		self.mRods = GuinanCommon.MonitoredIrods()
		irodsUp = isIrodsServerUp(self.mRods.homePath)

		# Update metric
		myMetric['alive'] = irodsUp

		# Load the json file containing last collected update.
		localMetrics = self.getLocalMetrics()
		if self.metricsMatch(myMetric, localMetrics):
			# Matched, nothing is new.
			logging.debug('Metrics match: returning None')
			myMetric =  None
		else:
            # Did not match.
			logging.debug('Metrics need to be updated')

		# Cleanup
		logging.info('Metric complete: %s' % self.__class__.__name__)

        # Return
		return myMetric
