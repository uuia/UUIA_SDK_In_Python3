#@writer : zhongbr
#@filename:
#@purpose:
from hbut_data_sipder.hbut_api import user_info_API
class User_info:
    """
    用户信息类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求post参数字典
        :return: 获取到的数据，Python字典格式
        """
        return user_info_API(request.get("uuid"))
