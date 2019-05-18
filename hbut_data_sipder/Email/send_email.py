import smtplib
from email.header import Header  # 用来设置邮件头和邮件主题
from email.mime.text import MIMEText  # 发送正文只包含简单文本的邮件，引入MIMEText即可
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from hbut_data_sipder.config import *
import base64, json


def base64encode(obj):
    if type(obj) != type(''):
        obj = json.dumps(obj)
    return str(base64.b64encode(obj.encode('utf-8')), 'utf-8')


def base64decode(string):
    decode_str = str(base64.b64decode(string), 'utf-8')
    return json.loads(decode_str)


class Email:
    """
    发送邮件
    """

    def __init__(self, title, body, recAdress, email_type='plain'):
        # 发件人和收件人
        self.sender = send_email_address
        self.receiver = recAdress
        # 所使用的用来发送邮件的SMTP服务器
        self.smtpServer = send_smtp_server
        # 发送邮箱的用户名和授权码（不是登录邮箱的密码）
        self.username = send_email_address
        self.password = send_email_passwd
        self.mail_title = title
        self.mail_body = body
        self.email_type = email_type
        # 创建一个实例
        txt = MIMEText(self.mail_body, self.email_type, email_encoding)  # 邮件正文
        self.message = MIMEMultipart()
        self.message.attach(txt)
        self.message['From'] = self.sender  # 邮件上显示的发件人
        self.message['To'] = self.receiver  # 邮件上显示的收件人
        self.message['Subject'] = Header(self.mail_title, email_encoding)  # 邮件主题

    def add_file(self, flie_name):
        file = MIMEApplication(open(flie_name, "rb").read())
        file.add_header('Content-Disposition', 'attachment', filename=flie_name.split("/")[-1])
        self.message.attach(file)

    def startSend(self):
        try:
            smtp = smtplib.SMTP()  # 创建一个连接
            smtp.connect(self.smtpServer)  # 连接发送邮件的服务器
            smtp.login(self.username, self.password)  # 登录服务器
            smtp.sendmail(self.sender, self.receiver, self.message.as_string())  # 填入邮件的相关信息并发送
            print("%s邮件发送成功！！！" % self.receiver)
            database.add(email_log_table,
                         {email_log_title: base64encode(self.mail_title), email_body: base64encode(self.mail_body),
                          email_receiver: self.receiver})
            smtp.quit()
        except smtplib.SMTPException:
            print("邮件发送失败！！！")


if __name__ == '__main__':
    e = Email("测试", "附件测试", "1178395080@qq.com")
    e.add_file("app.py")
    e.startSend()
