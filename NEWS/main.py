import requests
import time
import re
from datetime import datetime

from pymongo import MongoClient
from selenium import webdriver
from bs4 import BeautifulSoup

client = MongoClient()
db = client.crawler_c
limit = 10000


def main():
    ebc_main()
    # cht_main()


def ebc_main(use_api=True):
    if use_api:
        ebc_api()
    else:
        target_url = ebc_get_target_url()
        for i in target_url:
            url = target_url[i]
            ebc_get_page_news(url)


def ebc_api():
    url = 'https://news.ebc.net.tw/News/List_Category_Realtime'
    headers = {
        "x-requested-with": "XMLHttpRequest"
    }

    news = {
        "社會": "society",
        "政治": "politics",
        "生活": "living",
        "體育": "sport",
        "財經": "business"
    }

    for i in news:
        for page in range(100):
            data = {
                'cate_code': news[i],
                'exclude': '0',
                'page': page
            }
            r = requests.post(url=url, headers=headers, json=data)
            soup = BeautifulSoup(r.text, "html.parser")
            for cell in soup.select(".style1.white-box > a"):
                try:
                    title = cell['title']
                    href = cell['href']
                    if db.content.find_one({"title": title}) is None:
                        print("-" * 50)
                        content = ebc_get_news_content(href)
                        data_to_db(content)

                        spt = 3
                        print("睡覺{}秒..".format(spt))
                        time.sleep(spt)

                    else:
                        print("已存在---->{}".format(title))
                except:
                    pass
                print("-" * 50)


# 東森新聞抓取大項目網址-1
def ebc_get_target_url():
    url = "https://news.ebc.net.tw"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # need = ["熱門", "娛樂", "社會", "政治", "生活", "體育"]
    need = ["社會", "政治", "生活", "體育"]
    news_dict = {}
    for i in soup.select("#pc-nav > * > li > a"):
        if i.text in need:
            news_dict.update({i.text: url + i['href']})
            # print(i['href'])
            # print(i.text)
    for i in soup.select("#pc-nav > * > li > * > a"):
        if i.text in need:
            news_dict.update({i.text: url + i['href']})
            # print(i['href'])
            # print(i.text)

    return news_dict


# 東森新聞-取得新聞網址以及標題-2
def ebc_get_page_news(url):
    t_news = "東森新聞"
    view_text = "正在取得{}網址及標題".format(t_news)
    print(view_text)

    o_driver = webdriver.Chrome()
    o_driver.get(url)

    # 一頁
    while db.content.find({"news": "東森新聞"}).count() < limit:
        content = o_driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        for i in soup.select(".news-list-box > .style1.white-box > a"):
            try:
                if db.content.find_one({"title": i['title']}) is None:
                    print("href -- {}".format(i['href']))
                    print("text -- {}".format(i['title']))
                    content = ebc_get_news_content(i['href'])
                    data_to_db(content)
            except:
                pass

        # 下一頁
        next_page = o_driver.find_element_by_link_text("＞")
        next_page.click()
        time.sleep(3)

    o_driver.close()


# 東森新聞-取得新聞內容-3
def ebc_get_news_content(url):
    o_path = "https://news.ebc.net.tw/"
    url = o_path + url
    print("正在取得新聞內容... url:{}".format(url))

    use_webdriver = False

    if use_webdriver:
        driver_content = webdriver.Chrome()
        driver_content.get(url)

        time.sleep(3)

        content = driver_content.page_source
        soup = BeautifulSoup(content, "html.parser")
        driver_content.close()

    else:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")



    # 新聞標題
    title = soup.find("h1").text
    #     print(title)

    # 類型
    try:
        n_type = soup.select("#web-map > a")[-2].text
    except:
        n_type = ""

    # 資訊
    info = soup.select(".info > .small-gray-text")[0].text
    infos = info.split(" ")
    days = infos[0] if isinstance(infos, list) else infos
    times = infos[1] if len(infos) > 1 else ""
    news = infos[2] if len(infos) > 2 else ""
    post = infos[3] if len(infos) > 3 else ""
    author = infos[4] if len(infos) > 4 else ""

    # 新聞內容
    contents = ""
    for i in soup.select(".raw-style > * > * > p"):
        content = i.text
        content.replace(" ", "")
        if re.search("[★▼►●]", content) == None and len(content) > 25:
            #             print(content)
            contents += content
    #             print("_"*100)

    integration = {
        "day": days,
        "time": times,
        "type": n_type,
        "news": news,
        "post": post,
        "author": author,
        "title": title,
        "content": contents
    }

    # print(integration)
    return integration


