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
        <screen name="ScSelection" position="80,200" size="560,230" title="Softcam Setup">
                <widget name="entries" position="5,10" size="550,170" />
                <ePixmap name="red" position="5,190" zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                <ePixmap name="green" position="150,190" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="5,190" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="#9f1313" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="150,190" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="#1f771f" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "CiSelectionActions"],
			{
				"left": self.keyLeft,
				"right": self.keyRight,
				"cancel": self.cancel,
				"green": self.set_sc,
				"red": self.cancel
			},-1)

		self.list = [ ]

		self.softcam = CamControl('softcam')
		self.cardserver = CamControl('crdsvr')

		menuList = ConfigList(self.list)
		menuList.list = self.list
		menuList.l.setList(self.list)
		self["entries"] = menuList

		softcams = self.softcam.getList()
		cardservers = self.cardserver.getList()

		self.softcams = ConfigSelection(choices = softcams)
		self.softcams.value = self.softcam.current() or _("None")

		self.list.append(getConfigListEntry(_("Select Softcam"), self.softcams))
		if cardservers:
			self.cardservers = ConfigSelection(choices = cardservers)
			self.cardservers.value = self.cardserver.current() or _("None (Softcam)")
			self.list.append(getConfigListEntry(_("Select Card Server"), self.cardservers))

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))

	def keyLeft(self):
		self["entries"].handleKey(KEY_LEFT)

	def keyRight(self):
		self["entries"].handleKey(KEY_RIGHT)

	def restart(self):
		self.activityTimer.stop()
		if self.what == "both":
			self.cardserver.command('stop')
		self.softcam.command('stop')
		self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()

		self.softcam.select(self.softcams.value)
		if self.what == "both":
                        self.cardserver.select(self.cardservers.value)
			self.cardserver.command('start')
		self.softcam.command('start')
		self.mbox.close()
		self.close()
		self.session.nav.playService(self.oldref)

	def reset_both(self):
		self.what = "both"
		self.mbox = self.session.open(MessageBox, _("Please wait, restarting softcam and cardserver."), MessageBox.TYPE_INFO)
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.restart)
		self.activityTimer.start(100, False)

	def set_sc(self):
		self.what = "sc"
		if self.softcams.value != self.softcam.current():
			self.mbox = self.session.open(MessageBox, _("Please wait, (re)starting softcam."), MessageBox.TYPE_INFO)
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.restart)
			self.activityTimer.start(100, False)
		else:
			self.close()


	def cancel(self):
		self.close()
