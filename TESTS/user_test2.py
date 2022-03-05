
from user.view import *


def u2():
    MyClientGUI(('', 50002))


t2 = threading.Thread(target=u2)

t2.start()
