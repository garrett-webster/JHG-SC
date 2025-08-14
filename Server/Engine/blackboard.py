class BlackBoard:
    def __init__(self):
        self.board = {}

    def scribe(self, key, value):
        self.board[key] = value

    def erase(self, key):
        self.board.pop(key, None)

    def read(self, key):
        return self.board.get(key, None)

    def clear(self):
        self.board = {}
