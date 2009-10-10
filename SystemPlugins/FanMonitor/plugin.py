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
		<screen name="fanmonitorscreen" position="90,100" size="520,400" title="FanMonitor">
		
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		
		<eLabel name="rpm" text="Speed" position="70,35" size="60,20" font="Regular;18" halign="right" transparent="1" />
		<widget source="FanSource" render="Label" position="460,35" size="60,22" font="Regular;18">
			<convert type="FanInfo">RPM</convert>
		</widget>
		<eLabel name="rpm" text="Voltage" position="60,65" size="70,20" font="Regular;18" halign="right" transparent="1" />
		<widget source="FanSource" render="Label" position="460,65" size="60,22" font="Regular;18">
			<convert type="FanInfo">VLT</convert>
		</widget>
		<eLabel name="rpm" text="DutyCycle" position="30,95" size="100,20" font="Regular;18" halign="right" transparent="1" />
		<widget source="FanSource" render="Label" position="460,95" size="60,22" font="Regular;18">
			<convert type="FanInfo">PWM</convert>
		</widget>
		<widget source="FanSource" render="Progress" position="190,35" size="260,20" pixmap="skin_default/bar_snr.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FanInfo">RPM</convert>
		</widget>
		<widget source="FanSource" render="Progress" position="190,65" size="260,20" pixmap="skin_default/bar_snr.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FanInfo">VLT</convert>
		</widget>
		<widget source="FanSource" render="Progress" position="190,95" size="260,20" pixmap="skin_default/bar_snr.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FanInfo">PWM</convert>
		</widget>
	
		<widget source="TemperatureSource" render="Progress" position="100,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_1</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="120,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_2</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="140,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_3</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="160,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_4</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="180,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_5</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="200,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_6</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="220,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_7</convert>
		</widget>
		<widget source="TemperatureSource" render="Progress" position="240,130" size="20,260" orientation="orBottomToTop" pixmap="skin_default/v_temp_bar.png" borderWidth="2" borderColor="#cccccc">
			<convert type="TemperatureInfo">SENSOR_8</convert>
		</widget>
		<eLabel name="tmp" text="Temp 1:" position="300,130" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,130" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_1</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,130" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 2:" position="300,150" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,150" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_2</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,150" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 3:" position="300,170" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,170" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_3</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,170" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 4:" position="300,190" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,190" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_4</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,190" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 5:" position="300,210" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,210" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_5</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,210" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 6:" position="300,230" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,230" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_6</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,230" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 7:" position="300,250" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,250" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_7</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,250" size="100,18" font="Regular;16" halign="left" transparent="1" />
		<eLabel name="tmp" text="Temp 8:" position="300,270" size="90,18" font="Regular;16" halign="left" transparent="1" />
		<widget source="TemperatureSource" render="Label" position="380,270" size="48,18" font="Regular;16">
			<convert type="TemperatureInfo">SENSOR_8</convert>
		</widget>
		<eLabel name="tmp" text="Grad C" position="420,270" size="100,18" font="Regular;16" halign="left" transparent="1" />
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
		self["key_green"] = StaticText(_("xxx"))
		self["key_yellow"] = StaticText(_("yyy"))
		self["key_blue"] = StaticText(_("zzz"))
		
		self["FanSource"]=FanStatus(update_interval = 1000)	#der FP liefert sowieso nur aller 1s einen Wert
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
