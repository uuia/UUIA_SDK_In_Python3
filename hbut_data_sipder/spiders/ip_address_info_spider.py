# @writer : zhongbr
# @filename:
# @purpose:

import requests
from bs4 import BeautifulSoup


def query_informations_of_ip_address(ip_address):
    try:
        query_url_model = "http://www.ip138.com/ips1388.asp?ip={}&action=2"
        response = requests.get(query_url_model.format(ip_address))
        response.encoding = response.apparent_encoding
        page_html_codes = response.text
        page_soup = BeautifulSoup(page_html_codes, "html.parser")
        previous_informations = page_soup.find("ul", attrs={"class": "ul1"})
        lines = previous_informations.find_all("li")
        # informations = {
        #     "company":lines[0].text.split("：")[-1],
        #     "location":lines[1].text.split("：")[-1]
        # }
        informations = "{}|{}".format(lines[1].text.split("：")[-1], lines[0].text.split("：")[-1])
    except:
        informations = "获取IP地址：{}的信息失败".format(ip_address)
    return informations


if __name__ == '__main__':
    print(query_informations_of_ip_address("111.230.38.118"))
