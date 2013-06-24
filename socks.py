
"Socks auth and connect for NEs"

import socket
import struct

CONNECT_ERROR = -1
SOCKS_CONNECT = 1
SOCKS_IPV4 = 1
SOCKS_IPV6 = 4
SOCKS_NO_AUTH = 0
SOCKS_V5 = 5
SOCKS_VER = 3


def auth():
    "Socks authentication handler."
    # 454 SOCKS_VER
    msg = struct.pack('!BBB', SOCKS_VER, 1, SOCKS_NO_AUTH)
    return msg


def connect(target_ip, target_port):
    "Socks connection handler."
    msg = struct.pack('!BBBB', SOCKS_V5, SOCKS_CONNECT, 0, SOCKS_IPV4)
    # assuming ipv4 only
    ip_values = tuple([int(x) for x in target_ip.split('.')])
    msg = msg + struct.pack('!BBBB', *ip_values)
    msg = msg + struct.pack('!h', target_port)
    return msg


def handshake(proxy_addr, proxy_port, target_addr, target_port):
    "Socks protocol handshake"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((proxy_addr, proxy_port))
    s.send(auth())
    reply = s.recv(2)
    print 'reply bytes', len(reply), reply.encode('hex_codec')
    connect_msg = connect(target_addr, target_port)
    print connect_msg.encode('hex_codec')
    s.send(connect_msg)
    reply = s.recv(len(connect_msg))
    print 'reply bytes', len(reply), reply.encode('hex_codec')
    return s


if __name__ == '__main__':
    s = handshake('10.58.68.35', 1080, '10.58.68.36', 2015)
    s.close()
