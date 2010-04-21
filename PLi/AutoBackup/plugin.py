import time
import os
import enigma
from Components.config import config, ConfigEnableDisable, ConfigSubsection, \
			 ConfigYesNo, ConfigClock, getConfigListEntry, \
			 ConfigSelection, ConfigNumber
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor

#Set default configuration
config.plugins.autobackup = ConfigSubsection()
config.plugins.autobackup.wakeup = ConfigClock(default = ((4*60) + 45) * 60) # 4:45
config.plugins.autobackup.mode = ConfigSelection(default = "off", choices = [
		("off", _("Disabled")),
		("/media/hdd", _("Harddisk")),
		("/media/usb", _("USB")), 
		("/media/cf", _("CF"))
		])


# Global variables
autoStartTimer = None
_session = None

##################################
# Configuration GUI

def runBackup():
	destination = config.plugins.autobackup.mode.value
	if destination and (destination != "off"):
		try:
			print "[AutoBackup] **************** begin **************** destination:", destination
			os.system("/usr/lib/enigma2/python/Plugins/PLi/AutoBackup/settings-backup.sh %s" % destination)
		except Exception, e:
			print "[AutoBackup] FAIL:", e


class Config(ConfigListScreen,Screen):
	skin = """
<screen position="center,center" size="560,400" title="AutoBackup Configuration" >
	<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
	<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
	<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
	<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

	<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
	<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
	<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
	<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

	<widget name="config" position="10,40" size="540,240" scrollbarMode="showOnDemand" />

	<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,383" size="14,14" zPosition="3"/>
	<widget font="Regular;18" halign="left" position="505,380" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
		<convert type="ClockToText">Default</convert>
	</widget>
	<widget name="statusbar" position="10,380" size="470,20" font="Regular;18" />
	<widget name="status" position="10,300" size="540,60" font="Regular;20" />
</screen>"""
		
	def __init__(self, session, args = 0):
		self.session = session
		self.setup_title = _("AutoBackup Configuration")
		Screen.__init__(self, session)
		cfg = config.plugins.autobackup
		self.list = [
			getConfigListEntry(_("Daily automatic backup to"), cfg.mode),
			getConfigListEntry(_("Automatic start time"), cfg.wakeup),
			]
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self["status"] = Label()
		self["statusbar"] = Label()
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Ok"))
		self["key_yellow"] = Button(_("Manual"))
		self["key_blue"] = Button(_(""))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"yellow": self.dobackup,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self.save,
		}, -2)
		self.onChangedEntry = []
	
	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]
	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())
	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def save(self):
		self.saveAll()
		self.close(True,self.session)

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False,self.session)
		

	def dobackup(self):
		runBackup()
		

def main(session, **kwargs):
    session.openWithCallback(doneConfiguring, Config)

def doneConfiguring(session, retval):
    "user has closed configuration, check new values...."
    if autoStartTimer is not None:
        autoStartTimer.update()

##################################
# Autostart section
class AutoStartTimer:
	def __init__(self, session):
		self.session = session
		self.timer = enigma.eTimer() 
	    	self.timer.callback.append(self.onTimer)
	    	self.update()
	def getWakeTime(self):
	    if config.plugins.autobackup.mode.value and (config.plugins.autobackup.mode.value != "off"):
	        clock = config.plugins.autobackup.wakeup.value
	        nowt = time.time()
		now = time.localtime(nowt)
		return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday,  
	                      clock[0], clock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
	    else:
	        return -1 
	def update(self, atLeast = 0):
	    self.timer.stop()
	    wake = self.getWakeTime()
	    now = int(time.time())
	    if wake > 0:
		if wake < now + atLeast:
		    # Tomorrow.
		    wake += 24*3600
	        next = wake - now
		self.timer.startLongTimer(next)
	    else:
	    	wake = -1
	    return wake
	def onTimer(self):
		self.timer.stop()
		now = int(time.time())
		wake = self.getWakeTime()
		# If we're close enough, we're okay...
		atLeast = 0
		if wake - now < 60:
			runBackup() 
			atLeast = 60
	        self.update(atLeast)


def autostart(reason, session=None, **kwargs):
    "called with reason=1 to during shutdown, with reason=0 at startup?"
    global autoStartTimer
    global _session
    if reason == 0:
    	if session is not None:
		_session = session
		if autoStartTimer is None:
	    		autoStartTimer = AutoStartTimer(session)


description = _("Automatic settings backup")

def Plugins(**kwargs):
    result = [
        PluginDescriptor(
            name="AutoBackup",
            description = description,
            where = [
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART
            ],
            fnc = autostart
        ),
    
        PluginDescriptor(
            name="AutoBackup",
            description = description,
            where = PluginDescriptor.WHERE_PLUGINMENU,
            icon = 'plugin.png',
            fnc = main
        ),
    ]

    return result
