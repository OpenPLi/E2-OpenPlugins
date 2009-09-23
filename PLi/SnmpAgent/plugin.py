import time
from enigma import eTimer, iFrontendInformation, iPlayableService
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigText, ConfigYesNo, ConfigSubsection
from Components.Network import iNetwork

from twisted.internet import error as twisted_error
from twistedsnmp import agent, agentprotocol, bisectoidstore
from twistedsnmp.pysnmpproto import v1, oid

from Components.Sources.ServiceList import ServiceList
from enigma import eServiceReference, iServiceInformation

from enigma import eDVBResourceManager, eDVBFrontendParametersSatellite, eDVBFrontendParameters

from bitrate import Bitrate
from emm import Emm

config.plugins.SnmpAgent = ConfigSubsection()
config.plugins.SnmpAgent.managerip = ConfigText(default = '0.0.0.0')
config.plugins.SnmpAgent.systemname = ConfigText(default = 'dm7025')
config.plugins.SnmpAgent.systemdescription = ConfigText(default = 'signal quality monitor')
config.plugins.SnmpAgent.supportaddress = ConfigText(default = 'support@somewhere.tv')
config.plugins.SnmpAgent.location = ConfigText(default = 'default location')
config.plugins.SnmpAgent.measurebitrate = ConfigYesNo(default = False)
config.plugins.SnmpAgent.checkemm = ConfigYesNo(default = False)

config.tv.lastroot = ConfigText()

