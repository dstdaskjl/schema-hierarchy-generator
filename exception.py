class DuplicateHeaderError(Exception):
    def __init__(self, error):
        super().__init__(error)
        self.error = error

    def print_errors(self):
        print(self.__class__.__name__ + ': ' + self.error)
