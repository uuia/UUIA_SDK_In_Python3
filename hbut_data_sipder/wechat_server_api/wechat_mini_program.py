# @writer : zhongbr
# @filename:
# @purpose:
import requests, json
from hbut_data_sipder.config import *
from hbut_data_sipder.wechat_server_api.acess_token_admin import get_wechat_mini_program_token


def send_model_message(model_id, receiver, msg, form_id, page_url="", keyword=""):
    """
    发送微信小程序模板消息
    :param model_id: 模板ID
    :param receiver: 接收者
    :param msg: 消息体
    :param form_id: 表单ID
    :param page_url: 点击消息跳转的小程序页面
    :param keyword: 放大关键词
    :return:
    """
    token = get_wechat_mini_program_token()
    api_url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=" + token
    resp = requests.post(
        url=api_url,
        data=json.dumps({
            "touser": receiver,
            "template_id": model_id,
            "page": page_url,
            "form_id": form_id,
            "data": msg,
            "emphasis_keyword": keyword
        })
    )


def create_alarm_obj(receiver, alarm_time, model, form_id, args, keyword, page_url):
    """
    提前一周内创建提醒事件
    :param receiver: 接收者openid
    :param alarm_time: 提醒时间
    :param model: 模板ID
    :param form_id: 表单ID
    :param args: 模板消息内容参数
    :param keyword: 需要放大的关键词
    :param page_url: 点击消息跳转的URL
    :return:
    """
    database.add(mini_program_message.database_name,
                 {
                     mini_program_message.userid: receiver,
                     mini_program_message.send_time: str(alarm_time),
                     mini_program_message.args: {
                         "model_id": model,
                         "form_id": form_id,
                         "receiver": receiver,
                         "args": args,
                         "keyword": keyword,
                         "page_url": page_url
                     }
                 })


def res_code_to_openid(res_code):
    """
    获取微信openid
    :param res_code:向微信服务器换取openid的凭证
    :return:
    """
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={res_code}&grant_type=authorization_code"
    user_info = requests.get(
        url.format(appid=wechat_mini_program.appid, secret=wechat_mini_program.screct, res_code=res_code))
    userid, session_key = user_info.json()["openid"], user_info.json()["session_key"]
    return userid, session_key
