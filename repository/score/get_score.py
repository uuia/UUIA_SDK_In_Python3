#@writer : zhongbr
#@filename: get_score.py
#@purpose: 获取用户成绩的数据层实现

class Score:
    """
    成绩查询类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求post参数字典
        :return: 获取到的数据，Python字典格式
        """
        # TODO ( UUIA )：请在这里完成用户成绩的数据获取层