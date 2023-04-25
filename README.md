# TCP_migration_advanced
This project provides a TCP migration idea based on netfilterqueue. This migration is transparent, reproducible, keep-alive, and can be migrated at any time, but does not consider the state of the application layer. And this project considers dynamically adding hosts to simulate the needs of real network scenarios.

## Migration Design principle
![image](https://user-images.githubusercontent.com/105418310/234158371-ba619164-5365-428c-b45d-431d36084a94.png)

Stage 1: Three-way Handshake. The Client and Server 1 perform a normal TCP three-way handshake, which is recorded by Gateway. It mainly includes the IP address, port number, sequence number, and ACK of both parties.

Stage 2: TCP Normal Data Transmission. The Client and Server 1 perform the normal TCP data transmission phase. The gateway will record the last data packet sent by the Client, mainly recording the current status of the Client and Server 1, namely, sequence number and ACK number.

Stage 3: TCP-Migration. When the Client sends the payload packet (recorded as packet_m) and it is time to migrate, Gateway intercepts it and modifies the destination IP address and port number to Server 2's address. Gateway then recalculates the checksum and sends the packet to Server 2. Prior to sending the packets, Gateway replays a 3-way handshake to Server 2. The specific flow is as follows:
  1. First, it utilizes the recorded SYN packet from step 1 to establish the first handshake with Server 2. However, during this process, the sequence number of the SYN packet is changed to the sequence number of packet_m minus one.
  2. Server 2 responds with a SYN-ACK packet, believing that it is establishing a new connection with the Client.
  3. Gateway intercepts the SYN-ACK packet and records the sequence number from Server 2. It then modifies the destination IP address, port number, sequence number and ACK number in the recorded ACK packet from the original three-way handshake, using the recorded sequence number from Server 2. Gateway then sends the modified ACK packet to Server 2 to establish the third handshake. At this point, the TCP three handshake ends.
  4. The Gateway modifies the destination IP address, destination port number, and ACK number of packet_m, recalculates the checksum, and sends it to Server 2. 
  5. Similarly, for the packet received in the response from Server 2. The Gateway modifies the source IP address, source port number, and sequence number of the packet, recalculates the checksum, and then sends it to the Client. At this point, we have established a TCP link to migrate the initial TCP from FlowS1 to FlowS2.

Stage 4: TCP Data Transmission. The Gateway needs to constantly modify the destination/source IP address, destination/source port number, and ACK/sequence number of packets in the same form as before to maintain TCP migration from FlowS1 to FlowS2.

## Contributing
This project provides an idea to migrate TCP at any time. Great for stateless protocols. According to this idea, you can even migrate TCP back to the original host after TCP migration.

## Setup
1. Running: python3 mn.py in terminal of Virtual Machine, and open the terminal of Server1, Gateway, Client
![截屏2023-04-21 上午11 08 31](https://user-images.githubusercontent.com/105418310/233531326-1e58e60c-7b0e-47f7-bf5f-abc938e699f8.jpg)

2. Running: nfq.py in Gateway; server1.py in Server1; client.py in Client
![截屏2023-04-21 上午11 09 14](https://user-images.githubusercontent.com/105418310/233531398-c25c4d1a-015e-4f42-8dd5-06195fee67bb.jpg)
We can see that:  There are 3 TCP data interactions between Client and Server1， and now Gateway is notifying to add a new server Server2 and migrating the traffic to new server

3. Waiting: 
![截屏2023-04-21 上午11 15 51](https://user-images.githubusercontent.com/105418310/233532167-943fdc40-c4b3-4e80-809e-715ae9c06278.jpg)
We can see that: There are 5 TCP data interactions between Client and Server2，which means we have a new server(Server2), and migrated TCP connection to new server.

## Experiment Flow
1. Client sends a request_message_1 to Server 1.
2. Server 1 responds with a response_message_1 and prints the IP address and port number of the Client, along with n "I am client index (index means 0,1,2...)" in the terminal. The Client prints n "I am server 1".
3. Gateway uses TCP migration to redirect network traffic to Server 2, notifying the script running on the virtual machine to call the Mininet Engine to add a new host.
4. Subsequent request information from the Client is printed on Server 2, while subsequent response message received by Client will be the response_message_2 (for example, "I am server 2") from Server 2.
5. The terminal of Server 1 prints information about the IP address and port number of the Client and "I am client index (index means 0,1)", while the terminal of Server 2 prints information about the IP address and port number of the Client and "I am client index (index means 2,3,4...)" information. The Client terminal prints 2 "I am Server 1" and (n-2) "I am Server 2" information.

Note: The implementation of this project will not open the terminal of server 2, so you cannot see the printing of terminal 2 in the video, but the printing of terminal 2 can refer to the figure below.
![image](https://user-images.githubusercontent.com/105418310/234159785-54fca0ce-c91f-428e-aa40-1405b112ceed.png)


## Contact
LLY - atomy.lly@gmail.com
