# This is an example metric module.
# The class must be derived from IrodsMetricAbstract.

import logging
from IrodsMetricAbstract import IrodsMetric

class TestMetric(IrodsMetric):

    # This attribute lets Guinan know how often this metric
    # is collected (units are in minutes).
    # If it is missing or <=0, this metric will never be collected.
    # Also note that individual metrics can never be run more
    # frequently then Guinan is configured to run (via cron).
    # This attribute is required.
    runMeEvery = 1

    # This function is required.
    # Calculate/Collect/Generate the metric and return a dict() as shown.
    def runMetric(self):

        logging.debug('Running %s metrics' % self.__class__.__name__)

        # Placeholder for the test metric
        myMetric = dict()
        myMetric["message"] = "hello there"

        # Additional metric info used for display in Scotty
        myMetric[self.getDisplayName()] = "Test Metric"
        myMetric[self.getDescription()] = "This is just a test."

        # Debug message
        logging.debug('%s: returning metric to Guinan: %s' % (self.__class__.__name__, myMetric))

        # Return the dict() holding the metric value.
        #
        # Or return None if you do not want the metric
        # to be saved for some reason.
        return myMetric
