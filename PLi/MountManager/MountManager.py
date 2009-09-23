from enigma import *
from Screens.Screen import Screen
from Components.config import config, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigInteger, ConfigText, ConfigIP, NoSave, ConfigSubsection, ConfigNothing, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import *
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.Network import iNetwork
from Components.Harddisk import harddiskmanager
from Screens.Console import Console
import os

TMP_FSTAB = "/tmp/fstab"
FSTAB = "/etc/fstab"

class MountEdit(Screen, ConfigListScreen):
	skin = """
		<screen position="100,100" size="550,400" title="Mount edit" >
		<widget name="config" position="20,10" size="460,350" scrollbarMode="showOnDemand" />
		</screen>"""
	def __init__(self, session, selection):
		self.session = session
		self.skin = MountEdit.skin
		Screen.__init__(self, session)
		
		self.org_mp = selection[0]
		
		self.load_defaults()
		
		self.type = ConfigSelection(default = self.def_type, choices = ["cifs","nfs","smbfs"])
		self.server = ConfigIP(default = self.def_server)
		self.share = ConfigText(default = self.def_share, fixed_size = False)
		self.dir = ConfigSelection(default = self.def_dir, choices = ["/media/hdd","/media/net","/media/net1","/media/net2","/media/net3","/media/dm500","/media/dm600","/media/dm7000","/media/dm7020","/media/dm7025"])
		self.rsize_wsize = ConfigSelection(default = self.def_rsize_wsize, choices = ["4096","8192","16384","32786"])
		self.nfs_options = ConfigText(default = self.def_nfs_options, fixed_size = False)
		self.cifs_options = ConfigText(default = self.def_smbfs_options, fixed_size = False)
		self.smbfs_options = ConfigText(default = self.def_smbfs_options, fixed_size = False)
		self.username = ConfigText(default = self.def_username, fixed_size = False) 
		self.password = ConfigText(default = self.def_password, fixed_size = False)
		
		self.createSetup()
		
		ConfigListScreen.__init__(self, self.list, session = session)
		self.type.addNotifier(self.typeChange)
		
		self["setupActions"] = ActionMap(["SetupActions"],
		{
			"cancel": self.cancel,
			"ok": self.ok
		}, -2)
		
	def convertIP(self, ip):
		strIP = ip.split('.')
		ip = []
		for x in strIP:
			ip.append(int(x))
		return ip
		
	def load_defaults(self):
		self.def_type = "cifs"
		self.def_server = iNetwork.getAdapterAttribute("eth0", "gateway")
		if self.def_server == [0,0,0,0]:
			self.def_server = [192,168,1,1]
		self.def_dir = "/media/hdd"
		for partition in harddiskmanager.getMountedPartitions():
			print partition.mountpoint
			if self.def_dir == partition.mountpoint:
				self.def_dir = "/media/net"
				break
		self.def_share = "harddisk"
		self.def_nfs_options = "rw,nolock,soft"
		self.def_rsize_wsize = "16384"
		self.def_cifs_options = ""
		self.def_smbfs_options = ""
		self.def_username = ""
		self.def_password = ""

		try:
			file = open( TMP_FSTAB, "r" )
		except IOError:
			return
		while True:
			line = file.readline().strip()
			if line == "":
				break
			x = line.split()
			if x[1] == self.org_mp:
				self.def_type = x[2]
				if self.def_type == "nfs":
					self.def_nfs_options = ""
					options = x[3].split(',')
					for option in options:
						if not "rsize" in option and not "wsize" in option:
							if self.def_nfs_options is not "":
								self.def_nfs_options += ","
							self.def_nfs_options += option
						else:
							v = option.split('=')
							self.def_rsize_wsize = v[1]
					self.def_share = "media/hdd"
					s = x[0].split(':')
					if len(s) >= 2:
						self.def_server = self.convertIP(s[0])
						self.def_share = "/".join(s[1:])
				if self.def_type == "cifs":
					self.def_cifs_options = ""
					options = x[3].split(',')
					for option in options:
						if not "rsize" in option and not "wsize" in option:
							if self.def_cifs_options is not "":
								self.def_cifs_options += ","
							self.def_cifs_options += option
						else:
							v = option.split('=')
							self.def_rsize_wsize = v[1]
					self.def_share = "harddisk"
					s = x[0].split('/')
					if len(s) >= 4:
						self.def_server = self.convertIP(s[2])
						self.def_share = "/".join(s[3:])
					t1 = x[3].split(',')
					for i in range(len(t1)):
						t2 = t1[i].split('=')
						if len(t2) == 2:
							if t2[0] == "username":
								self.def_username = t2[1]
							if t2[0] == "password":
								self.def_password = t2[1]
				if self.def_type == "smbfs":
					self.def_smbfs_options = x[3]
					self.def_share = "harddisk"
					s = x[0].split('/')
					if len(s) >= 4:
						self.def_server = self.convertIP(s[2])
						self.def_share = "/".join(s[3:])
					t1 = x[3].split(',')
					for i in range(len(t1)):
						t2 = t1[i].split('=')
						if len(t2) == 2:
							if t2[0] == "username":
								self.def_username = t2[1]
							if t2[0] == "password":
								self.def_password = t2[1]
				self.def_dir = x[1]
		file.close()

	def typeChange(self, value):
		self.createSetup()
		self["config"].l.setList(self.list)

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Mount type"), self.type))
		self.list.append(getConfigListEntry(_("Server IP"), self.server))
		self.list.append(getConfigListEntry(_("Server share"), self.share))
		self.list.append(getConfigListEntry(_("Local directory"), self.dir))
		if self.type.value == "nfs":
			self.list.append(getConfigListEntry(_("rsize/wsize"), self.rsize_wsize))
			self.list.append(getConfigListEntry(_("Mount options"), self.nfs_options))
		if self.type.value == "cifs":
			self.list.append(getConfigListEntry(_("rsize/wsize"), self.rsize_wsize))
			self.list.append(getConfigListEntry(_("Mount options"), self.cifs_options))
			self.list.append(getConfigListEntry(_("Username"), self.username))
			self.list.append(getConfigListEntry(_("Password"), self.password))
		if self.type.value == "smbfs":
			self.list.append(getConfigListEntry(_("Mount options"), self.smbfs_options))
			self.list.append(getConfigListEntry(_("Username"), self.username))
			self.list.append(getConfigListEntry(_("Password"), self.password))

	def ok(self):
		changed = 0
		try:
			in_file = open( TMP_FSTAB, "r" )
		except IOError:
			self.close()
			return
		try:
			out_file = open( TMP_FSTAB + ".new", "w" )
		except IOError:
			self.close()
			return
		
		if self.org_mp == "new":
			self.org_mp = self.dir.value

		self.username.value = self.username.value.strip()
		self.password.value = self.password.value.strip()
		self.share.value = self.share.value.strip()

		if self.type.value == "nfs":
			f1 = "%d.%d.%d.%d" % tuple(self.server.value) + ":" + self.share.value
			f4 = "rsize=" + self.rsize_wsize.value + ",wsize=" + self.rsize_wsize.value
			if self.nfs_options.value != "":
				f4 += "," + self.nfs_options.value
		elif self.type.value == "cifs":
			f1 = "//%d.%d.%d.%d/" % tuple(self.server.value) + self.share.value
			f4 = "username=" + self.username.value + ",password=" + self.password.value
			f4 += ",rsize=" + self.rsize_wsize.value + ",wsize=" + self.rsize_wsize.value
			if self.cifs_options.value != "":
				f4 += "," + self.cifs_options.value
		elif self.type.value == "smbfs":
			f1 = "//%d.%d.%d.%d/" % tuple(self.server.value) + self.share.value
			f4 = "username=" + self.username.value + ",password=" + self.password.value
			if self.smbfs_options.value != "":
				f4 += "," + self.smbfs_options.value

		while True:
			line = in_file.readline().strip()
			if line == "":
				break
			x = line.split()
			if x[1] == self.org_mp and x[2] in ("nfs","cifs","smbfs") :
				out_file.write( "%-30s %-15s %-5s %-15s 1 0\n" % (f1, self.dir.value, self.type.value, f4) )
				changed = 1
			else:
				out_file.write( line + "\n" )
		in_file.close()
		if not changed:
			out_file.write( "%-30s %-15s %-5s %-15s 1 0\n" % (f1, self.dir.value, self.type.value, f4) )
		out_file.close()
		os.rename ( TMP_FSTAB + ".new", TMP_FSTAB )

		#create the mount point, if it doesn't exist yet
		try:
			os.makedirs(self.dir.value)
		except OSError:
			pass
		self.close()
		
	def cancel(self):
		self.close()
		
