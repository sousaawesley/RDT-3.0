import random
import socket
import struct
import time

class Server:
    def __init__(self, listen_port=60000, forward_port=60001):
        self.listen_port = listen_port
        self.forward_port = forward_port
        self.sender_address = None
        self.receiver_address = None
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(("", self.listen_port))
        self.forward_socket.bind(("", self.forward_port))
        self.network_condition = "pass"
        self.__identify_clients()

    def __identify_clients(self):
        log = ""
        while self.sender_address is None or self.receiver_address is None:
            packet, sender_address = self.listen_socket.recvfrom(1024)
            identifier = struct.unpack("!B", packet[:1])[0]
            if identifier == 1 and self.sender_address is None:
                self.sender_address = sender_address
                #log += f"Sender address set to {self.sender_address}\n"
            if identifier == 2 and self.receiver_address is None:
                self.receiver_address = sender_address
                #log += f"Receiver address set to {self.receiver_address}"
        #return log

    def set_network_condition(self, condition):
        valid_conditions = ["drop", "corrupt", "delay", "pass"]
        if condition in valid_conditions:
            self.network_condition = condition
        else:
            raise ValueError("Invalid network condition")

    def get_network_condition(self):
        return self.network_condition

    def listen(self):    
         while True:
            try:
                packet, sender_address = self.listen_socket.recvfrom(1024)
                udp_header, data = self.unpack(packet)
                dest_address = self.receiver_address if sender_address == self.sender_address else self.sender_address
                self.simulate_network_conditions(packet, dest_address)
            except socket.error as e:
                print(f"Socket error: {e}")

    def simulate_network_conditions(self, packet, dest_address):
        decision = self.get_network_condition()
        log = f"Network condition: {decision}\n"
        
        if decision == "drop":
            log += "Packet dropped\n"
        
        if decision == "corrupt":
            packet = self.corrupt_checksum_pkt(packet)
            self.forward_packet(packet, dest_address)
            log += "Packet corrupted and sent\n"
        
        if decision == "delay":
            time.sleep(3)
            self.forward_packet(packet, dest_address)
            log += "Packet delayed and sent\n"
        
        if decision == "pass":
            self.forward_packet(packet, dest_address)
            log += "Packet sent\n"
        
        return log

    def forward_packet(self, packet, address):
        self.forward_socket.sendto(packet, address)
        
    def unpack(self,packet):
        udp_header = packet[:9]
        data = packet[9:]
        udp_header = struct.unpack("!HHBHH", udp_header)
        return udp_header, data

    def __repack_pkt(self,sender_port, server_port, seq_number, data_length, checksum, data):
        udp_header = struct.pack("!HHBHH", sender_port, server_port, seq_number, data_length, checksum)
        pkt_with_header = udp_header + data
        return pkt_with_header

    def corrupt_checksum_pkt(self, packet):
        packet = self.unpack(packet)
        cksum = self.alter_bits(packet[0][4])
        repack = self.__repack_pkt(packet[0][0], packet[0][1], packet[0][2], packet[0][3], cksum, packet[1])
        return repack
    
    def alter_bits(self, checksum):
        num_bits_to_flip = random.randint(1, 4)

        for _ in range(num_bits_to_flip):
            bit_to_flip = 1 << random.randint(0, 15)
            checksum ^= bit_to_flip

        return checksum