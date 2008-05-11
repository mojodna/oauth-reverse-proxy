from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web.server import Site

# don't include SSL if it's not installed
try:
  from twisted.internet import ssl
except ImportError:
  pass

from twisted.web import proxy, server

from oauth_reverse_proxy import reverse_proxy

class OAuthReverseProxyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "oauth_reverse_proxy"
    description = "OAuth reverse HTTP proxy"
    options = reverse_proxy.Options

    def makeService(self, options):
        # TODO add error handling for missing params
        
        remoteHost = options["remote-host"]
        remotePort = options["remote-port"]
        pathPrefix = options["path-prefix"]
        proxyPort = options["port"]
        
        site = Site(reverse_proxy.OAuthReverseProxyResource(remoteHost, remotePort, pathPrefix, useSSL=options["ssl"]))
        
        if options["ssl"]:
            server = internet.SSLServer(proxyPort, site, ssl.DefaultOpenSSLContextFactory(options["ssl-private-key"], options["ssl-certificate"]))
        else:
            server = internet.TCPServer(proxyPort, site)

        return server
        
serviceMaker = OAuthReverseProxyServiceMaker()
