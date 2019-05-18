from bs4 import BeautifulSoup
import requests
import datetime


class Student_informations:
    def __init__(self, student_username):
        self.username = student_username
        self.post_data = {
            "user_name": student_username,
            "pass_word": student_username[-6:]
        }
        self.info = self.parse_for_information(self.login())
        self.portal_passwd = self.info["id"][12:]

    def login(self):
        login_url = "http://202.114.176.66:8081/xg/home/login.do"
        login_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        tsp = int(datetime.datetime.today().timestamp() * 1000)
        infomation_url_model = "http://202.114.176.66:8081/xg/student/toTableInfo.do?_tsp_={timestamp}&typeid=info&studentId={username}&method=edit"
        self.session = requests.Session()
        self.session.get(login_url, headers=login_header)
        login = self.session.post(login_url, data=self.post_data, headers=login_header).text
        infomation_page = self.session.get(infomation_url_model.format(timestamp=tsp, username=self.username),
                                           headers=login_header).text
        return infomation_page

    def parse_for_information(self, html_codes):
        soup = BeautifulSoup(html_codes, "html.parser")
        infomation = {"username": self.username}
        count = 1
        for info in soup.find_all("input"):
            text = info.get("value")
            if count == 2:
                infomation["name"] = text
            if count == 10:
                infomation["id"] = text
            count += 1
        return infomation


if __name__ == '__main__':
    from spiders.hbut_spider.hbut_website import Student

    userid = input(">>>")
    portal = Student_informations(userid)
    print(portal)
    stu = Student(userid, portal.portal_passwd)
    print(stu.getDetailInformations())
