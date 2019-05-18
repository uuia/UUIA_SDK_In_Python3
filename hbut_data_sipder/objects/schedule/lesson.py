# @writer : zhongbr
# @filename:
# @purpose:
import re


class Lesson:
    def __init__(self, name, teacher, place, weeks, day, time, classes=""):
        self.name = name
        self.teacher = teacher
        self.classes = classes
        self.place = place
        self.weeks_string = weeks
        self.day = day
        self.time = time

    def get_json(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "place": self.place,
            "classes": self.classes,
            "weeks_string": self.weeks_string,
            "weeks_list": self.get_busy_weeks_list(),
            "day": self.day,
            "time": self.time
        }

    def get_busy_weeks_list(self):
        week = re.findall("第(.*?)周", self.weeks_string)
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
        return result


if __name__ == '__main__':
    lesson = Lesson(
        name="test_name",
        teacher="test_teacher",
        place="test_place",
        weeks="第1-10周，第13周，第15周",
        day="星期一",
        time="第1-2节"
    )
    print(lesson.get_busy_weeks_list())
