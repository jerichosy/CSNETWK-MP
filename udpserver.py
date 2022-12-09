# Implement a UDP server

import socket

# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
SERVER_ADDRESS = ('localhost', 10000)
print('starting up on %s port %s' % SERVER_ADDRESS)
server.bind(SERVER_ADDRESS)

while True:
	print('waiting to receive message')
	data, address = server.recvfrom(1024)
	
	print('received %s bytes from %s' % (len(data), address))
	print(data)
	
    # Responses to commands
	# if data:
	# 	sent = server.sendto(data, address)
	# 	print('sent %s bytes back to %s' % (sent, address))