class ourOIDStore(bisectoidstore.BisectOIDStore):
	startTime = time.time()
	haspicture = False
	oldframes = 0
	iface = 'eth0'

	SYSUPTIME_OID = '.1.3.6.1.2.1.1.3.0'
	SYSTEMDESCRIPTION_OID = '.1.3.6.1.2.1.1.1.0'
	SYSTEMNAME_OID = '.1.3.6.1.2.1.1.6.0'
	SUPPORTADDRESS_OID = '.1.3.6.1.2.1.1.4.0'
	LOCATION_OID = '.1.3.6.1.2.1.1.5.0'
	BER_OID = '.1.3.6.1.2.1.1.10000.0'
	AGC_OID = '.1.3.6.1.2.1.1.10001.0'
	SNR_OID = '.1.3.6.1.2.1.1.10002.0'
	HASPICTURE_OID = '.1.3.6.1.2.1.1.10003.0'
	CHANNELNAME_OID = '.1.3.6.1.2.1.1.10010.0'
	SERVICESTRING_OID = '.1.3.6.1.2.1.1.10011.0'
	FASTSCANSTRING_OID = '.1.3.6.1.2.1.1.10012.0'
	SERVICEPARAMS_OID = '.1.3.6.1.2.1.1.10013.0'
	MANAGERIP_OID = '.1.3.6.1.2.1.1.10020.0'
	ENABLE_BITRATE_OID = '.1.3.6.1.2.1.1.10030.0'
	VIDEO_BITRATE_OID = '.1.3.6.1.2.1.1.10031.0'
	AUDIO_BITRATE_OID = '.1.3.6.1.2.1.1.10032.0'
	IP_OID = '.1.3.6.1.2.1.1.10050.0'
	NETMASK_OID = '.1.3.6.1.2.1.1.10051.0'
	GATEWAY_OID = '.1.3.6.1.2.1.1.10052.0'
	ENABLE_EMM_OID = '.1.3.6.1.2.1.1.10060.0'
	EMM_OID = '.1.3.6.1.2.1.1.10061.0'

	def __init__(self, session, oids = {}):
		self.session = session
		oids.update({
			self.SYSTEMDESCRIPTION_OID: self.getValue,
			'.1.3.6.1.2.1.1.2.0': '.1.3.6.1.4.1.88.3.1',
			self.SYSUPTIME_OID:  self.getValue,
			self.SUPPORTADDRESS_OID: self.getValue,
			self.SYSTEMNAME_OID: self.getValue,
			self.LOCATION_OID: self.getValue,
			self.BER_OID: self.getValue,
			self.AGC_OID: self.getValue,
			self.SNR_OID: self.getValue,
			self.HASPICTURE_OID: self.getValue,
			self.VIDEO_BITRATE_OID: self.getValue,
			self.AUDIO_BITRATE_OID: self.getValue,
			self.CHANNELNAME_OID: self.getValue,
			self.SERVICESTRING_OID: self.getValue,
			self.FASTSCANSTRING_OID: self.getValue,
			self.SERVICEPARAMS_OID: self.getValue,
			self.MANAGERIP_OID: self.getValue,
			self.ENABLE_BITRATE_OID: self.getValue,
			self.IP_OID: self.getValue,
			self.NETMASK_OID: self.getValue,
			self.GATEWAY_OID: self.getValue,
			self.ENABLE_EMM_OID: self.getValue,
			self.EMM_OID: self.getValue,
		})
		bisectoidstore.BisectOIDStore.__init__(self, OIDs = oids)
		self.session.nav.event.append(self.gotServiceEvent)
		if config.plugins.SnmpAgent.measurebitrate.value:
			self.bitrate = Bitrate(session)
		else:
			self.bitrate = None
		if config.plugins.SnmpAgent.checkemm.value:
			self.emm = Emm(session)
		else:
			self.emm = None

	def timerPoll(self):
		data = ''
		try:
			file = open('/proc/stb/vmpeg/0/stat_picture_displayed', 'r')
			data = file.readline()
			file.close()
		except:
			pass
		if len(data):
			frames = int(data, 16)
			if self.oldframes <> frames:
				self.haspicture = True
				self.oldframes = frames
			else:
				self.haspicture = False

	def gotServiceEvent(self, event):
		if self.bitrate:
			if event is iPlayableService.evEnd or event is iPlayableService.evStopped:
				self.bitrate.stop()
			else:
				#don't start bitrate measurement when playing recordings
				if self.session and self.session.nav and self.session.nav.getCurrentService():
					feinfo = self.session.nav.getCurrentService().frontendInfo()
					fedata = feinfo and feinfo.getFrontendData()
					if fedata and 'tuner_number' in fedata:
						self.bitrate.start()
		if self.emm:
			if event is iPlayableService.evEnd or event is iPlayableService.evStopped:
				self.emm.stop()
			else:
				#don't start emm measurement when playing recordings
				if self.session and self.session.nav and self.session.nav.getCurrentService():
					feinfo = self.session.nav.getCurrentService().frontendInfo()
					fedata = feinfo and feinfo.getFrontendData()
					if fedata and 'tuner_number' in fedata:
						self.emm.start()

	def getValue(self, oid, storage):
		oidstring = bisectoidstore.sortableToOID(oid)
		if oidstring == self.SYSTEMDESCRIPTION_OID:
			return v1.OctetString(str(config.plugins.SnmpAgent.systemdescription.value))
		elif oidstring == self.SYSUPTIME_OID:
			return self.getSysUpTime()
		elif oidstring == self.SUPPORTADDRESS_OID:
			return v1.OctetString(str(config.plugins.SnmpAgent.supportaddress.value))
		elif oidstring == self.SYSTEMNAME_OID:
			return v1.OctetString(str(config.plugins.SnmpAgent.systemname.value))
		elif oidstring == self.LOCATION_OID:
			return v1.OctetString(str(config.plugins.SnmpAgent.location.value))
		elif oidstring == self.BER_OID:
			return self.getBER()
		elif oidstring == self.AGC_OID:
			return self.getACG()
		elif oidstring == self.SNR_OID:
			return self.getSNR()
		elif oidstring == self.HASPICTURE_OID:
			return self.haspicture
		elif oidstring == self.VIDEO_BITRATE_OID:
			if self.bitrate:
				return self.bitrate.vcur
			else:
				return 0
		elif oidstring == self.AUDIO_BITRATE_OID:
			if self.bitrate:
				return self.bitrate.acur
			else:
				return 0
		elif oidstring == self.CHANNELNAME_OID:
			return v1.OctetString(self.getChannelName())
		elif oidstring == self.SERVICESTRING_OID:
			return v1.OctetString(self.getServiceString())
		elif oidstring == self.FASTSCANSTRING_OID:
			return v1.OctetString('')
		elif oidstring == self.SERVICEPARAMS_OID:
			return v1.OctetString(self.getServiceParams())
		elif oidstring == self.MANAGERIP_OID:
			return v1.OctetString(str(config.plugins.SnmpAgent.managerip.value))
		elif oidstring == self.ENABLE_BITRATE_OID:
			return config.plugins.SnmpAgent.measurebitrate.value
		elif oidstring == self.IP_OID:
			value = "%d.%d.%d.%d" % tuple(iNetwork.getAdapterAttribute(self.iface, "ip"))
			return v1.IpAddress(value)
		elif oidstring == self.NETMASK_OID:
			value = "%d.%d.%d.%d" % tuple(iNetwork.getAdapterAttribute(self.iface, "netmask"))
			return v1.IpAddress(value)
		elif oidstring == self.GATEWAY_OID:
			value = "%d.%d.%d.%d" % tuple(iNetwork.getAdapterAttribute(self.iface, "gateway"))
			return v1.IpAddress(value)
		elif oidstring == self.ENABLE_EMM_OID:
			return config.plugins.SnmpAgent.checkemm.value
		elif oidstring == self.EMM_OID:
			if self.emm:
				return v1.OctetString(self.emm.pids)
			else:
				return v1.OctetString('')

	def setValue(self, oid, value):
		#the first time we are called, we have to fill the bisect oid store, values are just values, no objects (we cannot call value.get)
		try:
			value.get()
		except:
			return bisectoidstore.BisectOIDStore.setValue(self, oid, value)

		oidstring = bisectoidstore.sortableToOID(oid)
		if oidstring == self.MANAGERIP_OID:
			if config.plugins.SnmpAgent.managerip.value <> value.get():
				config.plugins.SnmpAgent.managerip.value = value.get()
				config.plugins.SnmpAgent.managerip.save()
		elif oidstring == self.ENABLE_BITRATE_OID:
			if config.plugins.SnmpAgent.measurebitrate.value and not value.get():
				config.plugins.SnmpAgent.measurebitrate.value = False
				config.plugins.SnmpAgent.measurebitrate.save()
				if self.bitrate:
					self.bitrate.stop()
					self.bitrate = None
			elif not config.plugins.SnmpAgent.measurebitrate.value and value.get():
				config.plugins.SnmpAgent.measurebitrate.value = True
				config.plugins.SnmpAgent.measurebitrate.save()
				self.bitrate = Bitrate(self.session)
				self.bitrate.start()
		elif oidstring == self.SYSTEMNAME_OID:
			if config.plugins.SnmpAgent.systemname.value <> value.get():
				config.plugins.SnmpAgent.systemname.value = value.get()
				config.plugins.SnmpAgent.systemname.save()
		elif oidstring == self.SUPPORTADDRESS_OID:
			if config.plugins.SnmpAgent.supportaddress.value <> value.get():
				config.plugins.SnmpAgent.supportaddress.value = value.get()
				config.plugins.SnmpAgent.supportaddress.save()
		elif oidstring == self.SYSTEMDESCRIPTION_OID:
			if config.plugins.SnmpAgent.systemdescription.value <> value.get():
				config.plugins.SnmpAgent.systemdescription.value = value.get()
				config.plugins.SnmpAgent.systemdescription.save()
		elif oidstring == self.LOCATION_OID:
			if config.plugins.SnmpAgent.location.value <> value.get():
				config.plugins.SnmpAgent.location.value = value.get()
				config.plugins.SnmpAgent.location.save()
		elif oidstring == self.CHANNELNAME_OID:
			if self.getChannelName() <> value.get():
				root = config.tv.lastroot.value.split(';')
				fav = eServiceReference(root[-2])
				services = ServiceList(fav, command_func = self.zapTo, validate_commands = False)
				sub = services.getServicesAsList()

				if len(sub) > 0:
					for (ref, name) in sub:
						if name == value.get():
							self.zapTo(eServiceReference(ref))
							break
		elif oidstring == self.SERVICESTRING_OID:
			if self.getServiceString() <> value.get():
				self.zapTo(eServiceReference(value.get()))
		elif oidstring == self.FASTSCANSTRING_OID:
			refstring = ''
			fields = value.get().split(',')
			if len(fields) >= 15:
				onid,tsid,freq,id1,id2,sid,orbital_pos,f1,f2,f3,symbolrate,f4,name,provider,servicetype = fields[0:15]
				refstring = '%d:%d:%d:%x:%x:%x:%x:%x:%x:%x:' % (1, 0, int(servicetype), int(sid), int(tsid), int(onid), int(orbital_pos) * 65536, 0, 0, 0)
			if refstring is not '':
				self.zapTo(eServiceReference(refstring))
		elif oidstring == self.SERVICEPARAMS_OID:
			refstring = ''
			fields = value.get().split(',')
			if len(fields) >= 5:
				orbital_pos,tsid,onid,sid,servicetype = fields[0:5]
				refstring = '%d:%d:%d:%x:%x:%x:%x:%x:%x:%x:' % (1, 0, int(servicetype), int(sid), int(tsid), int(onid), int(orbital_pos) * 65536, 0, 0, 0)
			if refstring is not '':
				self.zapTo(eServiceReference(refstring))
		elif oidstring == self.IP_OID:
			ipstring = value.get().split('.')
			ipval = []
			for x in ipstring:
				ipval.append(int(x))
			if iNetwork.getAdapterAttribute(self.iface, "ip") <> ipval:
				iNetwork.setAdapterAttribute(self.iface, "dhcp", 0)
				iNetwork.setAdapterAttribute(self.iface, "ip", ipval)
				iNetwork.deactivateNetworkConfig()
				iNetwork.writeNetworkConfig()
				iNetwork.activateNetworkConfig()
		elif oidstring == self.IP_OID:
			ipstring = value.get().split('.')
			ipval = []
			for x in ipstring:
				ipval.append(int(x))
			if iNetwork.getAdapterAttribute(self.iface, "netmask") <> ipval:
				iNetwork.setAdapterAttribute(self.iface, "dhcp", 0)
				iNetwork.setAdapterAttribute(self.iface, "netmask", ipval)
				iNetwork.deactivateNetworkConfig()
				iNetwork.writeNetworkConfig()
				iNetwork.activateNetworkConfig()
		elif oidstring == self.GATEWAY_OID:
			ipstring = value.get().split('.')
			ipval = []
			for x in ipstring:
				ipval.append(int(x))
			if iNetwork.getAdapterAttribute(self.iface, "gateway") <> ipval:
				iNetwork.setAdapterAttribute(self.iface, "dhcp", 0)
				iNetwork.setAdapterAttribute(self.iface, "gateway", ipval)
				iNetwork.deactivateNetworkConfig()
				iNetwork.writeNetworkConfig()
				iNetwork.activateNetworkConfig()
		elif oidstring == self.ENABLE_EMM_OID:
			if config.plugins.SnmpAgent.checkemm.value and not value.get():
				config.plugins.SnmpAgent.checkemm.value = False
				config.plugins.SnmpAgent.checkemm.save()
				if self.emm:
					self.emm.stop()
					self.emm = None
			elif not config.plugins.SnmpAgent.checkemm.value and value.get():
				config.plugins.SnmpAgent.checkemm.value = True
				config.plugins.SnmpAgent.checkemm.save()
				self.emm = Emm(self.session)
				self.emm.start()
		else:
			print "oid not found!?"

		return None

	def zapTo(self, reftozap):
		self.session.nav.playService(reftozap)

	def getSysUpTime(self):
			seconds = time.time() - self.startTime
			return int(round(seconds * 100, 0))

	def getBER(self):
		if self.session and self.session.nav and self.session.nav.getCurrentService():
			feinfo = self.session.nav.getCurrentService().frontendInfo()
			return feinfo.getFrontendInfo(iFrontendInformation.bitErrorRate)
		return 0

	def getAGC(self):
		if self.session and self.session.nav and self.session.nav.getCurrentService():
			feinfo = self.session.nav.getCurrentService().frontendInfo()
			return feinfo.getFrontendInfo(iFrontendInformation.signalQuality) * 100 / 65536
		return 0

	def getSNR(self):
		if self.session and self.session.nav and self.session.nav.getCurrentService():
			feinfo = self.session.nav.getCurrentService().frontendInfo()
			return feinfo.getFrontendInfo(iFrontendInformation.signalPower) * 100 / 65536
		return 0

	def getChannelName(self):
		name = "unknown"
		if self.session and self.session.nav and self.session.nav.getCurrentService():
			name = self.session.nav.getCurrentService().info().getName()
		return name

	def getServiceString(self):
		name = "unknown"
		if self.session and self.session.nav and self.session.nav.getCurrentService():
			name = self.session.nav.getCurrentService().info().getInfoString(iServiceInformation.sServiceref)
		return name

	def getServiceParams(self):
		orbital_pos = 0
		tsid = 0
		onid = 0
		sid = 0
		servicetype = 0
		if self.session and self.session.nav and self.session.nav.getCurrentService():
			info = self.session.nav.getCurrentService().info()
			serviceref = info.getInfoString(iServiceInformation.sServiceref)
			servicedata = serviceref.split(':')
			orbital_pos = int(servicedata[6], 16) / 65536
			tsid = int(servicedata[4], 16)
			onid = int(servicedata[5], 16)
			sid = int(servicedata[3], 16)
			servicetype = servicedata[2]
		params = str(orbital_pos) + "," + str(tsid), "," + str(onid) + "," + str(sid) + "," + str(servicetype)
		return params

