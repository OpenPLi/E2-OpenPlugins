from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Button import Button

config.plugins.LipsyncSetup = ConfigSubsection()
config.plugins.LipsyncSetup.pcm_delay = ConfigInteger(default = 0)
config.plugins.LipsyncSetup.bitstream_delay = ConfigInteger(default = 0)

class LipsyncSetup(Screen, ConfigListScreen):
	skin = """
	<screen position="c-175,c-75" size="350,150" title="Lipsync Setup">
		<widget name="config" position="5,10" size="e-10,e-20" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="c-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="c+5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="ok" position="c-145,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="cancel" position="c+5,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	pcmfile = "/proc/stb/audio/audio_delay_pcm"
	bitstreamfile = "/proc/stb/audio/audio_delay_bitstream"

	def __init__(self, session):
		self.skin = LipsyncSetup.skin
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

		timingchoices = [ '0', '50', '100', '150', '200', '250', '300', '350', '400', '450', '500' ]

		value = str(config.plugins.LipsyncSetup.pcm_delay.value)
		if value not in timingchoices:
			value = '0'
		self.pcmtimings = ConfigSelection(choices = timingchoices, default = value)

		value = str(config.plugins.LipsyncSetup.bitstream_delay.value)
		if value not in timingchoices:
			value = '0'
		self.bitstreamtimings = ConfigSelection(choices = timingchoices, default = value)

		self.list.append(getConfigListEntry(_("PCM Delay"), self.pcmtimings))
		self.list.append(getConfigListEntry(_("Bitstream Delay"), self.bitstreamtimings))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyGo(self):
		value = int(self.pcmtimings.value)
		config.plugins.LipsyncSetup.pcm_delay.value = value
		try:
			file = open(LipsyncSetup.pcmfile, "w")
			file.write('%X' % (value * 90))
			file.close()
		except:
			pass

		value = int(self.bitstreamtimings.value)
		config.plugins.LipsyncSetup.bitstream_delay.value = value
		try:
			file = open(LipsyncSetup.bitstreamfile, "w")
			file.write('%X' % (value * 90))
			file.close()
		except:
			pass

		config.plugins.LipsyncSetup.save()

		self.close()

	def keyCancel(self):
		self.close()

def main(session, **kwargs):
	session.open(LipsyncSetup)

def startup(reason, **kwargs):
	try:
		file = open(LipsyncSetup.pcmfile, "w")
		file.write('%X' % (config.plugins.LipsyncSetup.pcm_delay.value))
		file.close()
		file = open(LipsyncSetup.bitstreamfile, "w")
		file.write('%X' % (config.plugins.LipsyncSetup.bitstream_delay.value))
		file.close()
	except:
		pass

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Lipsync setup", description = "Lets you configure audio delay", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main),
					PluginDescriptor(name = "Lipsync setup", description = "", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = startup)]