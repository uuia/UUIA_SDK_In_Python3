#@writer : zhongbr
#@filename:
#@purpose: uuia框架配置部分

class Constant:
    def __init__(self, app_name, app_id, app_token):
        # 框架配置
        self.app_id = app_id
        self.app_token = app_token
        self.app_name = app_name  # 应用名称
        # API 响应码
        self.RESPONSE_CODE_OK = "200"
        self.RESPONSE_CODE_UNAUTHORIZED = "401"
        self.RESPONSE_CODE_INTERNAL_SERVER_ERROR = "504"
        self.RESPONSE_CODE_GATEWAY_TIMEOUT = "504"
        #API响应消息
        self.RESPONSE_MSG_OK = "[{}] OK".format(self.app_name)
        self.RESPONSE_MSG_UNAUTHORIZED = "[{}] Unauthoruzed".format(self.app_name)
        self.RESPONSE_MSG_INTERNAL_SERVER_ERROR  = "[{}] Internal Server Error".format(self.app_name)
        self.RESPONSE_MSG_ACTION_DONT_EXIST = "[{}] The Action In Request Is Not Exist".format(self.app_name)
        self.RESPONSE_MSG_GATEWAY_TIMEOUT = "[{}] Gateway Timeout".format(self.app_name)