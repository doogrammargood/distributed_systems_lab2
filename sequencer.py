import sys
import socket
import threading
#import thread
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
    thread = threading.Thread(target = run, args=(message_from_client,))
    #add address when receving instead of initializion
    # if address not in client:
    #     client.add(address)
    thread.start()

def run(message_from_client):
    global Vclock
    global sequence
    delay=random.random()*5
    time.sleep(delay)    #stimulate delay
    print("receive message from id:%d,with LC:%d at %f"%(message_from_client["sender_id"],message_from_client["local_clock"],time.time()))  #for check purpose
    print message_from_client["local_clock"]
    print Vclock[message_from_client["sender_id"]]
    if message_from_client["local_clock"] == Vclock[message_from_client["sender_id"]]:
        print "in if statement"
        Vclock[message_from_client["sender_id"]]+=1
        sequence+=1
        print sequence
        send_message(message_from_client["message_contents"],sequence,+message_from_client["sender_id"])
        check=-1
        while (check < 0):
            check+=1
            for n in hold_back_list:
                check+=1
                if (message_from_client["sender_id"] == n["sender_id"]):
                    if(Vclock[message_from_client["sender_id"]] == n["local_clock"]):
                        send_message(n["message_contents"],sequence+1,n["sender_id"])
                        print("send message:%s with sequence:%d,sender_id:%d localclock:%d"%(n["message_from_client"],sequence+1,n["sender_id"],n["local_clock"]))
                        Vclock[message_from_client["sender_id"]]+=1
                        sequence+=1
                        check-=1
                        check-=len(hold_back_list)
                        hold_back_list.remove(n)

    else:
        print "hold back list appended"
        hold_back_list.append(message_from_client)
        print hold_back_list

if __name__ == '__main__':
    while True:
        message,address = server.recvfrom(1024)
        receive_message(pickle.loads(message), address)
        print "got a message from"
        print address
