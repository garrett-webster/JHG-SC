class GroupLogger():
    def __init__(self):
        # I THINK this will do it. we need room for the bot
        self.group_data = []

    def add_group(self, group_data):
        self.group_data.append(group_data)

    def get_group_data(self):
        return self.group_data

    def reset_group_data(self):
        self.group_data = []

    def print_group_data(self):
        print(self.group_data)