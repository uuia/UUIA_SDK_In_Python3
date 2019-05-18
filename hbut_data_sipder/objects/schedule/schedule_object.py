import re, json, base64
from hbut_data_sipder.config import *


def get_weeks(week_str):
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
            try:
                for week_code_str in string.split(","):
                    result.append(int(week_code_str))
            except:
                for week_code_str in string.split("、"):
                    result.append(int(week_code_str))
    result = list(set(result))
    place = re.sub(r"第.*?周| ", "", week_str)
    return place, result


def turn_week_list_to_week_string(data_list):
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


class Table:
    """请在新建课程时依次传入 课程名称、主讲信息、地点周数信息、以及上课的时间
       格式：
       课程名称：‘xxxxxx’
       主讲信息：‘xxx-主讲’
       地点周数信息： ‘didian 第x-y周 第a、b、c周’
       上课时间 ： '例：星期日第三四节'、'星期一第NI节'"""

    def __init__(self, username, table_name):
        self.username = username
        self.database = database
        self.table = json.loads(
            self.database.select_single(table_name, {user_id: username}, schedule_json_data, data_type='json',
                                        crypt=True))

    def turnChineseToNum(self, toTurn):
        toTurn = re.sub('星期一', '0', toTurn)
        toTurn = re.sub('星期二', '1', toTurn)
        toTurn = re.sub('星期三', '2', toTurn)
        toTurn = re.sub('星期四', '3', toTurn)
        toTurn = re.sub('星期五', '4', toTurn)
        toTurn = re.sub('星期六', '5', toTurn)
        toTurn = re.sub('星期日', '6', toTurn)
        toTurn = re.sub('一二', '0', toTurn)
        toTurn = re.sub('三四', '1', toTurn)
        toTurn = re.sub('五六', '2', toTurn)
        toTurn = re.sub('七八', '3', toTurn)
        toTurn = re.sub('NI', '4', toTurn)
        num = re.findall('\d+', toTurn)
        result = int(num[0]) + int(num[1]) * 7
        return result

    def creat(self, lessonName, teacherName, others, located):
        try:
            print('located_before>>', located)
            located = self.turnChineseToNum(located)
            print('located_after>>', located)
            self.lessonBaseInfo = [lessonName, teacherName, others]
            print(self.table[located][0])
            if self.table[located][0] == '本节课为空':
                self.table[located] = [self.lessonBaseInfo]
            else:
                self.table[located].append(self.lessonBaseInfo)
            return True
        except:
            return False

    def delete(self, location):
        try:
            self.table[location[0]].pop(location[1])
            if self.table[location[0]] == []:
                self.table[location[0]] = ['本节课为空']
            return True
        except:
            return False

    def edit(self, new, location):
        self.table[location[0]][location[1]] = new

    def save(self):
        self.database.update(users_informations_table_tag, {
            schedule_json_data: str(base64.b64encode(json.dumps(self.table).encode('utf-8')), 'utf-8')},
                             {user_id: self.username}, crypt=True)


def schedule_split(schedule, week):
    colors = []
    day_strings_in_weeks = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    lesson_string_in_day = ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "第9-10节"]
    week = int(week)
    result = {}
    count = 0
    for table_panes in schedule:
        day_title_string = day_strings_in_weeks[count % 7]
        lesson_title_string = lesson_string_in_day[count // 7]
        all_lessons_in_same_time = result.get(lesson_title_string, {})
        all_lessons_in_same_time[day_title_string] = []
        for lesson in table_panes:
            classroom, weeks_have_this_lesson = get_weeks(lesson[-1])
            if week in weeks_have_this_lesson:
                try:
                    color = colors.index(lesson[0])
                except:
                    colors.append(lesson[0])
                    color = colors.index(lesson[0])
                color = min(color, color % 20)
                all_lessons_in_same_time[day_title_string].append(
                    {
                        "location": "{} {}".format(turn_week_list_to_week_string(weeks_have_this_lesson), classroom),
                        "name": lesson[0],
                        "slice": lesson[0][:15],
                        "teacher": lesson[1],
                        "color": color
                    }
                )
        result[lesson_title_string] = all_lessons_in_same_time
        count += 1
    return result
