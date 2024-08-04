from Sender_rdt import sender_instance

while(True):
    msg = input("\nSend message: ")
    if not msg:
        print("\nExiting sender.")
        break
    sender_instance.rdt_send(msg)