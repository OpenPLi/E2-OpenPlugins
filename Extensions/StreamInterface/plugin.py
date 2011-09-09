from Plugins.Plugin import PluginDescriptor

from twisted.internet import reactor
from twisted.web import resource, server 

from Components.config import config
from Components.Sources.ServiceList import ServiceList
from enigma import eServiceReference

class BouquetList(resource.Resource):
	addSlash = True
	def __init__(self):
		resource.Resource.__init__(self)

	def render(self, req):
		s = '<br/>'

		if config.usage.multibouquet.value:
			bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
		else:
			bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(self.service_types)

		fav = eServiceReference(bouquet_rootstr)
		services = ServiceList(fav, command_func = None, validate_commands = False)
		sub = services.getServicesAsList()

		if len(sub) > 0:
			self.putChild('channel', ChannelList())
			for (ref, name) in sub:
				s = s + '<p>'
				ref = ref.replace(' ', '%20').replace(':', '%3A').replace('"', '%22')
				s = s + '<a href="/channel?ref=' + ref + '">' + name + '</a>'
			req.setResponseCode(200)
			req.setHeader('Content-type', 'text/html');
			return s;

	def locateChild(self, request, segments):
		return resource.Resource.locateChild(self, request, segments)


class ChannelList(resource.Resource):
	addSlash = True
	def __init__(self):
		resource.Resource.__init__(self)

	def render(self, req):
		try:
			w1 = req.uri.split("?")[1]
			w2 = w1.split("&")
			parts = {}
			for i in w2:
					w3 = i.split("=")
					parts[w3[0]] = w3[1]
		except:
			req.setResponseCode(200);
			return "no ref given with ref=???"

		if parts.has_key("ref"):
			s = '<br/>'

			ref = parts['ref'].replace('%20', ' ').replace('%3A', ':').replace('%22', '"')
			print ref
			fav = eServiceReference(ref)
			services = ServiceList(fav, command_func = None, validate_commands = False)
			sub = services.getServicesAsList()

			if len(sub) > 0:
				for (ref, name) in sub:
					s = s + '<p>'
					s = s + '<a href="http://%s:8001/%s" vod>%s</a>'%(req.host.host,ref,name)
				req.setResponseCode(200);
				req.setHeader('Content-type', 'text/html');
				return s;
		else:
			req.setResponseCode(200);
			return "no ref";

def startServer(session):
	list = BouquetList()
	channels = ChannelList()
	res = resource.Resource()
	res.putChild("", list)
	res.putChild("channel", channels) 
	reactor.listenTCP(40080, server.Site(res))

def autostart(reason, **kwargs):
	if "session" in kwargs:
		try:
			startServer(kwargs["session"])
		except ImportError,e:
			print "[WebIf] twisted not available, not starting web services", e

def Plugins(**kwargs):
	return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart)]
