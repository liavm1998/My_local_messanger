
from user.view import *


def u1():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    MyClientGUI((local_ip, 50001))


# def u2():
#     user2 = MyClientGUI(('', 50002))
#
#
# def u3():
#     user3 = MyClientGUI(('', 50003))


t1 = threading.Thread(target=u1)
# t2 = threading.Thread(target=u2)
# t3 = threading.Thread(target=u3)

t1.start()
# t2.start()
# t3.start()