class Tuner:
	def __init__(self, frontend):
		self.frontend = frontend
		
	def tune(self, transponder):
		if self.frontend:
			print "tuning to transponder with data", transponder
			parm = eDVBFrontendParametersSatellite()
			parm.frequency = transponder[0] * 1000
			parm.symbol_rate = transponder[1] * 1000
			parm.polarisation = transponder[2]
			parm.fec = transponder[3]
			parm.inversion = transponder[4]
			parm.orbital_position = transponder[5]
			parm.system = 0  # FIXMEE !! HARDCODED DVB-S (add support for DVB-S2)
			parm.modulation = 1 # FIXMEE !! HARDCODED QPSK 
			feparm = eDVBFrontendParameters()
			feparm.setDVBS(parm)
			self.lastparm = feparm
			self.frontend.tune(feparm)
	
	def retune(self):
		if self.frontend:
			self.frontend.tune(self.lastparm)

class ourTunerOIDStore(ourOIDStore):
	TRANSPONDERPARAMS_OID = '.1.3.6.1.2.1.1.10040.0'
	feid = 0 #TODO: different frontends?

	def __init__(self, session):
		oids = {
			self.TRANSPONDERPARAMS_OID: self.getTransponderParamsOIDValue,
		}
		ourOIDStore.__init__(self, session, oids)
		self.tuner = None
		self.frontend = None
		self.oldref = None
		self.transponderparams = 'freq(kHz),symbolrate(kHz),polarisation(H=0/V=1),fec(0=auto),inversion(0=no/1=yes/2=auto),orbitalpos(10ths of degrees)'

	def setServiceMode(self):
		self.tuner = None
		self.transponderparams = 'freq(kHz),symbolrate(kHz),polarisation(H=0/V=1),fec(0=auto),inversion(0=no/1=yes/2=auto),orbitalpos(10ths of degrees)'
		if self.frontend:
			self.frontend = None
			del self.raw_channel
		if self.session and self.session.nav:
			self.session.nav.playService(self.oldref)

	def setTransponderMode(self):
		if not self.openFrontend():
			self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
			self.session.nav.stopService() # try to disable foreground service
			if not self.openFrontend():
				if self.session.pipshown: # try to disable pip
					self.session.pipshown = False
					del self.session.pip
					if not self.openFrontend():
						self.frontend = None # in normal case this should not happen
		self.tuner = Tuner(self.frontend)

	def openFrontend(self):
		res_mgr = eDVBResourceManager.getInstance()
		if res_mgr:
			self.raw_channel = res_mgr.allocateRawChannel(self.feid)
			if self.raw_channel:
				self.frontend = self.raw_channel.getFrontend()
				if self.frontend:
					return True
				else:
					print "getFrontend failed"
			else:
				print "getRawChannel failed"
		else:
			print "getResourceManager instance failed"
		return False

	def tune(self, transponder):
		self.setTransponderMode()
		if self.frontend and self.tuner:
			if transponder is not None:
				self.tuner.tune(transponder)

	def zapTo(self, reftozap):
		self.setServiceMode()
		ourOIDStore.zapTo(self, reftozap)

	def setValue(self, oid, value):
		#the first time we are called, we have to fill the bisect oid store, values are just values, no objects (we cannot call value.get)
		try:
			value.get()
		except:
			return ourOIDStore.setValue(self, oid, value)

		oidstring = bisectoidstore.sortableToOID(oid)
		if oidstring == self.TRANSPONDERPARAMS_OID:
			print value.get()
			self.transponderparams = value.get()
			transponder = value.get().split(',')
			if len(transponder) >= 6:
				for i in range(0,6):
					transponder[i] = int(transponder[i])
				print transponder
				self.tune(transponder)
			return None
		else:
			return ourOIDStore.setValue(self, oid, value)

	def getBER(self):
		if self.frontend:
			return self.frontend.readFrontendData(iFrontendInformation.bitErrorRate)
		else:
			return ourOIDStore.getBER(self)

	def getAGC(self):
		if self.frontend:
			return self.frontend.readFrontendData(iFrontendInformation.signalQuality) * 100 / 65536
		else:
			return ourOIDStore.getAGC(self)

	def getSNR(self):
		if self.frontend:
			return self.frontend.readFrontendData(iFrontendInformation.signalPower) * 100 / 65536
		else:
			return ourOIDStore.getSNR(self)

	def getTransponderParamsOIDValue(self, oid, storage):
		value = self.transponderparams
		if not self.frontend:
			if self.session and self.session.nav and self.session.nav.getCurrentService():
				feinfo = self.session.nav.getCurrentService().frontendInfo()
				frontendData = feinfo and feinfo.getAll(True)
				if frontendData:
					value += ' example for current transponder: '
					value += str(frontendData["frequency"]/1000)
					value += ','
					value += str(frontendData["symbol_rate"]/1000)
					value += ','
					if frontendData["polarization"] == 'HORIZONTAL':
						value += '0'
					else:
						value += '1'
					value += ','
					#FEC: auto
					value += '0'
					value += ','
					#inversion: auto
					value += '2'
					value += ','
					value += str(frontendData["orbital_position"])
		return v1.OctetString(value)

