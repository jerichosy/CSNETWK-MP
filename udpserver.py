# Implement a UDP server

import json
import socket

# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
SERVER_ADDRESS = ('localhost', 9999)
print('starting up on %s port %s' % SERVER_ADDRESS)
server.bind(SERVER_ADDRESS)

clients = {}  # {address: handle}

while True:
	print('waiting to receive message')
	data, address = server.recvfrom(1024)
	
	print('received %s bytes from %s' % (len(data), address))
	print(data)
	
	# TODO: comment out after done debugging client
	# sent = server.sendto(data, address)
	# print('sent %s bytes back to %s' % (sent, address))

    # Responses to commands
	try:
		data_json = json.loads(data.decode())
	except json.decoder.JSONDecodeError:  # Will also catch empty string (bytes)
		print('Error: Invalid JSON')
		continue
	# Every valid JSON input should have a 'command' key. We will not check for its presence.
	else:
		if data_json['command'] == 'join':
			clients.update({address: None})
			print('clients:', clients)

		elif data_json['command'] == 'register':
			handle = data_json['handle']

			if clients.get(address) is not None:
				print('Error: Already registered')
				# inform sender of error
				response = json.dumps({'error': 'Already registered.'})
				server.sendto(response.encode(), address)
				continue

			# check if handle already exists
			if handle in clients.values():
				print('Error: Handle already exists')
				# inform sender of error
				response = json.dumps({'error': 'Registration failed. Handle is taken.'})
				server.sendto(response.encode(), address)
				continue

			# update clients
			clients.update({address: handle})
			print('clients:', clients)

			# inform sender of success
			response = json.dumps({'info': f"Welcome {handle}!"})
			server.sendto(response.encode(), address)

		elif data_json['command'] == 'msg':
			destination_handle = data_json['handle']
			print('destination_handle:', destination_handle)
			try:
				destination_addr = list(clients.keys())[list(clients.values()).index(destination_handle)]
			except ValueError:
				destination_addr = None
			print('destination_addr:', destination_addr)
			source_handle = clients.get(address)
			print('source_handle:', source_handle)

			# error check if handle exists
			if not destination_addr:
				print('Error: Invalid handle')
				# inform sender of error
				response = json.dumps({'error': 'Handle not found'})
				server.sendto(response.encode(), address)
				continue

			# change handle to source handle and send to destination
			data_json.update({'handle': source_handle})
			response = json.dumps(data_json)
			server.sendto(response.encode(), destination_addr)

			# inform sender of success
			response = json.dumps({'info': f"[To {destination_handle}]: {data_json['message']}"}) #FIXME:
			server.sendto(response.encode(), address)
