#@writer : zhongbr
#@filename:
#@purpose:

class Lack_necessary_info_exception(Exception):
    def __init__(self,message):
        self.message = message

    def __str__(self):
        return self.message

