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
    intro = '\nWelcome to the CSNETWK Message Board System.\nType /help or /? to list commands.\n\nTo exit the program, enter /quit.\n'
    
    server_address = ()

    # Normally, recvfrom() is expected to be after sendto().
    # However, because we may receive messages at any time, not just after sending data, we need to run it in a separate thread.
    # That's because recvfrom() is blocking. If we run it in the main thread, the program will not be able to accept user input.
    def _receive(self):
        while True:
            # Note: Modifying outside variables in this thread may not be thread-safe.

            # print('waiting to receive message')
            data, address = client.recvfrom(1024)
            
            # print('received %s bytes from %s' % (len(data), address))
            # print(data.decode())

            # Expect JSON
            response = json.loads(data.decode())
            # print(response)

            # If error received, print it and continue
            error, info = response.get('error'), response.get('info')
            if error:
                print(f"Error: {error}")
                continue
            if info:
                print(info)
                continue
                
            # Process receive chain of the commands
            if response['command'] == 'msg':
                print(f"[From {response['handle']}]: {response['message']}")
            elif response['command'] == 'all':
                print(f"{response['handle']}: {response['message']}")

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
        if self.server_address:
            print("Error: Already connected to server")
            return            
        
        try:
            self.server_address = (args[0], int(args[1]))
        except ValueError:
            print("Error: Invalid port number")
            return

        request = json.dumps({'command': 'join'})
        client.sendto(request.encode(), self.server_address)

        try:
            data, _ = client.recvfrom(1024)
        except ConnectionResetError:
            self.server_address = ()
            print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
            return
        
        # print('Connection to the Message Board Server is successful!')

        response = json.loads(data.decode())
        info = response.get('info')
        print(info)

        t = threading.Thread(target=self._receive)
        t.start()

    def do_register(self, arg: str) -> None:
        # Basic error checking
        if not arg:
            print("Error: No handle/alias passed in command")
            return

        # Command specific error checking
        if not self.server_address:
            print("Error: Not connected to server. Use '/join <ip> <port>'")
            return

        # Send data
        request = json.dumps({'command': 'register', 'handle': arg})
        client.sendto(request.encode(), self.server_address)

    def do_msg(self, arg: str) -> None:
        # Basic error checking
        args = self.validate_command(arg, 2)
        if not args:
            return

        # Command specific error checking
        if not self.server_address:
            # This being the 2nd error check is okay
            print("Error: Not connected to server. Use '/join <ip> <port>'")
            return

        dest_handle, message = args[0], args[1]            

        # Send data
        request = json.dumps({'command': 'msg', 'handle': dest_handle, 'message': message})
        client.sendto(request.encode(), self.server_address)
        # print(f"[To {dest_handle}]: {message}")  # handled in receive() thread

    def do_all(self, arg: str) -> None:
        # Basic error checking
        args = self.validate_command(arg, 1)
        if not args:
            return

        # Command specific error checking
        if not self.server_address:
            # This being the 2nd error check is okay
            print("Error: Not connected to server. Use '/join <ip> <port>'")
            return

        message = args[0]          

        # Send data
        request = json.dumps({'command': 'all', 'message': message})
        client.sendto(request.encode(), self.server_address)

    # Do not remove this command
    # def do_test(self, arg: str) -> None:
    #     print("test")

    # This is necessary because CTRL+C will not interrupt recvfrom() at least on Windows.
    def do_quit(self, arg: None) -> None:  # This is necessary 
        # close socket
        client.close()
        
        # TODO: gracefully handle thread exit

        # exit program
        sys.exit()

 
# t = threading.Thread(target=receive)
# t.start()
MBSClientShell().cmdloop()
