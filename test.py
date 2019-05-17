#@writer : zhongbr
#@filename:
#@purpose:
import requests
from util.validator import Validator

print(requests.post(
    "http://127.0.0.1:5000/uuia?signature={}&nonce=456&timestamp=789".format(Validator().sha1(["123","456","789"])),
    data={
        "uuid":"123",
        "group":"base",
        "action":"bind"
    }
).json())