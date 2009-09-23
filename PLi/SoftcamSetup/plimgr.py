import socket
from struct import *

class PLimgrSocket:
	def __init__(self):
		self.socket = None
		self.connect()

	def connect(self):
		if (self.socket != None):
			return 0
		try:
			self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		except socket.error, msg:
			print "socket error"
			self.socket = None
			return -1
		try:
			self.socket.connect('/tmp/.emud.socket')
		except socket.error, msg:
			print "connect error"
			self.socket.close()
			self.socket = None
			return -1

	def commandExchange(self, cmd, txdata):
		datapacket = pack('ii', cmd, len(txdata))
		if self.connect() < 0:
			return -1, ''
		try:
			self.socket.send(datapacket)
			if len(txdata):
				self.socket.send(txdata)
			data = self.socket.recv(calcsize('ii'))
			result = unpack('ii', data)
			rxdata = []
			if (result[1]):
				rxdata = self.socket.recv(result[1])
			return result[0], rxdata
		except socket.error, msg:
			print "transfer error"
			self.socket.close()
			self.socket = None
			return -1, ''

def isascii(text):
	def _ctoi(c):
		if type(c) == type(""):
			return ord(c)
		else:
			return c
	for n in text:
		if _ctoi(n) > 127:
			return False
	return True

class PLimgr(PLimgrSocket):
	def setChannelSettings(self, defaultemu, provideremu, channelemu, channelname, providername):
		result = self.commandExchange(0, pack('iii32s32s', defaultemu, provideremu, channelemu, channelname, providername))
		return result[0]

	def getChannelSettings(self):
		result = self.commandExchange(1, '')
		if result[0] < 0:
			return result[0], -1, -1, -1
		(defaultemu, provideremu, channelemu) = unpack('iii', result[1])
		return result[0], defaultemu, provideremu, channelemu

	def getSoftcamName(self, id):
		result = self.commandExchange(2, pack('i', id))
		if result < 0:
			return result, ''
		name = result[1].replace('\x00', '')
		if not isascii(name):
			name = ''
		return result[0], name

	def restartSoftcam(self):
		result = self.commandExchange(3, '')
		return result[0]

	def enumSettings(self, handle):
		result = self.commandExchange(4, pack('i', handle))
		if result[0] < 0:
			return result[0], 0, 0, '', ''
		(channel, provider, settingname, softcamname) = unpack('ii32s32s', result[1])
		return result[0], channel, provider, settingname.replace('\x00', ''), softcamname.replace('\x00', '')

	def getCardserverName(self, id):
		result = self.commandExchange(5, pack('i', id))
		if result < 0:
			return result, ''
		name = result[1].replace('\x00', '')
		if not isascii(name):
			name = ''
		return result[0], name

	def getCardserverSetting(self):
		result = self.commandExchange(6, '')
		return result[0], result[1].replace('\x00', '')

	def setCardserverSetting(self, name):
		result = self.commandExchange(7, name)
		return result[0]

	def restartCardserver(self):
		result = self.commandExchange(8, '')
		return result[0]

	def getServiceName(self, id):
		result = self.commandExchange(9, pack('i', id))
		return result[0], result[1].replace('\x00', '')

	def getServiceSetting(self, id):
		result = self.commandExchange(10, pack('i', id))
		if result[0] < 0:
			return result[0], 0
		setting = unpack('i', result[1])
		return result[0], setting

	def setServiceSetting(self, id, onoff):
		result = self.commandExchange(11, pack('ii', id, onoff))
		return result[0]

	def restartServices(self):
		result = self.commandExchange(12, '')
		return result[0]

	def putChannelSettingsAndRestart(self, defaultemu, provideremu, channelemu, channelname, providername):
		result = self.commandExchange(13, pack('iii32s32s', defaultemu, provideremu, channelemu, channelname, providername))
		return result[0]

	def getSoftcamInfo(self, id):
		result = self.commandExchange(14, pack('i', id))
		if result[0] < 0:
			return result[0], '', ''
		name = ''
		version = ''
		(name, version) = unpack('32s32s', result[1])
		name = name.replace('\x00', '')
		if not isascii(name):
			name = ''
		version = version.replace('\x00', '')
		if not isascii(version):
			version = ''
		return result[0], name, version

	def listCardservers(self):
		cardservers = []
		while 1:
			result = self.getCardserverName(len(cardservers))
			if result[0] < 0:
				break
			cardservers.append(result[1])
		return cardservers

	def listSoftcams(self):
		softcams = []
		while 1:
			result = self.getSoftcamInfo(len(softcams))
			if result[0] < 0:
				break
			softcams.append((result[1], result[2]))
		return softcams
