# @writer : zhongbr
# @filename:
# @purpose:

from hbut_data_sipder.config import *
from hbut_data_sipder.spiders.hbut_spider.place_schedule_update import update_start


def update_place_schedule():
    update_start()


def query_free_classrooms(part, building, week, day, lesson):
    result = []
    classrooms_in_build = database.select(place_schedule_table, [classroom_name, busy_time],
                                          {area_of_school: part, build_name: building})
    for classroom in classrooms_in_build:
        if int(week) not in database.base64decode(classroom[busy_time])[lesson][day]:
            result.append(classroom[classroom_name])
    return result


if __name__ == '__main__':
    update_place_schedule()
