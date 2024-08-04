import socket
import struct

class Sender:

    def __init__(self, ip="127.0.0.1", port=60000):
        self.server_ip = ip
        self.server_port = port
        self.dest = (self.server_ip, self.server_port)
        self.sender_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sender_socket.bind(('', 0))
        self.sender_port = self.sender_socket.getsockname()[1]
        self.seq_alternate = False
        self.expected_ack_seq = 0
        self.__identify_sender()
        self.timer = 2
        self.colors = ['\033[0m', '\033[92m', '\033[33m', '\033[91m']

    def rdt_send(self, data):
        packet = self.__pack_data(data)
        self.__udt_send(packet)
        self.sender_socket.settimeout(2)
        self.listem(packet)

    def listem(self, packet):
        while True:
            try:
                
                ack_packet, __ = self.sender_socket.recvfrom(1024)
                self.expected_ack_seq = self.unpack(packet)[0][2]
                ack_seq = struct.unpack("!HHBH", ack_packet)[2]
                
                if  self.__not_corrupted(ack_packet):
                    
                    if ack_seq == self.expected_ack_seq:
                        print(f"\n{self.colors[1]}[INFO]{self.colors[0]} ACK received for sequence number: {ack_seq}")
                        break
                    else:
                        print(f"\n{self.colors[2]}[WARNING]{self.colors[0]} Unexpected sequence number received."
                            f"    Expected : {self.expected_ack_seq}\n"
                            f"    Got: {ack_seq}\n")
                        self.__udt_send(packet)
                        self.sender_socket.settimeout(self.timer)
                else: 
                    self.__udt_send(packet)
                    self.sender_socket.settimeout(self.timer)

            except socket.timeout:
                print(f"\n{self.colors[3]}[ERROR]{self.colors[0]} Timeout waiting for ACK {self.expected_ack_seq}")
                self.__udt_send(packet)
                self.sender_socket.settimeout(self.timer)

    def __create_ack(self, receiver_port, server_port, last_valid_seq_number):
        ack_header_no_cksuum = struct.pack("!HHBH", receiver_port, server_port, last_valid_seq_number, 0)
        return ack_header_no_cksuum
    
    def unpack(self,packet):
        udp_header = packet[:9]
        data = packet[9:]
        udp_header = struct.unpack("!HHBHH", udp_header)
        return udp_header, data
    
    def ack_checksum_calculator(self, packet):
        ack = struct.unpack("!HHBH", packet)
        ack_without_cksum = self.__create_ack(ack[0], ack[1], ack[2])
        return self.__checksum_calculator(ack_without_cksum)
    
    def __not_corrupted(self, packet):
        received_checksum = struct.unpack("!HHBH", packet)[3]
        calculated_checksum = self.ack_checksum_calculator(packet)
        
        print("[INFO] Packet Integrity Check:")
        print(f"  - Received checksum: {received_checksum}")
        print(f"  - Calculated checksum: {calculated_checksum}")
        
        if calculated_checksum == received_checksum:
            print(f"  - Ack checksum is {self.colors[1]}not corrupted.{self.colors[0]}\n")
            return True
        
        print(f"  - Ack checksum is {self.colors[3]}corrupted.{self.colors[0]}\n")
        return False
        
    def __pack_data(self,data):
        encoded_data = data.encode()
        data_length = len(data)
        seq_number = self.__seq_number()
        header_without_cksum = self.__create_header_udp(seq_number, data_length, 0)
        checksum = self.__checksum_calculator(encoded_data + header_without_cksum)
        packet = self.__create_pkt(seq_number, encoded_data, data_length, checksum)
        return packet

    def __create_header_udp(self, seq_number, data_length, checksum):
        udp_header = struct.pack("!HHBHH", self.sender_port, self.server_port,seq_number, data_length, checksum)
        return udp_header

    def __create_pkt(self,seq_number, data, data_length, checksum):
        udp_header = self.__create_header_udp(seq_number, data_length, checksum)
        pkt_with_header = udp_header + data
        return pkt_with_header

    def __seq_number(self):
        if self.seq_alternate:
            self.seq_alternate = False
            return 1
        self.seq_alternate = True
        return 0
    
    def __checksum_calculator(self, data):
        if len(data) % 2 == 1:
            data += b'\0'
        s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff

    def __udt_send(self, pkt):
        self.sender_socket.sendto(pkt, self.dest)

    def __identify_sender(self):
        initial_packet = struct.pack("!B", 1)
        self.sender_socket.sendto(initial_packet, self.dest)


sender_instance = Sender()