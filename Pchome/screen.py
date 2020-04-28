import pandas as pd
import time
import re
from os import listdir
from os.path import isfile, join

from bs4 import BeautifulSoup as bs

from pchome_use import get_all_next, get_page_source, stopWord_split, to_json

# 資料放置位置設定
set_path = 'bin/data/'

platform = "pchome"
item = "screen"
screen_urls = {
    "acer": 'https://24h.pchome.com.tw/store/DSABEL',
    "asus": 'https://24h.pchome.com.tw/store/DSAB03',
    "view": 'https://24h.pchome.com.tw/store/DSABEW',
    "AOC": 'https://24h.pchome.com.tw/store/DSABGK',
    "Dell": 'https://24h.pchome.com.tw/store/DSAB92',
    "hp": 'https://24h.pchome.com.tw/store/DSABA9',
    "LG": 'https://24h.pchome.com.tw/store/DSABF8',
    "Samsung" : 'https://24h.pchome.com.tw/store/DSABEJ',
    "Banq" : 'https://24h.pchome.com.tw/store/DSABF1'
}


def screen_parsing(url, factory):
    name_ = []
    price_ = []
    factory_ = []
    size_ = []
    html = get_page_source(url)
    soup = bs(html, 'html.parser')

    goal_html = ['#Block1Container > * > .mL > .prod_info',  # 大區塊
                 '#Block1Container > * > * > * > .mMV > .prod_info',  # 大區塊旁
                 '#ProdGridContainer > dd'  # 小區塊
                 ]

    # 抓取型號 re
    name_patten = "..[型|吋]"

    for html_patten in goal_html:
        for i in soup.select(html_patten):
            name = i.select('h5 > a')[0].text
            price = i.select('.price_box > * > .price > .value')[0].text

            re_size = re.search(name_patten, str(name))
            if re_size is not None:
                size = name[re_size.span()[0]:re_size.span()[1]]
            else:
                size = ""

            name_.append(name)
            price_.append(int(price))
            factory_.append(factory)
            size_.append(size)

    df = pd.DataFrame({
        "platform": platform,
        "name": name_,
        "factory": factory_,
        "size": size_,
        "price": price_
    })
    return df


def screen_go(is_test=False):
    pds = pd.DataFrame()
    for i in screen_urls:
        url = screen_urls[i]
        next_page = get_all_next(url)
        for i2 in next_page:
            pdo = screen_parsing(url=i2, factory=i)
            pds = pd.concat([pdo, pds], ignore_index=True)
            if is_test:
                break
        if is_test:
            break

    # 去除多餘字元
    pds['name'] = pds['name'].apply(stopWord_split)
    # 依價格排序--升續
    pds = pds.sort_values(by=['price'])
    # 去除抓取時的重複資料
    pds = pds.drop_duplicates(subset=['name', 'price'], keep=False)
    # 紀錄時間
    now = time.strftime("%y%m%d%H%M%S", time.localtime())
    # 存檔
    to_json(df=pds, path=set_path + '{}Screen.json'.format(now), items=item)


# 比較最新兩筆資料差距
def compare_trend2():
    # 確認是檔案且為json檔
    files = [f for f in listdir(set_path) if isfile(join(set_path, f)) and f[-4:] == "json"]
    data2 = sorted(files, reverse=True)[:2]
    print(data2)
    new = pd.read_json(set_path + data2[0])
    prev = pd.read_json(set_path + data2[1])
    # print(new)
    # print(prev)
    group = pd.merge(left=new, right=prev, how='left', on=['name', 'factory', 'platform', 'size'])
    group = group.rename({"price_x": "new", "price_y": "price"}, axis=1)
    group = group.fillna(0)

    group['new'] = group['new'].astype(int)
    group['price'] = group['price'].astype(int)

    group['trend'] = group.apply(lambda x: "down" if x['new'] < x['price'] else "", axis=1)
    print(group)


if __name__ == "__main__":
    screen_go()
    # compare_trend2()
