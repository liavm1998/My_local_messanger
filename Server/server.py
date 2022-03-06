import os
import pickle
import sys
import threading
import socket
from collections import OrderedDict
from functools import partial
import bisect
from typing import List

from packets import packet
from packets.packet import MSG_TYPE, REQ_TYPE, UDP_TYPE


def index_of_seq(acks: list, seq: int):
    for i in range(len(acks)):
        if acks[i][0] == seq:
            return i
    return -1


class Server:
    def __init__(self, ip_address):
        self.my_address = (ip_address, 50000)  # server address
        self.users = {}  # ((socket,address):name)
        self.clients_threads = []
        self.files = ["cat_pic.jpeg", "weird_cat.jpeg", "text.txt"]
        self.stopped_download = None
        try:
            self.SelfSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for Client to connect
        except socket.error:
            print("ERROR with Server Socket creation")
        try:
            self.SelfSock.bind(self.my_address)
        except socket.error:
            print("ERROR with Server Socket bind")

        self.listen()
        self.SelfSock.close()

    def listen(self):
        self.SelfSock.listen(5)
        while True:
            user_socket, user_address = self.SelfSock.accept()
            accepted = (user_socket, user_address)
            # client accepting
            user_name = user_socket.recv(1024).decode()
            # user_name = user_name[1:]
            self.users[accepted] = user_name
            handle = partial(self.user_handler, user_id=accepted)
            user_handle = threading.Thread(target=handle)
            user_handle.start()

    def user_handler(self, user_id):
        user_sock = user_id[0]
        print("user " + self.users[user_id] + " connected")
        while True:
            try:
                pkt = user_sock.recv(4096).decode()
            except socket.error:
                continue
            if pkt != '|exit|':
                self.handle_pkt(pkt, user_sock)
            else:
                self.remove_user(user_id)
                break

    def get_user_by_name(self, find: str):
        for key in self.users.keys():
            if self.users[key] == find:
                return key[0]
        print("user user not found")

    def handle_pkt(self, pkt: str, user_sock):
        message = pkt.split(",")
        if message[0] is MSG_TYPE:
            if message[2] == 'broadcast':
                self.broadcast(pkt.encode())
            else:
                listening_user = self.get_user_by_name(message[2])
                listening_user.send(pkt.encode())
        elif message[0] is REQ_TYPE:
            if not (message[1] == 'True'):  # files
                print(message[1], 'True')
                response = packet.user_list_resp(self.get_name_list())
            else:
                response = packet.file_list_resp(self.files)
            try:
                user_sock.send(response.encode())
            except socket.error as err:
                print("server response error")
                raise err
        elif message[0] is UDP_TYPE:
            self.send_file(message)

    def broadcast(self, pkt):
        sockets = []
        for key in self.users.keys():
            sockets.append(key[0])
        for listening_user in sockets:
            listening_user.send(pkt)

    def remove_user(self, user_id):
        pkt = self.users[user_id] + " left the chat"
        user_id[0].send("bye".encode())
        del self.users[user_id]
        self.broadcast(pkt.encode())

    def get_name_list(self):
        ans = []
        for user in self.users.values():
            ans.append(user)
        return ans

    def send_file(self, message):
        """4 (UDP) , downloader name , ip , port , file name , mtu , window"""
        file_name = message[4]
        loc = os.path.dirname(os.path.abspath(__file__))
        loc = loc.split('/')
        file_directory = ''
        for i in range(len(loc) - 1):
            file_directory += loc[i] + '/'
        file_directory += 'files/'
        a = 0
        file = open(file_directory + file_name, 'rb')

        mtu = int(message[5])
        window = int(message[6])
        packets = file_to_packets(file, mtu)

        window_reach = int(window / mtu)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self_add = (self.my_address[0], 30001)

        udp_socket.bind(self_add)

        ip = message[2][2:len(message[2]) - 1]
        port = int(message[3][0:len(message[3]) - 1])
        address = (ip, port)
        udp_socket.connect(address)
        udp_socket.send(str(self_add).encode())
        acks = []
        size = 0
        print("seq number before sending")
        for data in packets:
            size += len(data)
            acks.append((size, False))

        acks.sort(key=lambda x: x[0])  # just in case
        # start selective repeat
        window_head = 0
        size_alert = True
        while window_head + window_reach <= len(packets) or not acks[window_head][1]:
            i = 0
            try:
                for i in range(window_head, window_head + window_reach, 1):
                    if not acks[i][1]:
                        udp_socket.settimeout(50)
                        try:
                            udp_socket.send(packets[i])
                            # if size >= 10000 and size_alert:
                            #     udp_socket.send(pickle.dumps((0, "alert")))
                            #     cont = self.SelfSock.recv(100).decode()
                            #     if cont == 'no':
                            #         self.stopped_download = (file_name, window_head)
                            #         return
                            ack = int(udp_socket.recv(mtu + 100).decode())
                            index = index_of_seq(acks, int(ack))
                            acks[index] = (ack, True)
                            while acks[window_head][1]:
                                window_head += 1
                        except Exception as err:
                            continue
            except IndexError as err:
                break
        udp_socket.send(pickle.dumps((0, 'end')))
        udp_socket.close()

    # def ack_listen(self, q: OrderedDict, mtu, udp_socket: socket.socket):
    #     while True:
    #         ack = udp_socket.recv(mtu).decode()
    #         if ack == "finish":
    #             break
    #         for tup in q:
    #             if tup[2] == int(ack.split(',')[1]):
    #                 tup[0] = True


def file_to_packets(file, mtu: int):
    try:
        data = file.read(mtu)
        packets = []
        sequence = 0
        i = 0
        print("file to packets:")
        while data:
            size = len(data)
            sequence += size
            pkt = pickle.dumps((sequence, data))
            packets.append(pkt)
            data = file.read(mtu)
    except Exception as err:
        raise err
    return packets


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(local_ip)
    # my_server = Server('10.0.2.4') for amosi linox
    my_server = Server(local_ip)
