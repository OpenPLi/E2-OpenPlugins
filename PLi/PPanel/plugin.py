from ppanel import ToplevelPPanel
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
	session.open(ToplevelPPanel)

def Plugins(**kwargs):
	return PluginDescriptor(name = "PPanels", description = "Lets you execute your PPanels", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main)