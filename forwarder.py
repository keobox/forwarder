
"Port forwarding based on activestate recipe 483732."

import asyncore
import socket

class forwarder(asyncore.dispatcher):
    "The 'accept' channel."

    def __init__(self, ip, port, remoteip, remoteport, allowed_addrs, backlog=5):
        "Constructor."
        asyncore.dispatcher.__init__(self)
        self.remoteip = remoteip
        self.remoteport = remoteport
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((ip, port))
        self.listen(backlog)
        self.allowed_addrs = allowed_addrs

    def handle_accept(self):
        "Accept handler."
        conn, addr = self.accept()
        # print '--- Connect --- '
        # filter by IP address 0.0.0.0 allows all
        if addr[0] in self.allowed_addrs or ('0.0.0.0' in self.allowed_addrs):
            # print "Accepting", addr[0]
            sender(receiver(conn), self.remoteip, self.remoteport)


class receiver(asyncore.dispatcher):
    "Local channel."

    def __init__(self, conn):
        "Constructor."
        asyncore.dispatcher.__init__(self, conn)
        self.from_remote_buffer=''
        self.to_remote_buffer=''
        self.sender = None

    def handle_connect(self):
        "Connect, do nothing since is a server side."

    def handle_read(self):
        "Read from local."
        read = self.recv(4096)
        # print '%04i -->'%len(read)
        self.from_remote_buffer += read

    def writable(self):
        "Check if there's something to forward."
        return (len(self.to_remote_buffer) > 0)

    def handle_write(self):
        "Forward to remote."
        sent = self.send(self.to_remote_buffer)
        # print '%04i <--'%sent
        self.to_remote_buffer = self.to_remote_buffer[sent:]

    def handle_close(self):
        "Close handler."
        self.close()
        if self.sender:
            self.sender.close()

class sender(asyncore.dispatcher):
    "Remote channel."

    def __init__(self, receiver, remoteaddr, remoteport):
        "Constructor."
        asyncore.dispatcher.__init__(self)
        self.receiver = receiver
        receiver.sender = self
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((remoteaddr, remoteport))

    def handle_connect(self):
        "Do nothing on connect."

    def handle_read(self):
        "Read from remote."
        read = self.recv(4096)
        # print '<-- %04i'%len(read)
        self.receiver.to_remote_buffer += read

    def writable(self):
        "Check if there's something to forward."
        return (len(self.receiver.from_remote_buffer) > 0)

    def handle_write(self):
        "Forward to local"
        sent = self.send(self.receiver.from_remote_buffer)
        # print '--> %04i'%sent
        self.receiver.from_remote_buffer = self.receiver.from_remote_buffer[sent:]

    def handle_close(self):
        "Close channel."
        self.close()
        self.receiver.close()

if __name__=='__main__':
    import optparse
    parser = optparse.OptionParser()

    parser.add_option(
        '-l','--local-ip',
        dest='local_ip',default='127.0.0.1',
        help='Local IP address to bind to')
    parser.add_option(
        '-p','--local-port',
        type='int',dest='local_port',default=80,
        help='Local port to bind to')
    parser.add_option(
        '-r','--remote-ip',dest='remote_ip',
        help='Local IP address to bind to')
    parser.add_option(
        '-P','--remote-port',
        type='int',dest='remote_port',default=80,
        help='Remote port to bind to')
    parser.add_option(
        '-a','--allowed_addrs',
        dest='allowed_addrs',default='127.0.0.1',
        help='Allowed addresses: can be a comma separated list of addresses')
    options, args = parser.parse_args()

    allowed_addrs = options.allowed_addrs.split(',')
    forwarder(options.local_ip,options.local_port,options.remote_ip,options.remote_port,allowed_addrs)
    asyncore.loop()
