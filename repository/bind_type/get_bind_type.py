#@writer : zhongbr
#@filename: bind_type.py
#@purpose: 需要绑定的账户类型的数据层实现

class Bind_type:
    """
    需要绑定的绑定账号的类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求post参数字典
        :return: 获取到的数据，Python字典格式
        """
        # TODO ( UUIA )：请在这里完成用户需绑定账户类型的数据获取层