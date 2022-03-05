
from user.view import *


def u4():
    MyClientGUI(('', 50004))


t4 = threading.Thread(target=u4)

t4.start()
