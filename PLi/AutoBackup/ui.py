##################################
# Configuration GUI

import plugin
import os
import enigma
from Components.config import config, configfile, getConfigListEntry, ConfigSelection
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
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
		cmd = plugin.backupCommand()
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

