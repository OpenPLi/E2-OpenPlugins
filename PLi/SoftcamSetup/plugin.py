from softcamsetup import PLiSoftcamSetup
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
	session.open(PLiSoftcamSetup)

def menu(menuid, **kwargs):
	if menuid == "cam":
		return [(_("Softcam setup..."), main, "softcam_setup", 45)]
	return []

def Plugins(**kwargs):
	return PluginDescriptor(name = "Softcam setup", description = "Lets you configure your softcams", where = PluginDescriptor.WHERE_MENU, fnc = menu)