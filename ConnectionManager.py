import json
import socket


class ConnectionManager:
    def __init__(self, host, port):
        self.message_type_names = {}
        self.received_message_type_names = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, *args):
        if isinstance(args[0], socket.socket):
            target_socket = args[0]
            message_args = args[1:]
        else:
            target_socket = self.socket
            message_args = args

        try:
            message_dict = self.compile_message(*message_args)
            message_str = json.dumps(message_dict) + '\n'  # Newline delimiter
            target_socket.sendall(message_str.encode('utf-8'))
        except (socket.error, BrokenPipeError) as e:
            print(f"Error sending message: {e}")

    def compile_message(self, *args):
        message_type = args[0]
        message = {"TYPE": message_type}
        for i, arg in enumerate(args[1:]):
            key = self.message_type_names.get(message_type, [])[i]
            if key:
                message[key] = arg
        return message