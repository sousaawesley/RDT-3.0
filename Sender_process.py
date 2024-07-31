from Sender_rdt import sender_instance

while(True):
    msg = input("Send message: ")
    if (msg == ''):
        break
    sender_instance.rdt_send(msg)