from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor

from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.config import ConfigSelection, getConfigListEntry

from Components.Sources.FanStatus import FanStatus
from Components.Sources.TemperatureStatus import TemperatureStatus

from Components.Converter.FanInfo import FanInfo
from Components.Converter.TemperatureInfo import TemperatureInfo

from Components.Sources.StaticText import StaticText
from enigma import eTimer

class FanMonitorScreen(Screen):
	skin = """
		<screen name="fanmonitorscreen" position="90,100" size="580,440" title="FanMonitor">
		
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="150,5" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="290,5" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="430,5" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="10,5" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="150,5" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget source="key_yellow" render="Label" position="290,5" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget source="key_blue" render="Label" position="430,5" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		
		<eLabel name="rpm" text="RPM" position="70,55" size="130,20" font="Regular;18" halign="right" transparent="1" />
		<widget source="FanSource" render="Label" position="485,55" size="60,22" font="Regular;18">
			<convert type="FanInfo">RPM</convert>
		</widget>
		<eLabel name="rpm" text="Voltage" position="70,85" size="130,20" font="Regular;18" halign="right" transparent="1" />
		<widget source="FanSource" render="Label" position="485,85" size="60,22" font="Regular;18">
			<convert type="FanInfo">VLT</convert>
		</widget>
		<eLabel name="rpm" text="Duty cycle" position="70,115" size="130,20" font="Regular;18" halign="right" transparent="1" />
		<widget source="FanSource" render="Label" position="485,115" size="65,22" font="Regular;18">
			<convert type="FanInfo">PWM</convert>
		</widget>
		<widget source="FanSource" render="Progress" position="210,55" size="260,20" pixmap="skin_default/bar_snr_klpsauger.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FanInfo">RPM</convert>
		</widget>
		<widget source="FanSource" render="Progress" position="210,85" size="260,20" pixmap="skin_default/bar_snr_klpsauger.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FanInfo">VLT</convert>
		</widget>
		<widget source="FanSource" render="Progress" position="210,115" size="260,20" pixmap="skin_default/bar_snr_klpsauger.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FanInfo">PWM</convert>
		</widget>
	
		<widget source="TemperatureSource" render="Progress" position="100,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_1</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="120,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_2</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="140,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_3</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="160,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_4</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="180,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_5</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="200,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_6</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="220,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_7</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="240,160" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_8</convert>
		</widget>
		<eLabel name="tmp" text="Tuner4" position="300,160" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,160" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_1</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,160" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="XILINX FPGA" position="300,190" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,190" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_2</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,190" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="WLAN" position="300,220" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,220" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_3</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,220" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Battery" position="300,250" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,250" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_4</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,250" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="CI front" position="300,280" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,280" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_5</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,280" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Card readers" position="300,310" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,310" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_6</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,310" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Security chip" position="300,340" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,340" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_7</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,340" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="SATA" position="300,370" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,370" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_8</convert>
		</widget>
		<eLabel name="tmp" text="C" position="420,370" size="100,18" font="Regular;16" halign="left" transparent="1" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["actions"] = ActionMap(["ColorActions","OkCancelActions"],
		{
			"red": self.calibrateFan,
			#"green": self.update,
			#"yellow": self.format,
			#"blue": self.eject,
			"cancel": self.close
		}, -1)
		
		self["key_red"] = StaticText(_("Calibrate"))
		self["key_green"] = StaticText("-")
		self["key_yellow"] = StaticText("-")
		self["key_blue"] = StaticText("-")
		
		self["FanSource"]=FanStatus(update_interval = 1000)	#der FP liefert sowieso nur alle 1s einen Wert
		self["TemperatureSource"]=TemperatureStatus(update_interval = 1000)

	def calibrateFan(self):
		print "calibrateFan"
		
		self.calibFanTimer = eTimer()
		
		
		self.setPWM(255)	# max PWM
		self.setVLT(0)		# min voltage
		self.FanTimeout = 10	#20 sec
		self.fnc = self.waitFanSpeedZero
		self.calibFanTimer.callback.append(self.nextCalibStep)
		self.calibFanTimer.start(2000,True)

	def waitFanSpeedZero(self):
		self.calibFanTimer.start(2000,True)
		if self["FanSource"].current_rps > 0:
			if self.FanTimeout > 0:
				self.getRPS()
				self.FanTimeout -= 1
				return
			self.calibrateFanFailed()
			return
		self.calibFanTimer.stop()
		self.fnc = self.SearchStartVoltage
		self.calibFanTimer.start(2000,True)
	
	def SearchStartVoltage(self):
		self.calibFanTimer.start(2000,True)
		rps = self["FanSource"].current_rps
		print "rps:", rps
		if rps < 10:
			self["FanSource"].vlt += 7
			return
		self.calibFanTimer.stop()
		print self["FanSource"].vlt

	
	
	
	
	def nextCalibStep(self):
		print "nextCalibStep"
		if self.fnc is not None:
			self.fnc()

	def setVLT(self,output):
		open("/proc/stb/fp/fan_vlt", "w").write("%x" % output)
	
	def setPWM(self,output):
		open("/proc/stb/fp/fan_pwm", "w").write("%x" % output)

	def getRPS(self):
		print self["FanSource"].current_rps
	
	def calibrateFanFailed(self):
		print "calibrateFanFailed"


#1.Motor stoppen
#Spannung 0V
#PWM 100%
#warten, wis Motor still steht
#2.Anlaufspannung suchen
#3. Maximale Spannung suchen
#4 PWM testen

###############################################################################
def FanMonitorMain(session, **kwargs):
	session.open(FanMonitorScreen)
	print "FanMonitor gestartet"

def FanMonitorStart(menuid, **kwargs):
	if menuid == "system":
		return [(_("FanMonitor"), FanMonitorMain, "fanmonitor", None)]
	else:
		return []

def Plugins(**kwargs):
	from Plugins.Plugin import PluginDescriptor
	from Tools.HardwareInfo import HardwareInfo
	# currently only available for DM8000
	if HardwareInfo().get_device_name() != "dm8000":
		return [PluginDescriptor()]
	return PluginDescriptor(name="FanMonitor", description="Monitoring and control of cpu-fan", where = PluginDescriptor.WHERE_MENU, fnc=FanMonitorStart)
