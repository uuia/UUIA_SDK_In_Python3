# @writer : zhongbr
# @filename:
# @purpose:

import requests, re
from bs4 import BeautifulSoup
from hbut_data_sipder.config import *

url_dict = {
    "经济与管理学院": "http://jgxy.hbut.edu.cn/index.php?a=lists&catid=29",
    "电气与电子工程学院": "http://eee.hbut.edu.cn/szdw",
    "材料与化学工程学院": "http://smce.hbut.edu.cn/szdw/jsdw1.htm",
    "机械工程学院": "http://tsme.hbut.edu.cn/szdw/jsml.htm",
    "生物工程与食品学院": "http://sgsp.hbut.edu.cn/szdw/jsml.htm",
    "土木建筑与环境学院": "http://tj.hbut.edu.cn/szdw.htm",
    "工业设计学院": "http://ids.hbut.edu.cn/index.php?a=lists&catid=67",
    "马克思主义学院": "http://mkszyxy.hbut.edu.cn/a/xueshengfazhan/jiaoshiduiwu/",
    "外国语学院": "http://fls.hbut.edu.cn/szdw/yyx.htm",
    "理学院": "http://lxy.hbut.edu.cn/szdw/jsxx.htm",
    "体育学院": "http://pehg.hbut.edu.cn/szdw/js.htm",
    "职业技术师范学院": "http://zsy.hbut.edu.cn/szdw/zrjs.htm",

}


def create_soup(url, parser="html.parser"):
    print(url)
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    return BeautifulSoup(res.text, parser)


class Teacher:
    def __init__(self, teacher_name):
        self.teacher_name = teacher_name
        self.teacher_info = database.select(
            teachers_database.db_name,
            [
                teachers_database.name,
                teachers_database.url,
                teachers_database.subject,
                teachers_database.colleage,
                teachers_database.job,
                teachers_database.id
            ],
            {
                teachers_database.name: teacher_name
            }
        )
        if self.teacher_info:
            self.teacher_info = self.teacher_info[0]
        else:
            self.teacher_info = {"name": teacher_name,
                                 "colleage": "暂未收录",
                                 "subject": "暂未收录"}

    def get_teacher_info(self):
        try:
            self.teacher_info["job"] = database.base64decode(self.teacher_info["job"], "json")
        except:
            pass
        self.colleage = self.teacher_info["colleage"]
        if self.colleage == "电气与电子工程学院":
            teacher = Electrical_colleage()
        if self.colleage == "经济与管理学院":
            teacher = Jg_colleage()
        if self.colleage == "材料与化学工程学院":
            teacher = Ch_colleage()
        if self.colleage == "生物工程与食品学院":
            teacher = Ss_colleage()
        if self.colleage == "理学院":
            teacher = Li_colleage()
        if self.colleage == "土木建筑与环境学院":
            teacher = Tm_colleage()
        if self.colleage == "暂未收录":
            return self.teacher_info
        if self.teacher_info["url"]:
            self.teacher_info = teacher.parse_teacher_info(self.teacher_info)
        return self.teacher_info


class Colleage:
    def save(self):
        for i in self.teachers.values():
            database.add("teacher_info", i)


