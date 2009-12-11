from Source import Source
from enigma import eTimer

class TemperatureStatus(Source):
	def __init__(self,update_interval = 1000):
		Source.__init__(self)
		self.update_interval = update_interval
		self.temp_timer = eTimer()
		self.temp_timer.callback.append(self.updateTemperatureStatus)
		self.temp_timer.start(update_interval, True)
	
	def updateTemperatureStatus(self):
		self.changed((self.CHANGED_ALL, ))
		self.temp_timer.start(self.update_interval, True)

	def doSuspend(self, suspended):
		if suspended:
			self.temp_timer.stop()
		else:
			self.temp_timer.start(self.update_interval)

	def readTemp(self):
		return int(open("/proc/stb/sensors/temp%d/value"%self.index).read())

	def setIndex(self,index):
		if (index < 0) or (index > 7):
			self.index = 0 
		else:
			self.index = index

	current = property(readTemp,setIndex)
	
	def destroy(self):
		self.temp_timer.callback.remove(self.updateTemperatureStatus)
		Source.destroy(self)
