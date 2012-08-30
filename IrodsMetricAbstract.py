from abc import ABCMeta, abstractmethod, abstractproperty

class IrodsMetric:
	__metaclass__ = ABCMeta

	@abstractmethod
	def runMetrics(self):
		pass

	@abstractproperty
	def runMeEvery(self):
		pass
