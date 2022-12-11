# Implement a UDP server

import json
import socket

# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
SERVER_ADDRESS = ('localhost', 9999)
print('starting up on %s port %s' % SERVER_ADDRESS)
server.bind(SERVER_ADDRESS)

clients = {}  # {handle: address}

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
			# TODO: Not really sure if we're supposed to do anything here
			pass

		elif data_json['command'] == 'register':
			clients.update({data_json['handle']: address})
			print('clients:', clients)

		elif data_json['command'] == 'msg':
			destination_handle = data_json['handle']
			print('destination_handle:', destination_handle)
			destination_addr = clients.get(destination_handle)
			print('destination_addr:', destination_addr)
			source_handle = list(clients.keys())[list(clients.values()).index(address)]
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