class Electrical_colleage(Colleage):
    def __init__(self):
        pass

    def start_parse(self):
        self.get_electrical_colleage_teachers()

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"])
        info_tags = soup.find_all(attrs={"class": "MsoNormal"})
        info_text = ""
        for i in info_tags:
            info_text += "{}\n".format(i.text.replace(" ", ""))
        info_text = info_text.split("::")
        teacher["base_info"] = {}
        for info_line in re.findall("(.*?)：(.*?)\n", info_text[0]):
            key, value = info_line
            key = key.replace("\u3000", "").replace(" ", "")
            teacher["base_info"][key] = value.replace(" ", "")
        teacher["other_info"] = {}
        for info in info_text[1:]:
            teacher["other_info"][info.split("\n")[0].replace(" ", "").replace("：", "")] = "".join(
                info.split("\n")[1:])
        return teacher

    def get_electrical_colleage_teachers(self):
        def get_zrjs():
            """
            获取专任教师
            :return:
            """
            __zrjs_soup__ = create_soup(url + "/zrjs.htm")
            td_tags = __zrjs_soup__.find_all("td")
            subject_lines = __zrjs_soup__.find_all("td", attrs={"colspan": "10"})  # 获取学科行
            result = {}
            for subject_line in subject_lines:
                subject = subject_line.text
                number = subject_lines.index(subject_line)
                location_line = td_tags.index(subject_line) + 1
                if number != len(subject_lines) - 1:
                    next_location_line = td_tags.index(subject_lines[number + 1])
                else:
                    next_location_line = -1
                teacher_lines = td_tags[location_line:next_location_line]
                for teacher_line in teacher_lines:
                    if teacher_line.text == "":
                        continue
                    teacher = dict(
                        name=teacher_line.text,
                        subject=subject,
                        job=["专任教师"],
                        colleage=colleage
                    )
                    result[teacher_line.text] = teacher
            return result

        def get_graduate_teacher_research_supervisor():
            soup = create_soup(url + "/yjsds.htm")
            a_tags = soup.find_all("a")
            for a in a_tags[:]:
                teacher_name = a.get("title")
                if teacher_name:
                    teacher = self.teachers.get(teacher_name,
                                                {"colleage": colleage, "subject": "null", "name": teacher_name,
                                                 "job": []})
                    teacher.update(url=a["href"].replace("..", base_url))
                    self.teachers[teacher_name] = self.parse_teacher_info(teacher)

        colleage = "电气与电子工程学院"
        url = url_dict[colleage]
        base_url = re.findall("http://.*?/", url)[0]
        self.teachers = get_zrjs()
        get_graduate_teacher_research_supervisor()


class Jg_colleage(Colleage):
    def __init__(self):
        self.colleage_name = "经济与管理学院"
        self.url = url_dict[self.colleage_name]
        self.base_url = re.findall("http://.*?/", self.url)[0][:-1]
        self.teachers = {}
        # self.get_zr_teacher()

    def start_parse(self):
        self.get_graduate_teacher()

    def get_zr_teacher(self):
        soup = create_soup(self.url)
        for subject in soup.find_all("ul", attrs={"class": "clearfix"})[2:]:
            subject_name = subject.parent.h3.text
            for li_tag in subject.find_all("li")[:]:
                teacher_name = li_tag.a.text.replace("※  ", "").replace(" ", "")
                teacher_url = self.base_url + li_tag.a["href"]
                self.teachers[teacher_name] = {
                    "colleage": self.colleage_name,
                    "subject": subject_name,
                    "url": teacher_url,
                    "name": teacher_name,
                    "job": "教师"
                }
                self.teachers[teacher_name] = self.parse_info(teacher_url, self.teachers[teacher_name])

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"])
        info_tags = soup.find_all("p")
        info_text = ""
        for i in info_tags[:-1]:
            info_text += "{}\n".format(i.text.replace(" ", ""))
        info_text = info_text.split("::")
        teacher["base_info"] = {}
        for info_line in re.findall("(.*?)：(.*?)\n", info_text[0]):
            key, value = info_line
            key = key.replace("\u3000", "").replace(" ", "")
            teacher["base_info"][key] = value.replace(" ", "")
        teacher["other_info"] = {}
        for info in info_text[1:]:
            teacher["other_info"][info.split("\n")[0].replace(" ", "").replace("：", "")] = "".join(
                info.split("\n")[1:])
        return teacher

    def get_graduate_teacher(self):
        soup = create_soup("http://jgxy.hbut.edu.cn/index.php?a=lists&catid=31")
        for subject in soup.find_all("ul", attrs={"class": "clearfix"})[2:]:
            subject_name = subject.parent.h3.text
            for li_tag in subject.find_all("li")[:]:
                teacher_name = li_tag.a.text.replace("※  ", "").replace(" ", "")
                teacher_url = self.base_url + li_tag.a["href"]
                self.teachers[teacher_name] = self.teachers.get(teacher_name, {
                    "colleage": self.colleage_name,
                    "subject": subject_name,
                    "url": teacher_url,
                    "name": teacher_name,
                    "job": ["硕士生导师"]
                })
                self.teachers[teacher_name] = self.parse_teacher_info(self.teachers[teacher_name])

    def parse_info(self, url, teacher):
        soup = create_soup(url)
        div = soup.find("div", attrs={"class": "hgdxqy"})
        p_tags = div.find_all("p")
        teacher["base_info"] = {"基本介绍": p_tags[0].text}
        teacher["others"] = {"其他介绍": p_tags[1].text}
        return teacher

    def save(self):
        for i in self.teachers.values():
            database.add("teacher_info", i)


