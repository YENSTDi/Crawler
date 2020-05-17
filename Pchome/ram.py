import pandas as pd
import time
import re
from datetime import datetime
from os import listdir
from os.path import isfile, join

from pymongo import MongoClient
from bs4 import BeautifulSoup as bs

from pchome_tool import get_all_next, get_page_source, to_json, screen_model, log

platform = "pchome"
item = "ram"
ram_urls = {
    "Apacer": 'https://24h.pchome.com.tw/store/DRAC4F',
    "ADATA": 'https://24h.pchome.com.tw/store/DRAC4S',
    "Kingston": 'https://24h.pchome.com.tw/store/DRAC03',
    "HyperX": 'https://24h.pchome.com.tw/store/DRAC04',
    "KLEVV": 'https://24h.pchome.com.tw/store/DRAC8Z',
    "TEAM": 'https://24h.pchome.com.tw/store/DRAC0H',
    "V-Color": 'https://24h.pchome.com.tw/store/DRAC0O',
    "Transcend": 'https://24h.pchome.com.tw/store/DRAC91',
    "Patriot": 'https://24h.pchome.com.tw/store/DRAC79'
}

# 資料放置位置設定
save_path = '../bin/data/{}/'.format(item)
log_path = "../bin/log/"


def to_db(df):
    client = MongoClient()
    # 資料庫名稱
    db = client.crawler
    table = db.ram

    record = df.to_dict("records")

    result = table.insert_many(record)
    return result.acknowledged


def ram_parsing(url, factory):
    name_ = []
    model_ = []
    price_ = []
    factory_ = []
    html = get_page_source(url)
    soup = bs(html, 'html.parser')

    goal_html = ['#Block1Container > * > .mL > .prod_info',  # 大區塊
                 '#Block1Container > * > * > * > .mMV > .prod_info',  # 大區塊旁
                 '#ProdGridContainer > dd'  # 小區塊
                 ]

    # 設定時間
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    now_time = now.strftime("%H:%M")

    for html_patten in goal_html:
        for i in soup.select(html_patten):
            name = i.select('h5 > a')[0].text
            price = i.select('.price_box > * > .price > .value')[0].text

            name, model = screen_model(name)

            name_.append(name)
            model_.append(model)
            price_.append(int(price))
            factory_.append(factory)

    df = pd.DataFrame({
        "date": now_date,
        "time": now_time,
        "platform": platform,
        "name": name_,
        "model": model_,
        "factory": factory_,
        "price": price_
    })
    return df


def ram_go(is_test=False):
    pds = pd.DataFrame()
    for i in ram_urls:
        url = ram_urls[i]
        next_page = get_all_next(url)
        for i2 in next_page:
            pdo = ram_parsing(url=i2, factory=i)
            pds = pd.concat([pdo, pds], ignore_index=True)
            if is_test:
                break
        if is_test:
            break

    # 依價格排序--升續
    pds = pds.sort_values(by=['price'])
    # 去除抓取時的重複資料
    pds = pds.drop_duplicates(subset=['name', 'price'], keep=False)
    # 紀錄時間
    now = time.strftime("%y%m%d%H%M%S", time.localtime())
    # 存檔
    check_save = to_json(df=pds, save_path=save_path, file_name='{}_{}.json'.format(now, item), is_Test=is_test)
    db_result = to_db(df=pds)

    # 紀錄log
    log(platform=platform, log_path=log_path, success=check_save, db_result=db_result,
        path=save_path + '{}_{}.json'.format(now, item),
        time_=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), items=item)

    if is_test:
        pds.to_csv("test.csv", encoding="big5")

# 比較最新兩筆資料差距
def compare_trend2():
    # 確認是檔案且為json檔
    files = [f for f in listdir(save_path) if isfile(join(save_path, f)) and f[-4:] == "json"]
    data2 = sorted(files, reverse=True)[:2]
    print(data2)
    new = pd.read_json(save_path + data2[0])
    prev = pd.read_json(save_path + data2[1])
    print(new)
    print(prev)
    new.to_csv("new.csv", encoding="big5")
    prev.to_csv("prev.csv", encoding="big5")
    return 0

    group = pd.merge(left=new, right=prev, how="left", on=list(new.columns.difference(['price'])))
    group = group.rename({"price_x": "new", "price_y": "price"}, axis=1)
    group = group.fillna(0)

    group['new'] = group['new'].astype(int)
    group['price'] = group['price'].astype(int)

    group['trend'] = group.apply(lambda x: "down" if x['new'] < x['price'] else "", axis=1)

    group.to_csv('trend.csv', encoding="big5")
    print(group)


if __name__ == "__main__":
    ram_go(is_test=True)
    # compare_trend2()
