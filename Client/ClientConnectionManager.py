import json
from collections import deque
from ConnectionManager import ConnectionManager


class ClientConnectionManager(ConnectionManager):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.socket.connect((host, port))
        self.buffer = ""  # Accumulate partial messages here

        self.message_type_names = {
            "SUBMIT_JHG": ["CLIENT_ID", "ROUND_NUMBER", "ALLOCATIONS"],
            "SUBMIT_SC": ["CLIENT_ID", "FINAL_VOTE"],
        }

    def initialize_connection(self):
        message = {"NEW_INPUT": "new_input"}
        self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))

    def get_message(self):
        messages = deque()
        while True:
            try:
                chunk = self.socket.recv(4096).decode('utf-8')
                if not chunk:
                    raise ConnectionError("Socket closed")

                self.buffer += chunk

                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            messages.append(message)
                        except json.JSONDecodeError as e:
                            print(f"Malformed JSON line: {line}")
                            continue

                if messages:
                    return messages

            except (ConnectionError, TimeoutError, OSError) as e:
                print(f"Socket error: {e}")
                break