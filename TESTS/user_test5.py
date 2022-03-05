
from user.view import *


def u5():
    MyClientGUI(('', 50005))


t5 = threading.Thread(target=u5)

t5.start()
