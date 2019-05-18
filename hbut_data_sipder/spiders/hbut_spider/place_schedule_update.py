# @writer : zhongbr
# @filename:
# @purpose:
from hbut_data_sipder.spiders.hbut_spider.hbut_website import Student
from hbut_data_sipder.config import *
import re, json, base64, time


def confir(str):
    for i in range(0, 32):
        str = str.replace(chr(i), '')
        str.replace("\r", " ")
    return str


def turnToWeeks(chinese):
    chinese = re.split(r'第|周', chinese)
    result = []
    for i in range(0, len(chinese)):
        if chinese[i] == '':
            continue
        result.append(chinese[i])
    weeks = []
    for i in result:
        if '-' in i:
            i = re.split('-', i)
            for j in range(int(i[0]), int(i[1]) + 1):
                weeks.append(j)
        else:
            for j in re.findall(r'\d+', i):
                j = int(j)
                weeks.append(j)
    return weeks


def base64encode(obj_to_encode):
    return str(base64.b64encode(json.dumps(obj_to_encode).encode('utf-8')), 'utf-8')


def get_busy_weeks(schedule):
    result = {}
    for lesson_code in schedule.keys():
        lesson_data = schedule[lesson_code]
        if result.get(lesson_code) == None:
            result[lesson_code] = {}
        for week_code in lesson_data.keys():
            if result[lesson_code].get(week_code) == None:
                result[lesson_code][week_code] = []
            week_data = lesson_data[week_code]
            busy_weeks = []
            for single_lesson in week_data:
                busy_weeks += turnToWeeks(single_lesson[-1])
            result[lesson_code][week_code] = list(set(busy_weeks))
    return result


def parse_place_list_to_get_schedule(student, classroom_list):
    count = 0
    all = 0
    for i in classroom_list.keys():
        for j in classroom_list[i].keys():
            for k in classroom_list[i][j]:
                all += 1
    for area in classroom_list.keys():
        area_data = classroom_list[area]
        for build in area_data.keys():
            build_data = area_data[build]
            for classroom in build_data:
                schedule = student.getPlaceSchedule(classroom)
                database.update(place_schedule_table,
                                {schedule_of_classroom: base64encode(schedule),
                                 busy_time: base64encode(get_busy_weeks(schedule))},
                                {area_of_school: area, build_name: build, classroom_name: classroom})
                count += 1
                print("第%d/%d个教室：%s" % (count, all, area + build + classroom))
                time.sleep(1)


# if __name__ == '__main__':
def update_start():
    student = Student('1710221405', '100019')
    time.sleep(1)
    classroom_list = student.getPlaceList()
    time.sleep(1)
    parse_place_list_to_get_schedule(student, classroom_list)
