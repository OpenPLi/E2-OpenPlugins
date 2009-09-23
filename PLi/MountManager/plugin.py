from MountManager import MountManager
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
	session.open(MountManager)

def menu(menuid, **kwargs):
	if menuid == "network":
		return [(_("Mount manager..."), main, "mount_manager", 45)]
	return []

def Plugins(**kwargs):
	return PluginDescriptor(name = "MountManager", description = "Lets you configure network mounts", where = PluginDescriptor.WHERE_MENU, fnc = menu)