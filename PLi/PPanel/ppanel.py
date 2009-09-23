from xml.dom.minidom import parse, getDOMImplementation
#import gettext
#_ = gettext.Catalog("PLiSetup",'').gettext

from os import system,path,listdir

from Components.GUIComponent import *
from Components.HTMLComponent import *
from Components.Button import Button
from Components.MenuList import MenuList
from Components.Label import Label
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.ProgressBar import ProgressBar
from url import *

from socket import gethostbyname

from enigma import eConsoleAppContainer

class PPanelEntry(Screen):
	def __init__(self, session, name, node):
		Screen.__init__(self, session)
		self.name = name
		self.node = node
		self.runBefore = ''
		self.runAfter = ''
		self.runAfterOut = ''
		if self.node:
			self.quit = node.getAttribute("quit")
			self.runBefore = node.getAttribute("runBefore")
			self.runAfter = node.getAttribute("runAfter")
			self.runAfterOut = node.getAttribute("runAfterOut")

		self.onShown.append(self.setWindowTitle)
		if self.runAfter is not '' or self.runAfterOut is not '':
			self.onHide.append(self.runAfterCommands)

		if self.runBefore is not '':
			system(self.runBefore)

	def setWindowTitle(self):
		self.setTitle(self.name)

	def getName(self):
		return self.name

	def runAfterCommands(self):
		if self.runAfter is not '':
			sytem(self.runAfter)
		if self.runAfterOut is not '':
			self.session.open(Execute, self.name, None, self.runAfterOut)

class PPanel(PPanelEntry):
	skin = """
	<screen position="c-250,c-200" size="500,400">
		<widget name="nodelist" position="5,10" size="e-10,e-45" />
		<widget name="helptext" position="5,e-35" size="e-10,30" valign="center" halign="left" font="Regular;20" />
	</screen>"""

	def __init__(self, session, name = 'PPanel', node = None, filename = '', deletenode = None):
		self.skin = PPanel.skin
		PPanelEntry.__init__(self, session, name, node)
		self.nodelist = []

		self["nodelist"] = MenuList(self.nodelist)
		self["helptext"] = Label()

		self.deletenode = deletenode
		self.node = node
		self.filename = filename

		self.onClose.append(self.deletePPanel)
		self.onShown.append(self.nodeSelectionChanged)
		self["nodelist"].onSelectionChanged.append(self.nodeSelectionChanged)

		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.okbuttonClick,
			"cancel": self.close,
		}, -1)

		self.createPPanel()

	def nodeSelectionChanged(self):
		selection = self["nodelist"].getCurrent()
		if selection == None or len(selection) < 3:
			return
		helptext = selection[2]
		self["helptext"].setText(helptext)

	def okbuttonClick(self):
		selection = self["nodelist"].getCurrent()
		if selection == None or len(selection) < 3:
			return
		e = selection[1]
		if e == None:
			return

		self.runBeforeOut = e.getAttribute("runBeforeOut")

		confirmation = e.getAttribute("confirmation")
		if confirmation is not '':
			if confirmation == "true":
				self.session.openWithCallback(self.confirmationResult, MessageBox, _("Are you sure?"))
			else:
				self.session.openWithCallback(self.confirmationResult, MessageBox, str(confirmation))
		else:
			self.openSelectedNode()

	def openSelectedNode(self):
		selection = self["nodelist"].getCurrent()
		if selection == None or len(selection) < 3:
			return
		e = selection[1]
		if e == None:
			return
		name = selection[0]

		if self.runBeforeOut is not '':
			self.session.openWithCallback(self.runBeforeFinished, Execute, name, None, self.runBeforeOut)
			#ensure we won't run the command again, after output is closed
			self.runBeforeOut = ''
			return

		if e.localName == "ppanel":
			target = e.getAttribute("target")
			self.session.open(PPanel, name, e, target)
		elif e.localName == "category":
			self.session.open(PPanel, name, e)
		elif e.localName == "file":
			self.session.open(File, name, e)
		elif e.localName == "tarball":
			self.session.open(Tarball, name, e)
		elif e.localName == "execute":
			target = e.getAttribute("target")
			self.session.open(Execute, name, e, target)
		#elif e.localName == "picture":
		#	self.session.open(Picture, name, e)
		#elif e.localName == "remove":
		#	self.session.open(Remove, name, e)
		#elif e.localName == "media":
		#	self.session.open(Media, name, e)

	def runBeforeFinished(self):
		self.openSelectedNode()

	def confirmationResult(self, result):
		if result:
			self.openSelectedNode()

	def createPPanel(self):
		self.nodelist = []
		node = self.node
		if self.filename is not '':
			#instead of the node that we got in our constructor, we need to parse a new node from a file
			try:
				node = parse(self.filename)
			except:
				print "Illegal xml file"
				print self.filename
				return
			#we created our own node, we have to remember and delete it when we're closed
			self.deletenode = node
			node = node.documentElement

		for e in node.childNodes:
			name = ''
			helptext = ''
			if e.nodeType == e.ELEMENT_NODE:
				#only ELEMENT_NODE has attributes
				if e.hasAttribute("condition"):
					condition = e.getAttribute("condition")
					result = system(condition)>>8
					if result:
						continue

				if e.localName == "separator":
					#note the trailing comma, we create a one element tuple here (so the listbox considers this a nonselectable entry)
					self.nodelist.append((str(("-"*40)),))
					continue
				elif e.localName == "update":
					#TODO
					continue

				name = e.getAttribute("name")
				if name == '':
					continue

				if e.localName == "comment":
					#note the trailing comma, we create a one element tuple here (so the listbox considers this a nonselectable entry)
					self.nodelist.append((str(name),))
					continue

				helptext = e.getAttribute("helptext")

				self.nodelist.append((str(name), e, str(helptext)))

		self["nodelist"].setList(self.nodelist)

	def deletePPanel(self):
		if self.deletenode:
			self.deletenode.unlink()
			del self.deletenode
			self.deletenode = None

