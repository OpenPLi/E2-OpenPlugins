from enigma import eConsoleAppContainer, iServiceInformation

class Bitrate():
	def __init__(self, session, refresh_func = None, finished_func = None):
		self.session = session
		self.refresh_func = refresh_func
		self.finished_func = finished_func

		self.running = False
		self.clearValues()
		self.datalines = []
		self.container = eConsoleAppContainer()
		self.container.appClosed.get().append(self.appClosed)
		self.container.dataAvail.get().append(self.dataAvail)

	def start(self):
		if self.running:
			return
		service = self.session.nav.getCurrentService()
		if service:
			#stream() doesn't work in HEAD enigma2, default data demux for tuner 0 seems to be 3...
			demux = 3
			try:
				stream = service.stream()
				if stream:
					streamdata = stream.getStreamingData()
					if streamdata and 'demux' in streamdata:
						demux = streamdata["demux"]
			except:
				pass
			info = service.info()
			vpid = info.getInfo(iServiceInformation.sVideoPID)
			apid = info.getInfo(iServiceInformation.sAudioPID)
			cmd = "bitrate "
			cmd += str(demux)
			cmd += " "
			cmd += str(vpid)
			cmd += " "
			cmd += str(apid)
			self.running = True
			self.container.execute(cmd)

	def clearValues(self):
		self.vmin = 0
		self.vmax = 0
		self.vavg = 0
		self.vcur = 0
		self.amin = 0
		self.amax = 0
		self.aavg = 0
		self.acur = 0

	def stop(self):
		self.container.kill()
		self.clearValues()
		self.running = False

	def appClosed(self, retval):
		self.clearValues()
		self.running = False
		if self.finished_func:
			self.finished_func(retval)

	def dataAvail(self, str):
		newlines = str.split('\n')
		for line in newlines:
			if len(line):
				self.datalines.append(line)
		if len(self.datalines) >= 2:
			self.vmin, self.vmax, self.vavg, self.vcur = self.datalines[0].split(' ')
			self.amin, self.amax, self.aavg, self.acur = self.datalines[1].split(' ')
			self.datalines = []
			if self.refresh_func:
				self.refresh_func()