from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.FileList import FileEntryComponent, FileList
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import ConfigList
from Components.Pixmap import Pixmap
import os
from camcontrol import CamControl
from enigma import eTimer, eDVBCI_UI, eListboxPythonStringContent, eListboxPythonConfigContent


class ScSelection(Screen):
	skin = """
        <screen name="ScSelection" position="center,center" size="560,230" title="Softcam Setup">
                <widget name="entries" position="5,10" size="550,140" />
                <ePixmap name="red" position="0,190" zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                <ePixmap name="green" position="140,190" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                <ePixmap name="yellow" position="280,190" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
                <ePixmap name="blue" position="420,190" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="0,190" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="140,190" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <eLabel text="Restart" position="280,160" size="280,70" zPosition="1" font="Regular;20" halign="center" valign="top" />
                <widget name="key_yellow" position="280,190" zPosition="3" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_blue" position="420,190" zPosition="3" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "CiSelectionActions"],
			{
				"left": self.keyLeft,
				"right": self.keyRight,
				"cancel": self.cancel,
				"green": self.okay,
				"red": self.cancel,
				"yellow": self.restartSoftcam,
				"blue": self.restartCardServer
			},-1)

		self.list = [ ]

		self.softcam = CamControl('softcam')
		self.cardserver = CamControl('cardserver')

		menuList = ConfigList(self.list)
		menuList.list = self.list
		menuList.l.setList(self.list)
		self["entries"] = menuList

		softcams = self.softcam.getList()
		cardservers = self.cardserver.getList()

		self.softcams = ConfigSelection(choices = softcams)
		self.softcams.value = self.softcam.current()

		self.list.append(getConfigListEntry(_("Select Softcam"), self.softcams))
		blueTxt = ""
		if cardservers:
			self.cardservers = ConfigSelection(choices = cardservers)
			self.cardservers.value = self.cardserver.current()
			self.list.append(getConfigListEntry(_("Select Card Server"), self.cardservers))
			blueTxt = _("Cardserver")

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_yellow"] = Label(_("Softcam"))
		self["key_blue"] = Label(blueTxt)

	def keyLeft(self):
		self["entries"].handleKey(KEY_LEFT)

	def keyRight(self):
		self["entries"].handleKey(KEY_RIGHT)

	def restart(self, what):
		self.what = what
		if "s" in what:
			if "c" in what:
				msg = _("Please wait, restarting softcam and cardserver.")
			else:
				msg  = _("Please wait, restarting softcam.")
                elif "c" in what:
			msg = _("Please wait, restarting cardserver.")
		self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStop)
		self.activityTimer.start(100, False)

	def doStop(self):
		self.activityTimer.stop()
		if "c" in self.what:
			self.cardserver.command('stop')
		if "s" in self.what:
			self.softcam.command('stop')
		self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		# Delay a second to give 'em a chance to stop
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStart)
		self.activityTimer.start(1000, False)

	def doStart(self):
		self.activityTimer.stop()
		del self.activityTimer 
		if "c" in self.what:
                        self.cardserver.select(self.cardservers.value)
			self.cardserver.command('start')
		if "s" in self.what:
			self.softcam.select(self.softcams.value)
			self.softcam.command('start')
		self.mbox.close()
		self.close()
		self.session.nav.playService(self.oldref)
		del self.oldref

	def restartCardServer(self):
		if hasattr(self, 'cardservers'):
			self.restart("c")
	
	def restartSoftcam(self):
		self.restart("s")

	def okay(self):
		what = ''
		if hasattr(self, 'cardservers') and (self.cardservers.value != self.cardserver.current()):
                        what = 'sc'
		elif self.softcams.value != self.softcam.current():
                        what = 's'
                if what:
                	self.restart(what)
		else:
			self.close()

	def cancel(self):
		self.close()
