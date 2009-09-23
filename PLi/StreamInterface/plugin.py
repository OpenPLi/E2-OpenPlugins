from Plugins.Plugin import PluginDescriptor

from twisted.internet import reactor, defer
from twisted.web2 import server, channel, http
from twisted.web2 import resource, static, responsecode, http, http_headers

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
				s = s + '<a href="/channel/?ref=' + ref + '">' + name + '</a>'
			return http.Response(responsecode.OK, {'Content-type': http_headers.MimeType('text', 'html')}, stream = s)

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
			return http.Response(responsecode.OK, stream="no ref given with ref=???")

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
					s = s + '<a href="http://' + req.host + ':8001/' + ref + '" vod>' + name + '</a>'
				return http.Response(responsecode.OK, {'Content-type': http_headers.MimeType('text', 'html')}, stream = s)
		else:
			return http.Response(responsecode.OK, stream="no ref")

def startServer(session):
	list = BouquetList()
	reactor.listenTCP(40080, channel.HTTPFactory(server.Site(list)))

def autostart(reason, **kwargs):
	if "session" in kwargs:
		try:
			startServer(kwargs["session"])
		except ImportError,e:
			print "[WebIf] twisted not available, not starting web services", e

def Plugins(**kwargs):
	return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart)]
