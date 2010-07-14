import time
import os
import enigma
from Components.config import config, configfile, \
			ConfigEnableDisable, ConfigSubsection, \
			ConfigYesNo, ConfigClock, getConfigListEntry, \
			ConfigSelection
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Tools.FuzzyDate import FuzzyTime

#Set default configuration
config.plugins.autobackup = ConfigSubsection()
config.plugins.autobackup.wakeup = ConfigClock(default = ((3*60) + 0) * 60) # 3:00
config.plugins.autobackup.enabled = ConfigEnableDisable(default = False)
config.plugins.autobackup.where = ConfigSelection(default = "/media/hdd", choices = [
		("/media/hdd", _("Harddisk")),
		("/media/usb", _("USB")),
		("/media/cf", _("CF")),
		("/media/mmc1", _("SD"))
		])


# Global variables
autoStartTimer = None
_session = None

##################################
# Configuration GUI

BACKUP_SCRIPT = "/usr/lib/enigma2/python/Plugins/PLi/AutoBackup/settings-backup.sh"

def runBackup():
	destination = config.plugins.autobackup.where.value
	if destination:
		try:
			os.system("%s %s" % (BACKUP_SCRIPT, destination))
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

	<widget name="config" position="10,40" size="540,200" scrollbarMode="showOnDemand" />
	<widget name="status" position="10,250" size="540,130" font="Regular;16" />

	<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,383" size="14,14" zPosition="3"/>
	<widget font="Regular;18" halign="left" position="505,380" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
		<convert type="ClockToText">Default</convert>
	</widget>
	<widget name="statusbar" position="10,380" size="470,20" font="Regular;18" />
</screen>"""
		
	def __init__(self, session, args = 0):
		self.session = session
		self.setup_title = _("AutoBackup Configuration")
		Screen.__init__(self, session)
		cfg = config.plugins.autobackup
		configList = [
			getConfigListEntry(_("Backup location"), cfg.where),
			getConfigListEntry(_("Daily automatic backup"), cfg.enabled),
			getConfigListEntry(_("Automatic start time"), cfg.wakeup),
			]
		ConfigListScreen.__init__(self, configList, session=session, on_change = self.changedEntry)
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Ok"))
		self["key_yellow"] = Button(_("Manual"))
		self["key_blue"] = Button("")
		self["statusbar"] = Label()
		self["status"] = Label()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"yellow": self.dobackup,
			"blue": self.disable,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self.save,
		}, -2)
		self.onChangedEntry = []
		self.data = ''
		self.container = enigma.eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)
		cfg.where.addNotifier(self.changedWhere)
		self.onClose.append(self.__onClose)
	
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

	def changedWhere(self, cfg):
		self.isActive = False
		path = os.path.join(cfg.value, 'backup')
		if not os.path.exists(path):
			self["status"].setText(_("No backup present"))
		else:
			try:
				st = os.stat(os.path.join(path, ".timestamp"))
				self.isActive = True
				self["status"].setText(_("Last backup date") + ": " + " ".join(FuzzyTime(st.st_mtime, inPast=True)))
			except Exception, ex:
				print "Failed to stat %s: %s" % (path, ex)
				self["status"].setText(_("Disabled"))
		if self.isActive:
			self["key_blue"].setText(_("Disable"))
		else:
			self["key_blue"].setText("")

	def disable(self):
		cfg = config.plugins.autobackup.where
		path = os.path.join(cfg.value, 'backup', ".timestamp")
		try:
			os.unlink(path)
		except:
			pass
		self.changedWhere(cfg)

	def __onClose(self):
		config.plugins.autobackup.where.notifiers.remove(self.changedWhere)

	def save(self):
		self.saveAll()
		self.close(True,self.session)

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False,self.session)
		
	def showOutput(self):
		self["status"].setText(self.data)
		
	def dobackup(self):
		self.saveAll()
		# Write config file before creating the backup so we have it all
		configfile.save()
		destination = config.plugins.autobackup.where.value
		self.data = ''
		self.showOutput()
		self["statusbar"].setText(_('Running'))
		cmd = "%s %s" % (BACKUP_SCRIPT, destination)
		if self.container.execute(BACKUP_SCRIPT + " " + destination):
			print "[AutoBackup] failed to execute"
			self.showOutput()
		
	def appClosed(self, retval):
		print "[AutoBackup] done:", retval
		if retval:
			txt = _("Failed")
		else:
			txt = _("Done")
		self.showOutput()
		self.data = ''
		self["statusbar"].setText(txt)
		self.changedWhere(config.plugins.autobackup.where)

	def dataAvail(self, str):
		self.data += str
		self.showOutput()
		

def main(session, **kwargs):
	session.openWithCallback(doneConfiguring, Config)

def doneConfiguring(session, retval):
	"user has closed configuration, check new values...."
	global autoStartTimer
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
	    if config.plugins.autobackup.enabled.value:
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
            where = [PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART],
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
