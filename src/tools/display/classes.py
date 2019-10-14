class Command:

    def __init__(self, name, function, args):
        self.name = name
        self.function = function
        self.args = args


    def call(self):
        return self.function.call

