# encoding:utf-8
import time
from random import random

from netfilterqueue import NetfilterQueue
from scapy.all import *
from scapy.layers.inet import IP, TCP
from scapy.fields import *
import os

os.system('iptables -A FORWARD -d 10.0.1.1 -j NFQUEUE --queue-num 1')
os.system('iptables -A FORWARD -s 10.0.1.1 -j NFQUEUE --queue-num 1')


class MigrationSession:
    def __init__(self):
        # stage1 : client-server 3 times TCP
        # stage2.1 : client-server1 msg TCP
        # stage2.2 : client-server2 3 times TCP + first msg
        # stage 3 : client-server2 msg TCP  # 后续可升级为 任意选择和server1 或server2 交互
        self.state = 1


# 初始化数据记录ip port
server1 = MigrationSession()
server2 = MigrationSession()
client = MigrationSession()
mysession = MigrationSession()

# record message and state
server2.mac = '00:00:00:00:00:34'
server2.ip = '10.0.3.4'
server2.port = 21000
server2.seq = -1  # the seq of  server2 receive message next
server2.ack = -1  # the ack of  server2 receive message next

server1.mac = '00:00:00:00:00:33'
server1.ip = '10.0.3.3'
server1.port = 21000
server1.seq = -1  # the seq of  server1 receive message next
server1.ack = -1  # the ack of  server1 receive message next

client.mac = '00:00:00:00:00:11'
client.ip = '10.0.1.1'
client.port = None
client.seq = -1  # the seq of  client receive message next
client.ack = -1  # the ack of  client receive message next
# 对next的解释： 目前包在gw上， 如果发给某个host 应该设置序列号为seq ack
# stage 2.2 以后： 收到谁的包 改谁的记录值， 更改包的目的序列号

hand1 = None
hand3 = None

n = 2
number = 0
print("server 1  receive ", n + 1, " packets")


def print_and_accept(pkt):
    global server1, server2, client, mysession, hand1, hand3, n, number

    ip = IP(pkt.get_payload())
    tcp = ip.getlayer(TCP)

    print(ip.src, '--', ip.dst, tcp.flags)
    if (mysession.state == 1):  # 3 times TCP hand
        if tcp.flags == 'S':
            hand1 = IP(pkt.get_payload())  # record packet of hand1
            client.ip = ip.src
            client.port = tcp.sport
            pkt.accept()
        elif tcp.flags == 'SA' and ip.src == server1.ip and ip.dst == client.ip:
            pkt.accept()
        elif tcp.flags == 'A' and ip.src == client.ip and ip.dst == server1.ip:
            hand3 = IP(pkt.get_payload())  # record packet of hand3
            # record seq numbers of client and server1
            # note : the len = 0 now
            client.seq = tcp.ack
            client.ack = tcp.seq
            print (tcp.getlayer(Raw))
            server1.seq = tcp.seq
            server1.ack = tcp.ack
            pkt.accept()
            mysession.state = 2  # 3 times handshakes over
            print ("1 over =====================================================")
    elif (mysession.state == 2):
        flag = 0
        if ip.src == client.ip and ip.dst == server1.ip and number <= n:
            if tcp.flags == 'PA':
                number += 1
            pkt.accept()
        elif ip.src == server1.ip and ip.dst == client.ip and number <= n + 1:
            pkt.accept()

        elif tcp.flags == 'A' and ip.src == client.ip and ip.dst == server1.ip and flag == 0:
            pkt.accept()
            flag = 1

        elif tcp.flags == 'PA' and ip.src == client.ip and ip.dst == server1.ip:
            #new host
            os.system('python3 new_host.py')
            time.sleep(3)
            # record the seq next
            client.seq = tcp.ack
            server1.seq = tcp.seq
            if tcp.haslayer(Raw):
                client.ack = tcp.seq + len(tcp.getlayer(Raw))
            else:
                client.ack = tcp.seq
            server1.ack = tcp.ack

            # create the TCP connection with server2 and hand1 , hand 2(copy) , hand 3
            hand1[IP].dst = server2.ip
            hand1[TCP].seq = tcp.seq - 1
            hand1[TCP].dport = server2.port

            del hand1[IP].chksum
            del hand1[TCP].chksum
            ans = srp1(Ether(dst='00:00:00:00:00:34', src='00:00:00:00:00:11') / hand1, iface='Gateway-eth1')
            server2.ack = ans[TCP].seq + 1
            server2.seq = ans[TCP].ack
            print ('hand2')

            # 建立第三次握手
            hand3[IP].dst = server2.ip
            hand3[TCP].dport = server2.port
            hand3[TCP].ack = server2.ack
            hand3[TCP].seq = server2.seq
            del hand3[IP].chksum
            del hand3[TCP].chksum
            sendp(Ether(dst='00:00:00:00:00:34', src='00:00:00:00:00:11') / hand3, iface='Gateway-eth1')

            ip.dst = server2.ip
            ip.dport = server2.port
            ip[TCP].ack = server2.ack
            ip[TCP].seq = server2.seq
            del ip[IP].chksum
            del ip[TCP].chksum
            pkt.set_payload(bytes(ip))
            pkt.accept()
            mysession.state = 3


    elif (mysession.state == 3):

        if tcp.seq == client.ack and ip.src == '10.0.1.1' and ip.dst == '10.0.3.3':
            client.seq = tcp.ack
            if tcp.haslayer(Raw):
                print(tcp.getlayer(Raw))
                client.ack = tcp.seq + len(tcp.getlayer(Raw))
            else:
                client.ack = tcp.seq
            change_pkt_toServer2(ip, pkt, server2.ip, server2.port, server2.seq, server2.ack)


        elif tcp.seq == server2.ack and ip.src == '10.0.3.4' and ip.dst == '10.0.1.1':

            server2.seq = tcp.ack
            if tcp.haslayer(Raw):
                print(tcp.getlayer(Raw))
                server2.ack = tcp.seq + len(tcp.getlayer(Raw))
            else:
                server2.ack = tcp.seq
            change_pkt_toClent(ip, pkt, server1.ip, server1.port, client.seq, client.ack)

        else: print("rejected")


def change_pkt_toServer2(pkt_ip, pkt, ip, port, seq, ack):
    pkt_ip.dst = ip
    pkt_ip.dport = port
    pkt_ip[TCP].seq = seq
    pkt_ip[TCP].ack = ack
    del pkt_ip[IP].chksum
    del pkt_ip[TCP].chksum
    pkt.set_payload(bytes(pkt_ip))
    pkt.accept()


def change_pkt_toClent(pkt_ip, pkt, ip, port, seq, ack):
    pkt_ip.src = ip
    pkt_ip.sport = port
    pkt_ip[TCP].seq = seq
    pkt_ip[TCP].ack = ack
    del pkt_ip[IP].chksum
    del pkt_ip[TCP].chksum
    pkt.set_payload(bytes(pkt_ip))
    pkt.accept()


if __name__ == '__main__':
    nfqueue = NetfilterQueue()
    nfqueue.bind(1, print_and_accept)
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        print('')
        os.system('iptables -F')

    nfqueue.unbind()

#  完成 不丢包  序列号无疑问
# nf2 稳定版1 ： 可随机选择某个包开始migration ， 但是server端不回传数据包，因为没有考虑server1 回传PA 接收

# 9.20 原先基础上 删除阶段2.1 的信息 试图达到服务器端可回传数据
# 结果： 1. 可按照原先nf2_2 版本使用  2. 可回传数据  删除linux系统的时间戳 以及， 修改客户端 socket的nagle算法
# clientSocket.setsockopt(IPPROTO_TCP, TCP_NODELAY, True)


