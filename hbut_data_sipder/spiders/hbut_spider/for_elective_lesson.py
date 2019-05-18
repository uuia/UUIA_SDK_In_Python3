# @writer : zhongbr
# @filename:
# @purpose:

import re
import requests
from bs4 import BeautifulSoup
import os
import time

session = requests.Session()


def get_elective(arg, userid):
    def login(username, password):
        login_url = 'https://sso.hbut.edu.cn:7002/cas/login?service=http%3A%2F%2Fportal.hbut.edu.cn%2Fportal%2Fhome%2Findex.do'
        response = session.get(login_url)
        response.encoding = response.apparent_encoding
        login_soup = BeautifulSoup(response.text, 'html.parser')
        # 用于登陆时的post数据中的lt项
        lt = login_soup.find_all('input')[0]['value']
        login_data = {'lt': lt,
                      '_eventId': 'submit',
                      'loginType': '0',
                      'username': username,
                      'password': password,
                      'j_digitPicture': ''}
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        session.post(login_url, headers=login_headers, data=login_data)
        # print('个人门户网站登陆成功，正在跳转教务处网站！')
        jw_url_2 = 'http://run.hbut.edu.cn/Account/sso'
        r = session.get(jw_url_2)
        # print(r)
        r.raise_for_status()
        # print('教务处网站登陆成功！')
        # print(r.text)

    teacher_name = arg[0]
    username = arg
    password = userid
    # password =  database.select_single(users_informations_table_tag,{user_id:userid},portal_site_password)
    # print('湖北工业大学抢课脚本')
    # username = input('学号:')
    # print('温馨提示此处密码是门户网站密码！')
    # password = input('密码:')
    # print('正在努力登陆中，请勿关闭程序！...')
    counting = 0
    while (1):
        try:
            login(username, password)
            # os.system('cls')
            # print('登陆成功!')
            break
        except:
            counting += 1
            # os.system('cls ')
            # print('登陆失败，正在重试', '.' * (counting % 5 + 1))
            continue
    response = session.get('http://run.hbut.edu.cn/SelectCurriculum/PublicElectiveIndex')
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    c = 0
    while (1):
        c += 1
        all_subject = []
        for i in soup.find_all('tr'):
            i = str(i)
            i = re.sub('\n', '', i)
            i = re.sub('\r', '', i)
            i = re.sub('  ', '', i)
            i = re.split('<.*?>', i)
            i = [j for j in i if j != '']
            all_subject.append(i)
        os.system('cls')
        # print('选修课列表空，继续刷新','.'*(c%3))
        time.sleep(2)
        if len(all_subject) > 4:
            break
        else:
            continue
    formats = '|{:{space}<3}\t|{:{space}<20}\t|{:<8}|{:<8}|{:<20} |{:{space}<6}|{:{space}<12}'
    if len(all_subject[1]) == 1:
        # print('选修课信息列表')
        # print('-' * 127)
        # print(formats.format('序号', '名称', 'selected', 'all', '时间地点', 'credit', '授课老师', space=chr(12288)))
        for i in range(3, len(all_subject)):
            if teacher_name in all_subject[i][7]:
                choose = i
                break
        else:
            choose = 0
            # print('-' * 127)
            # print(
            #     formats.format(int(i) - 2, all_subject[i][2], all_subject[i][3], ' ' + all_subject[i][4], all_subject[i][5],
            #                    '  ' + all_subject[i][6], all_subject[i][7], space=chr(12288)))
        # print('-' * 127)
        # print('一共%d门选修课' % (int(i) - 2))
        # os.system('lessons_info.txt')
        while (1):
            # choose = input('请输入你要选择的课程前面的序号:')
            # choose = int(choose) + 2
            id = all_subject[choose][0]
            url = 'http://run.hbut.edu.cn/SelectCurriculum/Add?Length=16'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            data = {
                'SelectX': id,
                'X-Requested-With': 'XMLHttpRequest'
            }
            needToRestart = False
            while (1):
                try:
                    response = session.post(url, data=data, headers=headers)
                    response.encoding = response.apparent_encoding
                    message = re.findall(r'"Message":"(.*?)"', response.text)
                    # print(message[0])
                    message = message[0]
                    if message[-3:] == '已满员':
                        needToRestart = True
                    else:
                        reply = "选课成功，%s" % (all_subject[choose][2])
                        # print('选课成功，%s' % (all_subject[choose][2]))
                    break
                except:
                    # print('选课失败,正在重试')
                    continue
            if not needToRestart:
                break
    else:
        # print('您已经选课:%s,%s' % (all_subject[1][1], all_subject[1][7]))
        reply = '您已经选课:%s,%s' % (all_subject[1][1], all_subject[1][7])
    return reply


get_elective("1710221405", "100019")
