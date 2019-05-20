from UUIA import Uuia
from hbut_data_sipder.hbut_api import *

uuia = Uuia(
    app_id="this_is_your_app_id",
    app_token="this_is_your_app_token",
    app_name="this_is_your_app_name",
    running_port=443,  # 运行端口
    running_ip="127.0.0.1",  # 运行Ip
    thread_name=__name__,  # 监听线程
    running_domain="/uuia"  # 运行url
)


# 绑定获取需绑定账户的函数
@uuia.bind_action_callback_function(groups=["base", "base1"], actions=["bindType"])
def get_bind_types(uuid, request_args):
    return {
        "uuid": uuid,
        "accounts": [
            {"account1": "001"},
            {"account2": "002"},
            {"account3": "003"},
            {"account4": "004"},
        ]
    }


# 绑定查询成绩的函数
@uuia.bind_action_callback_function(groups=["base"], actions=["score"])
def get_score(uuid, request_args):
    return score_API(uuid)


# 绑定查询课表的函数
@uuia.bind_action_callback_function(groups=["base"], actions=["schedule"])
def get_schedule(uuid, request_args):
    return schedule_API(uuid)

if __name__ == '__main__':
    uuia.run(
        flask_debug=True
    )
