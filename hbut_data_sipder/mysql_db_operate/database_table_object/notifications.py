# @writer : zhongbr
# @filename:
# @purpose:
from hbut_data_sipder.config import *
import datetime


def create_notifications(notification_title, notification_text, notification_type):
    data_to_save = \
        {
            notification.title: notification_title,
            notification.text: notification_text,
            notification.type: notification_type,
            notification.time: str(datetime.datetime.today()).split(".")[0]
        }
    database.add(
        notification.database_name,
        data_to_save
    )
    return database.select_single(notification.database_name, data_to_save, notification.id)


class Notification:
    def __init__(self, require_dict):
        self.id, self.title, self.time, self.text, self.type = \
        database.select(notification.database_name, select_data=require_dict)[0]


def get_notifications_of_any_type(type_):
    pre_data = database.select(notification.database_name, [notification.id, notification.time],
                               {notification.type: type_})
    today = datetime.datetime.today()
    if len(pre_data) == 0:
        return False
    minums = (today.timestamp() - pre_data[0]["time"].timestamp(), pre_data[0]["id"])
    for notification_ in pre_data[1:]:
        if today.timestamp() - notification_["time"].timestamp() < minums[0]:
            minums = (today.timestamp() - notification_["time"].timestamp(), notification_["id"])
    return Notification({notification.id: minums[1]})


def get_all_notifications():
    pre_data = database.select(notification.database_name)
    result = []
    for i in pre_data:
        result.append({
            "id": i[0],
            "title": str(i[1]),
            "time": str(i[2]),
            "text": str(i[3]),
            "type": i[4]
        })
    return result


if __name__ == '__main__':
    """
    通知关键词           对应页面
    ----------------------------------------
    open_notification   小程序打开即检查的通知
    bind                绑定账户页面通知
    sign_in             注册页面通知
    find_teacher        查找老师页面的通知
    gpa_calculator      查询绩点页面的通知
    grade_query         查询成绩页面的通知
    index               首页通知
    main_menu           菜单页面通知
    setting             我的 页面通知
    physic_test         物理实验页面的通知
    qrcode              二维码页面通知
    elective_query      选修课页面通知
    free_classroom      空教室页通知
    schedule            课表页通知
    """
    create_notifications(
        notification_title="小程序更新啦！",
        notification_text="1.由于用户反馈小程序内按钮颜色为灰色会产生按钮不能点击的错觉，本次更新更换了小程序内按钮的颜色！<text>\n</text>"
                          "2.小程序加入通知功能，方便开发者发送以及您获取小程序的最新信息！\n"
                          "3.选修课查询页面改进，显示更加清晰！\n"
                          "如果您使用过程中遇到任何问题，欢迎您反馈给我 反馈邮箱 zph1178395080@gmail.com\n"
                          "钟摆人。",
        notification_type="main_menu"
    )
