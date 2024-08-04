import socket
import struct

class Receiver:
        
    def __init__(self, ip="127.0.0.1", port=60000):
        self.server_ip = ip
        self.server_port = port
        self.dest = (self.server_ip, self.server_port)
        self.receiver_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.receiver_socket.bind(('', 0))
        self.receiver_port = self.receiver_socket.getsockname()[1]
        self.seq_number = 0
        self.seq_alternate = False
        self.__identify_receiver()

    def rdt_send(self, data):
        packet = self.__pack_data(data)
        self.__udt_send(packet)
        self.__start_timer()

    def rdt_rcv(self, pkt):
        pass

    def unpack(self,packet):
        udp_header = packet[:9]
        data = packet[9:]
        udp_header = struct.unpack("!HHBHH", udp_header)
        return udp_header, data

    def __pack_data(self,data):
        encoded_data = data.encode()
        data_length = len(data)
        seq_number = self.__seq_number()
        header_without_cksum = self.__create_header_udp(seq_number, data_length, 0)
        checksum = self.__checksum_calculator(encoded_data + header_without_cksum)
        packet = self.__create_pkt(seq_number, encoded_data, data_length, checksum)
        return packet
    
    def __checksum_calculator(self, data):
        if len(data) % 2 == 1:
            data += b'\0'
        s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff

    def __not_corrupted(self, packet):
        checksum = self.unpack(packet)[0][4]
        checksum_calculated = self.pkt_checksum_calculator(packet)
        print(f"Checksum received: {checksum}, Checksum calculated: {checksum_calculated}")
        return checksum_calculated == checksum
    
    def check_seq(self, packet):
        pkt_seq = self.unpack(packet)[0][2]
        print(f"Sequence number received: {pkt_seq}, Expected sequence number: {self.seq_number}")

        if pkt_seq == self.seq_number:
            self.seq_number ^= 1
            return True
        
        return False

    def pkt_checksum_calculator(self, packet):
        packet = self.unpack(packet)
        header_without_cksum = self.__create_header_udp(packet[0][0], packet[0][1], packet[0][2], packet[0][3], 0)
        encoded_data = packet[1]
        return self.__checksum_calculator(encoded_data + header_without_cksum)
    
    def __create_header_udp(self, sender_port, server_port, seq_number, data_length, checksum):
        udp_header = struct.pack("!HHBHH", sender_port, server_port, seq_number, data_length, checksum)
        return udp_header
    
    def __udt_send(self, pkt):
        self.socket_send.sendto(pkt, self.dest)

    def listen(self):
        print(f"Listening on port {self.receiver_port}...")
        last_valid_seq_number = self.seq_number ^ 1
        
        while True:
            packet, _ = self.receiver_socket.recvfrom(1024)
        
            unpack = self.unpack(packet)
            pkt_seq = unpack[0][2]

            if self.__not_corrupted(packet):
           
                if pkt_seq == self.seq_number:
                   
                    self.seq_number ^= 1 
                    last_valid_seq_number = pkt_seq 
                    print(f"Received valid packet from: {unpack[0][0]}")
                    print(f"Number seq: {pkt_seq}")
                    print(f"Message: {unpack[1].decode()}")
                else:
                    print(f"Received packet with incorrect sequence number: {pkt_seq}")
            else:
                print("Received corrupted packet.")

            ack_packet = self.__create_ack(last_valid_seq_number)
            self.receiver_socket.sendto(ack_packet, self.dest)
        
    def __create_ack(self, last_valid_seq_number):
        ack_header_no_cksuum = struct.pack("!HHBH", self.receiver_port, self.server_port, last_valid_seq_number, 0)
        checksum = self.__checksum_calculator(ack_header_no_cksuum)
        ack_header = struct.pack("!HHBH", self.receiver_port, self.server_port, self.seq_number ^ 1, checksum)
        return ack_header

    def __identify_receiver(self):
        initial_packet = struct.pack("!B", 2)
        self.receiver_socket.sendto(initial_packet, self.dest)

receiver_instance = Receiver()
receiver_instance.listen()
