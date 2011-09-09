from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSlider, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Button import Button

config.plugins.ScreenPosition = ConfigSubsection()
config.plugins.ScreenPosition.h_start = ConfigInteger(default = 0x21a)
config.plugins.ScreenPosition.h_end = ConfigInteger(default = 0xd2b)
config.plugins.ScreenPosition.v_start = ConfigInteger(default = 0x27)
config.plugins.ScreenPosition.v_end = ConfigInteger(default = 0x267)

class ScreenPosition(Screen, ConfigListScreen):
	skin = """
	<screen position="c-175,c-75" size="350,150" title="Screen position setup">
		<widget name="config" position="5,10" size="e-10,e-20" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="c-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="c+5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="ok" position="c-145,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="cancel" position="c+5,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	h_start_offset = 0x11a
	h_end_offset = 0xc2b
	v_start_offset = 0
	v_end_offset = 0x240

	def __init__(self, session):
		self.skin = ScreenPosition.skin
		Screen.__init__(self, session)

		self["ok"] = Button(_("OK"))
		self["cancel"] = Button(_("Cancel"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
			"green": self.keyGo,
			"red": self.keyCancel,
		}, -2)

		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session)

		h_start = self.h_start_offset
		h_end = self.h_end_offset
		v_start = self.v_start_offset
		v_end = self.v_end_offset

		try:
			file = open("/proc/stb/video/pal_h_start", "r")
			line = file.readline()
			file.close()
			h_start = int(line, 16)
			file = open("/proc/stb/video/pal_h_end", "r")
			line = file.readline()
			file.close()
			h_end = int(line, 16)
			file = open("/proc/stb/video/pal_v_start", "r")
			line = file.readline()
			file.close()
			v_start = int(line, 16)
			file = open("/proc/stb/video/pal_v_end", "r")
			line = file.readline()
			file.close()
			v_end = int(line, 16)
		except:
			pass

		self.h_start = ConfigSlider(default = h_start - self.h_start_offset, increment = 32, limits = (0, 0x200))
		self.h_end = ConfigSlider(default = h_end - self.h_end_offset, increment = 32, limits = (0, 0x200))
		self.v_start = ConfigSlider(default = v_start - self.v_start_offset, increment = 4, limits = (0, 0x50))
		self.v_end = ConfigSlider(default = v_end - self.v_end_offset, increment = 4, limits = (0, 0x50))
		self.list.append(getConfigListEntry(_("left"), self.h_start))
		self.list.append(getConfigListEntry(_("right"), self.h_end))
		self.list.append(getConfigListEntry(_("top"), self.v_start))
		self.list.append(getConfigListEntry(_("bottom"), self.v_end))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.setPreviewPosition()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.setPreviewPosition()

	def setPreviewPosition(self):
		try:
			file = open("/proc/stb/video/pal_h_start", "w")
			file.write('%X' % (int(self.h_start_offset + self.h_start.value)))
			file.close()
			file = open("/proc/stb/video/pal_h_end", "w")
			file.write('%X' % (int(self.h_end_offset + self.h_end.value)))
			file.close()
			file = open("/proc/stb/video/pal_v_start", "w")
			file.write('%X' % (int(self.v_start_offset + self.v_start.value)))
			file.close()
			file = open("/proc/stb/video/pal_v_end", "w")
			file.write('%X' % (int(self.v_end_offset + self.v_end.value)))
			file.close()
		except:
			return
		oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		self.session.nav.playService(oldService)

	def keyGo(self):
		config.plugins.ScreenPosition.h_start.value = self.h_start_offset + self.h_start.value
		config.plugins.ScreenPosition.h_end.value = self.h_end_offset + self.h_end.value
		config.plugins.ScreenPosition.v_start.value = self.v_start_offset + self.v_start.value
		config.plugins.ScreenPosition.v_end.value = self.v_end_offset + self.v_end.value
		config.plugins.ScreenPosition.save()
		self.close()

	def keyCancel(self):
		setConfiguredPosition()
		oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		self.session.nav.playService(oldService)
		self.close()

def setConfiguredPosition():
	try:
		file = open("/proc/stb/video/pal_h_start", "w")
		file.write('%X' % (int(config.plugins.ScreenPosition.h_start.value)))
		file.close()
		file = open("/proc/stb/video/pal_h_end", "w")
		file.write('%X' % (int(config.plugins.ScreenPosition.h_end.value)))
		file.close()
		file = open("/proc/stb/video/pal_v_start", "w")
		file.write('%X' % (int(config.plugins.ScreenPosition.v_start.value)))
		file.close()
		file = open("/proc/stb/video/pal_v_end", "w")
		file.write('%X' % (int(config.plugins.ScreenPosition.v_end.value)))
		file.close()
	except:
		return

def main(session, **kwargs):
	session.open(ScreenPosition)

def startup(reason, **kwargs):
	setConfiguredPosition()

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Screen position setup", description = "Lets you adjust the screen position", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main),
					PluginDescriptor(name = "Screen position setup", description = "", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = startup)]
