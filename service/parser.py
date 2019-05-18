#@writer : zhongbr
#@filename:
#@purpose:
import json
import domain.get_response_data as uuia
from util.uuid_logger import Uuia_logger

def paeser(request,form):
    """
    UUIA解析路由函数
    :param request: 待解析的http请求对象
    :return: UUIA解析结果，None为出现异常
    """
    group,action = form.get("group"),form.get("action")
    return handle_for_base(group,action,request,form)

def handle_for_base(group,action,request_object,form):
    """
    路由函数
    :param group: 用户组
    :param action: 用户要执行的动作
    :param request_object: http请求对象
    :return: 返回给中心服务器的json对象
    """
    if group == "base":
        return uuia.get_response_data(action,request_object,form)
    else:
        Uuia_logger().i("UUIA Parser","其他非法请求")
        return None
