#!/usr/bin/python3

from urllib import parse
from bs4 import BeautifulSoup
import argparse
import sys
import re
import time
import json
import requests

import review_crawler


site = "https://product.kyobobook.co.kr"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'Referer': "https://search.kyobobook.co.kr/",
}


def main(itemid_list, csv, noheader, order=None, showurl=None):
    review_crawler.mainloop(itemid_list, bookinfo, reviewlist, csv, noheader, order, showurl)


def bookinfo(itemid, showurl):
    if itemid.startswith('E'):
        url = "https://ebook-product.kyobobook.co.kr/dig/epd/ebook//" + itemid
    else:
        url = "https://product.kyobobook.co.kr/detail/" + itemid
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    if showurl:
        print(url)
    
    title = soup.find("span", class_="prod_title").text
#    ebook = False
#    if ebook:
#        title = '[ebook] ' + title
#
    div_author = soup.find('div', class_='author')
    authors = ','.join([a_tag.text for a_tag in div_author.find_all('a')])
    publisher = soup.find('a', class_='btn_publish_link').text
    pubdate = soup.find('div', class_='prod_info_text publish_date').contents[-1].replace('·', '').strip()
    pubdate = re.sub(r'(\d+)년 (\d+)월 (\d+)일', r'\1-\2-\3', pubdate)

    return {
        "itemid": itemid,
        "title": title,
        "url": url,
        "author": authors,
        "pubdate": pubdate
    }


def reviewlist(info, csv, order=None, showurl=None):
    result = []

    qrylist = [
        ("page", "1"),
        ("pageLimit", "10"),
        ("reviewSort", "001"),
        ("revwPatrCode", "000"),
        ("saleCmdtid", info["itemid"]),
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/api/review/list?" + qrystr
    if showurl:
        print(url)

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    data = response.json()
    #print(data)
    #data = json.loads(response)
    reviews = data["data"]["reviewList"]

    for review in reviews:
        buy_dict = {'001': '', '002': '구매자', '003': '한달 후 리뷰'}
        result.append({
            "reviewerid": review['mmbrId'], 
            "reviewdate": review['cretDttm'].split()[0],
            "content": review['revwCntt'],
            "buy": buy_dict[review['revwPatrCode']],
            "rating": str(review['revwRvgr']),
        })

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", action=argparse.BooleanOptionalAction)
    parser.add_argument("--noheader", action=argparse.BooleanOptionalAction)
    parser.add_argument("--showurl", action=argparse.BooleanOptionalAction)
    parser.add_argument("itemid_list", nargs='?', type=str)
    args = parser.parse_args()
    main(args.itemid_list, args.csv, args.noheader, args.showurl)

