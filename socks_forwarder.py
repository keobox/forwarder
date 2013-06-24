
"Port forwarding based on activestate recipe 483732."

import asyncore
import socket
import socks

class forwarder(asyncore.dispatcher):
    "The 'accept' channel."

    def __init__(self, options, backlog = 5):
        "Constructor."
        asyncore.dispatcher.__init__(self)
        self.remoteip = options['remote_ip']
        self.remoteport = options['remote_port']
        self.allowed_addrs = options['allowed_addrs']
        self.targetip = options['target_ip']
        self.targetport = options['target_port']
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((options['local_ip'], options['local_port']))
        self.listen(backlog)

    def handle_accept(self):
        "Accept handler."
        conn, addr = self.accept()
        # print '--- Connect --- '
        # filter by IP address 0.0.0.0 allows all
        if addr[0] in self.allowed_addrs or ('0.0.0.0' in self.allowed_addrs):
            if self.targetip != '127.0.0.1':
                socksified = socks.handshake(self.remoteip, self.remoteport, self.targetip, self.targetport)
            else:
                socksified = None
            sender(receiver(conn), self.remoteip, self.remoteport, socksified)


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

    def __init__(self, receiver, remoteaddr, remoteport, sock=None):
        "Constructor."
        if sock == None:
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((remoteaddr, remoteport))
        else:
            asyncore.dispatcher.__init__(self, sock)
        self.receiver = receiver
        receiver.sender = self

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
    parser.add_option(
        '-s','--target-ip',
        dest='target_ip',default='127.0.0.1',
        help='Target IP address reachable through remote socks server')
    parser.add_option(
        '-t','--target-port',
        type='int',dest='target_port',default=1080,
        help='Target port reachable through remote socks server')
    options, args = parser.parse_args()

    allowed_addrs = options.allowed_addrs.split(',')
    forwarder(vars(options))
    asyncore.loop()
