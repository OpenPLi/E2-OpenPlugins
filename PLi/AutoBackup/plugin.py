import time
import os
import enigma
from Plugins.Plugin import PluginDescriptor
from Components.config import config, \
			ConfigEnableDisable, ConfigSubsection, \
			ConfigClock, ConfigOnOff, ConfigText

#Set default configuration
config.plugins.autobackup = ConfigSubsection()
config.plugins.autobackup.wakeup = ConfigClock(default = ((3*60) + 0) * 60) # 3:00
config.plugins.autobackup.enabled = ConfigEnableDisable(default = False)
config.plugins.autobackup.autoinstall = ConfigOnOff(default = False)
config.plugins.autobackup.where = ConfigText(default = "/media/hdd")

# Global variables
autoStartTimer = None

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

def main(session, **kwargs):
	import ui
	session.openWithCallback(doneConfiguring, ui.Config)

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
	if reason == 0:
		if session is not None:
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
