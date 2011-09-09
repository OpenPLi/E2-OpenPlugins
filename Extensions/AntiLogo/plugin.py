from Screens.Screen import Screen
from Screens.InfoBar import InfoBar
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Input import Input
from Plugins.Plugin import PluginDescriptor

from enigma import ePoint, eSize

from ConfigParser import ConfigParser, DEFAULTSECT, DuplicateSectionError

class AntiLogoMain(InfoBar):
	def __init__(self, session, args = 0, size = None, position = None):
		config = AntiLogoConfig()
		try:
			preset = config.getLastPreset()
			self.size = [preset["width"], preset["height"]]
			self.position = [preset["x"], preset["y"]]
		except Exception:
			config.setPreset("standard",[100, 100],[20, 20])
			config = AntiLogoConfig()
			preset = config.getPreset("standard")

		self.size = [preset["width"],preset["height"]]
		self.position = [preset["x"],preset["y"]]
		skin = "<screen position=\"%i,%i\" size=\"%i,%i\" title=\"%s\"  flags=\"wfNoBorder\" >" %(preset["x"],preset["y"],preset["width"],preset["height"], "AntiLogo")
		skin += "<widget name=\"label\" position=\"0,0\" size=\"%i,%i\"  backgroundColor=\"transpBlack\"  />" %(preset["width"],preset["height"])
		skin += "</screen>"
		self.skin = skin
		InfoBar.__init__(self, session)
		self.hideTimer.callback.pop()

		self["label"] = Label()
		self["actions"] = ActionMap(["MenuActions"],
				{
				"menu": self.openmenu,
				}, prio=-4)

	def openmenu(self):
		self.session.open(AntiLogoMenu, callback = self.menuCallback, size = self.size, position = self.position)

	def menuCallback(self, size, position):
		if size and position:
			self.size = size
			self.position = position
			self.move(self.position[0], self.position[1])
			self.resize(self.size[0], self.size[1])
		else:
			self.close()

	def move(self, x, y):
		self.instance.move(ePoint(x, y))

	def resize(self, w, h):
		self.instance.resize(eSize(*(w, h)))
		self["label"].instance.resize(eSize(*(w, h)))

class AntiLogoBase(Screen):
	def __init__(self, session, size, position):
		preset = {}
		preset["width"] = size[0]
		preset["height"] = size[1]
		preset["x"] = position[0]
		preset["y"] = position[1]
		self.size = [preset["width"], preset["height"]]
		self.position = [preset["x"], preset["y"]]
		skin = "<screen position=\"%i,%i\" size=\"%i,%i\" title=\"%s\"  flags=\"wfNoBorder\" >" %(preset["x"], preset["y"],preset["width"], preset["height"], "AntiLogo")
		skin += "<widget name=\"label\" position=\"0,0\" size=\"%i,%i\"  backgroundColor=\"transpBlack\"  />" %(preset["width"],preset["height"])
		skin += "</screen>"
		self.skin = skin
		Screen.__init__(self, session)
		self["label"] = Label()
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "MenuActions"],
		{
			"ok": self.go,
			"back": self.go,
			"menu": self.go,
			"down": self.down,
			"up": self.up,
			"left": self.left,
			"right": self.right,
			}, -1)

	def move(self, x, y):
		self.instance.move(ePoint(x, y))

	def resize(self, w, h):
		self.instance.resize(eSize(*(w, h)))
		self["label"].instance.resize(eSize(*(w, h)))

class AntiLogoMove(AntiLogoBase):
	step = 5
	def __init__(self, session, args = 0, size = [], position = []):
		AntiLogoBase.__init__(self, session, size, position)

	def go(self):
		self.close(self.position)
	
	def up(self):
		self.position = [self.position[0],self.position[1]-self.step]
		self.move(self.position[0],self.position[1])

	def down(self):
		self.position = [self.position[0],self.position[1]+self.step]
		self.move(self.position[0],self.position[1])

	def left(self):
		self.position = [self.position[0]-self.step,self.position[1]]
		self.move(self.position[0],self.position[1])

	def right(self):
		self.position = [self.position[0]+self.step,self.position[1]]
		self.move(self.position[0],self.position[1])

class AntiLogoResize(AntiLogoBase):
	step = 5
	def __init__(self, session, args = 0, size = [], position = []):
		AntiLogoBase.__init__(self, session, size, position)

	def go(self):
		self.close(self.size)

	def up(self):
		self.size = [self.size[0],self.size[1]-self.step]
		self.resize(self.size[0],self.size[1])

	def down(self):
		self.size = [self.size[0],self.size[1]+self.step]
		self.resize(self.size[0],self.size[1])

	def left(self):
		self.size= [self.size[0]-self.step,self.size[1]]
		self.resize(self.size[0],self.size[1])

	def right(self):
		self.size = [self.size[0]+self.step,self.size[1]]
		self.resize(self.size[0],self.size[1])