def cht_main():
    st = time.time()
    target_url = cht_get_target_url()
    for i in target_url:
        print("{}類型新聞抓取中....".format(i))
        url = target_url[i]

        for page in range(1, limit):
            # if page > 1:

            tmp_url = url.replace("/?chdtv", "") + "?page={}&chdtv".format(page)
            print("正在抓取資料 url:{}".format(tmp_url))
            if not cht_get_page_news(tmp_url):
                print("page:{} no data".format(page))
                break

        print("+" * 50)
    et = time.time()
    print("資料已全數抓取成功!!  耗時{}秒".format(et-st))


def cht_get_target_url():
    url = "https://www.chinatimes.com/?chdtv"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    # need = ["政治", "生活", "娛樂", "社會", "體育"]
    need = ["政治", "生活", "社會", "體育"]

    news_dict = {}

    print("正在取得{}類新聞".format(','.join(need)))

    def cmt_fix(url_):
        s = url_.split('/')
        s = s + ['total']
        temp = s[-1]
        s[-1] = s[-2]
        s[-2] = temp
        s = '/'.join(s)
        s = "https:" + s
        return s

    for i in soup.select(".main-nav-item-group > li > a"):
        #     print(i['href'])
        #     print(i.text)
        if i.text in need:
            news_dict.update({i.text: cmt_fix(i['href'])})
    return news_dict


def cht_get_page_news(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    is_art = False

    o_path = "https://www.chinatimes.com"
    for i in soup.select(".vertical-list.list-style-none > li"):
        is_art = True
        title = i.find('h3').text
        href = o_path + i.find('a')['href']

        if db.content.find_one({"title": title}) is None:
            print(i.find('h3').text)
            print(i.find('a')['href'])
            content = cht_get_news_content(href)
            data_to_db(content)

            s_time = 5
            print("睡覺{}秒".format(s_time))
            for i in range(s_time):
                print(i+1, end=' ')
                time.sleep(1)
            print("-" * 50)
        else:
            print("{}\t已存在...".format(title))

    return is_art


def cht_get_news_content(url):
    print("取得新聞內容 url:{}".format(url))
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1").text
    #     print(title)

    infos = []
    for i in soup.select(".meta-info > *"):
        if i.text != "":
            s = i.text.replace("\n", "")
            infos.append(s)
    #             print(s)
    #             print("-"*50)
    days = infos[0][5:] if isinstance(infos, list) else infos
    times = infos[0][:5] if isinstance(infos, list) else infos
    news = infos[1] if len(infos) > 1 else ""
    author = infos[2] if len(infos) > 2 else ""

    # 文章類別
    type_ = []
    for i in soup.select(".breadcrumb-wrapper > * > * > a"):
        #         print(i.text.replace("\n",""))
        #         print("-"*50)
        r = i.text.replace("\n", "")
        type_.append(r)
    n_type = type_[-1]
    #     print(type_)

    contents = ""
    for i in soup.select(".article-body > p"):
        #         print(i.text)
        content = i.text
        contents += content

    integration = {
        "day": days,
        "time": times,
        "type": n_type,
        "news": news,
        "author": author,
        "title": title,
        "content": contents
    }
    return integration


def data_to_db(dicts):
    print("儲存至SQL {}\t{}\t{}\t{}\t{}".format(dicts['news'], dicts['type'], dicts['day'], dicts['time'], dicts['title']))
    coll = db.content

    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        if coll.insert_one(dicts):
            status = "success"
        else:
            status = "fail"
    except:
        status = "system_fail"
    # finally:
    #     client.close()

    # log to file
    log = "{}\t{}\t{}\t{}\t{}".format(now, status, dicts['news'], dicts['type'], dicts['title'])
    log_(log)


def log_(text):
    try:
        with open("log.txt", "a+") as f:
            f.write(text + "\n")
    except:
        with open("log.txt", "a+") as f:
            f.write("log write error")


main()
client.close()
