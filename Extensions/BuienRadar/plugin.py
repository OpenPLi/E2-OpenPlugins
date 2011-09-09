import time
import os
import enigma
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, fileExists, SCOPE_MEDIA
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.AVSwitch import AVSwitch

from twisted.web.client import downloadPage

def getScale():
	return AVSwitch().getFramebufferScale()

class Radar(Screen):
	def __init__(self, session):
		size = enigma.getDesktop(0).size()
		size_w = size.width()
		size_h = size.height()
		space = 30
		self.skin = '<screen position="0,0" size="' + str(size_w) + "," + str(size_h) + '" flags="wfNoBorder" > \
				<widget source="info" render="Label" position="' + str(space+45) + "," + str(space) + '" size="' + str(size_w-(space*2)-50) + ',25" font="Regular;20" borderWidth="1" borderColor="#000000" halign="left" zPosition="2" noWrap="1" transparent="1" /> \
				<widget name="pic" position="' + str(space) + "," + str(space) + '" size="' + str(size_w-(space*2)) + "," + str(size_h-(space*2)) +'" zPosition="1" />\
			</screen>'
		Screen.__init__(self, session)

		self["info"] = StaticText()	
		self["pic"] = Pixmap()
		self.picload = enigma.ePicLoad()
		self.picload.PictureData.get().append(self.showPic)
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"cancel": self.quit,
			"ok": self.quit,
		}, -1)
		self.startDownload()
		self.timer = enigma.eTimer()
		self.timer.callback.append(self.startDownload)

	def startDownload(self):
		self["info"].setText(_("Downloading..."))
		try:
			# experimenters can put their URL here
			url = open('/tmp/buienradar.url', 'rb').readline().strip()
		except:
			# This looks okay though:
			# url = "http://buienradar.mobi/image.gif?k=1&l=0"
			url = "http://www.buienradar.nl/images.aspx?jaar=-3"
		print "[BR] URL='%s'" % url
	        downloadPage(url, '/tmp/radar.gif').addCallbacks(self.afterDownload, self.downloadFail)
		
	def downloadFail(self, failure):
		print "[BR] download failed:", failure
		self["info"].setText(_("Error") + ": " + str(failure))
		self.quit()
		
	def afterDownload(self, result=None):
		print "[BR] download ready"
		self["info"].setText(_("please wait, loading picture..."))	
		sc = getScale()
		par = [self["pic"].instance.size().width(), self["pic"].instance.size().height(), sc[0], sc[1], False, 0, "#FF000000"]
		self.picload.setPara(par)
		self.picload.startDecode('/tmp/radar.gif')
		# refresh image every minute
		self.timer.start(60000, True)
		
	def showPic(self, picInfo=None):
		print "[BR] show picture"
		self["info"].setText("")	
		ptr = self.picload.getData()
		if ptr != None:
			self["pic"].instance.setPixmap(ptr.__deref__())
			self["pic"].show()
		self.cleanTemp()
	
	def cleanTemp(self):
		try:
			os.unlink('/tmp/radar.gif')
		except:
			pass
	
	def quit(self):
		self.cleanTemp()
		self.timer.stop()
		del self.picload
		self.close()

def main(session, **kwargs):
	session.open(Radar)


def Plugins(**kwargs):
	return \
		[PluginDescriptor(name="BuienRadar", description=_("Buienradar demootje"), icon="plugin.png", where = PluginDescriptor.WHERE_PLUGINMENU, needsRestart = False, fnc=main)]
