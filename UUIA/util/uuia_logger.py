#@writer : zhongbr
#@filename:
#@purpose:
import datetime

class Uuia_logger:
    def i(self,tag,content):
        date_string = str(datetime.datetime.today())[:16]
        print("{date}: INFO [{tag}] {content}".format(date=date_string,tag=tag,content=content))

    def e(self,tag,content):
        date_string = str(datetime.datetime.today())[:16]
        print("{date}: ERROR [{tag}] {content}".format(date=date_string,tag=tag,content=content))
