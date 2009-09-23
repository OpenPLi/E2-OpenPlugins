from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Button import Button

config.plugins.RemoteControlSetup = ConfigSubsection()
config.plugins.RemoteControlSetup.Channel = ConfigInteger(default = 0xf)

class RemoteControlSetup(Screen, ConfigListScreen):
	skin = """
	<screen position="c-175,c-75" size="350,150" title="Remote control setup">
		<widget name="config" position="5,10" size="e-10,e-20" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="c-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="c+5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="ok" position="c-145,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="cancel" position="c+5,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	def __init__(self, session):
		self.skin = RemoteControlSetup.skin
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

		rcchoices = [ ('15', _('all')), ('1', '1'), ('2', '2'), ('4', '3'), ('8', '4')]
		file = open("/proc/stb/ir/rc/mask0", "r")
		line = file.readline()
		file.close()
		mask = int(line, 16)
		if mask == 0 or mask > 0xf:
			mask = 0xf
		self.channel = ConfigSelection(choices = rcchoices, default = ('%d' % mask))
		self.list.append(getConfigListEntry(_("Channel"), self.channel))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyGo(self):
		file = open("/proc/stb/ir/rc/mask0", "w")
		file.write('%X' % (int(self.channel.value)))
		file.close()
		config.plugins.RemoteControlSetup.Channel.value = self.channel.value
		config.plugins.RemoteControlSetup.save()
		self.close()

	def keyCancel(self):
		self.close()

def main(session, **kwargs):
	session.open(RemoteControlSetup)

def startup(reason, **kwargs):
	file = open("/proc/stb/ir/rc/mask0", "w")
	file.write('%X' % (config.plugins.RemoteControlSetup.Channel.value))
	file.close()

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Remote control setup", description = "Lets you configure the remote control channel", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main),
					PluginDescriptor(name = "Remote control setup", description = "", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = startup)]
