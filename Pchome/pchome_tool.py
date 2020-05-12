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


# pchome螢幕型號與名稱專用
def screen_model(name):
    rname = re.sub(r"[^\w\s]", '*', name)

    word_list = re.split(r"[^\w]", name)
    model = []
    if isinstance(word_list, list):
        for i in word_list:
            if len(re.sub(r"\A[^a-zA-z]", '*--*', i)) == len(i) and i.lower() != "aoc" and i != "" and len(i) >= 4:
                model.append(i)
    model = ' '.join(model)
    return rname, model


# 將DF存至json
def to_json(df, save_path, file_name, is_Test=False):
    if file_name == "":
        file_name = 'noname.json'

    if is_Test:
        file_name = "test" + file_name



    try:
        df.to_json(save_path+file_name, orient='records')
        # df.to_json(path, orient='records', force_ascii=False, lines=True)
        print("{} ==> 資料寫入成功".format(save_path+file_name))
        return 1
    except:
        print("{} ==> 資料寫入錯誤".format(save_path+file_name))
        return 0


def log(platform, log_path, success, path, time_, items):
    success = "Successful" if success == 1 else "Failed"
    with open(log_path + "{}_log.txt".format(items), "a+") as f:
        f.writelines("{}\t{}\t{} ==> {}\n".format(time_, platform, success, path))

    print("log in ==> item status:{} ==> {}".format(success, time_))
