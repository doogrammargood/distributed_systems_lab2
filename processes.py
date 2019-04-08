import sys
import socket
import threading
import pickle
#def __main__():
#print sys.argv
process_id = int(sys.argv[1]) #proccess id is set by command line.
#sequencer_address = sys.argv[2] #the address of the sequencer.
sequencer_address =('', int(sys.argv[2]))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',12000+process_id))

clock = 0 #This is the number of messages which have been sent
expected_sequence_number = 1
hold_back_list = []
def wrap_message(message):
    dict = {"sender_id": process_id, "message_contents": message, "local_clock": clock}#, "seq_num": 1}
    return pickle.dumps(dict)

def send_message(message,clock):
    sock.sendto(wrap_message(message), sequencer_address)
    clock = clock+1
#send_message("weird",clock)

def deliver_message(message):
    print "You've got mail!"
    print message

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
        message = input("Ready for your message")
        send_message(message,clock)


input_thread = threading.Thread(target = listen_for_message)
input_thread.start()
while True:
    message, address = sock.recvfrom(1024)
    receive_message(pickle.loads(message))
