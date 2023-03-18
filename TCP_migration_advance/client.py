# encoding:utf-8
# virtual box client
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM, IPPROTO_TCP, TCP_NODELAY

other_port = 21000
other_ip = '10.0.3.3'


def client_tcp():
    while True:
        try:
            serverName = other_ip
            port = other_port
            serverPort = port
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            clientSocket.connect((serverName, serverPort))

            for i in range(10):
                msg = "Hi, I'm Client"+str(i)
                clientSocket.send(msg.encode())
                mssg = clientSocket.recv(1024)
                print(mssg.decode())
            time.sleep(1)
            clientSocket.close()
            break


        except Exception as e:
            time.sleep(1)
            # print('try to connect')
            pass

if __name__ == '__main__':
    client_tcp()

