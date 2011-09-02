import time
import os
import enigma
from Components.config import config, configfile, \
			ConfigEnableDisable, ConfigSubsection, \
			ConfigYesNo, ConfigClock, getConfigListEntry, \
			ConfigSelection, ConfigOnOff, ConfigText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Tools.FuzzyDate import FuzzyTime

FRIENDLY = {
	"/media/hdd": _("Harddisk"),
	"/media/usb": _("USB"),
	"/media/cf": _("CF"),
	"/media/mmc1": _("SD"),
	}
def getLocationChoices():
	result = []
	for line in open('/proc/mounts', 'r'):
		items = line.split()
		if items[1].startswith('/media'):
			desc = FRIENDLY.get(items[1], items[1])
			if items[0].startswith('//'):
				desc += ' (*)'
			result.append((items[1], desc))
	return result

#Set default configuration
config.plugins.autobackup = ConfigSubsection()
config.plugins.autobackup.wakeup = ConfigClock(default = ((3*60) + 0) * 60) # 3:00
config.plugins.autobackup.enabled = ConfigEnableDisable(default = False)
config.plugins.autobackup.autoinstall = ConfigOnOff(default = False)
config.plugins.autobackup.where = ConfigText(default = "/media/hdd")


# Global variables
autoStartTimer = None
_session = None

##################################
# Configuration GUI

BACKUP_SCRIPT = "/usr/lib/enigma2/python/Plugins/PLi/AutoBackup/settings-backup.sh"


def backupCommand():
	cmd = BACKUP_SCRIPT
	if config.plugins.autobackup.autoinstall.value:
		cmd += " -a"
	cmd += " " + config.plugins.autobackup.where.value
	return cmd

def runBackup():
	destination = config.plugins.autobackup.where.value
	if destination:
		try:
			global container  # Need to keep a ref alive...
			def appClosed(retval):
				global container
				print "[AutoBackup] complete, result:", retval
				container = None
			def dataAvail(data):
				print "[AutoBackup]", data.rstrip()
			print "[AutoBackup] start daily backup"
			cmd = backupCommand()
			container = enigma.eConsoleAppContainer()
			if container.execute(cmd):
				raise Exception, "failed to execute:" + cmd
			container.appClosed.append(appClosed)
			container.dataAvail.append(dataAvail)
		except Exception, e:
			print "[AutoBackup] FAIL:", e

def getStandardFiles():
	return [os.path.normpath(n.strip()) for n in open('/usr/lib/enigma2/python/Plugins/PLi/AutoBackup/backup.cfg', 'r')]

def getSelectedFiles():
	result = getStandardFiles()
	try:
		result += [os.path.normpath(n.strip()) for n in open('/etc/backup.cfg', 'r')]
	except:
		# ignore missing user cfg file
		pass
	return result

