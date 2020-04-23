import time
import re

from selenium import webdriver
from bs4 import BeautifulSoup as bs

# 取得所有下一頁網址
def get_all_next(url):
    print('正在取得全部網頁')
    nextpage = []
    nextpage.append(url)
    html = get_page_source(url)
    soup = bs(html, 'html.parser')
    for i in soup.select('#PaginationContainer > ul > li > a'):
        if i.text != '下一頁':
            nexts = i['href']
            nexts = 'https://' + nexts[2:]
            nextpage.append(nexts)
    return nextpage

# 取得網頁原始碼
def get_page_source(url):
    print("正在取得網頁原始碼 ==> {}".format(url))
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    htmls = driver.page_source
    driver.close()
    return htmls

# 去除名稱多餘字詞
def stopWord_split(df):
    tmp = re.split('[★].*[★]', df)
    if isinstance(tmp, list) and len(tmp) > 1:
        tmp = tmp[1]
    else:
        tmp = df
    return tmp

# 將DF存至json
def to_json(df, path=""):
    if path == "":
        path = 'noname.json'

    try:
        df.to_json(path, orient='records', force_ascii=False, lines=True)
        print(f"{path} ==> 資料寫入成功")
    except:
        print(f"{path} ==> 資料寫入錯誤")
