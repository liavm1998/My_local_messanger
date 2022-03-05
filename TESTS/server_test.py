import socket


from Server.server import Server
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(local_ip)
my_server = Server(local_ip)
