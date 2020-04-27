import pandas as pd
import time
import re
from os import listdir
from os.path import isfile, join

from bs4 import BeautifulSoup as bs

from pchome_use import get_all_next, get_page_source, stopWord_split, to_json

set_path = 'bin/data/'


def Screen_go():
    def paser(url, factory):
        name_ = []
        price_ = []
        factory_ =[]
        size_ = []
        html = get_page_source(url)
        soup = bs(html, 'html.parser')

        goal_html = ['#Block1Container > * > .mL > .prod_info',# 大區塊
                     '#Block1Container > * > * > * > .mMV > .prod_info',# 大區塊旁
                     '#ProdGridContainer > dd'# 小區塊
                     ]

        for html_patten in goal_html:
            for i in soup.select(html_patten):
                name = i.select('h5 > a')[0].text
                price = i.select('.price_box > * > .price > .value')[0].text

                name_patten = "..[型|吋]"
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
            "platform": "pchome",
            "name": name_,
            "factory": factory_,
            "size": size_,
            "price": price_
        })
        return df

    urls = {
        "acer": 'https://24h.pchome.com.tw/store/DSABEL',
        "asus": 'https://24h.pchome.com.tw/store/DSAB03',
        "view": 'https://24h.pchome.com.tw/store/DSABEW',
        "AOC": 'https://24h.pchome.com.tw/store/DSABGK'
    }

    pds = pd.DataFrame()
    for i in urls:
        url = urls[i]
        next_page = get_all_next(url)
        for i2 in next_page:
            pdo = paser(url=i2, factory=i)
            pds = pd.concat([pdo, pds], ignore_index=True)

    pds['name'] = pds['name'].apply(stopWord_split)
    pds = pds.sort_values(by=['price'])
    pds = pds.drop_duplicates(subset=['name', 'price'], keep=False)

    now = time.strftime("%y%m%d%H%M%S", time.localtime())
    to_json(pds, set_path + '{}Screen.json'.format(now))


def compare_trend2():
    files = [f for f in listdir(set_path) if isfile(join(set_path, f))]
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
    Screen_go()
    # compare_trend2()

