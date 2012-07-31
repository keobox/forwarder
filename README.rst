:Abstract: this script is a TCP proxy, or stated in another way a port forwarder with filtering capability: is possible to launch it passing a comma separated list of IP addresses or host names.

This script is the python version of a script written in perl for setting up TCP proxy servers with filtering capability.

Please refere to this blog post_ for detail.

.. _post: http://www.catonmat.net/blog/linux-socks5-proxy/

The implementation is based on Activestate's 483732_ recipe with a little enhancement: the "-a" option can be used to provide the list of hosts the port forwarder can accept connection from.

.. _483732: http://code.activestate.com/recipes/483732-asynchronous-port-forwarding/

I use this script as a frontend for simple SOCKS proxy servers based on SSH like the ones described in the post_ above.

Example of use: if I have a shell opened on *myproxyhost* I can setup a SOCKS proxy listening on localhost:10080 with this command:

ssh -D localhost

And then activate the port forwarding script as frontend to this SOCKS proxy server:

python -l *myproxyhost* -p 1080 -r localhost -P 10080 -a *x.x.x.x,y.y.y.y*

*x.x.x.x* and *y.y.y.y* are IPv4 addresses in this case.

The result is that *myproxyhost:1080* is a SOCKS proxy server that accepts connection only from the IP addresses specified in the "-a" option.
