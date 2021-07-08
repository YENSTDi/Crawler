import requests
from bs4 import BeautifulSoup
import time
import random


# 1 政治
# 5 生活
# 6 社會
target_board = [1, 5, 6]
years = [2020, 2021]
months = [i for i in range(1,13)]
days = [i for i in range(1,32)]

target_board = [5]
years = [2021]
months = [7]
days = [7,8]

# 年-月-日-新聞種類
ori_url = "https://www.ettoday.net"
target_URL = "https://www.ettoday.net/news/news-list-{}-{}-{}-{}.htm"

def web_GET_data(dicts):
    target_type = dicts['target_type']
    url = dicts['url']
    pattern = dicts['patten']
    reject_strs = dicts['reject_str']
    # print(reject_strs)
    reject_strs = reject_strs.split(',')
    
    webData = requests.post(url=url)
    webSource = BeautifulSoup(webData.text, "html.parser")
    
    content = []
    for i in webSource.select(pattern):
        if target_type == "url":
            iu = i['href']
            content.append(iu)
            continue
        i = i.text
        reject_Boolen = [True if reject_str not in i else False for reject_str in reject_strs]
        reject_Boolen = all(reject_Boolen)
        if reject_Boolen:
            content.append(i)

    return content


def ettoday_main():
    ## 抓取大標資訊 -->標題 URL
    urls = []
    for board in target_board:
        for year in years:
            for month in months:
                for day in days:
                    target_url = target_URL.format(year, month, day, board)
                    patten = ".part_list_2 > h3 > a"
                    big_title = {
                        "target_type": "url",
                        "url": target_url,
                        "patten": patten,
                        "reject_str": ""
                    }
                    print("目標網址===> {}".format(target_url))
                    res = web_GET_data(big_title)

                    if res is None:
                        break
                    urls.extend(res)
                    time.sleep(3)

    print("*"*50)
    urls = list(set(urls))
    print("All url len: {}".format(len(urls)))
    print("*"*50)

    ## 抓URL 標題以及內容
    for url in urls:
        ## 標題

        url = ori_url+url
        title = {
            "target_type": "str",
            "url": url,
            "patten": "header > .title",
            "reject_str": "None"
        }

        content = {
            "target_type": "str",
            "url": url,
            "patten": ".story > p",
            "reject_str": "▲,►,▼,其他人也看了這些新聞..."
        }

        day_time = {
            "target_type": "str",
            "url": url,
            "patten": ".date",
            "reject_str": "None"
        }

        type_ = {
            "target_type": "str",
            "url": url,
            "patten": "div > strong",
            "reject_str": "None"
        }


        art_title = web_GET_data(title)[0]
        art_content = web_GET_data(content)
        art_day_time = web_GET_data(day_time)[0]
        art_type = web_GET_data(type_)[0]
        time.sleep(random.randint(1,5))
        # print(art_title, art_content, art_day_time, art_type)

ettoday_main()