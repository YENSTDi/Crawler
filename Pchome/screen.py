import pandas as pd
import re
import time

from bs4 import BeautifulSoup as bs

from pchome_use import get_all_next, get_page_source, stopWord_split, to_json

set_path = 'data/'

def Screen_go():
    def paser(url):
        r1 = []
        r2 = []
        html = get_page_source(url)
        soup = bs(html, 'html.parser')

        # 大區塊
        for i in soup.select('#Block1Container > * > .mL > .prod_info'):
            name = i.select('h5 > a')[0].text
            price = i.select('.price_box > * > .price > .value')[0].text

            r1.append(name)
            r2.append(int(price))
        #         print(name)

        # 大區塊旁
        for i in soup.select('#Block1Container > * > * > * > .mMV > .prod_info'):
            name = i.select('h5 > a')[0].text
            price = i.select('.price_box > * > .price > .value')[0].text
            r1.append(name)
            r2.append(int(price))
        #         print(name,price)
        # 小區塊
        for i in soup.select('#ProdGridContainer > dd'):
            name = i.select('h5 > a')[0].text
            price = i.select('.price_box > * > .price > .value')[0].text
            r1.append(name)
            r2.append(int(price))
        #         print(name,price)

        df = pd.DataFrame({
            "name": r1,
            "price": r2
        })
        return df

    urls = {
        "acer": 'https://24h.pchome.com.tw/store/DSABEL',
        "asus": 'https://24h.pchome.com.tw/store/DSAB03',
        "view": 'https://24h.pchome.com.tw/store/DSABEW'
    }

    pds = pd.DataFrame()
    for i in urls:
        url = urls[i]
        next_page = get_all_next(url)
        for i2 in next_page:
            pdo = paser(i2)
            pds = pd.concat([pdo, pds], ignore_index=True)

    pds['name'] = pds['name'].apply(stopWord_split)
    pds = pds.sort_values(by=['price'])

    now = time.strftime("%y%m%d%H%M%S", time.localtime())
    to_json(pds, set_path + '{}Screen.json'.format(now))


if __name__ == "__main__":
    Screen_go()