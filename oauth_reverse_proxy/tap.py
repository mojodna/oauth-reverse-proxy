import sys
from twisted.application import internet, service
from twisted.web.server import Site
import oauth_reverse_proxy

# don't include SSL if it's not installed
try:
  from twisted.internet import ssl
except ImportError:
  pass

class Options(oauth_proxy.Options):
	pass


def makeService(self, options):
    s = service.MultiService()

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
        
    server.setServiceParent(s)
    
    return s
