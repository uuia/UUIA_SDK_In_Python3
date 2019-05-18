# @writer : zhongbr
# @filename:
# @purpose:
import datetime
import hashlib
from hbut_data_sipder.mysql_db_operate.mysql_opreate import mysql_database


class table:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)


############################################################################################
# flask配置部分
flask_salt = "CSH2dsf34fsS34D44dfe1233"
# 运行地址
running_host = "0.0.0.0"
# 运行端口
running_port = 443
############################################################################################
# 学期配置
# 查询成绩变化开关
# 打开将会跟踪教务处成绩公布情况，如果有新的科目成绩公布就会向用户发送邮件通知
# True 开 False 关
check_grade_update = False
# 学期第一周星期一的信息，用于计算周数时使用
year_code_first_day_of_term = 2019  # 年
month_code_first_day_of_term = 2  # 月
day_code_first_day_of_term = 25  # 日
# 当前学期名
now_semester_name = "20182"  # 数字格式
now_semester = "2018-2019学年第二学期"  # 文字格式
# 周内表示方法
weeks_day_titles = [
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日",
]
day_lessons_titles = [
    "第1-2节",
    "第3-4节",
    "第5-6节",
    "第7-8节",
    "第9-10节",
]
# 学校作息时间表
# 第1-2节上下课时间[[上课时,上课分],[下课时,下课分]]
time_of_lesson_1_2_ = [[8, 20], [9, 55]]
# 第3-4节上下课时间
time_of_lesson_3_4_ = [[10, 15], [11, 50]]
# 第5-6节上下课时间
time_of_lesson_5_6_ = [[14, 0], [15, 35]]
# 第7-8节上下课时间
time_of_lesson_7_8_ = [[15, 55], [17, 30]]
# 第9-10节上下课时间
time_of_lesson_9_10_ = [[18, 30], [20, 5]]
####################数据计算部分，请勿改动
time_of_lesson_1_2 = [0, 0]
time_of_lesson_3_4 = [0, 0]
time_of_lesson_5_6 = [0, 0]
time_of_lesson_7_8 = [0, 0]
time_of_lesson_9_10 = [0, 0]
time_of_lesson_1_2[0] = time_of_lesson_1_2_[0][0] * 60 + time_of_lesson_1_2_[0][1]
time_of_lesson_3_4[0] = time_of_lesson_3_4_[0][0] * 60 + time_of_lesson_3_4_[0][1]
time_of_lesson_5_6[0] = time_of_lesson_5_6_[0][0] * 60 + time_of_lesson_5_6_[0][1]
time_of_lesson_7_8[0] = time_of_lesson_7_8_[0][0] * 60 + time_of_lesson_7_8_[0][1]
time_of_lesson_9_10[0] = time_of_lesson_9_10_[0][0] * 60 + time_of_lesson_9_10_[0][1]
time_of_lesson_1_2[1] = time_of_lesson_1_2_[1][0] * 60 + time_of_lesson_1_2_[1][1]
time_of_lesson_3_4[1] = time_of_lesson_3_4_[1][0] * 60 + time_of_lesson_3_4_[1][1]
time_of_lesson_5_6[1] = time_of_lesson_5_6_[1][0] * 60 + time_of_lesson_5_6_[1][1]
time_of_lesson_7_8[1] = time_of_lesson_7_8_[1][0] * 60 + time_of_lesson_7_8_[1][1]
time_of_lesson_9_10[1] = time_of_lesson_9_10_[1][0] * 60 + time_of_lesson_9_10_[1][1]
############################################################################################
# mysql数据库配置部分
# 1.数据库连接信息配置
config_dict = {
    # 数据库地址
    "host": "127.0.0.1",
    # 数据库端口
    "port": 3306,
    # 数据库使用的用户名
    "user": "root",
    # 数据库密码
    "passwd": "123456",
    # 编码
    "charset": "utf8",
    # 使用的数据库名称
    "database": "we_hbut"
}
database_encrypt_token = "zhangweewndsju2dsSDwe23"
###########################################
# 存储用户信息的数据表表名
users_informations_table_tag = 'userinfo_enctypted'
users_informations_backup = "userInfo_backup"
# 用户信息数据表中的各个列名与系统中的各项信息的对应关系
primary_key_uf = "id"
# 1.学号
user_id = 'userid'
# 2.姓名
user_name = 'username'
# 3.邮件地址
email = 'Email'
# 4.邀请码
inviate_code = 'inviate_code'
# 5.物理实验密码
physic_test_password = 'sypassword'
# 6.门户网站密码
portal_site_password = 'mhpassword'
# 7.微信openid
wechat_openid = 'openid'
# 8.课表信息
schedule_json_data = 'schedule'
# 9.本网站密码
password = 'password'
# 10.用户组
user_group = "user_group"
# 11.注册时间
user_sign_in_time = "sign_in_at"
# 12.已修读课程
studied_subjects = "studied_lesson"
###########################################
# 邀请码信息的数据表名
inviate_codes_tag = 'inviate_codes'
# 1.存储邀请码的列名
inviate_code_text = 'inviate_code'
# 2.使用本邀请码的用户的列名
userid_who_use_inviate_code = "name_used"
# 3.创建该邀请码的用户ID
inviate_code_creater = "creater"
###########################################
# 管理员数据库信息表配置
# 管理员账户数据表名
admin_accounts = 'admin_accounts'
# 管理员账户名的列名
admin_id = 'admin_user_name'
# 管理员密码的列名
admin_passwd = 'admin_password'
# 管理员权限值
admin_right_level = 'admin_right_value'
###########################################
# 设置项数据库配置
# 设置数据库的数目
config_database = 'config'
# 设置项目名称
config_item = 'config_type_name'
# 设置项目数据
config_data = 'config_data'
# 时间设置项的名称
time_config = 'time_obj'
# 成绩更新邮件提醒设置项
grade_update_alarm = "grades"
# 课前提醒邮件模板设置项
lesson_alarm_email_model = "emailModel"
###########################################
# 地点课表数据表配置部分
# 1.地点课表数据表的表名
place_schedule_table = "place_schedule"
# 数据表各个列名
# 2.存校区的列名
area_of_school = "part_name"
# 3.存楼栋的列名
build_name = "build_name"
# 4.存教室的列名
classroom_name = "classroom_name"
# 5.存教室课表信息的列名
schedule_of_classroom = "place_schedule"
# 6.存教室占用时间信息的列名
busy_time = "busy_lesson"
###########################################
# 记录日志的数据表格配置
# 记录日志的表名
log_table = "logs"
# 1.操作的url
operate_name = "operate_name"
# 2.操作者id
operate_id = "operator"
# 3.操作客户端ip地址
operate_ip_address = "ip_address"
# 4.操作时间信息
operate_time = "operate_time"
# 5.操作其他信息
operate_tips = "operate_tips"
# 6.将数据存入数据库时，接收到用户的参数代号
args_receive = "args"
# 7.返回给用户的数据的代号
web_reply = "reply"
# 8.每一条log的id的列名
log_id = "id"
###########################################
# 公开用户标识数据表
# 表名
hash_table = "user_id_hash"
# 主键
hash_table_primary_key = "id"
# 用户ID
hash_table_userid = "userid"
# 公开用户标识
hash_table_hash_id = "userid_hash"
# 用户令牌
hash_table_acess_token = "access_token"
###########################################
# 微信登录
# 存储授权信息表名
wechat_login_base = "wechat_login"
# 授权网页的ID
wechat_login_webpage_code = "web_page_code"
# 有效时间
wechat_login_create_time = "time"
# 授权用户的ID
wechat_login_userid = "userid"
# 待授权PC的IP地址
wechat_login_ip_address = "ip_address"
# 操作ID
wechat_login_id = "operite"
# 网页已被试图登录
wechat_confirming = "confirming"
###########################################
# 邮件记录数据表设置
# 邮件记录数据表表名
email_log_table = "email_log"
# 1.邮件标题列
email_log_title = "email_title"
# 2.邮件ID列名
email_log_id = "id"
# 3.邮件发送时间列列名
email_sent_time = "email_send_time"
# 4.邮件收件人信息列
email_receiver = "email_receiver"
# 5.邮件正文列
email_body = "email_body"
############################################################################################
# 邮件发送配置部分
# 1. 发送邮件的邮箱地址
send_email_address = '13367283499@189.cn'
# 2. 发送邮箱的smtp地址
send_smtp_server = 'smtp.189.cn'
# 3. 发送邮件的邮箱密码（授权码）
send_email_passwd = 'zhang1234?'
# 4. 发送邮件的主题、内容编码
email_encoding = 'utf8'
############################################################################################
# 验证码表配置部分
# 验证码表名
check_code_table = "check_code"
# 1.验证码所属的用户列名
check_code_for = "for_userid"
# 2.验证码创建时间
check_code_create_time = "create_time"
# 3.验证码内容
check_code_text = "check_code"
# 4.验证码邮件模板
check_code_email_model = "您好，您在“下一节课的噩耗”网站的验证码为%s！\n请勿泄露给他人，有效时间10分钟！"
# 5.验证码邮件标题
check_code_email_title = "验证码！重要！ 下一节课的噩耗 验证码！"
# 6.验证码唯一id
check_code_id = "id"
############################################################################################
# 微信令牌获取凭据
wechat_access_token = "7cd238b438824a66cea59435b53660ee"
# access_token在数据表名称
access_token_table = "wechat_token"
# 微信公众平台appid
wechat_appid = "wxcf6f799f2cdadcd4"
# 验证微信服务器消息的token
wechat_server_token = 'zhaud12ewdji34w2ewdsaqd'
# 创建时间
token_creat_time = "create_time"
# token
access_token = "token"
# id列
token_id = "id"
# 类型
token_type = "type"


