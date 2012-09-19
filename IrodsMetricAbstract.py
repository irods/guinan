from abc import ABCMeta, abstractmethod, abstractproperty
import logging
import GuinanCommon
import json
import irods
import time

class IrodsMetric:
	__metaclass__ = ABCMeta

	@abstractmethod
	def runMetric(self):
		pass

	@abstractproperty
	def runMeEvery(self):
		pass

	def getDisplayName(self):
		return "DisplayName"

	def getDescription(self):
		return "Description"

	# TODO: change these methods to throw exceptions?

	def __init__(self):

                self.mRods = GuinanCommon.MonitoredIrods()

	def getLocalMetrics(self):

                localFile = 'metrics/' + self.__class__.__name__ + '.local'
                try:
                        f = open(localFile, 'r')
                except IOError as e:
                        logging.warning('%s: cannot find local metrics file' % \
                                self.__class__.__name__)
                        return None

                metricsStream = f.read()
                f.close
                localMetrics = json.loads(metricsStream)

                return localMetrics

        def setLocalMetrics(self, metrics):

                localFile = 'metrics/' + self.__class__.__name__ + '.local'
                f = open(localFile, 'w')
                if f is not None:
                        metricsJson = json.dumps(metrics)
                        f.write(metricsJson)
                        f.close

	def getIrodsMetrics(self):

                irodsMetrics = None
                conn = self.mRods.getConnection()

		if (conn is not None):
                	metricsFile = self.mRods.getMetricsFilePath() \
                        	+ '/' + self.__class__.__name__ + '.json'
                	f = irods.iRodsOpen(conn, metricsFile, 'r')
                	if f is not None:
                        	metricsStream = f.read()
                        	irodsMetrics = json.loads(metricsStream)
                        	f.close
			self.mRods.disconnect()

                return irodsMetrics

        def setIrodsMetrics(self, metrics):

                if (metrics is None):
                        return

                irodsMetricsList = list()

                # retrieve list of metrics passed in
                tmpMetricsList = metrics[self.__class__.__name__]

                # first see if irods metrics already exist
                irodsMetrics = self.getIrodsMetrics()
                if irodsMetrics is not None:
                        irodsMetricsList = \
                                 irodsMetrics[self.__class__.__name__]

                # now add my new metrics to these metrics
                irodsMetricsList += tmpMetricsList
                metrics[self.__class__.__name__] = irodsMetricsList

                # finally save as a json file to iRODS
                conn = self.mRods.getConnection()
		if (conn is not None):
			# create the guinan collection in iRODS if it does not already exist
			metricsCollection = self.mRods.getMetricsFilePath()
			self.createGuinanCollection()

                	metricsFile = metricsCollection \
                        	+ '/' + self.__class__.__name__ + '.json'
                	f = irods.iRodsOpen(conn, metricsFile, 'w')
                	if f is not None:
                        	metricsJson = json.dumps(metrics)
                        	f.write(metricsJson)
                        	f.close()
                        	logging.debug('Saved updated metrics to iRODS')
			self.mRods.disconnect()

	def isIrodsUp(self):

                conn = self.mRods.getConnection()

		return (conn is not None)

	def createGuinanCollection(self):

                conn = self.mRods.getConnection()
		path = '/' + self.mRods.getZone()
		if (conn is not None):
			coll = irods.irodsCollection(conn, path)
			coll.createCollection(self.mRods.getCollectionName())

	def runMe(self):
		# get metric from module
		moduleMetric = self.runMetric()

		# don't do anything id metric is None
		if (moduleMetric is None):
                        logging.info('%s: No metric provided - nothing to save' % \
                                      self.__class__.__name__)
			return

		# assume this must be a dict for now
		if (not isinstance(moduleMetric, dict)):
                        logging.warning('%s: returned incorrect metric format. Metric not saved' % \
                                      self.__class__.__name__)
			return

		# set up new dict for saving metric
		saveMetric = dict() # {<moduleName>: <value is timestampList>}

		# add a timestamp to this metric
		timestampList = list() # [<containing timestamp dictionary>]
                timestamp = dict() # {"metric": <metric dict>, "timestamp": <epoch here>}
                # get current time epoch
                timeNow = time.time()
                timestamp['timestamp'] = timeNow
		timestamp['metric'] = moduleMetric
		timestampList.append(timestamp)

                # here are the live metrics now
                saveMetric[self.__class__.__name__] = timestampList

                # first, save new live metrics after saving cache, if any
                cachedMetricsList = None

		# load the json file containing my last collected metrics
                localMetrics = self.getLocalMetrics()

                if (localMetrics is not None):
			# check and see if we have any cached metrics
                	try:
                        	cachedMetricsList = localMetrics['CachedStatus']
                        except:
                                cachedMetricsList = None

		self.setLocalMetrics(saveMetric)

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
                                tmpIrodsMetrics = saveMetric

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
