from abc import ABCMeta, abstractmethod, abstractproperty
import logging
import GuinanCommon
import json
import irods

class IrodsMetric:
	__metaclass__ = ABCMeta

	@abstractmethod
	def runMetrics(self):
		pass

	@abstractproperty
	def runMeEvery(self):
		pass

	# TODO: change these methods to throw exceptions?

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
                mRods = GuinanCommon.MonitoredIrods()
                conn = mRods.getConnection()

		if (conn is not None):
                	metricsFile = mRods.getMetricsFilePath() \
                        	+ '/' + self.__class__.__name__ + '.json'
                	f = irods.iRodsOpen(conn, metricsFile, 'r')
                	if f is not None:
                        	metricsStream = f.read()
                        	irodsMetrics = json.loads(metricsStream)
                        	f.close
			mRods.disconnect()

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
                mRods = GuinanCommon.MonitoredIrods()
                conn = mRods.getConnection()
		if (conn is not None):
                	metricsFile = mRods.getMetricsFilePath() \
                        	+ '/' + self.__class__.__name__ + '.json'
                	f = irods.iRodsOpen(conn, metricsFile, 'w')
                	if f is not None:
                        	metricsJson = json.dumps(metrics)
                        	f.write(metricsJson)
                        	f.close()
                        	logging.debug('Saved updated metrics to iRODS')
			mRods.disconnect()

	def isIrodsUp(self):

                mRods = GuinanCommon.MonitoredIrods()
                conn = mRods.getConnection()

		return (conn is not None)
