# @writer : zhongbr
# @filename:
# @purpose:
import hashlib


def sha1(args):
    tmp = "".join(args)
    sha1_str = hashlib.sha1()
    sha1_str.update(tmp.encode("utf-8"))
    return sha1_str.hexdigest()
