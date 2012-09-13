import re
import ConfigParser
import logging
import irods

# this method retrieves values from the iRODS config file
# given the KEYWORD as it appears in the config file (without the $)
def getIrodsConfigValueFor(homePath, key):

	for line in \
          open(homePath+'/config/irods.config', 'r').readlines():
        	if re.search('^\$'+key, line):
                	words = line.split()
                        value =  words[2].split("'")[1]

        return value

class MonitoredIrods(object):
	#conn = None
	def __init__(self):

		# load config info
		cfg = ConfigParser.ConfigParser()
		cfg.read('./GuinanConfig.ini')
	
		self.homePath = cfg.get('irods', 'home_path') 

		# got path of where iRODS is installed - now go get
		# rest of the credentials from the irods config file
		logging.info('collecting iRODS credentials from "%s"' %
		   self.homePath)

		self.collectionName = 'guinan'
		host = getIrodsConfigValueFor(self.homePath, 'IRODS_ICAT_HOST')
		if host == '':
			host = 'localhost'
		self.host = host
		self.port = int(getIrodsConfigValueFor(self.homePath, 'IRODS_PORT'))
		self.user = getIrodsConfigValueFor(self.homePath, 'IRODS_ADMIN_NAME')
		self.password = getIrodsConfigValueFor(self.homePath, 'IRODS_ADMIN_PASSWORD')
		self.zone = getIrodsConfigValueFor(self.homePath, 'ZONE_NAME')
		self.conn = None

	def getConnection(self):
		err = None

		logging.debug('connecting to iRODS: host=%s port=%d login=%s zone=%s' \
         		% (self.host, self.port, self.user, self.zone))
		# now connect
		self.conn, err = irods.rcConnect(self.host, self.port, self.user, self.zone)
		if self.conn is None:
        		logging.info('cannot connect to iRODS - Is server up?')
		else:
			irods.clientLoginWithPassword(self.conn, self.password)

		return self.conn

	def disconnect(self):
		if self.conn is not None:
			irods.rcDisconnect(self.conn)

	def getMetricsFilePath(self):
		return '/' + self.zone + '/' + self.collectionName
	
	def getZone(self):
		return self.zone

	def getCollectioName():
		return self.collectionName

