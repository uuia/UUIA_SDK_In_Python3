import requests
from hbut_data_sipder.config import *


def get_new_access_token():
    wechat_response = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
            wechat_appid, wechat_access_token))
    new_token = wechat_response.json()['access_token']
    return new_token


def get_new_mini_program_token():
    print("获取小程序口令！")
    wechat_response = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}".format(
            appid=wechat_mini_program.appid, secret=wechat_mini_program.screct)
    )
    return wechat_response.json()['access_token']


def get_token():
    token_in_database = database.select_single(access_token_table, {token_type: 0}, access_token)
    if token_in_database != None:
        if (datetime.datetime.today() - database.select_single(access_token_table, {token_id: 1},
                                                               token_creat_time)).seconds < 7140:
            return database.select_single(access_token_table, {token_type: 0}, access_token)
        else:
            token = get_new_access_token()
            database.update(access_token_table, {access_token: token, token_creat_time: str(datetime.datetime.today())},
                            {token_type: 0})
            return token
    else:
        token = get_new_access_token()
        database.add(access_token_table, {access_token: token, token_type: 0})
        return token


def get_wechat_mini_program_token():
    token_in_database = database.select_single(access_token_table, {token_type: 1}, access_token)
    if token_in_database != None:
        if (datetime.datetime.today() - database.select_single(access_token_table, {token_type: 1},
                                                               token_creat_time)).seconds < 7140:
            return database.select_single(access_token_table, {token_type: 1}, access_token)
        else:
            token = get_new_mini_program_token()
            database.update(access_token_table, {access_token: token, token_creat_time: str(datetime.datetime.today())},
                            {token_type: 1})
            return token
    else:
        token = get_new_mini_program_token()
        database.add(access_token_table, {access_token: token, token_type: 1})
        return token


if __name__ == '__main__':
    print(get_wechat_mini_program_token())
