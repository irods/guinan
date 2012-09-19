# this is an exmple metric module 
# class must be derived from IrodsMetricAbstract

import logging
from IrodsMetricAbstract import IrodsMetric

class TestMetric(IrodsMetric):

	# This attribute lets Guinan know how often this metric 
	# is collected (units are in minutes)
	# If it is missing or <=0, this metric will never be collected
	# Also note that individual metrics can never be run more 
	# frequently then Guinan is configured to run (via cron)
	# this attribute is required
	runMeEvery = 1

	# this function is required
	# do metric collection here and return metric in a dict() as shown
	def runMetric(self):

		logging.debug('Running %s metrics' % self.__class__.__name__)

		# get my live metrics
		myMetric = dict()
		
		# here is my metric
		myMetric["message"] = "hello there"

		# here is additional metric info - used for display
		# in Scotty
		myMetric[self.getDisplayName()] = "Test Metric:"
		myMetric[self.getDescription()] = "This is just a test"

		# Done!
		logging.debug('%s: returning metric to Guinan: %s' \
			      % (self.__class__.__name__, myMetric))

		# return None if you do not want the metric to be save
		# for some reason

		return myMetric