############################################################################################
# 湖北工业大学选修课信息数据库
class elective_lessons_table:
    def __init__(self):
        self.table_name = "elective_subjects_informations"
        self.primary_key = "id"
        self.semester = "semester"
        self.subject_name = "subject_name"
        self.subject_type = "subject_type"
        self.host_teacher = "host_teacher"
        self.others_info = "others_info"
        self.source = "source"


############################################################################################
# 学生团体对象表名数据
class student_group:
    def __init__(self):
        self.table_name = "student_groups"
        self.primary_key = "id"
        self.name = "group_name"
        self.minister = "group_minister_userid"
        self.id = "group_id"
        self.members = "group_members"
        self.type = "group_type"


############################################################################################
# 教师信息数据库配置部分
class Teacher_info_database:
    def __init__(self):
        self.db_name = "teacher_info"
        self.name = "name"
        self.id = "id"
        self.colleage = "colleage"
        self.base_info = "base_info"
        self.other_info = "other_info"
        self.job = "job"
        self.subject = "subject"
        self.url = "url"


############################################################################################
# 微信聊天机器人配置部分
# 机器人菜单文件名或者是字典
the_menu_file = "wechat_msg_parse.MainMenu"
# 开启图灵机器人对对象处理不了的消息进行回复
tulingFlag = False
# 从图灵机器人官网获取的key
tulingKey = '5d982231a3e4410ea46644fe574e366c'
# 机器人管理员用户的id
admin = '1710221405'
# 机器人管理员邮箱（用于接受管理员邮件）
adminEmail = '13367283499@189.cn'
# 等待用户回复的时间
wait_msg_time = 60
# 对对象做出的意外情况自动回复进行自定义设置
userTipDict = {
    # 提示用户选择的提示语
    "chooseTip": "回复“菜单”([Packet])、“退出”(\ue41d)查看菜单或者退出！"
                 "\n请发送下面的序号来选择:",
    # 用户发送错误的参数时，提醒用户重发
    "argErrorTip": "您提供的参数不符合要求哦，请检查一下重新发上一条消息吧！",
    # 用户指令错误的时候，提醒用户重新发指令
    "keyErrorTip": "您发送的消息我还不知道是什么呢，请按照提示语发送消息哦！",
    # 对未绑定账号密码的用户进行提示
    "unkownUserTip": "不好意思哦，由于有些功能需要注册才能使用，所以在使用之前请先注册“下一节课的噩耗”网站的账号并且与本公众号绑定才能继续使用哦！绑定账号可以发送指令“绑定账号#账号#密码”来绑定本公众号的服务！",
    # 菜单提示语结束部分的语言
    "chooseEnd": "小贴士:\n"
                 "<1>您可以使用“#”([發])作为分隔符，一次性回答多个问题\n"
                 "<2>公众号内的每条消息请您在60秒内回复，超过时间会自动回到主菜单哦！\n"
                 "如您在使用时遇到BUG烦请您通过“BUG反馈#您对的BUG描述”的方式反馈给我！"
}
# 绑定账号的指令关键词
bind_command = "绑定账号"
# 注册新用户的指令关键词
sign_in = "新用户"
# 微信公众号绑定成功的回复
bind_successful_tip = "绑定成功！可以开始使用本公众号提供的服务了！为了您的账号密码的安全，建议您删除这段聊天记录哦!"
# 注册成功回复(需要为邀请码的创建者名字创建占位符“%s”)
sign_in_successful_tip = "'您使用来自用户的“%s”的邀请码注册成功！可以开始使用本公众号提供的服务了！为了您的账号密码的安全，建议您删除这段聊天记录哦！'"
# 邀请码错误的回复
bind_err_with_wrong_inviate_code = "邀请码错误或者已经被使用！请重新获取邀请码！"
# 微信公众号门户账号密码错误的回复
bind_err_with_wrong_portal_passwd = "学号与门户密码不匹配呢！请检查重试吧！"
# 密码错误
bind_err_with_wrong_passwd = "账号密码不匹配呢！如忘记密码，请到“下一节课的噩耗”网站重新设置密码后绑定！"
# 关注账号提示语
subcribe_tips = "欢迎您关注下一节课的噩耗公众号！\n" \
                "发送“邀请码”可以获取注册新用户所需的邀请码.\n" \
                "任意发送其他文字内容，公众号将提示引导您如何绑定学号！"
