from plimgr import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import ConfigSelection, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList

from os import popen

class Execute(Screen):
	skin = """
	<screen position="c-250,c-200" size="500,400">
		<widget name="linelist" font="Fixed;16" position="5,5" size="e-10,e-55" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="e-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="key_yellow" position="5,e-45" size="140,40" zPosition="1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="yellow" />
		<widget name="key_blue" position="e-145,e-45" size="140,40" zPosition="1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
	</screen>"""

	def __init__(self, session, name, command):
		self.skin = Execute.skin
		Screen.__init__(self, session)

		self.name = name
		self.onShown.append(self.setWindowTitle)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"yellow": self.left,
			"blue": self.right
		}, -1)

		self["key_yellow"] = Button("<<")
		self["key_blue"] = Button(">>")

		pipe = popen('{ ' + command + '; } 2>&1', 'r')
		self.linelist = pipe.readlines()
		result = pipe.close()

		self.offset = 0
		self.maxoffset = 0
		for x in self.linelist:
			if len(x) > self.maxoffset:
				self.maxoffset = len(x)

		self["linelist"] = MenuList(list=[], enableWrapAround=True)
		self.setList()

	def setWindowTitle(self):
		self.setTitle(self.name)

	def setList(self):
		if self["linelist"] is not None:
			if self.offset > 0:
				list = []
				for line in self.linelist:
					list.append(line[self.offset:len(line)])
				self["linelist"].setList(list)
			else:
				self["linelist"].setList(self.linelist)

	def left(self):
		if self.offset > 0:
			self.offset = self.offset - 20
			self.setList()

	def right(self):
		if self.offset < self.maxoffset - 40:
			self.offset = self.offset + 20
			self.setList()

class PLiSoftcamSetup(Screen, ConfigListScreen):
	skin = """
	<screen position="c-225,c-100" size="450,200" title="Softcam Setup">
		<widget name="config" position="5,10" size="e-10,e-105" />
		<widget name="restartserver" position="c-215,e-55" size="100,40" valign="center" halign="center" zPosition="2" font="Regular;18" backgroundColor="red" />
		<widget name="ok" position="c-105,e-55" size="100,40" valign="center" halign="center" zPosition="2" font="Regular;18" backgroundColor="green" />
		<widget name="cardinfo" position="c+5,e-55" size="100,40" valign="center" halign="center" zPosition="2" font="Regular;18" backgroundColor="yellow" />
		<widget name="restartcam" position="c+115,e-55" size="100,40" valign="center" halign="center" zPosition="2" font="Regular;18" backgroundColor="blue" />
	</screen>"""

	def __init__(self, session):
		self.skin = PLiSoftcamSetup.skin
		Screen.__init__(self, session)

		self["ok"] = Button(_("Save and exit"))
		self["restartserver"] = Button(_("Restart cardserver"))
		self["cardinfo"] = Button(_("Show card info"))
		self["restartcam"] = Button(_("Restart softcam"))

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
			"green": self.keyGo,
			"red": self.keyRestartServer,
			"yellow": self.keyCardInfo,
			"blue": self.keyRestartSoftcam
		}, -2)

		self.plimgr = PLimgr()
		self.list = []
		self.createConfig()
		ConfigListScreen.__init__(self, self.list, session = self.session)
		self.createSetup("config")

	def createConfig(self):
		cardservers = self.plimgr.listCardservers()
		softcams = self.plimgr.listSoftcams()
		(result, defaultemu, provideremu, channelemu) = self.plimgr.getChannelSettings()
		(result, currentcardservername) = self.plimgr.getCardserverSetting()
		print currentcardservername

		validcardserver = False
		cardserverchoices = []
		cardserverchoices.append(("", _("--None--")))
		for id in range(len(cardservers)):
			print cardservers[id]
			if cardservers[id] != '':
				cardserverchoices.append((cardservers[id], cardservers[id]))

		if not currentcardservername in cardservers:
			currentcardservername = ''

		softcamchoices = []
		softcamchoices.append(("-1", _("--None--")))
		for id in range(len(softcams)):
			print softcams[id][0], '%(id)d' % {'id':id}
			name = softcams[id][0]
			version = softcams[id][1]
			if len(version):
				name += ' ' + version
			softcamchoices.append(('%d' % id, name))

		self.softcam = ConfigSelection(choices = softcamchoices, default = '%d' % defaultemu)
		self.cardserver = ConfigSelection(choices = cardserverchoices, default = currentcardservername)
		self.oldcardservername = currentcardservername
		self.oldsoftcamsetting = '%d' % defaultemu

	def createSetup(self, widget):
		self.list = []
		self.list.append(getConfigListEntry(_("Softcam"), self.softcam))
		self.list.append(getConfigListEntry(_("Cardserver"), self.cardserver))
		self[widget].list = self.list
		self[widget].l.setList(self.list)

	def saveSoftcam(self, result = 0):
		self.plimgr.setChannelSettings(int(self.softcam.value), -1, -1, '', '')
		if self.softcam.value != self.oldsoftcamsetting:
			self.session.openWithCallback(self.exitSetup, MessageBox, _("Setting softcam..."), MessageBox.TYPE_INFO, 5)
		else:
			self.exitSetup()

	def exitSetup(self, result = 0):
		del self.plimgr
		self.close()

	def keyGo(self):
		self.plimgr.setCardserverSetting(self.cardserver.value)
		if self.oldcardservername != self.cardserver.value:
			self.session.openWithCallback(self.saveSoftcam, MessageBox, _("Setting cardserver..."), MessageBox.TYPE_INFO, 5)
		else:
			self.saveSoftcam()

	def keyCancel(self):
		self.exitSetup()

	def keyRestartSoftcam(self):
		self.plimgr.restartSoftcam()
		self.session.openWithCallback(self.exitSetup, MessageBox, _("Restarting softcam..."), MessageBox.TYPE_INFO, 5)

	def keyRestartServer(self):
		self.plimgr.restartCardserver()
		if self.cardserver.value != '':
			self.session.openWithCallback(self.exitSetup, MessageBox, _("Restarting cardserver..."), MessageBox.TYPE_INFO, 5)
		else:
			self.exitSetup()

	def keyCardInfo(self):
		self.session.open(Execute, _("Card info"), "/usr/bin/cardinfo-pli.sh")

class PLiSetup:
	def __init__(self):
		self.addExtension((self.getSoftcamSetupName, self.openSoftcamSetup, lambda: True))

	def getSoftcamSetupName(self):
		return _("Softcam setup")

	def openSoftcamSetup(self):
		print "softcam setup..."
		self.session.open(PLiSoftcamSetup)