class SnmpAgent:
	oldmanagerip = ""
	oldber = 0
	theAgent = None
	pollTimer = None
	startTime = time.time()
	oldmanagers = []

	def __init__(self, session, storetype):
		self.oidstore = storetype(session)
		self.storetype = storetype

		agentport, port = self.createAgent()
		if port is not None:
			print 'Listening on port', port
			agentrunning = 1
			self.theAgent = agentport.protocol.agent
			self.pollTimer = eTimer()
			self.pollTimer.timeout.get().append(self.timerPoll)
			self.pollTimer.start(1000, False)

	def createAgent(self):
		from twisted.internet import reactor
		port = 161
		try:
			agentObject = reactor.listenUDP(
				port, agentprotocol.AgentProtocol(
					snmpVersion = 'v2c',
					agent = agent.Agent(dataStore = self.oidstore),
				),
			)
		except twisted_error.CannotListenError:
			pass
		else:
			return agentObject, port

	def timerPoll(self):
		self.oidstore.timerPoll()

		if self.theAgent:
			managerip = config.plugins.SnmpAgent.managerip.value

			if managerip <> self.oldmanagerip:
				newmanagers = managerip.split(',')
				for oldmanager in self.oldmanagers:
					self.theAgent.deregisterTrap(oldmanager)
				for newmanagerip in newmanagers:
					handler = agent.TrapHandler(
							managerIP = (newmanagerip, 162),
						)
					self.theAgent.registerTrap(handler)

				self.oldmanagerip = managerip
				self.oldmanagers = newmanagers

			if not len(managerip):
				return
			if managerip == '0.0.0.0':
				return

			ber = self.oidstore.getBER()
			if ber is not self.oldber:
				self.oldber = ber
				try:
					self.theAgent.sendTrap(pdus = [(self.storetype.BER_OID, ber),])
				except:
					pass

my_agent = None

def autostartEntry(reason, **kwargs):
	global my_agent

	session = None
	if kwargs.has_key("session"):
		session = kwargs["session"]

	if reason == 0:
		print "startup"
		my_agent = SnmpAgent(session, ourTunerOIDStore)
	elif reason == 1:
		print "shutdown"
		#no need to shut the agent down, the pollTimer will stop triggering when enigma2 shuts down
		my_agent = None

def Plugins(**kwargs):
	return PluginDescriptor(
		name = "SnmpAgent",
		description = "SNMP signal status agent",
		where = PluginDescriptor.WHERE_SESSIONSTART,
		fnc = autostartEntry
		)
