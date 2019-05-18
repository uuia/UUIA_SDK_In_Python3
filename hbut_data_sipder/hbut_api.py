# @writer : zhongbr
# @filename:
# @purpose:
import requests, io
from flask import Flask, request, send_file, json
from hbut_data_sipder.spiders.hbut_spider.place_schedule import *
from hbut_data_sipder.objects.user.student_objects import *
from hbut_data_sipder.spiders.hbut_spider.hbut_website import judge_elective_type, find_teacher_schedule, \
    find_teacher_detail_information, Student as St
from hbut_data_sipder.spiders.ip_address_info_spider import query_informations_of_ip_address
from hbut_data_sipder.wechat_server_api.acess_token_admin import get_wechat_mini_program_token
from hbut_data_sipder.encrypt.hash import sha1 as sha1_encrypt
from hbut_data_sipder.mysql_db_operate.database_table_object.notifications import *
from hbut_data_sipder.objects.schedule.schedule_object import *
from hbut_data_sipder.spiders.hbut_spider.place_schedule_update import get_busy_weeks
from hbut_data_sipder.objects.time.week_day_code import *


def create_user_for_mini_program(uuid):
    """
    使用uuid创建User实例
    :param uuid:
    :return:
    """
    user = User(
        {wechat_mini_program.publish_column: uuid},
        table_name=wechat_mini_program.database_name,
        userid_column_name=wechat_mini_program.userid_column,
        crypt=False
    )
    return user


def bind_types_API(uuid):
    return {
        "uuid": uuid,
        "accountType":
            {"comment": "门户网站", "code": "001"},
    }


def bind_API(request):
    uuid = request.get("uuid")
    accounts = request.get("accounts")
    vaild = True
    name = None
    invaild_account_types = []
    for account in accounts:
        if account["code"] == "001":
            student = St(account["username"], account["password"])
            if not student.login_state:
                vaild = False
                invaild_account_types.append(account["code"])
            else:
                name = student.get_user_base_info()["name"]
        else:
            pass
    if vaild and name:
        create_sign_in_a_new_user(
            name=name,
            userid=accounts[0]["username"],
            portal_password=accounts[0]["password"],
            uuid=uuid
        )
    return {
        "uuid": uuid,
        "vaild": vaild,
        "invaildAccountTypes": invaild_account_types
    }


def user_info_API(uuid):
    user = create_user_for_mini_program(uuid)
    # 获取教务处个人信息
    user_info = user.create_hbut_website_object().get_user_base_info()
    return {
        "uuid": uuid,
        "name": user_info["name"],
        "gender": user_info["gendar"],
        "college": user_info["colleage"],
        "major": user_info["subject"],
        "grade": user_info["class"][:2],
        "studentClass": user_info["class"],
        "studentID": user_info["student_id"]
    }


def score_API(uuid):
    user = create_user_for_mini_program(uuid)
    grade = user.create_hbut_website_object().getGrade(now_semester_name)  # 获取本学期成绩
    gpa = user.create_hbut_website_object(login=False).caculateGpa(grade[now_semester_name])
    response = []
    for course in grade[now_semester_name]:
        response.append(
            {
                "name": course["taskName"],
                "courseCode": course["taskNo"],
                "credit": course["taskScore"],
                "grade": course["taskGrade"],
                "extraData": [
                    {"key": "评教", "value": course["taskQualityAdvice"]},
                    {"key": "状态", "value": course["taskStatic"]},
                    {"key": "类型", "value": course["taskType"]}
                ]
            }
        )
    return {
        "uuid": uuid,
        "gpa": gpa[0],
        "courses": response
    }


def schedule_API(uuid):
    user = create_user_for_mini_program(uuid)
    schedule = user.create_hbut_website_object().getSchedule()
    sections_dict = {
        "第1-2节": [1, 2],
        "第3-4节": [3, 4],
        "第5-6节": [5, 6],
        "第7-8节": [7, 8],
        "第9-10节": [9, 10],
    }
    time_count = 0  # 计数用于计算时间
    course_schedule_dict = {}  # 暂时存放课程的字典，将同一课程归类
    for table_cell in schedule:
        for lesson in table_cell:
            if lesson == "本节课为空":
                continue
            name = lesson[0]
            course = course_schedule_dict.get(name, {})
            schedules = course.get("schedules", [])
            day = time_count % 7 + 1
            lesson_time = sections_dict[day_lessons_titles[time_count // 7]]
            place, weeks = turn_weeks_to_list(lesson[-1])
            teacher = lesson[1]
            schedules.append(
                {
                    "weeks": weeks,
                    "day": day,
                    "sections": lesson_time,
                    "classroom": place
                }
            )
            course = {
                "name": name,
                "teacher": teacher,
                "schedules": schedules
            }
            course_schedule_dict[name] = course
        time_count += 1
    resp = list(course_schedule_dict.values())
    return {
        "uuid": uuid,
        "courseTable": resp
    }
