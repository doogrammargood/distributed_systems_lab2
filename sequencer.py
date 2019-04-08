import sys
import socket
from threading import Thread
import thread
import pickle
import os
import random
import time

Vclock={1:0,2:0,3:0,4:0}
sequence=0
hold_back_list = []

ADDRESS=('localhost',8080)
g_conn_pool=[]
server = None
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(ADDRESS)

client_address1 =('', int(sys.argv[1]))
client_address2 =('', int(sys.argv[2]))
client_address3 =('', int(sys.argv[3]))
client_address4 =('', int(sys.argv[4]))
client={1:client_address1,2:client_address2,3:client_address3,4:client_address4}


print("Sequenser start running")

def wrap_message(message,seq_num,sender_id):
    dict = {"message_contents": message, "seq_num": seq_num,"sender_id": sender_id}
    return pickle.dumps(dict)

def send_message(message,seq_num,sender_id):
    #server.sendall(wrap_message(message,seq_num)
    for n in client:
        server.sendto(wrap_message(message,seq_num,sender_id), client[n])
def client_number(address):
    #returns the client number from a given address.
    #print address
    return [index for index in range(1,5) if client[index][1]==address[1]][0]

def receive_message(message_from_client, address):
    global Vclock
    global sequence
    delay=random.random()*5
    time.sleep(delay)    #stimulate delay
    #print("receive message:"+message_from_client["sender_id"]+" "+message_from_client["local_clock"]+"at"+time.time())  #for check purpose
    print message_from_client["local_clock"]
    print Vclock[client_number(address)]
    if message_from_client["local_clock"] == Vclock[client_number(address)]:
        Vclock[client_number(address)]+=1
        sequence+=1
        send_message(message_from_client["message_contents"],sequence,+message_from_client["sender_id"])
        check=0
        while (check < 0):
            for n in hold_back_list:
                if (message_from_client["sender_id"] == n["sender_id"]):
                    check+=1
                    if(Vclock[client_number(address)] == n["local_clock"]):
                        send_message(n["message_contents"],sequence+1,+message_from_client["sender_id"])
                        Vclock[client_number(address)]+=1
                        sequence+=1
                        check-=len(hold_back_list.remove)
                        hold_back_list.remove(n)

    else:
        hold_back_list.append(message_from_client)

if __name__ == '__main__':
    while True:
        message,address = server.recvfrom(1024)
        receive_message(pickle.loads(message), address)
        print "got a message from"
        print address
