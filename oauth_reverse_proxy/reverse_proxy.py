"""
Implementation of an OAuth reverse HTTP proxy.

Seth Fitzsimmons <seth@mojodna.net>
"""

import cgi
from oauth import oauth
from twisted.internet import reactor
from twisted.python import usage
from twisted.web import proxy
import urlparse
from urllib import quote as urlquote

class Options(usage.Options):
	synopsis = "Usage: oauth_reverse_proxy --remote-host <remote host> [--remote-port <remote port>] [--path-prefix <path prefix>] [-p <proxy port>] [--ssl] [--ssl-private-key <private key>] [--ssl-certificate <certificate>]"
	longdesc = "An OAuth reverse HTTP proxy server.."
	optParameters = [
		['path-prefix',		None, '',	"Path prefix"],
		['port',			'p',  8080, "Proxy port", int],
		['remote-host',		None, None, "Remote host"],
		['remote-port',		None, 80,	"Remote port", int],
		['ssl-certificate', None, None, "SSL certificate"],
		['ssl-private-key', None, None, "SSL private key"],
	]

	optFlags = [['ssl', 's']]



class OAuthReverseProxyResource(proxy.ReverseProxyResource):
	def __init__(self, host, port, path, reactor=reactor, useSSL=False, oauthServer=oauth.OAuthServer()):
		self.oauthServer = oauthServer;
		if useSSL:
			self.scheme = "https"
		else:
			self.scheme = "http"
		proxy.ReverseProxyResource.__init__(self, host, port, path, reactor)


	def getChild(self, path, request):
		return OAuthReverseProxyResource(
			self.host, self.port, self.path + '/' + urlquote(path, safe=""), oauthServer=self.oauthServer)


	def render(self, request):
		args = request.args # POST and GET params

		# get OAuth headers
		if request.received_headers.has_key("authorization"):
			if request.received_headers["authorization"].find('OAuth') >= 0:
				# merge parsed params from Authorization header
				args.update(OAuthRequest._split_header(request.received_headers["authorization"]))

				# remove OAuth headers from the request being passed on
				del request.received_headers["authorization"]


		# flatten parameter values
		# BUG this drops repeated query parameters (the OAuth lib expects a flattened list and is affected by the same bug)
		args = dict([(k,v[-1]) for k,v in args.items()])


		# construct an OAuthRequest
		uri = urlparse.urlunsplit((self.scheme, request.received_headers["host"], request.path, None, None))
		oauthRequest = oauth.OAuthRequest(request.method, request.path, args)


		# Attempt to validate the signature
		try:
			consumer, token, parameters = self.oauthServer.verify_request(oauthRequest)

			els = []
			for k, v in parameters.items():
				els.append("=".join((k, v)))

			request.uri = urlparse.urlunsplit((scheme, None, request.path, "&".join(els), None))

			# TODO figure out how to filter/rewrite the POST body for oauth params
			
			# TODO add consumer key and access token to proxied request, either as a query param, custom HTTP header, or as Basic Auth credentials

			# fall through to normal reverse proxying behavior with the rewritten request
			response = proxy.ReverseProxyResource.render(self, request)
		except oauth.OAuthError:
			# render an error message
			# TODO use error message encapsulated in raised OAuthError
			# TODO return NOT_DONE_YET in order to write content-type headers
			response = "Invalid signature\n"

		return response
