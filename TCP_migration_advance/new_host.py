# encoding:utf-8
import socket

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# server address
server_address = ('10.0.2.64', 8880)

# send a message
message = 'add'
sock.sendto(message.encode(), server_address)

# close the socket
sock.close()
