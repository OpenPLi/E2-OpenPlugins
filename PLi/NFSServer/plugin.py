from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.config import ConfigSelection, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Button import Button
from os import system

class NFSServerSetup(Screen, ConfigListScreen):
	skin = """
	<screen position="c-175,c-75" size="350,150" title="NFS server setup">
		<widget name="config" position="5,10" size="e-10,e-50" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="c-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="c+5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="ok" position="c-145,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="cancel" position="c+5,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	exportfile = "/etc/exports"

	def __init__(self, session):
		self.skin = NFSServerSetup.skin
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

		exportchoices = [ '-', '/media/hdd/movie', '/media/hdd', '/' ]
		value = '-'
		try:
			file = open(NFSServerSetup.exportfile, "r")
			line = file.readline()
			file.close()
			if len(line):
				options = line.split()
				value = options[0]
				if value not in exportchoices:
					value = '-'
		except IOError:
			pass
		self.exports = ConfigSelection(choices = exportchoices, default = value)

		self.list.append(getConfigListEntry(_("Export"), self.exports))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyGo(self):
		file = open(NFSServerSetup.exportfile, "w")
		if self.exports.value is not '-':
			file.write('%s\t*(rw,no_root_squash,sync)' % self.exports.value)
		file.close()
		system("exportfs -r")

		self.close()

	def keyCancel(self):
		self.close()

def main(session, **kwargs):
	session.open(NFSServerSetup)

def Plugins(**kwargs):
	return PluginDescriptor(name = "NFS server setup", description = "Lets you configure nfs exports", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main)