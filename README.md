# TCP_migration_advanced
## 1. Running: python3 mn.py in terminal of Virtual Machine, and open the terminal of Server1, Gateway, Client
![截屏2023-04-21 上午11 08 31](https://user-images.githubusercontent.com/105418310/233531326-1e58e60c-7b0e-47f7-bf5f-abc938e699f8.jpg)

## 2. Running: nfq.py in Gateway; server1.py in Server1; client.py in Client
![截屏2023-04-21 上午11 09 14](https://user-images.githubusercontent.com/105418310/233531398-c25c4d1a-015e-4f42-8dd5-06195fee67bb.jpg)
We can see that:  There are 3 TCP data interactions between Client and Server1， and now Gateway is notifying to add a new server Server2 and migrating the traffic to new server

## 3. Waiting: 
![截屏2023-04-21 上午11 15 51](https://user-images.githubusercontent.com/105418310/233532167-943fdc40-c4b3-4e80-809e-715ae9c06278.jpg)
We can see that: There are 5 TCP data interactions between Client and Server2，which means we have a new server(Server2), and migrated TCP connection to new server.