# 未绑定或注册用户提示语
wechat_err_with_unknown_id = "不好意思哦，由于有些功能需要登录学校门户网站,需要您提供信息\n您可以视情况通过下面的两种方式向本公众号提供信息：\n" \
                             "方式一：如果您有“下一节课的噩耗”网站的账号，可以直接发送指令“绑定账号#账号#密码”来绑定本公众号的服务！\n\n" \
                             "方式二：如果您没有账号，需要先获取一个邀请码，然后发送指令" \
                             "“新用户#(邀请码)#(姓名)#(学号)#(门户密码)#(物理实验密码)#(邮箱地址)”" \
                             "[请您用对应的信息替换括号的内容]来注册新账号使用本服务！\n" \
                             "\n回复“邀请码”可以获取未被使用的公开邀请码！\n\n注意：为了避免每个功能操作都访问学校服务器，对学校服务器造成压力，本公众号服务器可能会存储部分您的数据（包括但不限于您的课表、您的成绩表等，您的所有数据在服务器上均为加密存储）来完成相应的功能，如果您仍然注册账号，则代表您悉知并同意本公众号在合理范围内使用这些信息！" \
                             "\n如果您通过方式二多次注册新用户失败，您可以访问如下链接使用刚才的邀请码完成注册后采用方式一绑定账号！" \
                             "\nhttps://www.zhongbr.cn/newuser"


