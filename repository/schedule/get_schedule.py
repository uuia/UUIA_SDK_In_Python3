#@writer : zhongbr
#@filename:
#@purpose:

class Schedule:
    """
    课表类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求
        :return: 获取到的数据，Python字典格式
        """
        # TODO ( UUIA )：请在这里完成用户课表的数据获取层