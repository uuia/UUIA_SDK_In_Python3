#@writer : zhongbr
#@filename: bind.py
#@purpose: 绑定账号的数据层实现
from hbut_data_sipder.hbut_api import bind_API

class Bind:
    """
    绑定账号的类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求post参数字典
        :return: 获取到的数据，Python字典格式
        """
        return bind_API(request)
