from Components.Converter.Converter import Converter
from Components.Element import cached

class FanInfo(Converter, object):
	RPM = 0
	VLT = 1
	PWM = 2

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "RPM":
			self.type = self.RPM
		elif type == "VLT":
			self.type = self.VLT
		else :
			self.type = self.PWM
	@cached
	def getText(self):
		if self.type == self.RPM:
			return "%d" % self.source.rpm
		elif self.type == self.VLT:
			return "%d" % self.source.vlt
		else:
			return "%d" % self.source.pwm


	@cached
	def getBool(self):
		return False

	text = property(getText)

	boolean = property(getBool)

	@cached
	def getValue(self):
		if self.type == self.RPM:
			return int((self.source.rpm * 255)/5500)
		elif self.type == self.VLT:
			return self.source.vlt
		else:
			return self.source.pwm

	range = 255
	value = property(getValue)

