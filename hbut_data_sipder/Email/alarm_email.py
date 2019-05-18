import re
from Email.send_email import Email
import time
from database.mysql_opreate import *
from hbut_data_sipder.config import *


def local_parser(username1):
    demo = database.select_single(users_informations_table_tag, {user_id: username1}, schedule_json_data,
                                  data_type="json", crypt=True)
    demo = json.loads(demo)
    return demo


def td_matters(td, temp_li):
    code = td[0]
    day = td[1]
    response = lessons_each_week(temp_li, code)
    tests = getPhysicTest(response)
    tests_nextweek = getPhysicTest(lessons_each_week(temp_li, code + 1))
    tests_preweek = getPhysicTest(lessons_each_week(temp_li, code - 1))
    matter_name = response[0][day::7]
    matter_add = response[1][day::7]
    print_datas = ''
    lesson_dict = {}
    lesson_title = {0: '第一二节课:', 1: '第三四节课:', 2: '第五六节课:', 3: '第七八节课:', 4: '晚上:', }
    for i in range(0, 5):
        if matter_name[i] == '这一节没课':
            continue
        print_datas += '%s  %s %s \n' % (lesson_title[i], matter_name[i], matter_add[i])
        lesson_dict[lesson_title[i]] = '课程名称：%s\n%s\n' % (matter_name[i], matter_add[i])
    if print_datas == '':
        print_datas = '你今天可以休息一下啦，没有课哦！'
    return [print_datas, lesson_dict, tests, tests_nextweek, tests_preweek]


def lessons_each_week(data, code):
    global week_code
    # print(data)
    week_code = code
    terminal_contact = []
    # 遍历整个课表数据中所有的节次
    for i in data:
        temp_contact = []  # 每节课程对应的周数索引，储存周数信息
        # 遍历每个节次中的所有课程
        for j in i:
            # print(j[0])
            # 取出这门课程所在的周数信息
            temp_data = re.findall(r'第(.*?)周', j[len(j) - 1])
            # print(temp_data)
            if temp_data:
                contact = []
                for k in temp_data:
                    temp = []
                    if re.search(r'\d+-\d+', k):
                        l = re.findall(r'\d+', k)
                        # print('before_line :',l)
                        for m in range(int(l[0]), int(l[1]) + 1):
                            temp.append(m)
                            # print('temp_line:',temp)
                    else:
                        l = re.findall(r'\d+', k)
                        # print('before_point :', l)
                        for m in l:
                            temp.append(int(m))
                            # print('temp_point:',temp)
                    contact.append(temp)
                temp = []
                for p in contact:
                    for q in p:
                        temp.append(q)
                contact = temp
                # print('after', contact)
                temp_contact.append(contact)
        # print('temp_contact',temp_contact)
        terminal_contact.append(temp_contact)
    # print(terminal_contact)
    temp = []  # 存储所有包含要查阅的周数的课程的索引信息
    lesson_list = []  # 存储课程的名称信息
    pt_list = []  # 存储主讲教师信息和上课地点和时间
    # 这个循环用于遍历周数索引，找到含有等待查询周数的课程在整张课表中所在的位置信息，并且将这个信息存储到索引temp列表中
    # 由于这个列表是一个三维列表，所以这里用了三次for循环来遍历到里面的每一个元素
    for m in range(0, len(terminal_contact)):
        for n in range(0, len(terminal_contact[m])):
            for p in range(0, len(terminal_contact[m][n])):
                if terminal_contact[m][n][p] == int(code):
                    temp.append([m, n])

    for m in range(0, 35):
        freetime = True
        lesson_list_to_append = ''
        pt_list_to_append = ''
        for n in temp:
            if m == n[0]:
                freetime = False
                if len(data[n[0]][n[1]]) <= 2:  # 由于教务处课表中有些课程没有主讲老师信息，所以这样的课程需要单独处理
                    lesson_list_to_append += data[n[0]][n[1]][0] + '\n' + data[n[0]][n[1]][1] + '\n'
                else:
                    lesson_list_to_append += data[n[0]][n[1]][0] + '\n' + data[n[0]][n[1]][1] + data[n[0]][n[1]][
                        2] + '\n'
        if freetime:
            lesson_list.append('这一节没课')
            pt_list.append('这一节没课')
        else:
            lesson_list.append(lesson_list_to_append)
            pt_list.append(pt_list_to_append)
    return [lesson_list, pt_list]