class AntiLogoMenu(Screen):
	def __init__(self,session,callback=None,size=None,position=None,arg=0):
		self.session = session
		self.callBack = callback
		self.size= size
		self.position = position
		ss  ="<screen position=\"200,200\" size=\"300,200\" title=\"AntiLogo menu\" >"
		ss +="<widget name=\"menu\" position=\"0,0\" size=\"300,150\" scrollbarMode=\"showOnDemand\" />"
		ss +="</screen>"
		self.skin = ss
		Screen.__init__(self,session)
		list = []
		list.append((_("exit"), self.exit))
		list.append((_("move"), self.move))
		list.append((_("resize"), self.resize))
		list.append((_("load"), self.load))
		list.append((_("save"), self.save))
		list.append((_("save as"), self.saveas))
		self["menu"] = MenuList(list)
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
						{
						"ok": self.go,
						"back": self.close,
						}, -1)

	def exit(self):
		self.callBack(None, None)
		self.close()

	def go(self):
		selection = self["menu"].getCurrent()
		selection[1]()

	def load(self):
		config = AntiLogoConfig()
		list = []
		for i in config.getPresets():
			list.append((i,i))
		self.session.openWithCallback(self.loadPreset,ChoiceBox,_("select preset to load"),list)

	def loadPreset(self,value):
		if value is not None:
			config = AntiLogoConfig()
			preset = config.getPreset(value[1])
			if preset is not False:
				self.callBack([preset["width"],preset["height"]],[preset["x"],preset["y"]])

	def presetnameEntered(self,value):
		if value is not None:
			config = AntiLogoConfig()
			config.setPreset(value,self.size,self.position)

	def save(self):
		config = AntiLogoConfig()
		list = []
		for i in config.getPresets():
			list.append((i, i))
		self.session.openWithCallback(self.savePreset, ChoiceBox,_("select preset to save"), list)

	def saveas(self):
		name = ""
		if self.session.nav.getCurrentService():
			name = self.session.nav.getCurrentService().info().getName()
		self.session.openWithCallback(self.presetnameEntered, InputBox, title = _("please enter a name"), text=name, maxSize=False, type=Input.TEXT)

	def savePreset(self, value):
		if value is not None:
			config = AntiLogoConfig()
			config.setPreset(value[1], self.size, self.position)

	def move(self):
		self.session.openWithCallback(self.moveCompleted, AntiLogoMove, size = self.size, position = self.position)

	def moveCompleted(self, position):
		self.position = position
		self.callBack(self.size, self.position)

	def resize(self):
		self.session.openWithCallback(self.resizeCompleted, AntiLogoResize, size = self.size, position = self.position)

	def resizeCompleted(self, size):
		self.size = size
		self.callBack(self.size, self.position)

class AntiLogoConfig:
	configfile = "/etc/enigma2/AntiLogo.conf"

	def __init__(self):
		self.configparser = ConfigParser()
		self.configparser.read(self.configfile)

	def setLastPreset(self,name):
		self.configparser.set(DEFAULTSECT, "lastpreset",name)
		self.writeConfig()

	def getLastPreset(self):
		last = self.configparser.get(DEFAULTSECT, "lastpreset")
		return self.getPreset(last)

	def getPresets(self):
		presets = []
		sections = self.configparser.sections()
		for section in sections:
			presets.append(section)
		return presets

	def getPreset(self,name):
		if self.configparser.has_section(name) is True:
			print "loading preset ",name
			l = {}
			l["x"] = int(self.configparser.get(name, "x"))
			l["y"] = int(self.configparser.get(name, "y"))
			l["width"] = int(self.configparser.get(name, "width"))
			l["height"] = int(self.configparser.get(name, "height"))
			self.setLastPreset(name)
			return l
		else:
			print "couldn't find preset", name
			return False

	def setPreset(self,name,size,position):
		try:
			self.configparser.add_section(name)
			self.configparser.set(name, "x", position[0])
			self.configparser.set(name, "y", position[1])
			self.configparser.set(name, "width", size[0])
			self.configparser.set(name, "height", size[1])
			self.configparser.set(DEFAULTSECT, "lastpreset",name)
			self.writeConfig()
			return True
		except DuplicateSectionError:
			self.deletePreset(name)
			self.setPreset(name, size, position)

	def deletePreset(self,name):
		self.configparser.remove_section(name)
		self.writeConfig()

	def writeConfig(self):
		fp = open(self.configfile, "w")
		self.configparser.write(fp)
		fp.close()


def main(session, **kwargs):
	session.open(AntiLogoMain)

def Plugins(**kwargs):
	return [PluginDescriptor(name = "AntiLogo" ,description = _("mask irritating logos"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main),
					PluginDescriptor(name = "AntiLogo", description = _("mask irritating logos"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main)]
