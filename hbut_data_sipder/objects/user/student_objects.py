# @writer : zhongbr
# @filename:
# @purpose:

crypt_flag = False

import json, random, time, re
from hbut_data_sipder.config import *
from hbut_data_sipder.spiders.hbut_spider.hbut_website import Student
from hbut_data_sipder.Email.send_email import Email
from hbut_data_sipder.encrypt.hash import sha1
from hbut_data_sipder.objects.time.week_day_code import *


def create_new_student_group(group_name, group_type, minister):
    """
    创建一个新的学生团体
    :param group_name: 团体名称
    :param minister: 部长ID
    :return: 学生团体ID
    """
    # 检查团体名称是否被占用：
    exist_group_id = database.select_single(student_groups_table.table_name, {student_groups_table.name: group_name},
                                            student_groups_table.id)
    if exist_group_id != None:
        return False, exist_group_id
    group_id_is_satisfied = False
    group_id = "123456"
    while not group_id_is_satisfied:
        group_id = "{:0>6d}".format(random.randint(0, 999999))
        if database.select_single(student_groups_table.table_name, {student_groups_table.id: group_id},
                                  student_groups_table.id) == None:
            group_id_is_satisfied = True
    database.add(student_groups_table.table_name, {
        student_groups_table.name: group_name,
        student_groups_table.type: group_type,
        student_groups_table.minister: minister,
        student_groups_table.members: [minister],
        student_groups_table.id: group_id
    }, crypt=crypt_flag)
    return True, group_id


def create_sign_in_a_new_user(name, userid, portal_password, uuid):
    if User({user_id: userid}):  # 以前已经注册过
        return False, 2
    stu = Student(userid, portal_password)
    if not stu.login_state:
        return False, 1
    else:
        schedule = stu.getSchedule()
    # 用户信息注册
    database.add(
        users_informations_table_tag,
        {
            user_id: userid,
            user_name: name,
            portal_site_password: portal_password,
            schedule_json_data: schedule,
            email: "_unknown_",
            physic_test_password: "123456"
        },
        crypt=True
    )
    database.add(
        wechat_mini_program.database_name,
        {
            wechat_mini_program.userid_column: userid,
            wechat_mini_program.publish_column: uuid,
        }
    )
    return True, 0


def check_wechat_mini_program_pubish_userid(publish_userid):
    userid = database.select_single(wechat_mini_program.database_name,
                                    {wechat_mini_program.publish_column: publish_userid},
                                    wechat_mini_program.userid_column)
    if userid == None:
        return False
    else:
        return True


def turn_weeks_to_list(week_str):
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


