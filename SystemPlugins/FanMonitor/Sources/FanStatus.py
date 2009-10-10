from Source import Source
from enigma import eTimer

class FanStatus(Source):
	def __init__(self,update_interval = 1000):
		Source.__init__(self)
		self.update_interval = update_interval
		self.fan_timer = eTimer()
		self.fan_timer.callback.append(self.updateFanStatus)
		self.fan_timer.start(update_interval, True)
		self.rps_flt_coef_dest = 64.0
		self.rps_flt_coef = 1.0
		self.rps = float(open("/proc/stb/fp/fan_speed").read().split(' ')[0])/60.0
		self.rps_old = 0.0
		self.rps_flt = self.rps_flt_coef * self.rps
		self.current_rps = 0

	def inc_flt(self):
		delta =abs(self.rps - self.rps_old)
		delta2 = abs(self.current_rps - self.rps)
		print "delta", delta
		print "delta2", delta2
		if delta != 0:
			print "1/delta", 1/delta
		else:
			print "1/delta unendlich"
		treshold_1 = (1.0/(2.0*self.rps_flt_coef))
		treshold_2 = (2.0/self.rps_flt_coef)
		print "treshold_1", treshold_1
		print "treshold_2", treshold_2
		
		
		if delta > treshold_2 or delta2 > 1 :
			if self.rps_flt_coef > 1:
				if delta2 > 2:
					self.rps_flt = self.current_rps
					self.rps_flt_coef = 1
				else:
					self.rps_flt = self.rps_flt / 2
					self.rps_flt_coef = self.rps_flt_coef / 2
					if self.rps_flt_coef < 1:
						self.rps_flt_coef = 1
		elif delta <= treshold_1:
			if self.rps_flt_coef < self.rps_flt_coef_dest:
				self.rps_flt = self.rps_flt * 2
				self.rps_flt_coef = self.rps_flt_coef * 2

	def updateFanStatus(self):
		self.current_rps = float(open("/proc/stb/fp/fan_speed").read().split(' ')[0])/60	#
		print "curr_rps:", self.current_rps
		print "rps:", self.rps
		print "coef:",self.rps_flt_coef
		
		self.inc_flt()
		self.rps_flt = float(self.rps_flt) - (float(self.rps_flt) / float(self.rps_flt_coef)) + self.current_rps
		self.changed((self.CHANGED_ALL, ))
		self.fan_timer.start(self.update_interval, True)
		self.rps_old = self.rps
		self.rps = (self.rps_flt / self.rps_flt_coef)

	def doSuspend(self, suspended):
		if suspended:
			self.fan_timer.stop()
		else:
			self.fan_timer.start(self.update_interval)
	
	def getRPM(self):
		return int(self.rps*60)
	
	def getVLT(self):
		return int(open("/proc/stb/fp/fan_vlt").read().split(' ')[0],16)
	
	def getPWM(self):
		return int(open("/proc/stb/fp/fan_pwm").read().split(' ')[0],16)
	
	def setVLT(self,output):
		open("/proc/stb/fp/fan_vlt", "w").write("%x" % output)

	def setPWM(self,output):
		open("/proc/stb/fp/fan_pwm", "w").write("%x" % output)

	rpm = property(getRPM)
	vlt = property(getVLT,setVLT)
	pwm = property(getPWM,setPWM)

	def destroy(self):
		self.fan_timer.callback.remove(self.updateFanStatus)
		Source.destroy(self)
