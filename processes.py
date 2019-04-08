import sys
import socket
import threading
import pickle
from termcolor import colored
#def __main__():
#print sys.argv
test_behavior = 1
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

def send_message(message):
    global clock
    sock.sendto(wrap_message(message), sequencer_address)
    clock = clock+1

def deliver_message(message):
    # print "You've got mail!"
    # print message
    delivered_messages.append(message)
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

def cascade_deliveries():
    global hold_back_list
    global expected_sequence_number
    hold_back_list = sorted(hold_back_list, key = lambda x: x["seq_num"])
    #well sort the messages, then check that
    for message in hold_back_list:
        if expected_sequence_number == message["seq_num"]:
            deliver_message(message)
            expected_sequence_number +=1
        else:
            return

def receive_message(message_from_seq):
    #print message_from_seq
    print "message received!"
    global expected_sequence_number
    global delivered_messages
    global hold_back_list
    if message_from_seq["seq_num"] == expected_sequence_number:
        deliver_message(message_from_seq)
        cascade_deliveries()
        expected_sequence_number += 1
    elif not message_from_seq["seq_num"] in map(lambda x: x["seq_num"],hold_back_list):
        #as long as this isnt a duplicate
        hold_back_list.append(message_from_seq)
def listen_for_message():
    global clock
    while True:
        #message = input("Ready for your message")
        message = input()
        # if message == "pretty print delivered":
        #     pretty_print_messages(delivered_messages)
        # elif message == "pretty print hold back":
        #     pretty_print_messages(hold_back_list)
        send_message(message)

if test_behavior ==0:
    input_thread = threading.Thread(target = listen_for_message)
    input_thread.start()
elif test_behavior == 1:
    if process_id == 1:
        send_message("2 please forward this message.")
while True:
    message, address = sock.recvfrom(1024)
    receive_message(pickle.loads(message))
