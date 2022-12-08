import socket
from cmd import Cmd

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ()  #FIXME: scoping
joined = False

class MBSClientShell(Cmd):
    prompt = 'MBS Client> '
    
    def do_join(self, arg):
        global joined
        if joined:
            print('already joined')
            return

        # split arg into server_address
        split = arg.split()
        server_address = split[0], int(split[1])
        print('joining %s port %s' % server_address)
        # connect to server
        # sock.connect(server_address)
        # send join message in JSON format
        message = '{"command":"join"}'
        sock.sendto(message.encode(), server_address)
        # join successful
        joined = True

    def do_msg(self, arg):
        message = arg
        # Send data
        print('sending "%s"' % message)
        sent = sock.sendto(message.encode(), server_address)
        print(sent)
 
MBSClientShell().cmdloop()
print("after")