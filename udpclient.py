import json
import random
import socket
import sys
import threading
from cmd import Cmd

# Create a UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Technically, this is not necessary for client but recvfrom() will complain without it.
client.bind(('localhost', random.randint(8000, 9000)))

class MBSClientShell(Cmd):
    prompt = ''
    intro = 'Welcome to the CSNETWK Message Board System.\nType /help or /? to list commands.\n'
    
    server_address = ()
    handle = ''

    def validate_command(self, command_args: str, required_arg_count: int) -> bool:
        split = command_args.split(maxsplit=1)
        if not split:
            print("Error: No arguments passed in command")
            return False
        elif len(split) != required_arg_count:
            print("Error: Invalid number of arguments")
            return False

        return split

    def precmd(self, line: str) -> str:
        if line:
            if line[0] == '/':
                line = line[1:]
            else:
                print("Error: Command must start with '/'")
                line = ''

        return super().precmd(line)

    def emptyline(self) -> None:
        # https://docs.python.org/3/library/cmd.html#cmd.Cmd.emptyline

        # Do not repeat last command when user presses enter with no input
        pass
    
    def do_join(self, arg: str) -> None:
        # Basic error checking
        args = self.validate_command(arg, 2)
        if not args:
            return

        # Command specific error checking
        if self.server_address:  # FIXME: CONSIDER MOVING TO SERVER
            print("Error: Already connected to server")
            return            
        
        try:
            self.server_address = (args[0], int(args[1]))
        except ValueError:
            print("Error: Invalid port number")
            return

        # connect to server
        # print('joining %s port %s' % self.server_address)
        request = json.dumps({'command': 'join'})
        client.sendto(request.encode(), self.server_address)

        # TODO: There's no check whether the dest. address is valid. But recvfrom() will complain if it's not.
        
        # Assuming joined anyway
        print('Connection to the Message Board Server is successful!')

    def do_register(self, arg: str) -> None:
        # Basic error checking
        if not arg:
            print("Error: No handle/alias passed in command")
            return

        # Command specific error checking
        if not self.server_address:  # FIXME: CONSIDER MOVING TO SERVER
            print("Error: Not connected to server. Use '/join <ip> <port>'")
            return

        if self.handle:  # FIXME: CONSIDER MOVING TO SERVER
            print("Error: Already registered")
            return

        self.handle = arg

        # Send data
        request = json.dumps({'command': 'register', 'handle': self.handle})
        client.sendto(request.encode(), self.server_address)

        # TODO: Handle duplicate checking (either re-prompt or auto-generate new handle)
        # response = client.recvfrom(1024)

        print(f"Welcome {self.handle}!")

    def do_msg(self, arg: str) -> None:
        # Basic error checking
        args = self.validate_command(arg, 2)
        if not args:
            return

        # Command specific error checking
        if not self.server_address:  # FIXME: CONSIDER MOVING TO SERVER 
            # This being the 2nd error check is okay
            print("Error: Not connected to server. Use '/join <ip> <port>'")
            return

        if not self.handle:  # FIXME: CONSIDER MOVING TO SERVER 
            print("Error: Not registered. Use '/register <handle>'")
            return

        dest_handle, message = args[0], args[1]            

        # Send data
        request = json.dumps({'command': 'msg', 'handle': dest_handle, 'message': message})
        client.sendto(request.encode(), self.server_address)
        print(f"[To {dest_handle}]: {message}")

    # Do not remove this command
    # def do_test(self, arg: str) -> None:
    #     print("test")

    def do_quit(self, arg: None) -> None:
        # close socket
        client.close()
        
        # TODO: gracefully handle thread exit

        # exit program
        sys.exit()
 

# Normally, recvfrom() is expected to be after sendto().
# However, because we may receive messages at any time, not just after sending data, we need to run it in a separate thread.
# That's because recvfrom() is blocking. If we run it in the main thread, the program will not be able to accept user input.
def receive():
    while True:
        # print('waiting to receive message')
        data, address = client.recvfrom(1024)
        
        # print('received %s bytes from %s' % (len(data), address))
        # print(data.decode())

        # Expect JSON
        response = json.loads(data.decode())
        # print(response)

        # If error received, print it and continue
        error = response.get('error')
        if error:
            print(f"Error: {error}")
            continue
            
        # Other types of response depending on the command
        if response['command'] == 'msg':
            print(f"[From {response['handle']}]: {response['message']}")

 
t = threading.Thread(target=receive)
t.start()
MBSClientShell().cmdloop()
