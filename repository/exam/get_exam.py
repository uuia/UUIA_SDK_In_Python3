#@writer : zhongbr
#@filename: get_exam.py
#@purpose: 获取用户考试安排的数据层实现

class Exam:
    """
    考试安排的类
    """
    def get_data(self,request):
        """
        数据层实现对接方法，请在此方法内返回获取到的数据
        :param request: http请求
        :return: 获取到的数据，Python字典格式
        """
        # TODO ( UUIA )：请在这里完成用户考试安排的数据获取层