class MountManager(Screen):
	skin = """
	<screen name="MountManager" position="140,148" size="420,280" title="Mount manager">
		<ePixmap pixmap="skin_default/buttons/green.png" position="0,0" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="140,0" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="280,0" zPosition="0" size="140,40" alphatest="on" />
		<widget name="green" position="0,0" size="140,40" zPosition="1" halign="center" valign="center" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="yellow" position="140,0" size="140,40" zPosition="1" halign="center" valign="center" font="Regular;20" transparent="1" backgroundColor="yellow" />
		<widget name="blue" position="280,0" size="140,40" zPosition="1" halign="center" valign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
		<widget name="entries" position="10,50" size="410,175" scrollbarMode="showOnDemand" />
	</screen>"""

	def __init__(self, session):
		self.skin = MountManager.skin
		Screen.__init__(self, session)

		os.system ( "cp " + FSTAB + " " + TMP_FSTAB)
		self["yellow"] = Button(_("Delete"))
		self["blue"] = Button(_("Add"))
		self["green"] = Button(_("Save"))
		
		self.list = []
		self["entries"] = ConfigList(self.list)
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"left": self.keyLeft,
			"right": self.keyRight,
			"ok": self.ok,
			"cancel": self.cancel,
			"green": self.save,
			"blue": self.add,
			"yellow": self.remove
		}, -2)
		
		self.createSetup()
		
	def keyLeft(self):
		self["entries"].handleKey(KEY_LEFT)
	
	def keyRight(self):
		self["entries"].handleKey(KEY_RIGHT)
		
	def createSetup(self):
		#self.mountlist = []
		self.list = []
		try:
			file = open( TMP_FSTAB, "r" )
		except IOError:
			return
		while True:
			line = file.readline().strip()
			if line == "":
				break
			x = line.split()
			if x[2] in ["nfs","cifs","smbfs"]:
				self.list.append(getConfigListEntry (x[1],ConfigNothing() ))
				#self.mountlist.append(x[1])
		file.close()

		#for i in range(len(self.mountlist)):
			#self.list.append(getConfigListEntry (self.mountlist[i],ConfigNothing() ))
			
		self["entries"].l.setList(self.list)
			
	def ok(self):
		selection = self["entries"].getCurrent()
		if selection != None:
			self.session.openWithCallback(self.createSetup, MountEdit, selection)
	
	def save(self):
		os.system( "cp " + TMP_FSTAB + " " + FSTAB)
		#TODO: we do not have to use grep, only modprobe the filesystems which were just added by the user
		os.system("grep smbfs " + FSTAB + " && modprobe smbfs")
		os.system("grep cifs " + FSTAB + " && modprobe cifs")
		self.session.open(Console, title = "Mounting...", cmdlist = ["mount -a -t smbfs,cifs,nfs"], finishedCallback = self.close, closeOnSuccess = True)
		self.close()
	
	def cancel(self):
		self.close()
	
	def add(self):
		self.session.openWithCallback(self.createSetup, MountEdit, ["new"])
	
	def remove(self):
		if self["entries"].getCurrent() == None:
			return
		try:
			in_file = open( TMP_FSTAB, "r" )
		except IOError:
			self.close()
			return
		try:
			out_file = open( TMP_FSTAB + ".new", "w" )
		except IOError:
			self.close()
			return
		
		while True:
			line = in_file.readline().strip()
			if line == "":
				break
			x = line.split()
			if not x[2] in ("nfs","cifs","smbfs") or not x[1] == self["entries"].getCurrent()[0]:
				out_file.write( line + "\n" )
		in_file.close()
		out_file.close()
		os.rename ( TMP_FSTAB + ".new", TMP_FSTAB )
			
		self.createSetup()
