#@writer : zhongbr
#@filename:
#@purpose:
from ..domain.get_response_data import get_response_data
from ..util.uuia_logger import Uuia_logger


def paeser(request, form, callbacks):
    """
    UUIA解析路由函数
    :param request: 待解析的http请求对象
    :param form: 请求提交的表单字典
    :param callbacks: 动作回调函数字典
    :return: UUIA解析结果，None为出现异常
    """
    group,action = form.get("group"),form.get("action")
    return handle_for_base(group, action, request, form, callbacks)


def handle_for_base(group, action, request_object, form, callbacks):
    """
    路由函数
    :param group: 用户组
    :param action: 用户要执行的动作
    :param request_object: http请求对象
    :return: 返回给中心服务器的json对象
    """
    return get_response_data(group, action, request_object, form, callbacks)