class Ch_colleage(Colleage):
    def __init__(self):
        self.colleage = "材料与化学工程学院"
        self.url = url_dict[self.colleage]
        self.base_url = re.findall("http://.*?/", self.url)[0][:-1]
        self.teachers = {}

    def start_parse(self):
        self.get_teachers()

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"])
        ul_tags = soup.find_all("ul")
        base_info_html = ul_tags[13]
        title_tags = ul_tags[14].find_all("li")
        other_info_html = ul_tags[15:]
        base_info = {}
        for li in base_info_html.find_all("li"):
            print(li.text)
            key, value = li.text.split("：")[-2:]
            base_info[key] = value
        others_info = {}
        for other_info in other_info_html:
            title = title_tags[other_info_html.index(other_info)].text
            info = other_info.text
            others_info[title] = info
        teacher["base_info"] = base_info
        teacher["other_info"] = others_info
        return teacher

    def get_teachers(self):
        soup = create_soup(self.url)
        levels = ["正高级", "副高级", "中级及以下"]
        td_tags = soup.find_all("td", attrs={"valign": "top"})
        for td in td_tags[:]:
            td_same_line = td.parent.find_all("td")
            subject_name = td_same_line[0].text
            level = levels[td_same_line.index(td) - 1]
            for a in td.find_all("a")[:]:
                teacher_name = a.text.replace("\u3000", "")
                print(teacher_name)
                url = self.base_url + a["href"][2:]
                teacher = {
                    "name": teacher_name,
                    "url": url,
                    "subject": subject_name,
                    "job": level,
                    "colleage": self.colleage
                }
                print(teacher)
                self.teachers[teacher_name] = teacher
                self.teachers[teacher_name] = self.parse_teacher_info(self.teachers.get(teacher_name))

    def save(self):
        for i in self.teachers.values():
            database.add("teacher_info", i)


class Jx_colleage(Colleage):
    def __init__(self):
        self.colleage_name = "机械工程学院"
        self.url = url_dict[self.colleage_name]
        self.base_url = re.findall("http://.*?/", self.url)[0][:-1]
        self.teachers = {}
        # self.get_zr_teacher()

    def start_parse(self):
        self.get_graduate_teacher()

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"])
        tbody_tags = soup.find_all("tbody")
        base_info = {}
        for td in tbody_tags[1].find_all("td"):
            if td.text:
                key, value = td.text.split("：")
                base_info[key] = value
        other_info = {}
        for tbody in tbody_tags[3::2]:
            try:
                key = tbody.find_all("strong")[0].text
                value = tbody.find_all("form")[0].text
                other_info[key] = value
            except:
                pass
        teacher["base_info"] = base_info
        teacher["other_info"] = other_info
        print(teacher)
        return teacher

    def get_graduate_teacher(self):
        soup = create_soup("http://tsme.hbut.edu.cn/szdw/jsml.htm")
        for subject in soup.find_all("div", attrs={"class": "teacher-list"})[:]:
            subject_name = subject.h2.text
            for li_tag in subject.find_all("li")[:]:
                teacher_name = li_tag.a.text.replace("※  ", "").replace(" ", "")
                teacher_url = self.base_url + li_tag.a["href"][2:]
                self.teachers[teacher_name] = self.teachers.get(teacher_name, {
                    "colleage": self.colleage_name,
                    "subject": subject_name,
                    "url": teacher_url,
                    "name": teacher_name,
                    "job": ["教师"]
                })
                self.teachers[teacher_name] = self.parse_teacher_info(self.teachers[teacher_name])

    def parse_info(self, url, teacher):
        soup = create_soup(url)
        div = soup.find("div", attrs={"class": "hgdxqy"})
        p_tags = div.find_all("p")
        teacher["base_info"] = {"基本介绍": p_tags[0].text}
        teacher["others"] = {"其他介绍": p_tags[1].text}
        return teacher

    def save(self):
        for i in self.teachers.values():
            database.add("teacher_info", i)