class User:
    def __new__(cls, require_dict, table_name=users_informations_table_tag, userid_column_name=user_id, crypt=True):
        """
        控制实例化的过程
        :param require_dict:
        :param table_name:
        :param userid_column_name:
        :param crypt:
        :return:
        """
        if database.select_single(table_name, require_dict, userid_column_name, crypt=crypt) == None:
            return False
        return super(User, cls).__new__(cls)

    def __init__(self, require_dict, table_name=users_informations_table_tag, userid_column_name=user_id, crypt=True):
        """
        用户数据对象，使用户与数据库内的数据产生联系
        以下四个参数中的三个可选参数要么三个都省略，代表依据来自users_informations_table_tag，
        要么不省略，依据实际情况填写！
        :param require_dict: 查找用户的依据，字典类型
        :param table_name: 查找的依据所在的数据表，默认是用户数据表users_informations_table_tag，可选参数
        :param userid_column_name:用户ID在查找依据所在数据表中的列名，可选参数
        :param crypt: 查找依据所在的数据表是否被加密，可选参数
        """
        # 从数据库查询用户的用户ID
        self.userid = database.select_single(table_name, require_dict, userid_column_name, crypt=crypt)
        # 从数据库获取用户的属性
        # 用户姓名
        self.name = database.select_single(users_informations_table_tag, {user_id: self.userid}, user_name, crypt=True)
        # 用户门户网站密码
        self.portal_password = database.select_single(users_informations_table_tag, {user_id: self.userid},
                                                      portal_site_password, crypt=True)
        # 用户物理实验网站密码
        self.physic_password = database.select_single(users_informations_table_tag, {user_id: self.userid},
                                                      physic_test_password, crypt=True)
        # 用户邮箱地址
        self.email = database.select_single(users_informations_table_tag, {user_id: self.userid}, email, crypt=True)
        # 用户课表对象
        self.schedule = json.loads(
            database.select_single(users_informations_table_tag, {user_id: self.userid}, schedule_json_data, crypt=True,
                                   data_type="json"))
        try:
            # 用户修过科目数据
            previous_studied_subjects_data = database.select_single(users_informations_table_tag,
                                                                    {user_id: self.userid}, studied_subjects,
                                                                    crypt=True,
                                                                    data_type="json")
            if previous_studied_subjects_data != None:
                self.studied_subjects = json.loads(previous_studied_subjects_data)
            else:
                self.studied_subjects = {}
        except:
            self.studied_subjects = {}
        # 用户的注册时间
        self.sign_in_time = database.select_single(users_informations_table_tag, {user_id: self.userid},
                                                   user_sign_in_time, crypt=True, data_type="target_uncrypt")
        # 用户微信的openid
        self.openid = database.select_single(users_informations_table_tag, {user_id: self.userid}, wechat_openid,
                                             crypt=True)
        # 获取用户的公开ID
        self.query_hash_token()
        # 用户加入的学生组织
        self.student_group = []
        student_group_previous_data = database.select(student_groups_table.table_name, [
            student_groups_table.name,
            student_groups_table.members,
            student_groups_table.type,
            student_groups_table.id,
            student_groups_table.minister
        ], crypt=crypt_flag)
        for i in range(len(student_group_previous_data)):
            student_group_previous_data[i][student_groups_table.members] = database.base64decode(
                student_group_previous_data[i][student_groups_table.members])
            if self.userid in student_group_previous_data[i][student_groups_table.members]:
                self.student_group.append(student_group_previous_data[i])
        # 微信小程序的公开ID
        self.wechat_mini_program_openid = database.select_single(
            wechat_mini_program.database_name,
            {wechat_mini_program.userid_column: self.userid},
            wechat_mini_program.publish_column
        )

    def login_website_edit(self, web_page_code, confirm=False):
        timestamps = database.select(wechat_login_base, [wechat_login_create_time])
        print(web_page_code, timestamps)
        for timestamp in timestamps:
            database_sign = sha1([web_page_code, timestamp[wechat_login_create_time]])
            ip_address = database.select_single(wechat_login_base, {wechat_login_webpage_code: database_sign},
                                                wechat_login_ip_address)
            if not confirm:
                if ip_address == None:
                    continue
                return ip_address
            if ip_address == None:
                continue
            print(self.userid, database_sign)
            database.update(wechat_login_base,
                            {
                                wechat_login_userid: self.userid
                            },
                            {
                                wechat_login_webpage_code: database_sign
                            })
            return True, "登录成功"
        return "此登录请求不存在，请检查！"

    def create_hbut_website_object(self, login=True):
        """
        创建用户的湖北工业大学门户网站对象
        :return: 湖北工业大学门户网站对象
        """
        return Student(self.userid, self.portal_password, login=login)

    def send_email_to_this_user(self, email_title, email_body, email_type="plain", path_of_file=None):
        """
        向此用户发送邮件的方法
        :param email_title: 邮件标题
        :param email_body: 邮件内容
        :param email_type: 邮件类型
        :param path_of_file: 邮件附件路径,list对象，每个元素代表一个文件
        :return: 无返回值
        """
        # 创建邮件对象
        email = Email(title=email_title, body=email_body, email_type=email_type, recAdress=self.email)
        # 如果有附件，向邮件对象添加附件
        if path_of_file != None:
            for file in path_of_file:
                email.add_file(file)
        # 邮件发送
        email.startSend()

    def emails_sent_to_this_user(self):
        """
        获取公众号曾经向本用户发送的邮件
        :return: 发送邮件的字典组成的列表，字典包含 id,send_time,title,body 四个键
        """
        previous_data_of_the_emails = database.select(email_log_table, select_data={email_receiver: self.email})
        emails = []
        for previous_data in previous_data_of_the_emails:
            email_dict = {
                "id": previous_data[0],
                "send_time": previous_data[3],
                "title": database.base64decode(previous_data[1], data_type="common"),
                "body": database.base64decode(previous_data[4], data_type="common")
            }
            emails.append(email_dict)
        return emails

    def operations_of_this_user(self):
        """
        获取用户在网页访问中留下的日志记录
        :return: 用户的日志列表
        """
        previous_data_of_logs = database.select(log_table, select_data={operate_id: self.userid})
        logs = []
        for previous_data in previous_data_of_logs:
            logs.append({
                "id": previous_data[0],
                "operate_name": previous_data[1],
                "operate_time": previous_data[2],
                "ip": previous_data[4],
                "attributes": database.base64decode(previous_data[5])
            })
        return logs

    def query_hash_token(self):
        """
        查询用户的授权令牌
        :return: 令牌字典,包含token,public_id两个键
        """
        public_hash_id = database.select_single(hash_table, {hash_table_userid: self.userid}, hash_table_hash_id)
        token_access = database.select_single(hash_table, {hash_table_userid: self.userid}, hash_table_acess_token)
        if public_hash_id == None or token_access == None:
            timestamp = str(datetime.datetime.today().timestamp())
            sha1 = hashlib.sha1()
            sha1.update((timestamp + self.userid + self.userid).encode("utf-8"))
            public_hash_id = sha1.hexdigest()
            token_access = str(random.randint(9999999, 99999999))
            database.add(hash_table, {hash_table_userid: self.userid, hash_table_hash_id: public_hash_id,
                                      hash_table_acess_token: token_access})
        self.public_hash_id = public_hash_id
        self.token_access = token_access
        return {"token": token_access, "public_id": public_hash_id}

    def update_hash_token(self):
        """
        更新用户授权苹果捷径等其他使用方式的令牌消息
        :return: 令牌字典,包含token,public_id两个键
        """
        timestamp = str(datetime.datetime.today().timestamp())
        sha1 = hashlib.sha1()
        sha1.update((timestamp + self.userid + self.userid).encode("utf-8"))
        public_hash_id = sha1.hexdigest()
        token_access = str(random.randint(9999999, 99999999))
        if database.select_single(hash_table, {hash_table_userid: self.userid}, hash_table_hash_id) == None:
            database.add(hash_table, {hash_table_userid: self.userid, hash_table_hash_id: public_hash_id,
                                      hash_table_acess_token: token_access})
        else:
            database.update(hash_table, {hash_table_acess_token: token_access, hash_table_hash_id: public_hash_id},
                            {hash_table_userid: self.userid})
        return {"token": token_access, "public_id": public_hash_id}

    def update_users_info(self, table_name, update_data, require_dict={}, crypt=False):
        """
        更新用户在某个数据表内的信息的方法
        :param table_name: 更新信息的表名
        :param update_data: 待更新的数据
        :return:
        """
        if require_dict == {}:
            require_dict = {user_id: self.userid}
        print(list(require_dict.keys())[-1])
        if database.select_single(table_name=table_name, select_root=require_dict,
                                  select_target=list(require_dict.keys())[-1], crypt=crypt) != None:
            database.update(table_name, update_data, require_dict, crypt=crypt)
        else:
            database.add(table_name, update_data, crypt=crypt)

    def delete_this_user(self):
        """
        注销用户的方法，将用户从数据库内移除
        :return:
        """
        database.delete(users_informations_table_tag, {user_id: self.userid}, crypt=True)
        database.delete(email_log_table, {email_receiver: self.email})
        database.delete(hash_table, {hash_table_hash_id: self.userid})
        database.delete(log_table, {operate_id: self.userid})
        database.delete(check_code_table, {check_code_for: self.userid})
        database.delete(inviate_codes_tag, {inviate_code_creater: self.userid})
        database.delete(inviate_codes_tag, {userid_who_use_inviate_code: self.userid})
        database.delete(wechat_login_base, {wechat_login_userid: self.userid})

    def join_to_a_student_group(self, group_id):
        """
        加入某个学生团体的方法
        :param group_id: 团体ID
        :return: 状态，数据
                    出错时为错误码
                    0 代表团体不存在
        """
        student_group = Student_group(group_id)
        if not student_group:
            return False, 0
        return student_group.join_to_this_group(self.userid)

    def save_this_user_to_database(self):
        """
        将用户对象中最新的属性保存到数据可
        :return:
        """
        # 更新用户数据表
        self.update_users_info(users_informations_table_tag, {
            user_id: self.userid,
            user_name: self.name,
            schedule_json_data: self.schedule,
            inviate_code: self.inviate_code,
            portal_site_password: self.portal_password,
            physic_test_password: self.physic_password,
            studied_subjects: self.studied_subjects,
            email: self.email,
            user_group: self.exp,
            user_sign_in_time: self.sign_in_time,
            wechat_openid: self.openid
        })

    def quit_from_group(self, group_id):
        """
        退出学生组织
        :param group_id:组织ID
        :return:
        """
        student_group = Student_group(group_id)
        if not student_group:
            return False, "您发送的学生团体不存在！"
        return student_group.quit_from_this_group(self.userid)

    def divide_lessons_into_types(self):
        types = {}
        for semster in self.studied_subjects:
            for lesson in self.studied_subjects[semster]:
                type_string = lesson["taskType"]
                type_lessons = types.get(type_string, [])
                type_lessons.append(lesson)
                types[type_string] = type_lessons
        return types

    def update_studied_subjects(self):
        student = self.create_hbut_website_object()
        semesters = student.getSemesterList()
        grades_of_all = {}
        time.sleep(1)
        for semester in semesters:
            grades = student.getGrade(semester)[semester]
            grades_of_all[semester] = grades
            time.sleep(1)
        self.update_users_info(users_informations_table_tag, {studied_subjects: grades_of_all}, crypt=True)
        return grades_of_all

    def get_date_arrangement(self, year, month, day, hour=None, minute=None):
        if hour != None and minute != None:
            time_not_determination_sign = False
            date = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        else:
            time_not_determination_sign = True
            date = datetime.datetime(year=year, month=month, day=day)
        day = Day(date)
        week_code, week_day, lesson_ = day.get_the_date_values()
        lessons = []
        for id in range(len(self.schedule)):
            lesson_container = self.schedule[id]
            for lesson in lesson_container:
                if lesson != "本节课为空":
                    place, weeks = turn_weeks_to_list(lesson[-1])
                    if weeks_day_titles.index(week_day) == id % 7 and week_code in weeks and (
                            time_not_determination_sign or day_lessons_titles.index(lesson_) == id // 7):
                        lessons.append({
                            "name": lesson[0],
                            "time": lesson[-1].replace(place, "").replace(" ", ""),
                            "place": place,
                            "teacher": lesson[1],
                            "lesson": day_lessons_titles[id // 7]
                        })
        return lessons


class Minister(User):
    """
    学生团体部长对象
    """

    def query_groups_of_minister(self):
        """
        获取部长对象管理的部门的方法
        :return: 部长对象管理的部门
        """
        self.manage_group_id = database.select_single(student_groups_table.table_name, {
            student_groups_table.minister: self.userid
        }, student_groups_table.id, crypt=crypt_flag)
        self.manage_group = False
        if self.manage_group_id != None:
            self.manage_group = Student_group(self.manage_group_id)
        return self.manage_group

    def query_free_time_of_member(self, member_name):
        """
        部长查询团体成员空闲时间的方法
        :param member_id:
        :return: 查询状态，数据（失败时为错误代码）
                    查询失败时会返回错误码
                    错误码0 代表查询的用户不存在
                    错误码1 代表查询的用户存在但是不是本团体的成员
        """
        self.query_groups_of_minister()
        query_user = User({user_name: member_name})
        if not query_user:
            return False, 0
        if query_user.userid not in self.manage_group.members:
            return False, 1
        return True, query_user.create_hbut_website_object().get_freetime_schedule(query_user.schedule)

    def query_for_free_user_of_some_time(self, query_time):
        """
        查询指定时间有空的用户
        :param query_time: 查询的时间，列表类型["","周数","星期","节次"]
        :return: 有空的用户列表
        """
        self.query_groups_of_minister()
        query_week, query_day, query_lesson = query_time
        free_members_list = []
        # 遍历部长管理的部门成员
        for userid in self.manage_group.members:
            user = User({user_id: userid})
            user_hbut = user.create_hbut_website_object(login=False)
            # 获取成员的空闲时间白
            user_hbut.get_freetime_schedule(user.schedule)
            # 如果用户在指定时间有空就加入列表中
            if eval(query_week) in user_hbut.free_time_dict[query_lesson][query_day]:
                free_members_list.append(user.name)
        return free_members_list

    def create_a_free_schedule_of_group(self, week):
        group_schedule = {}
        for lesson in ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "第9-10节"]:
            group_schedule[lesson] = {}
            for day in ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]:
                group_schedule[lesson][day] = self.query_for_free_user_of_some_time(["", week, day, lesson])
        return group_schedule


