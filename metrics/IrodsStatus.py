import logging
import sys
import GuinanCommon
import subprocess
import re
import time
from IrodsMetricAbstract import IrodsMetric

# IrodsStatus metrics local metrics file is formatted like this:
# {
#  "IrodsStatus": [{"alive": True}, {"timestamp": 134777777}]
#  "CachedStatus":[{"alive": False}, {"timestamp": 1347777777}]
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

	# Monitored iRODS
	mRods = None

	def __init__(self):

		logging.debug('Initialized %s module' % self.__class__.__name__)

	def metricsMatch(self, live, local):

		# if there are no saved local metrics - assume
		#  there has been a change
		if local is None:
			return False

		liveM = live[self.__class__.__name__][0]
		localM = local[self.__class__.__name__][0]
		# now check to see if actual metric has changed
		if (liveM['alive'] != localM['alive']):
			return False

		# now check to see if metric is stale
		if (time.time() > (localM['timestamp'] + (self.expiration*60))):
			return False

		return True

	# this function is required
	def runMetrics(self):

		irodsUp = False

		logging.debug('Running %s metrics' % self.__class__.__name__)
		self.mRods = GuinanCommon.MonitoredIrods()

		# get my live metrics
		irodsStatus = dict() # {"IrodsStatus": <value is timestampList>}
		timestampList = list() # [<containing timestamp dictionary>]
		timestamp = dict() # {"alive": True, "timestamp": <epoch here>}

		# get current time epoch
		timeNow = time.time()
		timestamp['timestamp'] = timeNow

		# find out if server is up
		irodsUp = isIrodsServerUp(self.mRods.homePath)
		timestamp['alive'] = irodsUp

		timestampList.append(timestamp)
		# here are my live metrics now

		irodsStatus[self.__class__.__name__] = timestampList

		# load the json file containing my last collected metrics
		# and compare to my live metrics (just looking at alive and
		# to see if the timestamp is too stale)
		localMetrics = self.getLocalMetrics()

		if self.metricsMatch(irodsStatus, localMetrics):
			# Done! Nothing else to do	
			logging.debug('Metrics match: returning without updating')
			return
		else:
			logging.debug('Metrics need to be updated')

			# first, save new live metrics	
			# after saving cache, if any
			cachedMetricsList = None
			if (localMetrics is not None):
				try:
					cachedMetricsList = localMetrics['CachedStatus']
				except:
					cachedMetricsList = None
					
			self.setLocalMetrics(irodsStatus)

			if self.isIrodsUp():
				# save all of the data in the local metrics file to iRODS
				# will take cached data, if any, in preference
				# do not need to restore CachedStatus list in local file
				# since it has now been saved to iRODS
				tmpIrodsMetrics = dict()
				if ((cachedMetricsList is not None) and \
				    (cachedMetricsList.__len__() > 0)):
					# add the latest metric
					cachedMetricsList.append(timestamp)
					tmpIrodsMetrics[self.__class__.__name__] = \
					 	 cachedMetricsList
				else:
					tmpIrodsMetrics = irodsStatus
					
				self.setIrodsMetrics(tmpIrodsMetrics)

			else:
				# add live metric data to CachedStatus list
				# and save updated CachedStatus list to local
				# metrics file
				logging.warning('%s: cannot connect to iRODS. Will cache metrics.' \
					% self.__class__.__name__)
				if cachedMetricsList is None:
					cachedMetricsList = list()
				cachedMetricsList.append(timestamp)
				tmpLocalMetrics = self.getLocalMetrics()
				if tmpLocalMetrics is None:
					tmpLocalMetrics = dict()
				tmpLocalMetrics['CachedStatus'] = cachedMetricsList
				self.setLocalMetrics(tmpLocalMetrics)


		# Done!
		logging.info('%s: completed metric collection successfully' % self.__class__.__name__)
