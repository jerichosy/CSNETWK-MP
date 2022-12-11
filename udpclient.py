import json
import socket
from cmd import Cmd

# Create a UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class MBSClientShell(Cmd):
    prompt = '(MBS Client) '
    
    server_address = ()

    def precmd(self, line: str) -> str:
        if line:
            if line[0] == '/':
                line = line[1:]
            else:
                print("Command must start with '/'")
                line = ''

        return super().precmd(line)

    def emptyline(self) -> None:
        # https://docs.python.org/3/library/cmd.html#cmd.Cmd.emptyline

        # Do not repeat last command when user presses enter with no input
        pass
    
    def do_join(self, arg: str) -> None:
        # Basic error checking
        args = validate_command(arg, 2)
        if not args:
            return

        # Command specific error checking
        if self.server_address:  # TODO: Not sure if this is meant to be a client-side check
            print("Error: Already connected to server")
            return            
        
        try:
            self.server_address = (args[0], int(args[1]))
        except ValueError:
            print("Error: Invalid port number")
            return

        # connect to server
        print('joining %s port %s' % self.server_address)
        request = json.dumps({'command': 'join'})
        client.sendto(request.encode(), self.server_address)

    def do_msg(self, message: str) -> None:
        # Basic error checking
        if not message:
            print("Error: No message passed in command")
            return

        # Command specific error checking
        if not self.server_address:  # This being the 2nd error check is okay
            print("Error: Not connected to server. Use '/join <ip> <port>'")
            return

        # Send data
        print('sending "%s"' % message)
        sent = client.sendto(message.encode(), self.server_address)
        print(sent)

    # Do not remove this command
    # def do_test(self, arg: str) -> None:
    #     print("test")
 

def validate_command(command_args: str, required_arg_count: int) -> bool:
    split = command_args.split()
    if not split:
        print("Error: No arguments passed in command")
        return False
    elif len(split) != required_arg_count:
        print("Error: Invalid number of arguments")
        return False

    return split
 
MBSClientShell().cmdloop()
print("cmdloop exited")  # Should never get here
