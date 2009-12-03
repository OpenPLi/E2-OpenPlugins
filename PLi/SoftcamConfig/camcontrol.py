import os

class CamControl:
	'''CAM convention  is that a softlink named /etc/rcS.d/S40... points
	to the start/stop script. In order to be nice to update-rc scripts,
	the link name will be appended with the currently selected softcam's name,
	so that CCcam has a link /etc/rcS.d/S40emu_CCcam -> /etc/init.d/emu_CCcam'''
	def __init__(self, name):
		self.name = name
		self.link = '/etc/rcS.d/S40' + name
		if not os.path.exists(self.link):
			lname = 'S40' + name
			for l in os.listdir('/etc/rcS.d'):
				if l.startswith(lname):
					self.link = '/etc/rcS.d/' + l

	def getList(self):
		result = []
		prefix = self.name + '_'
		for f in os.listdir("/etc/init.d"):
			if f.startswith(prefix):
				result.append(f[len(prefix):])
		return result

	def current(self):
		try:
			l = os.readlink(self.link)
			return os.path.split(l)[1].split('_')[1]
		except:
			pass
		return None

	def command(self, cmd):
		if os.path.exists(self.link):
			print "Executing", self.link + ' ' + cmd
			os.system(self.link + ' ' + cmd)

	def select(self, which):
		print "Selecting CAM:", which
		try:
			os.unlink(self.link)
		except:
			pass
		if not which:
			return
		dst = '../init.d/' + self.name + '_' + which
		if not os.path.exists('/etc/init.d/' + self.name + '_' + which):
			return # probably "None" was selected here
		try:
			newlink = '/etc/rcS.d/S40' + self.name + '_' + which
			os.symlink(dst, newlink);
		except:
			print "Failed to create symlink for softcam:", dst
			import sys
			print sys.exc_info()[:2]
