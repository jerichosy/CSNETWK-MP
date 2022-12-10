# Implement a UDP server

import json
import socket

# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
SERVER_ADDRESS = ('localhost', 10000)
print('starting up on %s port %s' % SERVER_ADDRESS)
server.bind(SERVER_ADDRESS)

clients = []

while True:
	print('waiting to receive message')
	data, address = server.recvfrom(1024)
	
	print('received %s bytes from %s' % (len(data), address))
	print(data)
	
    # Responses to commands
	try:
		data_json = json.loads(data.decode())
	except json.decoder.JSONDecodeError:  # Will also catch empty string (bytes)
		print('Error: Invalid JSON')
		continue
	# Every valid JSON input should have a 'command' key. We will not check for its presence.
	else:
		if data_json['command'] == 'join':
			clients.append(address)
			print('clients:', clients)
	# 	sent = server.sendto(data, address)
	# 	print('sent %s bytes back to %s' % (sent, address))