class File(PPanelEntry):
	skin = """
	<screen position="c-250,c-50" size="500,100">
		<widget name="progress" position="5,10" size="e-10,50" />
	</screen>"""

	def __init__(self, session, name, node):
		self.skin = File.skin
		PPanelEntry.__init__(self, session, name, node)

		self["progress"] = ProgressBar()

		self["progress"].setRange((0, 100))
		self["progress"].setValue(0)

		self.onLayoutFinish.append(self.startDownload)

		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"cancel": self.abort,
		}, -1)

		self.url = geturl(str(self.node.getAttribute("url")))
		self.target = self.node.getAttribute("target")
		self.connection = None

	def startDownload(self):
		from twisted.internet import reactor
		from twisted.internet.protocol import ClientCreator
		from twisted.web2 import http_headers, stream
		from twisted.web2.client.http import ClientRequest, HTTPClientProtocol

		port = 80
		host = self.url[1]

		if "port" in self.url:
			port = self.url.port
		if "hostname" in self.url:
			host = self.url.hostname

		try:
			ip = gethostbyname(host)
		except:
			self.close()
			return

		self.file = None
		self.progress = 0
		self.contentlength = 0

		def gotData(data):
			self.progress = self.progress + len(data)
			if self.contentlength:
				self["progress"].setValue(self.progress * 100 / self.contentlength)
			self.file.write(data)

		def responseCompleted(_):
			self.file.close()
			self.close()
			return _

		def gotResponse(response):
			self.progress = 0
			if response.stream.length is not None:
				self.contentlength = response.stream.length
			else:
				print "Hmmm. twisted still doesn't parse the content-length tag..."
			self["progress"].setValue(0)
			self.file = file(self.target, "w")
			stream.readStream(response.stream, gotData).addBoth(responseCompleted)

		def sendRequest(proto):
			proto.submitRequest(ClientRequest("GET", self.url[2], {'Host':host}, None)).addCallback(gotResponse)

		self.connection = ClientCreator(reactor, HTTPClientProtocol).connectTCP(ip, port)
		self.connection.addCallback(sendRequest)

	def abort(self):
		if self.connection is not None:
			#TODO disconnect somehow
			#self.connection.disconnect()
			self.connection = None
		self.close()

class Tarball(PPanelEntry):
	skin = """
	<screen position="c-250,c-50" size="500,100">
		<widget name="progress" position="5,10" size="e-10,50" />
	</screen>"""

	def __init__(self, session, name, node):
		self.skin = File.skin
		PPanelEntry.__init__(self, session, name, node)

		self["progress"] = ProgressBar()

		self["progress"].setRange((0, 100))
		self["progress"].setValue(0)

		self.onLayoutFinish.append(self.startDownload)

		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"cancel": self.abort,
		}, -1)

		self.url = geturl(str(self.node.getAttribute("url")))
		self.target = self.node.getAttribute("target")
		self.connection = None

	def startDownload(self):
		from twisted.internet import reactor
		from twisted.internet.protocol import ClientCreator
		from twisted.web2 import http_headers, stream
		from twisted.web2.client.http import ClientRequest, HTTPClientProtocol

		port = 80
		host = self.url[1]

		if "port" in self.url:
			port = self.url.port
		if "hostname" in self.url:
			host = self.url.hostname

		try:
			ip = gethostbyname(host)
		except:
			self.close()
			return

		self.file = None
		self.progress = 0
		self.contentlength = 0

		def gotData(data):
			self.progress = self.progress + len(data)
			if self.contentlength:
				self["progress"].setValue(self.progress * 100 / self.contentlength)
			self.file.write(data)

		def responseCompleted(_):
			self.file.close()
			system("tar -zxvf /tmp/tarball.tar.gz -C " + self.target)
			system("rm /tmp/tarball.tar.gz")
			self.close()
			return _

		def gotResponse(response):
			self.progress = 0
			if response.stream.length is not None:
				self.contentlength = response.stream.length
			else:
				print "Hmmm. twisted still doesn't parse the content-length tag..."
			self["progress"].setValue(0)
			self.file = file("/tmp/tarball.tar.gz", "w")
			stream.readStream(response.stream, gotData).addBoth(responseCompleted)

		def sendRequest(proto):
			proto.submitRequest(ClientRequest("GET", self.url[2], {'Host':host}, None)).addCallback(gotResponse)

		self.connection = ClientCreator(reactor, HTTPClientProtocol).connectTCP(ip, port)
		self.connection.addCallback(sendRequest)

	def abort(self):
		if self.connection is not None:
			#TODO disconnect somehow
			#self.connection.disconnect()
			self.connection = None
		self.close()