def saveSelectedFiles(files):
	standard = getStandardFiles()
	try:
		f = open('/etc/backup.cfg', 'w')
		for fn in files:
			fn = os.path.normpath(fn)
			if fn not in standard:
				f.write(fn + '\n')
		f.close()
	except Exception, ex:
		print "[AutoBackup] Failed to write /etc/backup.cfg", ex

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
		choices=getLocationChoices()
		if choices:
			currentwhere = cfg.where.value
			defaultchoice = choices[0][0] 
			for k,v in choices:
				if k == currentwhere:
					defaultchoice = k
					break
		else:
			defaultchoice = ""
			choices = [("", _("Nowhere"))]
		self.cfgwhere = ConfigSelection(default=defaultchoice, choices=choices)
		configList = [
			getConfigListEntry(_("Backup location"), self.cfgwhere),
			getConfigListEntry(_("Daily automatic backup"), cfg.enabled),
			getConfigListEntry(_("Automatic start time"), cfg.wakeup),
			getConfigListEntry (_("Create Autoinstall"), cfg.autoinstall),
			]
		ConfigListScreen.__init__(self, configList, session=session, on_change = self.changedEntry)
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Ok"))
		self["key_yellow"] = Button(_("Manual"))
		self["key_blue"] = Button("")
		self["statusbar"] = Label()
		self["status"] = Label()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"yellow": self.dobackup,
			"blue": self.disable,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self.save,
			"menu": self.menu,
		}, -2)
		self.onChangedEntry = []
		self.data = ''
		self.container = enigma.eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)
		self.cfgwhere.addNotifier(self.changedWhere)
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
		if not cfg.value:
			self["status"].setText(_("No suitable media found, insert USB stick, flash card or harddisk."))
			self.isActive = False
		else:
			config.plugins.autobackup.where.value = cfg.value
			path = os.path.join(cfg.value, 'backup')
			if not os.path.exists(path):
				self["status"].setText(_("No backup present"))
			else:
				try:
					st = os.stat(os.path.join(path, ".timestamp"))
					try:
						macaddr = open('/sys/class/net/eth0/address').read().strip().replace(':','')
						fn = "PLi-AutoBackup%s.tar.gz" % macaddr
						st = os.stat(os.path.join(path, fn))
					except:
						# No box-specific backup found
						pass
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
		cfg = self.cfgwhere
		if not cfg.value:
			return
		path = os.path.join(cfg.value, 'backup', ".timestamp")
		try:
			os.unlink(path)
		except:
			pass
		self.changedWhere(cfg)

	def __onClose(self):
		self.cfgwhere.notifiers.remove(self.changedWhere)

	def save(self):
		config.plugins.autobackup.where.value = self.cfgwhere.value
		config.plugins.autobackup.where.save()
		self.saveAll()
		self.close(True,self.session)

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False,self.session)

	def menu(self):
		self.session.open(BackupSelection)

	def showOutput(self):
		self["status"].setText(self.data)

	def dobackup(self):
		if not self.cfgwhere.value:
			return
		self.saveAll()
		# Write config file before creating the backup so we have it all
		configfile.save()
		self.data = ''
		self.showOutput()
		self["statusbar"].setText(_('Running'))
		cmd = backupCommand()
		if self.container.execute(cmd):
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
		self.changedWhere(self.cfgwhere)

	def dataAvail(self, s):
		self.data += s
		print "[AutoBackup]", s.strip()
		self.showOutput()

class BackupSelection(Screen):
	skin = """
		<screen name="BackupSelection" position="center,center" size="560,400" title="Select files/folders to backup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="checkList" position="5,50" size="550,350" transparent="1" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		from Components.Sources.StaticText import StaticText
		from Components.FileList import MultiFileSelectList
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText()
		selectedFiles = getSelectedFiles()
		defaultDir = '/'
		inhibitDirs = ["/bin", "/boot", "/dev", "/autofs", "/lib", "/proc", "/sbin", "/sys", "/hdd", "/tmp", "/mnt", "/media"]
		self.filelist = MultiFileSelectList(selectedFiles, defaultDir, inhibitDirs = inhibitDirs )
		self["checkList"] = self.filelist
		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions", "ShortcutActions"],
		{
			"cancel": self.exit,
			"red": self.exit,
			"yellow": self.changeSelectionState,
			"green": self.saveSelection,
			"ok": self.okClicked,
			"left": self.filelist.pageUp,
			"right": self.filelist.pageDown,
			"down": self.filelist.down,
			"up": self.filelist.up
		}, -1)
		if not self.selectionChanged in self.filelist.onSelectionChanged:
			self.filelist.onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		idx = 0
		self["checkList"].moveToIndex(idx)
		self.setWindowTitle()
		self.selectionChanged()

	def setWindowTitle(self):
		self.setTitle(_("Select files/folders to backup"))

	def selectionChanged(self):
		current = self["checkList"].getCurrent()[0]
		if current[2] is True:
			self["key_yellow"].setText(_("Deselect"))
		else:
			self["key_yellow"].setText(_("Select"))

	def changeSelectionState(self):
		self["checkList"].changeSelectionState()

	def saveSelection(self):
		saveSelectedFiles(self["checkList"].getSelectedList())
		self.close(None)

	def exit(self):
		self.close(None)

	def okClicked(self):
		if self.filelist.canDescent():
			self.filelist.descent()

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
			# it could be that we do not have the correct system time yet,
			# limit the update interval to 1h, to make sure we try again soon
			if next > 3600:
				next = 3600
			# also, depending on the value of 'atLeast', next could be negative.
			# which would stop our time
			if next <= 0:
				next = 60
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
		if abs(wake - now) < 60:
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
