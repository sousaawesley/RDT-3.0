import socket
import struct

class Receiver:
    def __init__(self):
        self.seq_number = None


    def __init__(self, ip="127.0.0.1", port=60000):
        self.server_ip = ip
        self.server_port = port
        self.dest = (self.server_ip, self.server_port)
        self.receiver_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.receiver_socket.bind(('', 0))
        self.receiver_port = self.receiver_socket.getsockname()[1]
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
    
    def __checksum_calculator(self, packet):
        if len(data) % 2 == 1:
            data += b'\0'
        s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff

    def __not_corrupted(self, packet):
        checksum = self.unpack(packet)[0][4]
        return self.__checksum_calculator(packet) == checksum
    
    def check_seq(self, packet):
        pkt_seq = self.unpack(packet)[0][2]
        
        if pkt_seq is None:
            self.seq_number = pkt_seq
        
        if pkt_seq == self.seq_number:
            self.seq_number = ~self.seq_number
            return True
        
        return False

    def __udt_send(self, pkt):
        self.socket_send.sendto(pkt, self.dest)

    def listen(self):
        print(f"Listening on port {self.receiver_port}...")
        packet, _ = self.receiver_socket.recvfrom(1024)
        tupla = self.unpack(packet)
        print(f"Received packet from: {tupla[0][0]}")
        print(f"number seq: {tupla[0][2]}")
        print(f"checksum number: {tupla[0][4]}")
        print(f"message: {tupla[1].decode()}")
        

    def __identify_receiver(self):
        initial_packet = struct.pack("!B", 2)
        self.receiver_socket.sendto(initial_packet, self.dest)

receiver_instance = Receiver()
while True:
    receiver_instance.listen()
