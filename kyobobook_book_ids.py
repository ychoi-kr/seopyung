#!/usr/bin/python3

from urllib import parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import argparse
import re

import spider


site = "https://search.kyobobook.co.kr"


def main(keyword, page):

    qrylist = [
        ("keyword", keyword),
        ("target", "total"),
        ("gbCode", "TOT"),
        ("ra", "date"),
        ("len", "100"),
        ("page", page)
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/search?" + qrystr

    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')

    for x in soup.select_one('div.view_type_list').find_all("a", class_="prod_info"):
        item_id = x["href"].split('/')[-1]
        if item_id.startswith('E'):
            continue
        else:
            print(x["href"].split('/')[-1])
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--publisher", default="위키북스", type=str)
    parser.add_argument("--page", default=1, type=int)
    args = parser.parse_args()
    main(args.publisher, args.page)

