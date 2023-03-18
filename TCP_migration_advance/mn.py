# encoding:utf-8

import os
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM, IPPROTO_TCP, TCP_NODELAY
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import info

# from socket import socket_constants
from socket import SOL_SOCKET, SO_REUSEADDR

import time
server_port = 8880

#gw 后的地址为 分配到h2的interface
os.system('route add -net 10.0.1.0/24 gw 10.0.2.15')
os.system('route add -net 10.0.3.0/24 gw 10.0.2.15')

def addHost():
    time.sleep(1)
    s1.attach('s1-eth4')
    h5 = net.addHost('server2', ip='10.0.3.4')
    net.addLink(h5, s1, 0, 4)
    h5.setIP('10.0.3.4')
    h5.setMAC('00:00:00:00:00:34')
    net.get('server2').cmd('route add -net 10.0.1.0/24 gw 10.0.3.1 dev server2-eth0')
    net.get('server2').cmd('route add -net 10.0.2.0/24 gw 10.0.3.1 dev server2-eth0')

    s1.attach('s1-eth5')
    net.addLink(h5, s1, 1, 5)
    net.get('server2').cmd('ifconfig server2-eth1 10.0.3.6')
    h5.cmd('python3 server2.py')

    print('already add new host reHost')

def server_udp(net):

    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('', server_port))


    print('The server is ready to receive: UDP')

    while True:
        message, client_address = server_socket.recvfrom(20480)
        code=message.decode()
        if code=='add':
            addHost()
            time.sleep(3)
        break



net = Mininet(switch = OVSBridge)
h1 = net.addHost('Client',ip='10.0.1.1')
h2 = net.addHost('Gateway',ip='10.0.1.2')
s1=net.addSwitch('s1')
h3 = net.addHost('Server1',ip='10.0.3.3')
# h4 = net.addHost('reHost',ip='10.0.3.4')

net.addLink(h1, h2,0,0)
net.addLink(h2, s1,1,1)
net.addLink(h3, s1,0,2)
# net.addLink(h4, s1,0,3)

Intf( 'enp0s3', node=h2 )

net.build()
h1.setMAC('00:00:00:00:00:11','Client-eth0')
h2.setMAC('00:00:00:00:00:12','Gateway-eth0')
h2.setMAC('00:00:00:00:00:31','Gateway-eth1')
h3.setMAC('00:00:00:00:00:33','Server1-eth0')
# h4.setMAC('00:00:00:00:00:34','reHost-eth0')
net.build()
h1.cmd('ifconfig Client-eth0 10.0.1.1')
h2.cmd('ifconfig Gateway-eth0 10.0.1.2')
h2.cmd('ifconfig Gateway-eth1 10.0.3.1')
h2.cmd('ifconfig enp0s3 10.0.2.15/24')
h3.cmd('ifconfig Server1-eth0 10.0.3.3')
# h4.cmd('ifconfig reHost-eth0 10.0.3.4')

h2.cmd('route add -net 10.0.1.0/24 gw 10.0.1.2 dev Gateway-eth0')
h2.cmd('route add -net 10.0.3.0/24 gw 10.0.3.1 dev Gateway-eth1')
# h2.cmd('route add -net 10.0.2.0/24 gw 10.0.2.15 dev enp0s3')


h1.cmd('route add -net 10.0.2.0/24 gw 10.0.1.2 dev Client-eth0')
h1.cmd('route add -net 10.0.3.0/24 gw 10.0.1.2 dev Client-eth0')
h3.cmd('route add -net 10.0.1.0/24 gw 10.0.3.1 dev Server1-eth0')
h3.cmd('route add -net 10.0.2.0/24 gw 10.0.3.1 dev Server1-eth0')
# h4.cmd('route add -net 10.0.1.0/24 gw 10.0.3.1 dev reHost-eth0')
# h4.cmd('route add -net 10.0.2.0/24 gw 10.0.3.1 dev reHost-eth0')

h2.cmd('sysctl -w net.ipv4.tcp_timestamps=0')
h3.cmd('sysctl -w net.ipv4.tcp_timestamps=0')
# h4.cmd('sysctl -w net.ipv4.tcp_timestamps=0')
h1.cmd('sysctl -w net.ipv4.tcp_timestamps=0')

s2=net.addSwitch('s2')

h2.cmd('sysctl net.ipv4.ip_forward=1')
# net.addLink(h4, s2)
# net.get('h4').cmd('ifconfig h4-eth1 10.0.3.3')


#h2 --vm route
h2.cmd('route add -host 10.0.2.64 dev enp0s3')

net.start()
net.pingAll()

p = Thread(target=server_udp, args=(net,))
p.start()

CLI(net)
net.stop()

os.system('route del -net 10.0.1.0/24 gw 10.0.2.15')
os.system('route del -net 10.0.3.0/24 gw 10.0.2.15')

