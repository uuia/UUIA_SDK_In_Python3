#@writer : zhongbr
#@filename:
#@purpose:

class Campus_card:
    """
    一卡通信息类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求post参数字典
        :return: 获取到的数据，Python字典格式
        """
        # TODO ( UUIA )：请在这里完成用户一卡通信息的数据获取层