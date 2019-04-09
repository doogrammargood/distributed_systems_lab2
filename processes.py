import sys
import socket
import threading
import pickle
from termcolor import colored
import random
import time

#def __main__():
#print sys.argv
test_behavior = 2
#test behavior 0 accepts messages from the command line.
# '''''''''''''1 sends a message to the next process.

process_id = int(sys.argv[1]) #proccess id is set by command line.
#sequencer_address = sys.argv[2] #the address of the sequencer.
sequencer_address =('', int(sys.argv[2]))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',12000+process_id))

colors = {1: 'red', 2: 'green', 3: 'blue', 4: 'magenta'} #used to pretty print messages which have been delivered

clock = 0 #This is the number of messages which have been sent
expected_sequence_number = 1
hold_back_list = []

delivered_messages = [] #a list of messages which have been delivered
def wrap_message(message):
    global clock
    dict = {"sender_id": process_id, "message_contents": message, "local_clock": clock}#, "seq_num": 1}
    return pickle.dumps(dict)

lock = threading.Lock()
def send_message(message):
    global clock
    lock.acquire()
    try:
        sock.sendto(wrap_message(message), sequencer_address)
        clock = clock+1
    finally:
        lock.release()

def deliver_message(message):
    # print "You've got mail!"
    # print message
    delivered_messages.append(message)
    global expected_sequence_number
    expected_sequence_number +=1
    if test_behavior == 1:
        if int(message['message_contents'][0]) == process_id:
            next_process = (process_id +1)%4
            if next_process == 0:
                next_process = 4
            send_message("%d please forward this message" %next_process)

def pretty_print_messages(queue):
    #prints the messages in delivered messages
    for message in queue:
        text = colored(message["message_contents"], colors[message["sender_id"]])
        print text

cascade_lock = threading.Lock()

def cascade_deliveries():
    cascade_lock.acquire()
    try:
        global hold_back_list
        global expected_sequence_number
        hold_back_list = sorted(hold_back_list, key = lambda x: x["seq_num"])
        #well sort the messages, then check that
        for message in hold_back_list:
            if expected_sequence_number == message["seq_num"]:
                deliver_message(message)
                #hold_back_list.remove(message)
        hold_back_list = filter(lambda message: message["seq_num"]>expected_sequence_number,hold_back_list)
    finally:
        cascade_lock.release()
    return

def receive_message(message_from_seq):
    delay=random.random()*5
    time.sleep(delay)    #stimulate delay
    global expected_sequence_number
    global delivered_messages
    global hold_back_list
    print "recieved message", message_from_seq
    print expected_sequence_number
    if message_from_seq["seq_num"] == expected_sequence_number:
        deliver_message(message_from_seq)
        cascade_deliveries()
    elif not message_from_seq["seq_num"] in map(lambda x: x["seq_num"],hold_back_list):
        #as long as this isnt a duplicate
        cascade_lock.acquire()
        try:
            hold_back_list.append(message_from_seq)
        finally:
            cascade_lock.release()
def listen_for_message():
    #listens for messages from keyboard, only for test_behavior = 0
    global clock
    while True:
        message = input()
        send_message(message)
def send_messages_randomly():
    #This method is specifically for test 2
    global clock
    global test2_ongoing
    while test2_ongoing:
        delay=random.random()
        time.sleep(delay)
        send_message("%d" %clock)

if test_behavior ==0:
    #This is the default behavior, where the user inputs a message to send to the other processes.
    input_thread = threading.Thread(target = listen_for_message)
    input_thread.start()
    while True:
        message, address = sock.recvfrom(1024)
        receive_thread = threading.Thread(target = receive_message, args = (pickle.loads(message),))
        receive_thread.start()
        #receive_message(pickle.loads(message))
elif test_behavior == 1:
    #This is the test behavior, where process 1 sends a message containing '2',
    #process 2 sends a message containing '3', and so forth cyclically.
    #Then we check after 10 messages that the delivered messages follow the desired order.
    if process_id == 1:
        send_message("2 please forward this message.")
    while len(delivered_messages)<10:
        message, address = sock.recvfrom(1024)
        receive_thread = threading.Thread(target = receive_message, args = (pickle.loads(message),))
        receive_thread.start()
    pretty_print_messages(delivered_messages)
elif test_behavior == 2:
    #In this test behavior, each process will continually send messages.
    time.sleep(15) #so that there's enough time to start all of the processes before any send messages.
    print "starting"
    test2_ongoing = True
    sending_thread = threading.Thread(target = send_messages_randomly)
    sending_thread.start()
    while len(delivered_messages)<10:
        message, address = sock.recvfrom(1024)
        receive_thread = threading.Thread(target = receive_message, args = (pickle.loads(message),))
        receive_thread.start()
    test2_ongoing = False

    pretty_print_messages(delivered_messages)
