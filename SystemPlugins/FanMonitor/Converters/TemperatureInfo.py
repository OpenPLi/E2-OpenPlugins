from Components.Converter.Converter import Converter
from Components.Element import cached

class TemperatureInfo(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "SENSOR_1":
			self.type = 0
		elif type == "SENSOR_2":
			self.type = 1
		elif type == "SENSOR_3":
			self.type = 2
		elif type == "SENSOR_4":
			self.type = 3
		elif type == "SENSOR_5":
			self.type = 4
		elif type == "SENSOR_6":
			self.type = 5
		elif type == "SENSOR_7":
			self.type = 6
		elif type == "SENSOR_8":
			self.type = 7
		else:
			self.type = 7
	@cached
	def getText(self):
		self.source.current = self.type
		return "%d" % self.source.current


	@cached
	def getBool(self):
		return False

	text = property(getText)

	boolean = property(getBool)

	@cached
	def getValue(self):
		self.source.current = self.type
		return int((self.source.current * 255)/70)

	range = 255
	value = property(getValue)

