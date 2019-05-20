# @writer : zhongbr
# @filename:
# @purpose:

class Callback_exception(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
