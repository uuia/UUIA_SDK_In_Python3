#@writer : zhongbr
#@filename: bind.py
#@purpose: 绑定账号的数据层实现

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
        # TODO ( UUIA )：请在这里完成用户绑定的数据获取层