class Student_group:
    """
    学生团体对象
    """

    def __new__(cls, group_id):
        if database.select_single(student_groups_table.table_name, {student_groups_table.id: group_id},
                                  student_groups_table.name, crypt=crypt_flag) == None:
            return False
        return super().__new__(cls)

    def __init__(self, group_id):
        """
        获取学生团体对象
        :param group_id:团体的团体ID
        """
        self.group_id = group_id
        self.group_name = database.select_single(student_groups_table.table_name, {student_groups_table.id: group_id},
                                                 student_groups_table.name, crypt=crypt_flag)
        self.type = database.select_single(student_groups_table.table_name, {student_groups_table.id: group_id},
                                           student_groups_table.type, crypt=crypt_flag)
        self.minister = Minister({user_id: database.select_single(student_groups_table.table_name,
                                                                  {student_groups_table.id: group_id},
                                                                  student_groups_table.minister, crypt=crypt_flag)})
        self.members = json.loads(
            database.select_single(student_groups_table.table_name, {student_groups_table.id: group_id},
                                   student_groups_table.members, crypt=crypt_flag, data_type="json"))

    def save_data_to_database(self):
        """
        保存到数据库
        :return:
        """
        database.update(student_groups_table.table_name, {
            student_groups_table.id: self.group_id,
            student_groups_table.name: self.group_name,
            student_groups_table.minister: self.minister.userid,
            student_groups_table.members: self.members
        }, {student_groups_table.id: self.group_id})

    def join_to_this_group(self, join_user):
        """
        用户加入此团体的方法
        :param join_user: 加入用户的ID
        :return: 状态，数据
                    出错时为错误码
                    0 代表用户不存在
        """
        if not User({user_id: join_user}):
            return False, 0
        if join_user not in self.members:
            self.members.append(join_user)
        self.save_data_to_database()
        return True, "加入成功"

    def quit_from_this_group(self, quit_user):
        """
        从这个团体退出
        :param quit_user:退出的用户
        :return:
        """
        if quit_user in self.members:
            self.members.remove(quit_user)
        else:
            return False, "您不在此学生团体中！"
        self.save_data_to_database()
        return True, "退出成功"

    def query_info_of_this_group(self):
        """
        查询此学生团体基本信息
        :return: 基本信息字典
        """
        return {
            "minister": self.minister.name,
            "type": self.type,
            "number_of_members": len(self.members),
            "name": self.group_name
        }

    def delete(self):
        database.delete(student_groups_table.table_name, {student_groups_table.id: self.group_id})


if __name__ == '__main__':
    user = User({user_id: "1710221405"})
    print(user.get_date_arrangement(2019, 5, 14))