class Execute(PPanelEntry):
	skin = """
	<screen position="c-250,c-200" size="500,400">
		<widget name="linelist" font="Fixed;16" position="5,5" size="e-10,e-55" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="5,e-45" zPosition="1" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="e-145,e-45" zPosition="1" size="140,40" alphatest="on" />
		<widget name="key_yellow" position="5,e-45" size="140,40" zPosition="2" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="yellow" />
		<widget name="key_blue" position="e-145,e-45" size="140,40" zPosition="2" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
	</screen>"""

	def __init__(self, session, name, node, command):
		self.skin = Execute.skin
		PPanelEntry.__init__(self, session, name, node)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"yellow": self.left,
			"blue": self.right
		}, -1)

		self["key_yellow"] = Button("<<")
		self["key_blue"] = Button(">>")

		self.data = ''
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)

		self.offset = 0
		self.maxoffset = 0

		self["linelist"] = MenuList(list=[], enableWrapAround=True)

		if self.container.execute(str(command)):
			self.appClosed(-1)

	def appClosed(self, retval):
		print "appClosed"
		if retval:
			self.data += '\nexecute error %d' % retval
		self.setList()

	def dataAvail(self, str):
		print "dataAvail: " + str
		self.data += str

	def setList(self):
		if self["linelist"] is not None:
			lines = self.data.split('\n')
			list = []
			for line in lines:
				if self.offset > 0:
					list.append(line[self.offset:len(line)])
				else:
					list.append(line)
				if len(line) > self.maxoffset:
					self.maxoffset = len(line)
			self["linelist"].setList(list)

	def left(self):
		if self.offset > 0:
			self.offset = self.offset - 20
			self.setList()

	def right(self):
		if self.offset < self.maxoffset - 40:
			self.offset = self.offset + 20
			self.setList()

class Picture(PPanelEntry):
	def __init__(self, session, name, node):
		PPanelEntry.__init__(self, session, name, node)

class Remove(PPanelEntry):
	def __init__(self, session, name, node):
		PPanelEntry.__init__(self, session, name, node)

class Media(PPanelEntry):
	def __init__(self, name, node):
		PPanelEntry.__init__(self, session, name, node)


class ToplevelPPanel(PPanel):
	def __init__(self, session):
		ppaneldir = "/etc/ppanels/"
		impl = getDOMImplementation()
		newdoc = impl.createDocument(None, "directory", None)
		attr = newdoc.createAttribute("name")
		attr.nodeValue = "Installed PPanels"
		newdoc.documentElement.setAttributeNode(attr)
		for ppanelfile in listdir(ppaneldir):
			fullname = path.join(ppaneldir, ppanelfile)
			if path.isfile(fullname):
				if len(ppanelfile) > 4:
					if ppanelfile[len(ppanelfile) - 4:len(ppanelfile)] == ".xml":
						try:
							node = parse(fullname)
							if node.documentElement:
								name = node.documentElement.getAttribute("name")
								if name is not '':
									ppanel = newdoc.createElement("ppanel")
									attr = newdoc.createAttribute("name")
									attr.nodeValue = name
									ppanel.setAttributeNode(attr)
									attr = newdoc.createAttribute("target")
									attr.nodeValue = fullname
									ppanel.setAttributeNode(attr)
									newdoc.documentElement.appendChild(ppanel)
							del node
						except:
							print "Illegal xml file"
		PPanel.__init__(self, session = session, node = newdoc.documentElement, deletenode = newdoc)

class PLiPPanel:
	def __init__(self):
		self.addExtension((self.getPPanelsName, self.openPPanels, lambda: True))

	def getPPanelsName(self):
		return _("Show PPanels")

	def openPPanels(self):
		print "open ppanels..."
		self.session.open(ToplevelPPanel)
