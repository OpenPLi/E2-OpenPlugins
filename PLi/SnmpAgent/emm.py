from enigma import eConsoleAppContainer, iServiceInformation

class Emm():
	def __init__(self, session, refresh_func = None, finished_func = None):
		self.session = session
		self.refresh_func = refresh_func
		self.finished_func = finished_func

		self.pids = ''
		self.running = False
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
			cmd = "emm "
			cmd += str(demux)
			self.running = True
			self.container.execute(cmd)

	def stop(self):
		self.container.kill()
		self.pids = ''
		self.running = False

	def appClosed(self, retval):
		self.running = False
		if self.finished_func:
			self.finished_func(retval)

	def dataAvail(self, str):
		#we only need the first line
		self.pids = str.split('\n')[0]
		if self.refresh_func:
			self.refresh_func()