# encoding:utf8
# @writer : zhongbr
# @filename: hbut_website.py
# @purpose: 这个文件中存储的是到湖北工业大学信息门户网站查询信息的类


import requests, re, json, urllib3
from bs4 import BeautifulSoup
from spiders.hbut_spider.teacher_info_spider import Teacher

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from hbut_data_sipder.config import *
from difflib import SequenceMatcher


class Student:
    """
    这是针对湖北工业大学个人门户的类
    实例化这个类的时候，需要传入两个个参数
    username 这个参数是要实例化的学生的学号（必须传入）
    password 这个参数是要实例化的学生的个人门户密码（必须传入）

    这个类中，方法和属性调用请注意以下几点：
    实例化Student对象之后
    1、调用getBaseSchedule方法之后，会得到一个包含了实例选修课和教务处课表中的课程的属性，temp_li
        temp_li属性：三维列表类型，一共35个元素
        每一个元素都对应一个星期中的一节课，是当前节次所包含的所有课组成的列表
        每一节课的一门课，用长度为2或者3的列表表示，[[['课名','主讲教师','地点周数'],['课名'.'地点周数']],['本节课为空']......]
    2、调用getPhysicTestInfo方法之后，如果该实例对象有物理实验，会得到一个在上一个方法得到的课表基础之上，有物理实验信息的课表属性，temp_li和一个实验列表physicTestList
    3、调用getGrade方法之后，会返回实例对象当前和过去所有学期的课程成绩信息，得到一个包含实例对象成绩信息的属性,grade_info
        grade_info属性：字典类型
        {学期编号:[{课程和成绩}...],学期编号:[{课程和成绩}...]...}
        学期编号格式：2018年第一学期为20182，每学期的课程和成绩信息为字典类型
    4、调用getTeachingQualityAdvice方法之后，会返回一个包含有该生当前教务系统中有待评教的内容的列表，和一个属性qualityList
        qualityList属性： 列表属性，元素是评教课程信息字典
    5、调用teachingQualityUpload方法,完成将实例对象所有没有评教的课程一键评教的操作
    6、调用getRestartLesson方法，返回实例对象本学期的重修/补考列表，和得到一个与之对应的属性,restartLessonList
    7、调用getDetailInformations方法，返回实例详细信息的字典，和得到一个对应的属性，informations
        informations 属性：字典类型
    以上7个方法，在需要时推荐调用，其他方法不推荐从外部直接调用
    如果有其他需求，还可以直接调用实例的session属性，session属性是带有实例的登陆状态的，用法与requests库的session用法一致
    """

    def __init__(self, username, password, login=True):
        # 给这个类定义一个全局的属性，并且将初始值赋予它们

        # 类的用户名属性，通常是实例的学号
        self.username = username
        # 类的门户密码属性
        self.password = password
        if login:
            # 类的session属性，这个属性是通过调用requests属性里面的Session方法得到的，
            self.session = requests.Session()
            self.session.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
            self.login_state = self.login()

    def login(self):
        """
        登陆方法，根据用户提供的账户名和密码登陆湖北工业大学个人门户网站
        :return: 布尔值
        返回True代表个人门户登陆成功
        返回False代表个人门户登陆失败
        """
        login_url = 'https://sso.hbut.edu.cn:7002/cas/login?service=http%3A%2F%2Fportal.hbut.edu.cn%2Fportal%2Fhome%2Findex.do'
        response = self.session.get(login_url, verify=False)
        response.encoding = response.apparent_encoding
        login_soup = BeautifulSoup(response.text, 'html.parser')
        # 用于登陆时的post数据中的lt项
        lt = login_soup.find_all('input')[0]['value']
        login_data = {'lt': lt,
                      '_eventId': 'submit',
                      'loginType': '0',
                      'username': self.username,
                      'password': self.password,
                      'j_digitPicture': ''}
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        r = self.session.post(login_url, headers=login_headers, data=login_data).text
        if '页面跳转中' in r:
            codeMh = True
        else:
            codeMh = False
        jw_url_2 = 'http://run.hbut.edu.cn/Account/sso'
        r = self.session.get(jw_url_2)
        # r.raise_for_status()
        self.cookies = self.session.cookies
        return codeMh

    def getBaseSchedule(self, sypassword):
        """
        获取实例的基本课表，只包含有选修课和课表中本来就包含有的课
        :return:
        """
        self.getSchedule()
        self.getElective()
        self.getPhysicTest(sypassword)
        return self.temp_li

    def getPhysicTestInfo(self, sypassword):
        """
        使用这个方法可以获取用户的大学物理实验信息
        :param sypassword: 大学物理实验预约网站的密码
        :return: 返回添加了用户物理实验信息的课表
        """
        try:
            # 调用此类中的physicTestList方法，获取用户的物理实验信息的列表，这个方法回自动将用户的物理实验添加到课表的列表（self.temp_li）中
            self.physicTestList = self.getPhysicTest(sypassword)
            return self.physicTestList
        except:
            pass

    def getSchedule(self):
        soup = BeautifulSoup(self.session.get('http://run.hbut.edu.cn/ArrangeTask/MyselfSchedule').text, 'html.parser')
        classes = []
        lesson = []
        temp_classes = []
        for i in soup.tr.next_siblings:
            # for i in soup.find_all('tr')[1]:
            temp = re.findall(r'<th>(.*?)</th>', str(i))
            temp_classes.append(temp)
            for k in range(0, len(temp_classes) - 1):
                if k % 2 != 0:
                    classes.append(temp_classes[k][0])
            for j in soup.find_all('td'):
                j = str(j)
                temp = re.findall(r'<td align="left">(.*?)</td>', j, re.S)
                if temp:
                    temp = temp[0]
                temp = re.sub(r'\r\n', '', str(temp))
                temp = re.sub(r'\n\n', '', temp)
                test = re.split(r'<br.*?>', temp)
                temp = re.sub(r'<br>|<br/>', '', temp)
                temp = re.sub('.(\n)', ' ', temp, re.S)
                temp = re.sub('\n', '本节课为空', temp)
                if temp != '本节课为空':
                    lessonTemp = []
                    if test:
                        if len(test) % 4 == 1 and len(test) != 1:
                            # print(len(test))
                            for i in range(0, len(test) // 4):
                                temp = ['', '', '']
                                temp[0] = test[4 * i]
                                temp[1] = test[4 * i + 1]
                                temp[2] = test[4 * i + 2]
                                lessonTemp.append(temp)
                        if len(test) % 4 == 0:
                            for i in range(0, len(test) // 4):
                                temp = ['', '']
                                temp[0] = test[3 * i]
                                temp[1] = test[3 * i + 1]
                                lessonTemp.append(temp)
                    lesson.append(lessonTemp)
                else:
                    lesson.append(['本节课为空'])
                classes.append(temp)
        terminal_lesson = []
        for i in lesson:
            if not i:
                break
            else:
                terminal_lesson.append(i)
        self.temp_li = terminal_lesson
        # self.temp_li = self.getTotalWeekSchedule(soup,terminal_lesson)
        return self.temp_li

    def getTotalWeekSchedule(self, soup, schedule):
        week_replace = {"星期一": 0, "星期二": 1, "星期三": 2, "星期四": 3, "星期五": 4, "星期六": 5, "星期日": 6}
        lesson_replace = {1.5: "第1-2节", 3.5: "第3-4节", 5.5: "第5-6节", 7.5: "第7-8节", 9.5: "第9-10节"}
        week_schedule_data = soup.find("div", id="weekSchedule")
        for week_lesson in week_schedule_data.find_all("tr"):
            week_lesson_infos = []
            for info in week_lesson.find_all("td"):
                text = re.sub(r",", "", info.text)
                # text = text.replace("~","-")
                week_lesson_infos.append(text)
            week_days = week_lesson_infos[2].split("~")
            if len(week_days) == 2:
                for day in range(week_replace[week_days[0]], week_replace[week_days[1]] + 1):
                    lesson_range = re.findall("\d+", week_lesson_infos[3])
                    lesson_range[0], lesson_range[1] = int(lesson_range[0]), int(lesson_range[1])
                    for lesson_value in lesson_replace.keys():
                        if lesson_range[0] < lesson_value < lesson_range[1]:
                            lesson_value = (lesson_value - 0.5) // 2
                            if schedule[int(lesson_value * 7 + day)][0] != "本节课为空":
                                schedule[int(lesson_value * 7 + day)].append(
                                    [week_lesson_infos[0], week_lesson_infos[0],
                                     week_lesson_infos[1] + " " + week_lesson_infos[-1]])
                            else:
                                schedule[int(lesson_value * 7 + day)] = [[week_lesson_infos[0], week_lesson_infos[0],
                                                                          week_lesson_infos[1] + " " +
                                                                          week_lesson_infos[-1]]]
            else:
                day = week_replace[week_days[0]]
                lesson_range = re.findall("\d+", week_lesson_infos[3])
                lesson_range[0], lesson_range[1] = int(lesson_range[0]), int(lesson_range[1])
                for lesson_value in lesson_replace.keys():
                    if lesson_range[0] < lesson_value < lesson_range[1]:
                        lesson_value = (lesson_value - 0.5) // 2
                        if schedule[int(lesson_value * 7 + day)][0] != "本节课为空":
                            schedule[int(lesson_value * 7 + day)].append([week_lesson_infos[0], week_lesson_infos[0],
                                                                          week_lesson_infos[1] + " " +
                                                                          week_lesson_infos[-1]])
                        else:
                            schedule[int(lesson_value * 7 + day)] = [[week_lesson_infos[0], week_lesson_infos[0],
                                                                      week_lesson_infos[1] + " " + week_lesson_infos[
                                                                          -1]]]
        return schedule

    def getElective(self, tempAppendFlag=True):
        import re
        from bs4 import BeautifulSoup
        try:
            url = 'http://run.hbut.edu.cn/SelectCurriculum/PublicElectiveIndex'
            soup = BeautifulSoup(self.session.get(url).text, 'html.parser')
            table = str(soup.table)
            pre_data = re.findall(r'<td.*?>(.*?)</td>', table, re.S)
            pre_data = pre_data[1:]
            for i in range(len(pre_data)):
                pre_data[i] = re.sub(r'\r', '', pre_data[i])
                pre_data[i] = re.sub(r'\n', '', pre_data[i])
                pre_data[i] = re.sub(r'  ', '', pre_data[i])
            public_elective_info = [pre_data[1], '公选课\n', pre_data[7]]
            time_in_week = re.findall(r'星期(. .*?)节', public_elective_info[2])[0]
            public_elective_info[2] = re.sub(r'星期.*?节', '', public_elective_info[2], re.S)
            public_elective_info[2] = re.sub(r' ', ' 第', public_elective_info[2], 1, re.S)
            code_lesson = self.__turn_to_numbers__(time_in_week)
            if tempAppendFlag:
                for i in code_lesson:
                    if self.temp_li[i] == ['本节课为空']:
                        self.temp_li[i] = [public_elective_info]
                    else:
                        self.temp_li[i].append(public_elective_info)
            else:
                return public_elective_info
        except:
            return None

    def getPhysicTest(self, password, getScheduleFlag=True):
        """
        获取物理实验的方法
        :param password:物理实验网站的密码
        :param getScheduleFlag: 是否同时获取课表并整合
        :return: 物理实验表
        """
        try:
            if getScheduleFlag:
                self.getSchedule()
            url = 'http://dxwlsy.hbut.edu.cn/Account/LogOn?ReturnUrl=%2fStudent%2fListScores'
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            data = {'username': self.username, 'password': password, 'rememberMe': 'false'}
            r = self.session.post(url, headers=header, data=data)
            r.encoding = r.apparent_encoding
            texts = re.sub(' ', '', r.text)
            texts = re.sub('\n', '', texts)
            texts = re.sub('\r', '', texts)
            soup = BeautifulSoup(texts, 'html.parser')
            base_info = []
            test_table = []
            base_info.append(soup.p.b.string)
            for i in soup.p.b.next_siblings:
                base_info.append(i.string)
            labidDict = {}
            for i in soup.find_all('td'):
                i = str(i)
                if '撤销' in i:
                    labid = re.findall('labid=\'(\d+)', i)[0]
                    tp = re.findall('Tp=(\d+)', i)[0]
                    labidDict[test_table[-2]] = (labid, tp)
                i = re.sub('<.*?>', '', i)
                i = re.sub(r' ', '', i)
                i = re.sub(r'\r\n', '', i)
                i = re.sub("""撤销""", '', i)
                test_table.append(i)
            to_append_temp_li = []
            result = []
            for i in range(0, len(test_table)):
                if i % 7 == 0:
                    appending = {'testName': test_table[i], 'testLocate': test_table[i + 1],
                                 'testTime': test_table[i + 2],
                                 'previewScore': test_table[i + 3], 'operateScore': test_table[i + 4],
                                 'reportScore': test_table[i + 5], 'testStatic': test_table[i + 6]}
                    if test_table[i] in labidDict.keys():
                        appending['labid'], appending['tp'] = labidDict[test_table[i]]
                    result.append(appending)
                if i % 7 == 0 or i % 7 == 1 or i % 7 == 2:
                    to_append_temp_li.append(test_table[i])
            if getScheduleFlag:
                data = to_append_temp_li
                for i in range(len(data)):
                    if i % 3 == 0 and data[i - 1] != '预约':
                        append_code = self.turn_to_code(data[i - 1])
                        if append_code <= 34:
                            data[i - 1] = re.sub(r'星期.*?节', '', data[i - 1])
                            data[i - 1] = self.sub_chinese_to_num(data[i - 1])
                            data[i - 1] = re.sub(r'周', '周 ', data[i - 1])
                            to_append = ['物理实验-' + data[i - 3], data[i - 2], data[i - 1]]
                            if self.temp_li[append_code] == ['本节课为空']:
                                self.temp_li[append_code] = [to_append]
                            else:
                                self.temp_li[append_code].append(to_append)
                    else:
                        continue
            return result
        except:
            return None

    def getUnbootedPhysicTest(self, sypassword):
        """
        获取未预约的物理实验信息
        :param sypassword: 物理实验网站密码
        :return: 未预约的物理实验信息，列表类型 每个元素为[ 实验名称 , [实验ID，实验预约时间表]]
        """
        postdata = {'username': self.username, 'password': sypassword, 'rememberMe': 'false'}
        physicSoup = BeautifulSoup(
            self.session.post('http://dxwlsy.hbut.edu.cn/Account/LogOn?ReturnUrl=%2fStudent%2fListScores',
                              data=postdata).text, 'html.parser')
        self.unboot = []
        # 遍历soup中的所有 tr 标签
        for foo in physicSoup.find_all('tr'):
            for i in foo.find_all('a'):
                name = re.sub('<.*?>', '', str(foo.find_all('td')[0]))
                i = str(i)
                labid = re.findall('LabID=(\d+)', i, re.S)[0]
                bootData = json.loads(
                    self.session.get('http://dxwlsy.hbut.edu.cn/Student/AboutLab?labid=' + labid).text)
                bootData = self.turnToStandable(bootData)
                self.unboot.append([name, [labid, bootData]])

    def bookPhysicTest(self, sypassword, labid, tp):
        """
        预约物理书实验
        :param sypassword:物理实验网站密码
        :param labid: 实验ID
        :param tp: 预约时间CODE
        :return:
        """
        self.getPhysicTest(sypassword)
        book_url = "http://dxwlsy.hbut.edu.cn/Student/Registerr"
        self.session.post(book_url,
                          data={
                              "labid": labid,
                              "tp": tp
                          })

    def getPhysicTestTimeTable(self, sypassword, labid):
        """
        获取物理实验的预约时间表
        :param sypassword: 物理实验网站密码
        :param labid: 实验ID
        :return:
        """
        self.getPhysicTest(sypassword)
        time_table = self.session.get("http://dxwlsy.hbut.edu.cn/Student/AboutLab?labid=" + labid).json()
        lesson_title = ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "第9-10节", "最后两节"]
        week_title = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        result = {}
        for table_cell in time_table:
            time_code, num = table_cell["tp"], table_cell["num"]
            time_code = int(time_code)
            week = str(time_code // 42 + 1)
            day = week_title[(time_code % 42) // 6 - 1]
            lesson = lesson_title[(time_code % 42) // 7]
            result[week] = []
            result[week].append({
                "week": week,
                "day": day,
                "lesson": lesson,
                "number": num,
                "tp": str(time_code)
            })
        return {"labid": labid, "times": result}

    def unbootPhysicTest(self, sypassword, labid, tp):
        """
        撤销物理实验预约
        :param sypassword:物理实验网站密码
        :param labid: 撤销的实验ID
        :param tp: 撤销的预约时间
        :return:
        """
        self.getPhysicTest(sypassword)
        # self.session.get("http://dxwlsy.hbut.edu.cn/Student/Cancel?Labid={}&Tp={}".format(labid,tp))

    def getSemesterList(self):
        """
        获取实例的学期名称列表的方法

        :return:
        """
        import time
        time.sleep(1)
        s = BeautifulSoup(self.session.get('http://run.hbut.edu.cn/StuGrade/Index').text, 'html.parser')
        result = []
        self.semesterNameDict = {}
        for i in s.find_all('option'):
            semesterCode = re.findall(r'value="(\d+)"', str(i))[0]
            result.append(semesterCode)
            semesterNameStr = re.sub(' ', '%', i.string)
            self.semesterNameDict[semesterCode] = semesterNameStr
        self.semesterList = result
        return result

    def getGrade(self, semester):
        """
        获取实例所有的成绩信息，学期数较多的情况下，可能花费的时间较长
        :return:实例成绩信息的列表
        """

        def turn_code_to_str(code):
            code = code[-1].replace("1", "学年 第一学期")
            semester_string = code[-1].replace("2", "学年 第二学期")
            return semester_string

        gradeUrlBase = 'http://run.hbut.edu.cn/StuGrade/Index?SemesterName='
        scoresInfo = {}
        scoresInfo[semester] = []
        semesterNameStr = turn_code_to_str(semester)
        gradeUrl = gradeUrlBase + semester + '&SemesterNameStr=' + semesterNameStr
        soup = BeautifulSoup(self.session.get(gradeUrl).text, 'html.parser')
        for j in soup.find_all('tr')[1:]:
            single = []
            for i in re.findall('<td>(.*?)</td>', str(j), re.S):
                i = self.__deleteUnseeableStr__(str(i))
                single.append(i)
            scoresInfo[semester].append(
                {'taskNo': single[0], 'taskName': single[1], 'taskType': single[2], 'taskGpa': single[3],
                 'taskScore': single[4], 'taskGrade': single[5], 'taskStatic': single[6],
                 'taskQualityAdvice': single[7]})
        self.gradeInfo = scoresInfo
        return scoresInfo

    def caculateGpa(self, semester):
        self.getSemesterList()
        grade = self.getGrade(semester)[semester]
        uppon = 0
        down = 0
        for j in grade:
            if j['taskStatic'] != '未公布' and j['taskQualityAdvice'] != '未评教':
                uppon += float(j['taskGpa']) * float(j['taskScore'])
                down += float(j['taskScore'])
        self.gpa = uppon / down
        return [self.gpa, down]

    def getTeachingQualityAdvice(self):
        """
        获取实例的未评教课程的方法
        实例以后直接调用即可，不用传入其他参数
        :return: 返回实例的评教科目的列表，每个科目在列表中对应一个字典类型的元素
        """
        import threading
        def threadingfunc(j):
            postData = {'PageIndex': j, 'semester': '', 'isRedirect': '', 'TaskNo': 20181}
            soup = BeautifulSoup(
                self.session.post('http://run.hbut.edu.cn/TeachingQualityAssessment/StudentsEvaluation',
                                  data=postData).text, 'html.parser')
            for i in soup.find_all('tr')[1:]:
                previousList = []
                for j in i.find_all('td'):
                    j = re.findall('>(.*?)</td', str(j), re.S)[0]
                    j = re.sub(r'\n|\r| |<.*?>', '', j)
                    previousList.append(j)
                previousDict = {'teachers': previousList[0], 'taskNo': previousList[1], 'taskName': previousList[2],
                                'taskType': previousList[3], 'taskScore': previousList[4],
                                'taskColleage': previousList[5],
                                'taskClass': previousList[6], 'taskStatic': previousList[7]}
                lock.acquire()
                self.qualityList.append(previousDict)
                lock.release()

        soup = BeautifulSoup(
            self.session.get('http://run.hbut.edu.cn/TeachingQualityAssessment/StudentsEvaluation').text, 'html.parser')
        self.qualityList = []
        print(soup)
        pages = int(re.findall('<span>当前显示\d+/(\d+)页</span>', str(soup.find_all('span')[-3]))[0])
        lock = threading.Lock()
        for j in range(1, pages + 1):
            t = threading.Thread(target=threadingfunc, args=(j,))
            t.start()
            t.join()
        return self.qualityList

    def teachingQualityUpload(self):
        """
        自动评教方法，调用这个方法会对实例的未自动评教课程进行自动评教
        注意，在调用这个方法之前先调用getTeachingQualityAdvice()方法，获取评教的列表

        调用这个方法不需要传入参数
        :return:
        """
        # 找出未评教的课程
        waitToUpdate = []
        results = []
        for i in self.qualityList:
            if i['taskStatic'] == '未评教':
                waitToUpdate.append(i)
                results.append(i['taskName'])
        # 开始评教
        url = 'http://run.hbut.edu.cn/TeachingQualityAssessment/Update'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        for i in waitToUpdate:
            data = {
                'PageSize': '10',
                'PageIndex': '1',
                'TaskNo': i['taskNo'],
                'CUserId': '',
                'CurDep': '',
                'Classes': i['taskClass'],
                'GrdAdmin': '',
                'CUserType': 'Student',
                'CurID': '',
                'CurName': '',
                'CUserName': '',
                'Teachers': i['teachers'],
                'SearchType': 'searchAndAdd_ForGrade',
                'Returns': '',
                'SumFs': '100',
                'PfStr': '10, 10, 10, 10, 10, 10, 10, 10, 10, 10',
                'Opinion': '',
            }
            print(data, url)
            self.session.post(url, data=data, headers=header)
            import time
            time.sleep(1)
        return results

    def getRestartLesson(self):
        """
        获取实例的重修课程列表
        :return:实例的重修课程列表
        """
        url = 'http://run.hbut.edu.cn/StuGrade/ViewBukaoSchedule'
        soup = BeautifulSoup(self.session.get(url).text, 'html.parser')
        # 存储重修课
        self.restartLessonList = []
        try:
            for i in soup.find_all('tr')[1:]:
                print(i)
                previousData = []
                for j in re.findall('<td>(.*?)</td>', str(i), re.S):
                    j = self.__deleteUnseeableStr__(j)
                    j = re.sub(' | ', '', j, re.S)
                    previousData.append(j)
                self.restartLessonList.append([previousData[0], previousData[1]])
        except:
            self.restartLessonList = []
        return self.restartLessonList

    def getDetailInformations(self):
        """
        获取实例的详细信息
        :return: 实例的详细信息字典
        """
        url = 'http://202.114.176.67/xszhfw/desktop/digitalDocument.htm'
        soup = BeautifulSoup(self.session.get(url).text, 'html.parser')
        tables = soup.find_all('table')
        informations = {}
        for i in range(len(tables)):
            if i == 0:
                informations['基本信息'] = {}
                singleSoup = BeautifulSoup(str(tables[i]), 'html.parser')
                for j in singleSoup.find_all('tr'):
                    previousData = re.findall(r'<.*?td.*?>(.*?)</td>', str(j), re.S)
                    for i in range(len(previousData)):
                        previousData[i] = self.__deleteUnseeableStr__(previousData[i])
                        if i % 2 != 0:
                            if previousData[i - 1] == '' and previousData[i] == '':
                                continue
                            informations['基本信息'][re.sub('：', '', previousData[i - 1])] = previousData[i]
            if i == 1 or i == 2 or i == 4 or i == 6:
                singleSoup = BeautifulSoup(str(tables[i]), 'html.parser')
                infoType = singleSoup.find_all('td')[0].string
                informations[infoType] = []
                infoTitle = re.findall(r'>(.*?)</td>', str(singleSoup.find_all('tr')[1]))
                for j in singleSoup.find_all('tr')[2:]:
                    previousInfo = re.findall('>(.*?)</td>', str(j))
                    previousDict = {}
                    for i in range(len(previousInfo)):
                        previousDict[infoTitle[i]] = previousInfo[i]
                    informations[infoType].append(previousDict)
        self.informations = informations
        return informations

    def getPlaceList(self):
        """
        获取实例教务处的地点列表
        :return: 教务处地点列表的字典
        """
        soup = BeautifulSoup(self.session.get('http://run.hbut.edu.cn/ArrangeTask/PlaceSchedule').text, 'html.parser')
        roomDict = {}
        for i in soup.ul.children:
            if '>' in str(i):
                singleBuildingDict = {}
                keyA = str(i.div.find_all('span', attrs={'class': 't-in'})[0].string)
                for j in i.ul.children:
                    if '>' in str(j):
                        keyB = str(j.div.find_all('input')[0]['value'])
                        roomsList = []
                        for k in j.find_all('li', attrs={'class': 't-item'}):
                            room = k.div.input['value']
                            roomsList.append(room)
                        singleBuildingDict[keyB] = roomsList
                roomDict[keyA] = singleBuildingDict
        self.placeDict = roomDict
        return roomDict

    def getPlaceSchedule(self, placeName):
        """
        获取地点课表
        :param placeName:教室名
        :return:
        """
        url = 'http://run.hbut.edu.cn/ArrangeTask/RightPlaceSchedule?ClassRoom=' + placeName
        previousData = self.session.get(url).text
        soup = BeautifulSoup(previousData, 'html.parser')
        schedule = {}
        dayTitle = []
        # 获取日期表头
        for n in soup.find_all('tr')[0].find_all('th'):
            dayTitle.append(n.string)
        # 遍历所有的tr变量，获取表格的内容
        s = soup.find_all('table')[0]
        s = BeautifulSoup(str(s), 'html.parser')
        for n in s.find_all('tr')[1:]:
            # 获取第一个节次信息
            # print('n:',n)
            keyB = n.th.string
            # 存储这一节课的所有课的字典
            schedule[keyB] = {}
            # 计数
            count = 0
            # 遍历所有的td标签
            for i in n.find_all('td'):
                count += 1
                # 获取这一节课所在的td标签序号，与日期表头列表里的数据对应
                keyA = dayTitle[count]
                schedule[keyB][keyA] = []
                i = re.sub('<.*td>|\n', '', str(i))
                previous = re.split('<br.*?>', i, re.S)
                for j in previous:
                    j = re.split('\|', re.sub(' |\*', '', j))
                    # 删除空元素
                    for m in j:
                        if m == '':
                            j.remove(m)
                    if j:
                        schedule[keyB][keyA].append(j)
        return schedule

    def getClassList(self):
        """
        获取实例教务处的班级列表
        :return: 教务处地点班级的字典
        """
        soup = BeautifulSoup(self.session.get('http://run.hbut.edu.cn/ArrangeTask/Index').text, 'html.parser')
        roomDict = {}
        for i in soup.ul.children:
            if '>' in str(i):
                singleBuildingDict = {}
                keyA = str(i.div.find_all('span', attrs={'class': 't-in'})[0].string)
                # for j in i.ul.find_all('li',attrs={'class':'t-item'}):
                for j in i.ul.children:
                    if '>' in str(j):
                        keyB = str(j.div.find_all('input')[0]['value'])
                        roomsList = []
                        for k in j.find_all('li', attrs={'class': 't-item'}):
                            room = k.div.input['value']
                            roomsList.append(room)
                        singleBuildingDict[keyB] = roomsList
                roomDict[keyA] = singleBuildingDict
        self.placeDict = roomDict
        return roomDict

    def getClassSchedule(self, className):
        """
        获取班级课表
        :param className: 班级名
        :return:
        """
        url = 'http://run.hbut.edu.cn/ArrangeTask/ClassSchedule?ClassName=' + className
        previousData = self.session.get(url).text
        soup = BeautifulSoup(previousData, 'html.parser')
        schedule = {}
        dayTitle = []
        # 获取日期表头
        for n in soup.find_all('tr')[0].find_all('th'):
            dayTitle.append(n.string)
        # 遍历所有的tr变量，获取表格的内容
        for n in soup.find_all('tr')[1:]:
            # 获取第一个节次信息
            keyB = n.th.string
            # 存储这一节课的所有课的字典
            schedule[keyB] = {}
            # 计数
            count = 0
            # 遍历所有的td标签
            for i in n.find_all('td'):
                count += 1
                # 获取这一节课所在的td标签序号，与日期表头列表里的数据对应
                keyA = dayTitle[count]
                schedule[keyB][keyA] = []
                i = re.sub('<.*td>|\n', '', str(i))
                previous = re.split('<br.*?>', i, re.S)
                for j in previous:
                    j = re.split('\|', re.sub(' |\*', '', j))
                    # 删除空元素
                    for m in j:
                        if m == '':
                            j.remove(m)
                    if j:
                        schedule[keyB][keyA].append(j)
        return schedule

    def getYearQuality(self):
        """
        获取学年鉴定表
        :return:
        """
        soup = BeautifulSoup(self.session.get('http://202.114.176.66/xg/xnjdApply/main.do').text, 'html.parser')
        labels = soup.find_all('label')
        yearQuality = {}
        for i in range(len(labels)):
            if i % 2 == 1:
                print(labels[i - 1].string, labels[i].string)
                yearQuality[labels[i - 1].string] = self.__deleteUnseeableStr__(labels[i].string)
        self.yearQualityForm = yearQuality
        return yearQuality

    def getSearchClass(self, keyword):
        """
        搜索课表
        :param keyword:
        :return:
        """
        baseUrl = 'http://run.hbut.edu.cn/ArrangeTask/_SearchSchedule'
        postData = {'SearchScheduleType': 'Course', 'Context': keyword, 'PageIndex': 1,
                    '-Requested-With': 'XMLHttpRequest'}
        soup = BeautifulSoup(self.session.get(baseUrl, data=postData).text, 'html.parser')
        classList = []
        for i in soup.find_all('tr'):
            s = BeautifulSoup(str(i), 'html.parser')
            td = s.find_all('td')
            if td:
                toappend = self.__deleteUnseeableStr__(td[1].string)
                if toappend != None:
                    classList.append(toappend)
        self.classList = classList
        return classList

    def getSearchSchedule(self, keyword):
        urlBase = 'http://run.hbut.edu.cn/ArrangeTask/RightCourseSchedule?CourseName='
        soup = BeautifulSoup(self.session.get(urlBase + keyword).text, 'html.parser')
        schedule = self.__turnSoupToSchedule(soup)
        return schedule

    def getGpa(self):
        r = self.session.get('http://run.hbut.edu.cn/StuGrade/Index')
        soup = BeautifulSoup(r.text, 'html.parser')
        self.gpa = re.findall('平均学分绩点.*?(\d+\.\d+).*?</div>', r.text, re.S)[0]
        return self.gpa

    def get_freetime_schedule(self, schedule=None):
        if schedule == None:
            schedule = self.getSchedule()

        def remove_list(list_1, list_2):
            for i in list_2:
                if i in list_1:
                    list_1.remove(i)
            return list_1

        lesson_title = ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "第9-10节"]
        week_title = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        count = 0
        result = {}
        before_result = {}
        for row in schedule:
            count += 1
            for column in row:
                place, weeks = self.__get_weeks__(column[-1])
                day, lesson = week_title[(count - 1) % 7], lesson_title[(count - 1) // 7]
                try:
                    standard = before_result[lesson][day]
                except:
                    standard = list(range(1, 21))
                free_weeks = self.__turn_week_list_to_week_string__(remove_list(standard, weeks))
                if result.get(lesson) == None:
                    result[lesson] = {}
                    before_result[lesson] = {}
                result[lesson][day] = free_weeks
                before_result[lesson][day] = remove_list(standard, weeks)
        self.free_time_dict = before_result
        return result

    # 内置方法，请尽量不在外部调用
    def turnToStandable(self, previousData):
        weekDict = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}
        lessonDict = {0: '第一二节', 1: '第三四节', 2: '第五六节', 3: '第七八节', 4: '第九十节', 5: '最后两节'}
        result = []
        for i in previousData:
            j = int(i['tp'])
            week = j // 42 + 1
            locateTip = '第%d周' % (week)
            result.append([locateTip, [j % 42, i['num']]])
        return result

    def __turn_to_numbers__(self, data):
        data = re.split(r' ', data)
        day_dict = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6}
        class_dict = {'12': [0], '34': [1], '56': [2], '78': [3], 'NI': [4], '1234': [0, 1], '5678': [2, 3]}
        data[0] = day_dict[data[0]]
        data[1] = class_dict[data[1]]
        if len(data[1]) == 1:
            result = [data[0] + data[1][0] * 7]
        else:
            result = [data[0] + data[1][0] * 7, data[0] + data[1][1] * 7]
        return result

    def turn_to_code(self, data):
        previous_data = [re.findall('星期.(.*?)节', data)[0], re.findall('星期(.)', data)[0]]
        class_dict = {'第一二': 1, '第三四': 2, '第五六': 3, '第七八': 4, '第九十': 5, '最后两': 5}
        day_dict = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7}
        day = day_dict[previous_data[1]]
        lesson = class_dict[previous_data[0]]
        result = 7 * (lesson - 1) + day - 1
        return result

    def sub_chinese_to_num(self, str):
        str = re.sub(r'一二', '0', str)
        str = re.sub(r'三四', '1', str)
        str = re.sub(r'五六', '2', str)
        str = re.sub(r'七八', '3', str)
        str = re.sub(r'九十', '4', str)
        str = re.sub(r'最后两节', '第5节', str)
        str = re.sub(r'第十周', '第10周', str)
        str = re.sub(r'一', '1', str)
        str = re.sub(r'二', '2', str)
        str = re.sub(r'三', '3', str)
        str = re.sub(r'四', '4', str)
        str = re.sub(r'五', '5', str)
        str = re.sub(r'六', '6', str)
        str = re.sub(r'七', '7', str)
        str = re.sub(r'八', '8', str)
        str = re.sub(r'九', '9', str)
        str = re.sub(r'十', '1', str)
        str = re.sub(r'日', '7', str)
        return str

    def __deleteUnseeableStr__(self, str):
        for i in range(0, 32):
            str = str.replace(chr(i), '')
        str = re.sub(r'<.*?>| |\xa0', '', str)
        return str

    def __turnSoupToSchedule(self, soup):
        schedule = {}
        dayTitle = []
        # 获取日期表头
        for n in soup.find_all('tr')[0].find_all('th'):
            dayTitle.append(n.string)
        # 遍历所有的tr变量，获取表格的内容
        for n in soup.find_all('tr')[1:]:
            # 获取第一个节次信息
            keyB = n.th.string
            # 存储这一节课的所有课的字典
            schedule[keyB] = {}
            # 计数
            count = 0
            # 遍历所有的td标签
            for i in n.find_all('td'):
                count += 1
                # 获取这一节课所在的td标签序号，与日期表头列表里的数据对应
                keyA = dayTitle[count]
                schedule[keyB][keyA] = []
                i = re.sub('<.*td>|\n', '', str(i))
                previous = re.split('<br.*?>', i, re.S)
                for j in previous:
                    j = re.sub('\r', '', j)
                    j = re.split('\|', re.sub(' |\*', '', j))
                    # 删除空元素
                    for m in j:
                        if m == '':
                            j.remove(m)
                    if j:
                        schedule[keyB][keyA].append(j)
        return schedule

    def get_elective_lessons_list(self):
        """
        获取选修课列表
        :return: 所有的选修课列表
        """
        web_page_soup = BeautifulSoup(
            self.session.get("http://run.hbut.edu.cn/SelectCurriculum/PublicElectiveIndex").text, "html.parser")
        tables = web_page_soup.find_all("table")
        if len(tables) > 1:
            elective_table = tables[1]
        else:
            return False
        table_header = []
        for header in elective_table.find_all("th"):
            table_header.append(self.__deleteUnseeableStr__(str(header)))
        elective_lessons = []
        for table_line in elective_table.find_all("tr")[1:]:
            count = 0
            lesson_info = {}
            for table_pane in table_line.find_all("td"):
                lesson_info[table_header[count]] = self.__deleteUnseeableStr__(str(table_pane))
                count += 1
            elective_lessons.append(lesson_info)
        return elective_lessons

    def select_elective_lesson(self, elective_task_code):
        """
        发送选课请求
        :param elective_task_code:选课的任务编号
        :return:
        """
        post_url = "http://run.hbut.edu.cn/SelectCurriculum/Add?Length=16"
        post_data = {"SelectX": elective_task_code,
                     "X-Requested-With": "XMLHttpRequest"}
        resp = self.session.post(post_url, data=post_data).json()
        print(resp)
        if resp["Message"] != "选课门数达到限制，不能再选":
            return True
        else:
            return False

    def __turn_week_list_to_week_string__(self, data_list):
        """
        将表示周数得列表转换为字符串
        :param data_list: 周数列表，例如[1,2,3,4,7,8,10]
        :return: 字符串格式周数：第1-4周、第7-8周、第10周
        """
        import copy
        result = ""
        data_list.sort()
        new_list = copy.deepcopy(data_list)
        complete_flag = False
        the_first_time = True
        while not complete_flag:
            if data_list == new_list and not the_first_time:
                complete_flag = True
            data_list = copy.deepcopy(new_list)
            for i in range(len(data_list)):
                restart = False
                for j in range(1, len(data_list)):
                    j = -j
                    if data_list[i] - data_list[j] == i - len(data_list) - j:
                        for k in range(i, len(data_list) + j + 1):
                            new_list.remove(data_list[k])
                        result += "第{}-{}周、".format(data_list[i], data_list[len(data_list) + j])
                        restart = True
                        break
                if restart:
                    break
            the_first_time = False
        for i in data_list:
            result += "第{}周、".format(i)
        return result[:-1]

    def __get_weeks__(self, week_str):
        if week_str == "本节课为空"[-1]:
            return re.sub("第.*?周", "", week_str), []
        week = re.findall("第(.*?)周", week_str)
        result = []
        for string in week:
            if "-" in string:
                min_week, max_week = string.split("-")
                min_week, max_week = int(min_week), int(max_week)
                for week_code in range(min_week, max_week + 1):
                    result.append(week_code)
            else:
                for week_code_str in string.split(","):
                    result.append(int(week_code_str))
        result = list(set(result))
        place = re.sub(r"第.*?周| ", "", week_str)
        return place, result

    def get_password_of_webiste(self, qq_number=None, mobile_phone=None, email=None, id_card=None):
        url = "http://run.hbut.edu.cn/Account/ReturnPassword"
        res = requests.post(url, {
            "CType": "Student",
            "IDCard": "",
            "PhoneNumber": mobile_phone,
            "QQNumber": qq_number,
            "EMail": email
        })
        print(res.text)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def judge_elective_type(name):
    if name.startswith("兴趣体育选修课"):
        return "哲学与社会科学类", "来自教务处"
    elif name.startswith("大学生创业基础"):
        return "大学生创业基础", "来自教务处"
    elif name.startswith("创新理论基础"):
        return "创新理论基础", "来自教务处"
    info_from_database = database.select_single(elective_subject.table_name, {elective_subject.subject_name: name},
                                                elective_subject.subject_type)
    data_source = database.select_single(elective_subject.table_name, {elective_subject.subject_name: name},
                                         elective_subject.source)
    if info_from_database != None and info_from_database != "数据缺失":
        return info_from_database, data_source
    else:
        all_elective_lessons = database.select(elective_subject.table_name)
        for elective in all_elective_lessons:
            if similar(elective[-2], name) > 0.4 and elective[-3] != "数据缺失":
                return elective[-3], elective[-1]
        else:
            return "数据缺失", "数据缺失"


def find_teacher_schedule(tofind):
    result = {}
    for i in ['第1-2节', '第3-4节', '第5-6节', '第7-8节', '第9-10节']:
        result[i] = {}
        for j in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']:
            result[i][j] = []
    for place_schedule in database.total_table(place_schedule_table,
                                               [schedule_of_classroom, area_of_school, build_name, classroom_name]):
        schedule = database.base64decode(place_schedule[schedule_of_classroom])
        area = place_schedule[area_of_school]
        bulid = place_schedule[build_name]
        classroom = place_schedule[classroom_name]
        for lesson_code in schedule.keys():
            lessons_with_this_lesson_code = schedule[lesson_code]
            for week_day_code in lessons_with_this_lesson_code.keys():
                lessons = lessons_with_this_lesson_code[week_day_code]
                for single_lesson in lessons:
                    if tofind in single_lesson[-2]:
                        print(single_lesson)
                        result[lesson_code][week_day_code].append([single_lesson[0], single_lesson[-2],
                                                                   '%s|%s(地点:%s%s%s)' % (
                                                                       single_lesson[-1], single_lesson[1], area, bulid,
                                                                       classroom)])
    return result


def find_teacher_detail_information(tofind_teacher):
    previous_data = database.select("teacher_info", select_data={"name": tofind_teacher})
    teachers = []
    for data in previous_data:
        id_, colleage, name, base_info_data, other_info_data, subject, job, url = data
        try:
            base_info = database.base64decode(base_info_data, data_type="json")
            other_info = database.base64decode(other_info_data, data_type="json")
        except:
            base_info = {}
            other_info = {}
        teachers.append({
            "id": id_,
            "name": name,
            "colleage": colleage,
            "subject": subject,
            "job": database.base64decode(job, data_type="json"),
            "url": url,
            "base_info": base_info,
            "other_info": other_info
        })
    tofind_teacher = re.sub("[a-z]|[A-Z]", "", tofind_teacher)
    data = Teacher(tofind_teacher).get_teacher_info()
    teachers = [data]
    return teachers
