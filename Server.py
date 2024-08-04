import random
import socket
import struct
import time
from threading import Lock

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
        self.net_sndr_condition = "pass"
        self.net_rcv_condition = "pass"
        self.valid_conditions = ["drop", "corrupt", "delay", "pass"]
        self.delay = 3
        self.logs = []
        self.logs_lock = Lock()
        self.__identify_clients()
        self.corruption_limit = 2
        self.corrupted_packet_count = 0
        
    def __identify_clients(self):
        while self.sender_address is None or self.receiver_address is None:
            packet, sender_address = self.listen_socket.recvfrom(1024)
            identifier = struct.unpack("!B", packet[:1])[0]
            if identifier == 1 and self.sender_address is None:
                self.sender_address = sender_address
            if identifier == 2 and self.receiver_address is None:
                self.receiver_address = sender_address

    def set_net_sndr_condition(self, condition):
        if condition in self.valid_conditions:
            self.net_sndr_condition = condition
        else:
            raise ValueError("Invalid network condition for sender")
        
    def get_net_sndr_condition(self):
        return self.net_sndr_condition
    
    def set_net_rcv_condition(self, condition):
        if condition in self.valid_conditions:
            self.net_rcv_condition = condition
        else:
            raise ValueError("Invalid network condition for receiver")

    def get_net_rcv_condition(self):
        return self.net_rcv_condition

    def listen(self):    
        while True:
            try:
                packet, sender_address = self.listen_socket.recvfrom(1024)
                dest_address = self.receiver_address if sender_address == self.sender_address else self.sender_address
                
                if sender_address == self.sender_address:
                    self.simulate_net_sndr_conditions(packet, dest_address)
                else:
                    self.simulate_net_rcv_conditions(packet, dest_address)

            except socket.error as e:
                self.add_log(f"Socket error: {e}")

    def simulate_net_rcv_conditions(self, packet, dest_address):
        decision = self.get_net_rcv_condition()
        log = f"Network rcv condition: {decision}"
        self.add_log(log)

        if decision == "drop":
            self.add_log("\nAck dropped\n")
        
        if decision == "corrupt" and self.corrupted_packet_count < self.corruption_limit:
            packet = self.corrupt_checksum_ack(packet)
            self.forward_packet(packet, dest_address)
            self.corrupted_packet_count += 1
            self.add_log("\nAck corrupted and sent\n")
            if self.corrupted_packet_count >= self.corruption_limit:
                self.corrupted_packet_count = 0
                self.set_net_rcv_condition("pass")
        
        if decision == "delay":
            time.sleep(self.delay)
            self.forward_packet(packet, dest_address)
            self.add_log("\nAck delayed and sent\n")
        
        if decision == "pass":
            self.forward_packet(packet, dest_address)
            self.add_log("\nAck sent\n")
        

    def simulate_net_sndr_conditions(self, packet, dest_address):
        decision = self.get_net_sndr_condition()
        log = f"Network sndr condition: {decision}"
        self.add_log(log)
        
        if decision == "drop":
            self.add_log("\nPacket dropped\n")
        
        if decision == "corrupt" and self.corrupted_packet_count < self.corruption_limit:
            packet = self.corrupt_checksum_pkt(packet)
            self.forward_packet(packet, dest_address)
            self.corrupted_packet_count += 1
            self.add_log("\nPacket corrupted and sent\n")
            if self.corrupted_packet_count >= self.corruption_limit:
                self.corrupted_packet_count = 0
                self.set_net_sndr_condition("pass")
        
        if decision == "delay":
            time.sleep(self.delay)
            self.forward_packet(packet, dest_address)
            self.add_log("\nPacket delayed and sent\n")
        
        if decision == "pass":
            self.forward_packet(packet, dest_address)
            self.add_log("\nPacket sent\n")
        

    def forward_packet(self, packet, address):
        self.forward_socket.sendto(packet, address)

    def unpack(self, packet):
        udp_header = packet[:9]
        data = packet[9:]
        udp_header = struct.unpack("!HHBHH", udp_header)
        return udp_header, data

    def __repack_pkt(self, sender_port, server_port, seq_number, data_length, checksum, data):
        udp_header = struct.pack("!HHBHH", sender_port, server_port, seq_number, data_length, checksum)
        pkt_with_header = udp_header + data
        return pkt_with_header

    def __create_ack(self):
        ack_header_no_cksuum = struct.pack("!HHBH", self.receiver_port, self.server_port, ~self.seq_number, 0)
        checksum = self.__checksum_calculator(ack_header_no_cksuum)
        ack_header = struct.pack("!HHBH", self.receiver_port, self.server_port, ~self.seq_number, checksum)
        return ack_header

    def corrupt_checksum_ack(self, packet):
        ack_header = struct.unpack("!HHBH", packet)
        checksum = self.alter_bits(ack_header[3])
        return self.__create_ack(ack_header[0], ack_header[1], ack_header[3], checksum)

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

    def add_log(self, log_message):
        with self.logs_lock:
            self.logs.append(log_message)

    def get_logs(self):
        with self.logs_lock:
            return list(self.logs)
