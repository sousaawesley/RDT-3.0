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
        self.__identify_sender()
        self.timer = 3

    def rdt_send(self, data):
        packet = self.__pack_data(data)
        self.__udt_send(packet)

        self.sender_socket.settimeout(2)
        self.listem(packet)

    def listem(self, packet):
        while True:
            try:
                ack_packet, __ = self.sender_socket.recvfrom(1024)
                ack_seq = struct.unpack("!HHBH", ack_packet)[2]
                
                if ack_seq == 1 ^ (int(self.seq_alternate)):
                    print(f"ACK received for sequence number: {ack_seq}")
                    break
                else:
                    print(f"Unexpected ACK received, expected: {1 ^ (int(self.seq_alternate))}, got: {ack_seq}")
                    self.__udt_send(packet)
                    self.sender_socket.settimeout(self.timer)
            
            except socket.timeout:
                print(f"Timeout waiting for ACK{1 ^ (int(self.seq_alternate))}")
                self.__udt_send(packet)
                self.sender_socket.settimeout(self.timer)
    

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