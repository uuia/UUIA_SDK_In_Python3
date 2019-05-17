#@writer : zhongbr
#@filename:
#@purpose: 数据获取逻辑索引
from repository.bind.bind import Bind as bind
from repository.bind_type.get_bind_type import Bind_type as bind_type
from repository.campus_card.get_campus_card import Campus_card as campus_card
from repository.exam.get_exam import Exam as exam
from repository.schedule.get_schedule import Schedule as schedule
from repository.score.get_score import Score as score
from repository.user_info.get_user_info import User_info as user_info
#请将中心服务器的action字段与其相应的数据获取类填入到下面的字典中
get_resopne_index_dict = {
    "bindType":bind_type,
    "bind":bind,
    "exam":exam,
    "userInfo":user_info,
    "score":score,
    "eCard":campus_card,
    "schedule":schedule
}
