import pickle
import socket
from collections import OrderedDict

from packets import packet
from packets.packet import MSG_TYPE, RESP_TYPE
from user import view


def size_alert():
    view.size_alert()


class user_module:
    def __init__(self, address: tuple, user_name: str):
        self.mtu = 1500
        self.window = 10000
        self.stopped_download = None
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.user_name = user_name
        except socket.error as error:
            print(" user socket init fail")
            raise error
        try:
            self.sock.bind(address)
        except socket.error as error:
            print(" user socket bind fail")
            raise error

    def connect(self, address: tuple, user_name: str):
        # if self.user_name is not None:
        #     self.__init__()
        # self.user_name = user_name
        try:
            self.sock.connect(address)
            self.sock.send(user_name.encode())

        except socket.error as err:
            print("ERROR, Client failed to connect the Server")
            raise err

    def disconnect(self):
        """
        This method disconnects the Client from the Server
        :return:
        """
        self.sock.send('|exit|'.encode())
        self.sock.close()

    def alert_ans(self, ans: str):
        self.sock.send(ans.encode())

    def receive(self):
        try:
            pkt = self.sock.recv(1024).decode()
            if pkt == 'bye':
                return None
            if pkt == 'alert':
                size_alert()
            return pkt
        except socket.error:
            print('error at Client side receiving')

    def send_msg(self, msg, receiver_name='broadcast'):
        msg = packet.create_message(self.user_name, receiver_name, msg)
        try:
            self.sock.send(msg.encode())
        except socket.error:
            print('error at Client side sending')

    def get_names_list(self):
        """
        This method returns all the Client names in the chat
        :return:
        """
        try:
            self.sock.send(packet.get_user_list().encode())
        except socket.error as err:
            raise err

    def get_file_list(self):
        """
            This method returns all the file names in the Server.
            :return:
            """
        try:
            self.sock.send(packet.get_files_list().encode())
        except socket.error as err:
            raise err

    def download_file(self, file_name: str):
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.mtu)
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        udp_address = (local_ip, 30000)
        udp_socket.bind(udp_address)
        pkt = packet.download_req(self.user_name, udp_address, file_name, self.mtu, self.window)
        d = OrderedDict()
        self.sock.send(pkt.encode())
        size = 0
        pkt = udp_socket.recv(self.mtu + 33).decode()
        pkt = pkt.split(',')
        ip = pkt[0][2:len(pkt[0]) - 1]
        port = int(pkt[1][0:len(pkt[1]) - 1])
        server_udp = (ip, port)
        udp_socket.connect(server_udp)
        # if self.stopped_download and (self.stopped_download[0] == file_name):
        #     d = self.stopped_download[1]
        #     size = max(dict(d).keys())
        while pkt != 'end':
            pkt = udp_socket.recv(self.mtu + 100)
            sequence = len(pkt)
            size += sequence
            pkt = pickle.loads(pkt)
            x, data = pkt
            if data == 'end':
                break
            if data == 'alert':
                self.stopped_download = (file_name, d)
            ack = size
            d[ack] = data
            udp_socket.send(str(ack).encode())
        file = open("udp_transferred"+file_name, 'wb')
        for item in d.items():
            file.write(item[1])
        file.close()
        udp_socket.close()



