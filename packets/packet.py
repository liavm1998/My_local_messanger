

MSG_TYPE = '1'
REQ_TYPE = '2'
RESP_TYPE = '3'
UDP_TYPE = '4'

file = True
names = False
"""
---------------------------message packet template----------------------------
 1 (message type) , sender name , receiver name (could be 'broadcast'), message
-------------------------------------------------------------------------------

-----------------------------client request packet template----------------------
 2 (request type) , files/names(boolean)
-------------------------------------------------------------------------------

--------------------------server response packet template------------------------
 3 (response) , files/names files/names(boolean) , the list in str format separate with '|'
-------------------------------------------------------------------------------

---------------------------message packet template----------------------------
 4 (UDP) , downloader name , extension , file name , mtu , window
-------------------------------------------------------------------------------
"""


def get_user_list():
    return REQ_TYPE + "," + str(False)


def user_list_resp(users: list):
    pkt = RESP_TYPE + "," + str(False) + ","

    for name in users:
        pkt += "|" + name
    return pkt


def get_files_list():
    return REQ_TYPE + "," + str(True)


def file_list_resp(files: list):
    pkt = RESP_TYPE + "," + str(True) + ","
    for f in files:
        pkt += "|" + f
    return pkt


def create_message(sender_name, receiver_name, message):
    return str(MSG_TYPE + "," + sender_name + "," + receiver_name + "," + message)


def download_req(downloader_name: str, address: tuple, file_name: str, mtu: int, window: int):
    return UDP_TYPE + "," + downloader_name + "," + str(address) + "," + file_name + "," + str(mtu) + "," + str(window)