class Ss_colleage(Colleage):
    def __init__(self):
        self.colleage_name = "生物工程与食品学院"
        self.url = url_dict[self.colleage_name]
        self.base_url = re.findall("http://.*?/", self.url)[0][:-1]
        self.teachers = {}

    def start_parse(self):
        self.get_teachers()

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"], parser="lxml")
        tr_tags = soup.find_all("tr")
        base_info = {}
        for tr in tr_tags[2:7]:
            td_tags = tr.find_all("td")
            base_info[td_tags[0].text.replace("\u3000", "")] = td_tags[1].text
        other_info = {}
        keys = soup.find_all(attrs={"class": "js_tab"})
        values = soup.find_all("div", attrs={"class": "js_tab_body"})
        for other in values:
            other_info[keys[values.index(other)].text] = other.text.replace("\r", "")
        teacher["base_info"] = base_info
        teacher["other_info"] = other_info
        return teacher

    def get_teachers(self):
        soup = create_soup(self.url)
        subjects_div = soup.find_all(attrs={"class": "subclass2"})
        for subject_div in subjects_div[:]:
            subject_name = subject_div.text
            subject_soup = create_soup("http://sgsp.hbut.edu.cn/szdw/" + subject_div.a["href"])
            for teacher_tag in subject_soup.find_all(attrs={"class": "newslist"}):
                for li in teacher_tag.find_all("li")[:]:
                    self.teachers[li.a.text] = \
                        self.parse_teacher_info({
                            "name": li.a.text,
                            "url": li.a["href"].replace("../..", self.base_url),
                            "colleage": self.colleage_name,
                            "subject": subject_name,
                            "job": ["教师"]
                        })


class Tm_colleage(Colleage):
    def __init__(self):
        self.colleage_name = "土木建筑与环境学院"
        self.url = url_dict[self.colleage_name]
        self.base_url = re.findall("http://.*?/", self.url)[0][:-1]
        self.teachers = {}

    def start_parse(self):
        self.get_teachers()

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"], parser="lxml")
        text_tag = soup.find(attrs={"class": "formMiddle formMiddle14"})
        texts = re.sub("\n+", "_", re.sub("\xa0|\r| ", "", text_tag.text)).split("_教师详情_")[1].replace("_", " ")
        teacher["other_info"] = {"html": str(text_tag.find_all("form", attrs={"name": "_newscontent_fromname"}))}
        teacher["base_info"] = {"texts": texts}
        return teacher

    def get_teachers(self):
        for i in range(0, 20):
            soup = create_soup(self.base_url + "/szdw/{}.htm".format(i))
            if i == 0:
                soup = create_soup(self.url)
            for teacher_tag in soup.find_all("a", attrs={"class": "fk-productName"})[:]:
                teacher_name = teacher_tag.text.replace("\xa0", "").replace(" ", "")
                teacher = {
                    "name": teacher_name,
                    "colleage": self.colleage_name,
                    "job": ["研究生导师"],
                    "url": self.base_url + "/" + teacher_tag["href"].replace("../", ""),
                    "subject": "见其他信息"
                }
                self.teachers[teacher_name] = self.parse_teacher_info(teacher)


class Li_colleage(Colleage):
    def __init__(self):
        self.colleage_name = "理学院"
        self.url = url_dict[self.colleage_name]
        self.base_url = re.findall("http://.*?/", self.url)[0][:-1]
        self.teachers = {}

    def start_parse(self):
        self.get_teachers()

    def parse_teacher_info(self, teacher):
        soup = create_soup(teacher["url"])
        base_info_tag = soup.find("div", attrs={"class": "teacherinfomation"})
        base_info = {}
        for div in base_info_tag.find_all("div")[1:-1]:
            key, value = div.text.split("：")
            base_info[key] = value
        other_info = {}
        main_div = soup.find("div", attrs={"class": "page_main"}).find_all("div")
        for i in soup.find_all("div", attrs={"class": "page-header infotitle"})[1:]:
            key = i.text
            value = main_div[main_div.index(i) + 1].text
            other_info[key] = value
        teacher["base_info"] = base_info
        teacher["other_info"] = other_info
        return teacher

    def get_teachers(self):
        soup = create_soup(self.url)
        teacher_tags = soup.find_all("div", attrs={"class": "col-lg-2 col-md-4 col-xs-6 teacher-list"})
        subjects = soup.find_all("div", attrs={"class": "col-lg-12 belong"})
        rows = soup.find_all("div", attrs={"class": "row"})
        for teacher_tag in teacher_tags[:]:
            subject_name = subjects[rows.index(teacher_tag.parent) // 2 - 2].text.replace("：(按姓氏拼音排序)", "")
            teacher_name = teacher_tag.text
            url = teacher_tag.a["href"].replace("..", self.base_url)
            teacher = {
                "name": teacher_name,
                "url": url,
                "subject": subject_name,
                "job": ["教师"],
                "colleage": self.colleage_name
            }
            self.teachers[teacher_name] = self.paese_teacher_info(teacher)


if __name__ == '__main__':
    # colleage = Li_colleage()
    # colleage.save()
    print(Teacher("曾亮").get_teacher_info())
