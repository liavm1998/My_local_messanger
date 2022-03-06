import user.view
from Server.server import *


hostname = socket. gethostname()
local_ip = socket. gethostbyname(hostname)
server = Server(local_ip)
user1 = user.view.MyClientGUI(('', 50001))
user2 = user.view.MyClientGUI(('', 50001))
user3 = user.view.MyClientGUI(('', 50001))

