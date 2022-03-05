
from user.view import *


def u3():
    MyClientGUI(('', 50003))


t3 = threading.Thread(target=u3)

t3.start()
