#@writer : zhongbr
#@filename:
#@purpose:
import json
from flask import Flask, request
from ..service import parser
from ..util.validator import Validator
from ..util.uuia_logger import Uuia_logger
from ..constant.constant import Constant
from ..exception.not_implemented_exception import Not_implemented_exception
from ..exception.lack_necessary_info_exception import Lack_necessary_info_exception
from ..exception.config_error_exception import Config_error_exception
from ..exception.action_callback_exception import Callback_exception


def setting_flask_application(thread, running_domain, constant, callbacks):
    """
    设置并返回flask app
    :param running_domain: UUIA项目运行的URL
    :return: 
    """
    app = Flask(thread)

    @app.route(running_domain, methods=["POST"])
    def uuia_controller():
        # 验证请求是否来自中心服务器
        if not Validator().validate(request, constant):
            code = constant.RESPONSE_CODE_UNAUTHORIZED
            message = constant.RESPONSE_MSG_UNAUTHORIZED
            data = {}
        else:
            code = constant.RESPONSE_CODE_OK
            message = constant.RESPONSE_MSG_OK
            try:
                form = json.loads(request.get_data(as_text=True))
                data = parser.paeser(request, form, callbacks)
            except Lack_necessary_info_exception as e:
                code = constant.RESPONSE_CODE_INTERNAL_SERVER_ERROR
                message = constant.RESPONSE_MSG_INTERNAL_SERVER_ERROR
                data = {}
                Uuia_logger().i(tag="UUIA Controller", content=str(e))
            except Not_implemented_exception as e:
                code = constant.RESPONSE_CODE_INTERNAL_SERVER_ERROR
                message = constant.RESPONSE_MSG_INTERNAL_SERVER_ERROR
                data = {}
                Uuia_logger().i(tag="UUIA Controller", content=str(e))
            except Callback_exception as e:
                code = constant.RESPONSE_CODE_INTERNAL_SERVER_ERROR
                message = constant.RESPONSE_MSG_ACTION_DONT_EXIST
                data = {}
                Uuia_logger().i(tag="UUIA Controller", content=str(e))
            except:
                code = constant.RESPONSE_CODE_INTERNAL_SERVER_ERROR
                message = constant.RESPONSE_MSG_INTERNAL_SERVER_ERROR
                data = {}
                Uuia_logger().i(tag="UUIA Controller", content=str("Some error has happed in the server !"))
        return json.dumps({
            "code": code,
            "message": message,
            "data": data
        })

    return app
