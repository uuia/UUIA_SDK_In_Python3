#@writer : zhongbr
#@filename:
#@purpose:
import json
from flask import Flask, request
from service import parser
from util.validator import Validator
from util.uuid_logger import Uuia_logger
from constant.constant import Constant
from exception.not_implemented_exception import Not_implemented_exception
from exception.lack_necessary_info_exception import Lack_necessary_info_exception

app = Flask(__name__)

@app.route("/uuia",methods=["POST"])
def uuia_controller():
    #验证请求是否来自中心服务器
    if not Validator().validate(request):
        code = Constant().RESPONSE_CODE_UNAUTHORIZED
        message = Constant().RESPONSE_MSG_UNAUTHORIZED
        data = {}
    else:
        code = Constant().RESPONSE_CODE_OK
        message = Constant().RESPONSE_MSG_OK
        try:
            form = json.loads(request.get_data(as_text=True))
            data = parser.paeser(request,form)
        except Lack_necessary_info_exception as e:
            code = Constant().RESPONSE_CODE_INTERNAL_SERVER_ERROR
            message = Constant().RESPONSE_MSG_INTERNAL_SERVER_ERROR
            data = {}
            Uuia_logger().i(tag="UUIA Controller",content=str(e))
        except Not_implemented_exception as e:
            code = Constant().RESPONSE_CODE_INTERNAL_SERVER_ERROR
            message = Constant().RESPONSE_MSG_INTERNAL_SERVER_ERROR
            data = {}
            Uuia_logger().i(tag="UUIA Controller",content=str(e))
    return json.dumps({
        "code":code,
        "message":message,
        "data":data
    })