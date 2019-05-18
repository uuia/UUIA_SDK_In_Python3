# @writer : zhongbr
# @filename:
# @purpose:
import requests
from bs4 import BeautifulSoup
from hbut_data_sipder.config import *
from difflib import SequenceMatcher


def get_elective_lessons(web_page_url):
    html_demo = requests.get(web_page_url)
    html_demo.encoding = html_demo.apparent_encoding
    soup_demo = BeautifulSoup(html_demo.text, "html.parser")
    tables = soup_demo.find_all("table")[0]
    table_lines = tables.find_all("tr")
    semester_title = soup_demo.find("title").string
    elective_lessons = []
    for table_line in table_lines[2:]:
        lesson_previous_info_list = []
        for table_pane in table_line.find_all("td"):
            lesson_previous_info_list.append(table_pane.text)
        if len(lesson_previous_info_list) == 4:
            elective_lesson = {
                "lesson_name": lesson_previous_info_list[0],
                "lesson_type": lesson_previous_info_list[1],
                "host_teacher": lesson_previous_info_list[2],
                "other_info": lesson_previous_info_list[3]
            }
        elif len(lesson_previous_info_list) == 3:
            elective_lesson = {
                "lesson_name": lesson_previous_info_list[0],
                "lesson_type": "数据缺失",
                "host_teacher": lesson_previous_info_list[1],
                "other_info": lesson_previous_info_list[2]
            }
        else:
            elective_lesson = {}
        elective_lessons.append(elective_lesson)
    return semester_title, elective_lessons


def write_to_database(semester, subjects):
    for subject in subjects:
        print(subject)
        database.add(elective_subject.table_name, {
            elective_subject.subject_name: subject["lesson_name"],
            elective_subject.subject_type: subject["lesson_type"],
            elective_subject.host_teacher: subject["host_teacher"],
            elective_subject.others_info: subject["other_info"],
            elective_subject.semester: semester[:15]
        })


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_type_of_unkonwn_lesson():
    unknown_lessons = database.select(elective_subject.table_name, select_data={elective_subject.subject_type: "数据缺失"})
    all_lessons = database.select(elective_subject.table_name)
    count = 0
    for uk_lesson in unknown_lessons:
        uk_lesson_name = uk_lesson[-2]
        uk_lesson_id = uk_lesson[0]
        probably_type = None
        same_lesson = None
        max_sim = 0
        for lesson in all_lessons:
            lesson_id = lesson[0]
            lesson_name = lesson[-2]
            sim = similar(uk_lesson_name, lesson_name)
            max_sim = max(sim, max_sim)
            if sim > 0.2 and lesson_id != uk_lesson_id:
                if lesson[-3] != "数据缺失" and max_sim == sim:
                    same_lesson = uk_lesson_name
                    probably_type = lesson[-3]
        if probably_type != None:
            print(same_lesson, uk_lesson_name, probably_type)
            count += 1
            database.update(elective_subject.table_name,
                            {elective_subject.subject_type: probably_type, elective_subject.source: "来自程序推断"},
                            {elective_subject.primary_key: uk_lesson_id})
    print(count, "/", len(unknown_lessons))


if __name__ == "__main__":
    table_url_list = [
        "http://dean.hbut.edu.cn/contents/290/11013.html",
        "http://dean.hbut.edu.cn/contents/290/10321.html",
        "http://dean.hbut.edu.cn/contents/290/7607.html",
        "http://dean.hbut.edu.cn/contents/290/6154.html",

    ]
    elective_lesson = {}
    for url in table_url_list:
        semester, elective_lessons = get_elective_lessons(url)
        print(semester)
        write_to_database(semester, elective_lessons)
    find_type_of_unkonwn_lesson()
