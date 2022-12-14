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
	
	# echo for debug
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
		# Note: Do not specify command syntax in error messages. The server doesn't know how the client parses commands.

		if data_json['command'] == 'join':
			# update clients
			clients.update({address: None})
			print('clients:', clients)

			# inform sender of success
			response = json.dumps({'command': 'info', 'message': 'Connection to the Message Board Server is successful! Please register.'})
			server.sendto(response.encode(), address)

		elif data_json['command'] == 'leave':
			# broadcast to all clients
			response = json.dumps({'command': 'info', 'message': f'{handle} left the chat'}).encode() #pre
			for client in clients:
					server.sendto(response, client)

			# update clients
			clients.pop(address)  # will remove regardless of whether handle is registered
			print('clients:', clients)

			# inform sender of success
			response = json.dumps({'command': 'info', 'message': 'You have left the Message Board Server.'})
			server.sendto(response.encode(), address)

		elif data_json['command'] == 'register':
			handle = data_json['handle']

			if clients.get(address) is not None:
				print('Error: Already registered')
				# inform sender of error
				response = json.dumps({'command': 'error', 'message': 'Already registered.'})
				server.sendto(response.encode(), address)
				continue

			# check if handle already exists
			if handle in clients.values():
				print('Error: Handle already exists')
				# inform sender of error
				response = json.dumps({'command': 'error', 'message': 'Registration failed. Handle is taken.'})
				server.sendto(response.encode(), address)
				continue

			# update clients
			clients.update({address: handle})
			print('clients:', clients)

			# broadcast to all clients
			response = json.dumps({'command': 'info', 'message': f'{handle} joined the chat'}).encode() #pre-encode response
			for client_address in clients:
				server.sendto(response, client_address)

			# inform sender of success
			response = json.dumps({'command': 'info', 'message': f"Welcome {handle}!"})
			server.sendto(response.encode(), address)

		# below this line, handle must be registered
		# error check if not registered
		elif clients.get(address) is None:
			print('Error: Not registered')
			# inform sender of error
			response = json.dumps({'command': 'error', 'message': 'Not registered.'})
			server.sendto(response.encode(), address)
			continue

		elif data_json['command'] == 'list':
			# get list of handles
			handle_list = list(clients.values())
			
			# send list of handles
			response = json.dumps({'command': 'info', 'message': f"List of users: {', '.join(handle_list)}"})
			server.sendto(response.encode(), address)

		elif data_json['command'] == 'msg':
			# Note: Allow the sender to send a message to themselves

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
				response = json.dumps({'command': 'error', 'message': 'Handle not found'})
				server.sendto(response.encode(), address)
				continue

			# change handle to source handle and send to destination
			data_json.update({'handle': source_handle})
			response = json.dumps(data_json)
			server.sendto(response.encode(), destination_addr)

			# inform sender of success
			response = json.dumps({'command': 'info', 'message': f"[To {destination_handle}]: {data_json['message']}"})
			server.sendto(response.encode(), address)
			
		elif data_json['command'] == 'all':
			# Note: Unlike 'msg' where the sender can only send to registered clients, 
			# 		'all' will the sender can send to all clients (including unregistered clients)
			#       This behavior is okay.

			print('destination_addr:', "ALL")
			source_handle = clients.get(address)
			print('source_handle:', source_handle)

			# change handle to source handle and send to All destinations
			data_json.update({'handle': source_handle})
			response = json.dumps(data_json).encode() #pre-encode response
			for client_address in clients:
				server.sendto(response, client_address)

			# sender was already informed of success in the above loop
