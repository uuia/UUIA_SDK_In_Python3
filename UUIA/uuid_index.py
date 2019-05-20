# @writer : zhongbr
# @filename:
# @purpose:
from .controler.uuia_controller import setting_flask_application  # 从controller导入flask app
from .util.uuia_logger import Uuia_logger
from .constant.constant import Constant


class Uuia:
    """
    Uuia类
    """

    def __init__(self,
                 thread_name="",
                 app_name="uuia",
                 app_id="",
                 app_token="",
                 running_port=80,
                 running_ip="0.0.0.0",
                 running_domain="/uuia",
                 ssl_flag=False,
                 ssl_key="",
                 ssl_crt="",
                 ):
        self.app_name = app_name
        self.running_port = running_port
        self.running_ip = running_ip
        self.running_domain = running_domain
        self.app_id = app_id
        self.app_token = app_token
        self.run_thread_name = thread_name
        self.ssl_flag = ssl_flag
        self.ssl_key = ssl_key
        self.ssl_crt = ssl_crt
        self.callback_functions = {}  # 回调函数字典

    def __config_check__(self):
        """
        检查项目配置是否合规的内置方法
        :return: 合规返回True，否则返回Fasle以及错误消息
        """
        if not self.__getattribute__("app_id"):
            message = "An app_id is needed for UUIA ."
            return False, message
        if not self.__getattribute__("app_token"):
            message = "An app_token is needed for UUIA ."
            return False, message
        if not self.__getattribute__("run_thread_name"):
            message = "Please clear a thread name to start flask app , it is '__name__' in common ."
            return False, message
        if self.ssl_flag and (not self.__getattribute__("ssl_crt") or not self.__getattribute__("ssl_key")):
            message = "The ssl mode is on , but the crt or key file is not provided . Please proviede crt and key file path ."
            return False, message
        return True, "right"

    def bind_action_callback_function(self, actions, groups):
        """
        绑定动作回调函数的装饰器方法
        :param action_name: 要绑定的action字段名称
        :param group_name: 要绑定的用户组
        :return:
        """

        def wrapper(func):
            # 绑定回调函数
            for group in groups:
                for action in actions:
                    callback_path = "{}/{}".format(group, action)
                    self.callback_functions[callback_path] = func

        return wrapper

    def run(self, flask_debug=False):
        """
        run方法，启动UUIA项目
        :return:
        """
        # 检查项目设置是否合法
        is_right, messgae = self.__config_check__()
        if not is_right:
            Uuia_logger().e(tag="UUIA.run", content=messgae)
        # 创建自定义设置实例
        constant = Constant(app_name=self.app_name, app_id=self.app_id, app_token=self.app_token)
        web_app = setting_flask_application(
            running_domain=self.running_domain,
            constant=constant,
            callbacks=self.callback_functions,
            thread=self.run_thread_name
        )
        Uuia_logger().i(tag="UUIA.run", content="The flask app of UUIA is created completed .")
        if self.ssl_flag:
            Uuia_logger().i(tag="UUIA.run",
                            content="The UUIA is running on the address of \"https://{}:{}{}\"".format(self.running_ip,
                                                                                                       self.running_port,
                                                                                                       self.running_domain))
        else:
            Uuia_logger().i(tag="UUIA.run",
                            content="The UUIA is running on the address of \"http://{}:{}{}\"".format(self.running_ip,
                                                                                                      self.running_port,
                                                                                                      self.running_domain))
        web_app.run(
            host=self.running_ip,
            port=self.running_port,
            debug=flask_debug
        )
