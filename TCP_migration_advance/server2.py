# encoding:utf-8
# local service
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM, IPPROTO_TCP, TCP_NODELAY
import time
local_port = 21000
local_ip='10.0.3.4'

def server():
    server_port = local_port
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('', server_port))
    server_socket.listen(10)
    print(local_ip, 'The server is ready to receive')
    # server_socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, True)
    while True:
        connectionSocket, addr = server_socket.accept()
        print(addr, 'success connection')
        for i in range(5):
            msg = connectionSocket.recv(1024)
            print(msg.decode())
            mssg = "Hello, I'm Server 2"
            connectionSocket.send(mssg.encode())



if __name__ == '__main__':
     server()
