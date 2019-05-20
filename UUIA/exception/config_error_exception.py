# @writer : zhongbr
# @filename:
# @purpose: 配置错误的异常

class Config_error_exception(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