def getHourMinute():
    timeToSend = json.loads(
        database.select_single(config_database, {config_item: time_config}, config_data, data_type="json"))
    NowHour = datetime.datetime.today().hour
    NowMinu = datetime.datetime.today().minute
    print('-' * 30)
    print('当前时间', NowHour, ':', NowMinu)
    for i in range(len(timeToSend)):
        if NowHour == timeToSend[i][0] and NowMinu == timeToSend[i][1]:
            toReturn = i
            break
    else:
        toReturn = 1000
    return toReturn


def getPhysicTest(table):
    tests = []
    for i in range(len(table[0])):
        if '物理实验' in table[0][i]:
            tests.append([re.sub('\n', ' ', table[0][i]), i])
    return tests


def getTodayWeekDay():
    term_start_day = datetime.datetime(year_code_first_day_of_term, month_code_first_day_of_term,
                                       day_code_first_day_of_term)  # 这个变量用于存储一个学期开始的第一天（第一周周一的日期）
    today = datetime.datetime.today()
    the_past_days = today - term_start_day  # 确定今天距离第一周第一天过去的天数
    the_past_days = int(the_past_days.days)
    weekt = the_past_days // 7 + 1
    dayt = the_past_days % 7
    return [weekt, dayt]


def getPhysicTestTips(tests, testsNext, testsPre):
    daytitle = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}
    lessontitle = {0: '第一二节课', 1: '第三四节课', 2: '第五六节课', 3: '第七八节课', 4: '晚上', }
    tips = ''
    for m in testsPre:
        if m[1] % 7 > dayt:
            tips += '（上%s）做了%s，过了接近一个星期，实验报告可能要交了哦！\n' % (daytitle[m[1] % 7], re.sub('\n', ' ', m[0]))
    for m in tests:
        if m[1] % 7 > dayt:
            tips += '（本周）%d天后%s有%s，记得预习\n' % (m[1] % 7 - dayt, lesson_title[m[1] // 7], re.sub('\n', ' ', m[0]))
        if m[1] % 7 == dayt:
            tips += '（本周）今天%s有%s，千万别忘了\n' % (lesson_title[m[1] // 7], re.sub('\n', ' ', m[0]))
        if m[1] % 7 < dayt:
            tips += '（本周）%d天前做了%s,报告要赶紧写起来鸭！\n' % (dayt - m[1] % 7, re.sub('\n', ' ', m[0]))
    for m in testsNext:
        tips += '(下周)%s%s:%s,如果有必要请提前预习预习哟！\n' % (daytitle[m[1] % 7], lessontitle[m[1] // 7], re.sub('\n', ' ', m[0]))
    if tips != '':
        tips = '以下是近3周的物理实验信息：\n' + tips
    return tips


def getWeather():
    from others.getWeather import Weather
    json = Weather('狮子山街道').weatherJson
    weathers = '武汉市洪山区狮子山街道近12个小时天气（来源中国天气网）:\n'
    for i in range(0, 12):
        weathers += '%s点：%s %s度 %s%s\n' % (
            json[i]['time_obj'], json[i]['weather'], json[i]['temp'], json[i]['windD'], json[i]['windL'])
    if '雨' in weathers:
        weathers += '近几个小时可能有雨，出门在外，尤其是在武汉，出门记得带伞！\n'
    return weathers


def turnModelToExample(keywords, typename):
    model = json.loads(database.select_single(config_database, {config_item: lesson_alarm_email_model}, config_data,
                                              data_type="json"))[typename]
    modelList = re.split(r'//', model, re.S)
    result = ''
    for i in modelList:
        if i in keywords.keys():
            result += keywords[i]
        else:
            result += i
    print(result)
    return result


def userLoop(username1, emailAdress, name, td, NowCode, ck):
    daytitle = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}
    temp_li = local_parser(username1)
    tds = td_matters(td, temp_li)
    today_matters_total, dict, tests, testsNextWeek, testsPreWeek = tds[0], tds[1], tds[2], tds[3], tds[4]
    tips = getPhysicTestTips(tests, testsNextWeek, testsPreWeek)
    gradesNewest = ''
    if ck:
        print('正在查询%s同学的成绩.....' % name)
        gradesNewest = getNewestGrade(username1)
    if NowCode == 1000:
        if not gradesNewest:
            gradesNewest = ''
            toPrintTip = '<成绩还未更新>'
        else:
            toPrintTip = '<%s>' % gradesNewest
        email_address = database.select_single(users_informations_table_tag, {user_id: username1}, email)
        print('<', username1, '>', '<%s>' % email_address, name, "同学，现在不需要发送邮件", toPrintTip)
    if NowCode == 0:
        # weather = getWeather()
        weather = ""
        emailTitle = '今日课程提醒！'
        emailData = {'grades': gradesNewest, 'name': name, 'weekcode': str(td[0]), 'daycode': daytitle[td[1]],
                     'lessons': today_matters_total, 'physicTest': tips, 'weather': weather}
        emailBody = turnModelToExample(emailData, 'wholeDayEmail')
        Email(emailTitle, emailBody, emailAdress).startSend()
    else:
        if NowCode != 0:
            if NowCode != 1000 and lesson_title[NowCode - 1] in dict.keys():
                weather = getWeather()
                # weather = ''
                print('%s 到点发邮件了！' % name)
                title = '温馨提示：下一节课（%s）有课' % lesson_title[NowCode - 1]
                #                 body = '%s同学,你好！，下一节课(%s)将在二十分钟后开始，不要忘了去！\n%s%s\n%s\n这封邮件来自——钟摆人的网站。\n课程添加请戳http://111.230.38.118/'%(name,lesson_title[NowCode-1],dict[lesson_title[NowCode-1]],tips,weather)
                emaildata = {'grades': gradesNewest, 'name': name, 'lessoncode': lesson_title[NowCode - 1],
                             'lesson': dict[lesson_title[NowCode - 1]], 'weather': weather, 'physicTest': tips}
                body = turnModelToExample(emaildata, 'eachLessonEmail')
                Email(title, body, emailAdress).startSend()


def getNewestGrade(userid):
    global gradeFile
    semester = gradeFile['semester']
    user = stuClasses[userid]
    try:
        grade = user.getGrade(semester)
    except:
        from spiders.hbut_spider.hbut_website import Student
        portal_password = database.select_single(users_informations_table_tag, {user_id: userid}, portal_site_password)
        user = Student(userid, portal_password)
        grade = user.getGrade(semester)
    oldGrade = gradeFile.get(userid)
    if oldGrade == None:
        oldGrade = []
    result = []
    if oldGrade != grade:
        for i in grade[semester]:
            if i not in oldGrade:
                result.append(i)
            else:
                continue
    gradeFile[userid] = grade[semester]
    toSend = ''
    toreturn = ''
    if result:
        users_name = database.select_single(users_informations_table_tag, {user_id: userid}, user_name)
        toSend = '%s,您好，您在教务处的成绩有如下更新:\n' % (users_name)
        for i in result:
            if i['taskStatic'] != '未公布':
                toSend += '科目名称：%s\n学分：%s分，绩点：%s 成绩%s分\n' % (
                    i['taskName'], i['taskScore'], i['taskGpa'], i['taskGrade'])
                toreturn += toSend
    emailAddress = database.select_single(users_informations_table_tag, {user_id: userid}, email)
    if toSend != '':
        Email('教务处成绩更新啦！', toSend, emailAddress).startSend()
    else:
        pass
    return toreturn


def getUserList(loginFlag=False):
    from spiders.hbut_spider.hbut_website import Student
    user_id_list = database.total_table(users_informations_table_tag, [user_id])
    tempListUsers = []
    toappend = {}
    for i in user_id_list:
        i = i[user_id]
        portal_password = database.select_single(users_informations_table_tag, {user_id: i}, portal_site_password)
        email_address = database.select_single(users_informations_table_tag, {user_id: i}, email)
        user_total_name = database.select_single(users_informations_table_tag, {user_id: i}, user_name)
        if loginFlag:
            toappend[i] = Student(i, portal_password)
        tempListUsers.append([i, email_address, user_total_name])
    users = tempListUsers
    if loginFlag:
        return [users, toappend]
    else:
        return users


if __name__ == '__main__':
    import threading

    print('started')
    gradeFile = json.loads(
        database.select_single(config_database, {config_item: grade_update_alarm}, config_data, data_type="json"))
    users, stuClasses = getUserList(loginFlag=True)
    td = getTodayWeekDay()
    print(td)
    today = datetime.datetime.today()
    dayt = td[1]
    lesson_title = {0: '第一二节课:', 1: '第三四节课:', 2: '第五六节课:', 3: '第七八节课:', 4: '晚上:', }
    count = 0
    while 1:
        if count % 5 == 0:
            count = 0
            checkGrade = check_grade_update
        else:
            checkGrade = False
        count += 1
        users = getUserList()
        NowCode = getHourMinute()
        for i in users:
            threading.Thread(target=userLoop, args=(i[0], i[1], i[2], td, NowCode, checkGrade)).start()
        # open('grades.txt','w',encoding='utf8').write(json.dumps(gradeFile))
        database.update(config_database, {config_data: gradeFile}, {config_item: grade_update_alarm})
        if datetime.datetime.today().day != today.day:
            td = getTodayWeekDay()
            print(td)
            dayt = td[1]
        time.sleep(60)
