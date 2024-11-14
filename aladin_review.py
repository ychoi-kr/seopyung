#!/usr/bin/python3

from urllib import parse
from bs4 import BeautifulSoup
import argparse
import sys
import re

import spider
import review_crawler


site = "https://www.aladin.co.kr"


def reviewlist(info, csv, order=None, showurl=None):
    return commentReviewList(info, 1, csv, showurl) + commentReviewList(info, 0, csv, showurl) + myReviewList(info, 2, csv, showurl) + myReviewList(info, 0, csv, showurl)


def main(itemid_list, csv, noheader, order=None, showurl=None):
    review_crawler.mainloop(itemid_list, bookinfo, reviewlist, csv, noheader, order, showurl)


def bookinfo(itemid, showurl):
    url = site + "/shop/wproduct.aspx?ItemId=" + itemid
    if showurl:
        print(url)

    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.select_one("span.Ere_bo_title").text
    ebook = False
    if ebook:
        title = '[ebook] ' + title

    li = soup.select_one("li.Ere_sub2_title")
    ap = li.select("a.Ere_sub2_title")
    authors = ','.join([a.text for a in ap[:-1]])
    publisher = ap[-1].text
    pubdate = re.search(r"\d{4}-\d{2}-\d{2}", li.text).group()

    return {
        "itemid": itemid,
        "title": title,
        "url": url,
        "author": authors,
        "pubdate": pubdate
    }


def myReviewList(info, orderer, csv, showurl):
    '''마이리뷰'''
    result = []

    qrylist = [
        #("ProductItemId", info["itemid"]),
        ("itemId", info["itemid"]),
        #("pageCount", "5"),
        ("communitytype", "MyReview"),
        #("nemoType", "-1"),
        #("page", "1"),
        #("startNumber", "1"),
        #("endNumber", "10"),
        #("sort", "1"),
        ("IsOrderer", str(orderer)),  # 2: 구매자, 0: 비구매자
        #("BranchType", "1"),
        #("IsAjax", "true"),
        #("pageType", "0")
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/ucl/shop/product/ajax/GetCommunityListAjax.aspx?" + qrystr
    if showurl:
        print(url)

    html = spider.readurl(url)

    soup = BeautifulSoup(html, 'html.parser')

    for hundred in soup.select('div.hundred_list'):
        rating = str(str(hundred.select_one("div.HL_star")).count("icon_star_on")) + "점"
        HL_write = hundred.select_one("div.HL_write")
        buy = "구매" if HL_write.select_one("img") else ''
        li = hundred.select("div.blog_list3")[1].select("li")
        paperShort = li[0].select_one("div").text.strip()
        left = li[1].select_one("div.left")
        
        result.append({
            "reviewerid": left.select_one("a.Ere_sub_gray8").text,
            "reviewdate": left.select_one("span.Ere_sub_gray8").text,
            "content": HL_write.text.strip() + ' ' + paperShort,
            "buy": buy,
            "rating": rating
        })
        
    return result


def commentReviewList(info, orderer, csv, showurl):
    '''100자평'''
    result = []

    qrylist = [
        #("ProductItemId", info["itemid"]),
        ("itemId", info["itemid"]),
        #("pageCount", "5"),
        ("communitytype", "CommentReview"),
        #("nemoType", "-1"),
        #("page", "1"),
        #("startNumber", "1"),
        #("endNumber", "10"),
        #("sort", "1"),
        ("IsOrderer", str(orderer)),  # 1: 구매자, 0: 비구매자
        #("BranchType", "1"),
        #("IsAjax", "true"),
        #("pageType", "0")
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/ucl/shop/product/ajax/GetCommunityListAjax.aspx?" + qrystr
    if showurl:
        print(url)

    html = spider.readurl(url)

    soup = BeautifulSoup(html, 'html.parser')

    for hundred in soup.select('div.hundred_list'):
        rating = str(str(hundred.select_one("div.HL_star")).count("icon_star_on")) + "점"
        HL_write = hundred.select_one("div.HL_write")
        buy = "구매" if HL_write.select_one("img") else ''
        li = hundred.select("li")
        content = li[0].select_one("div").text.strip()
        left = li[1].select_one("div.left")
        
        result.append({
            "reviewerid": left.select_one("a.Ere_sub_gray8").text,
            "reviewdate": left.select_one("span.Ere_sub_gray8").text,
            "content": content,
            "buy": buy,
            "rating": rating
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

