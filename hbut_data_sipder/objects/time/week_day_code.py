# @writer : zhongbr
# @filename:
# @purpose:

from hbut_data_sipder.config import *
import datetime

# 开学第一天
first_day = datetime.datetime(year_code_first_day_of_term, month_code_first_day_of_term, day_code_first_day_of_term)


class Day():
    def __init__(self, date):
        self.date = date
        self.__weeks__ = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        self.past_days = (date - first_day).days
        self.week_string = self.__weeks__[self.past_days % 7]
        self.week_code = self.past_days // 7 + 1
        self.__caculate_lesson__()

    def __caculate_lesson__(self):
        min_sec = self.date.hour * 60 + self.date.minute
        if min_sec < time_of_lesson_1_2[0]:
            self.lesson_string = "第1-2节|前课间"
        if time_of_lesson_1_2[0] < min_sec < time_of_lesson_1_2[1]:
            self.lesson_string = "第1-2节"
        if time_of_lesson_1_2[1] < min_sec < time_of_lesson_3_4[0]:
            self.lesson_string = "第3-4节|前课间"
        if time_of_lesson_3_4[0] < min_sec < time_of_lesson_3_4[1]:
            self.lesson_string = "第3-4节"
        if time_of_lesson_3_4[1] < min_sec < time_of_lesson_5_6[0]:
            self.lesson_string = "第5-6节|中午"
        if time_of_lesson_5_6[0] < min_sec < time_of_lesson_5_6[1]:
            self.lesson_string = "第5-6节|前课间"
        if time_of_lesson_5_6[1] < min_sec < time_of_lesson_7_8[0]:
            self.lesson_string = "第7-8节|前课间"
        if time_of_lesson_7_8[0] < min_sec < time_of_lesson_7_8[1]:
            self.lesson_string = "第7-8节"
        if time_of_lesson_7_8[1] < min_sec < time_of_lesson_9_10[0]:
            self.lesson_string = "第9-10节|前课间"
        if time_of_lesson_9_10[0] < min_sec < time_of_lesson_9_10[1]:
            self.lesson_string = "第9-10节"
        if min_sec > time_of_lesson_9_10[1]:
            self.lesson_string = "晚上"

    def get_the_date_values(self):
        return self.week_code, self.week_string, self.lesson_string.split("|")[0]


def turn_week_string_to_data_object(week, day, lesson):
    __weeks__ = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    __lessons__ = \
        {
            "第1-2节": {
                "hour": time_of_lesson_1_2_[0][0],
                "minute": time_of_lesson_1_2_[0][1],
            },
            "第3-4节": {
                "hour": time_of_lesson_3_4_[0][0],
                "minute": time_of_lesson_3_4_[0][1],
            },
            "第5-6节": {
                "hour": time_of_lesson_5_6_[0][0],
                "minute": time_of_lesson_5_6_[0][1],
            },
            "第7-8节": {
                "hour": time_of_lesson_7_8_[0][0],
                "minute": time_of_lesson_7_8_[0][1],
            },
            "第9-10节": {
                "hour": time_of_lesson_9_10_[0][0],
                "minute": time_of_lesson_9_10_[0][1],
            },
        }
    pass_days = datetime.timedelta(days=(eval(week) - 1) * 7 + __weeks__.index(day),
                                   hours=__lessons__[lesson]["hour"],
                                   minutes=__lessons__[lesson]["minute"])
    return pass_days + first_day


if __name__ == '__main__':
    print(Day(datetime.datetime.today()).get_the_date_values())
