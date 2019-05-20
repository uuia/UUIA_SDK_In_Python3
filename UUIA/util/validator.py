#@writer : zhongbr
#@filename:
#@purpose:
import hashlib
from UUIA.constant.constant import Constant
from UUIA.util.uuia_logger import Uuia_logger

class Validator:
    def validate(self, request, constant):
        signature = request.args.get("signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        try:
            state = signature == self.sha1([constant.app_token,timestamp,nonce])
        except:
            state = False
        if state:
            Uuia_logger().i(tag="UUIA Validator",content="Successful")
        else:
            Uuia_logger().i(tag="UUIA Validator",content="Failed")
        return state

    def sha1(self,args):
        args.sort()
        tmp = "".join(args)
        sha1_str = hashlib.sha1()
        sha1_str.update(tmp.encode("utf-8"))
        return sha1_str.hexdigest()