#####################################################
# 微信小程序后端配置
class Wechat_mini_program:
    def __init__(self):
        self.appid = "wxcc86ffef8311d096"
        self.screct = "ec4d457d6c10f9423c125d753aee0aa6"
        self.database_name = "wechat_mini_program"
        self.userid_column = "userid"
        self.publish_column = "publish_userid"
        self.uuid = "publish_userid"
        self.openid = "openid"
        self.session_key = "session_key"
        self.app_token = "zhasdfgshidwqdinSs515etfesfsfdwqdinSsf344aq13"


class Wechat_mini_program_session_key:
    def __init__(self):
        self.database_name = "wechat_mini_program_session_key"
        self.openid = "openid"
        self.session_key = "session_key"


class Wechat_mini_program_send_message:
    def __init__(self):
        self.database_name = "mini_program_alarm_message"
        self.create_time = "create_time"
        self.send_time = "send_time"
        self.args = "msg_args"
        self.userid = "userid"
        self.id = "id"
        self.before_time = 30


# 课程提醒
send_model_message_flag = True


# 微信小程序弹窗通知
class Notifications_Database:
    """
    微信小程序通知弹窗
    """

    def __init__(self):
        """
        初始化
        :param database:mysql_database数据库对象
        """
        self.database_name = "wechat_mini_program_notifications"
        self.id = "id"
        self.title = "title"
        self.type = "type"
        self.time = "time"
        self.text = "text"


# 实例化配置类
notification = Notifications_Database()
elective_subject = elective_lessons_table()
mini_program_message = Wechat_mini_program_send_message()
wechat_mini_program = Wechat_mini_program()
wechat_mini_session = Wechat_mini_program_session_key()
teachers_database = Teacher_info_database()
student_groups_table = student_group()
sha1 = hashlib.sha1()
sha1.update(database_encrypt_token.encode("utf-8"))
database_encrypt_token = sha1.hexdigest()
database = mysql_database(config_dict, database_encrypt_token)
