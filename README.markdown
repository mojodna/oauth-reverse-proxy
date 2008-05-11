# OAuth Reverse Proxy

I am a reverse HTTP proxy, suitable for running in front of web services that you wish to protect using [OAuth](http://oauth.net/ "OAuth").

This will not run out of the box, as a suitable implementation of `OAuthDataStore` must exist and be wired into the `OAuthServer` passed to `OAuthReverseProxyResource`.


## Running

Provided that "." is in your `PYTHONPATH`, you should be able to run the proxy with `twistd`:

    twistd -n oauth_reverse_proxy --remote-host <remote host> [--remote-port <remote port>] [--path-prefix <path prefix>] [-p <proxy port>] [--ssl] [--ssl-private-key <private key>] [--ssl-certificate <certificate>]


## Running as a daemon

You may run the proxy with `twistd` directly (omitting the _-n_ argument) or you may generate a pre-configured tap, which can then be packaged and distributed.  To generate a tap:

    mktap oauth_reverse_proxy --remote-host <remote host> [--remote-port <remote port>] [--path-prefix <path prefix>] [-p <proxy port>] [--ssl] [--ssl-private-key <private key>] [--ssl-certificate <certificate>]

To run the tap (using the settings that were provided when creating it):

    twistd -f oauth_reverse_proxy.tap
