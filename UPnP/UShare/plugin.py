from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.config import ConfigSelection, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Button import Button
from os import system

class UShareSetup(Screen, ConfigListScreen):
	skin = """
	<screen position="c-175,c-75" size="350,150" title="uShare setup">
		<widget name="config" position="5,10" size="e-10,e-50" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="c-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="c+5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="ok" position="c-145,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="cancel" position="c+5,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	configfile = "/etc/ushare.conf"

	def __init__(self, session):
		self.skin = UShareSetup.skin
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

		dirchoices = [ '/media/hdd', '/media/hdd/movie', '/media', '/' ]
		defaultdir = '/media/hdd'
		dir = defaultdir

		compatibilitychoices = [ ('', 'default'), ('-x', 'xbox 360'), ('-d', 'PS3') ]
		defaultcompatibility = ''
		compatibility = defaultcompatibility

		try:
			file = open(UShareSetup.configfile, "r")
			lines = file.readlines()
			file.close()
			for line in lines:
				if len(line):
					token = 'USHARE_DIR='
					if token in line:
						value = line[len(token):]
						if value in dirchoices:
							dir = value
					token = 'USHARE_OPTIONS='
					if token in line:
						for choice in compatibilitychoices:
							if len(choice[0]) and choice[0] in line:
								compatibility = choice[0]
								break
		except IOError:
			pass

		self.dir = ConfigSelection(choices = dirchoices, default = dir)
		self.list.append(getConfigListEntry(_("Directory"), self.dir))
		self.compatibility = ConfigSelection(choices = compatibilitychoices, default = compatibility)
		self.list.append(getConfigListEntry(_("Compatibility"), self.compatibility))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyGo(self):
		lines = []
		try:
			file = open(UShareSetup.configfile, "r")
			lines = file.readlines()
			file.close()
		except IOError:
			pass
		file = open(UShareSetup.configfile, "w")
		for line in lines:
			written = False
			token = 'USHARE_DIR='
			if token in line:
				file.write('%s%s\n' % (token, self.dir.value))
				written = True
			token = 'USHARE_OPTIONS='
			if token in line:
				file.write('%s%s\n' % (token, self.compatibility.value))
				written = True
			if not written:
				file.write(line)
		file.close()
		system("/etc/init.d/ushare stop; /etc/init.d/ushare start")
		self.close()

	def keyCancel(self):
		self.close()

def main(session, **kwargs):
	session.open(UShareSetup)

def Plugins(**kwargs):
	return PluginDescriptor(name = "uShare setup", description = "Lets you configure uShare", where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main)