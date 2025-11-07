#!/usr/bin/python3

from urllib import parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import argparse
import re

import spider


site = "https://www.aladin.co.kr"


def main(publisher, page, exact_match):

    qrylist = [
        ("SearchTarget", "Book"),
        ("KeyPublisher", publisher),
        ("KeyMonthStart", "01"),
        ("KeyMonthEnd", "01"),
        ("KeyRecentPublish", "0"),
        ("OutStock", "0"),
        ("ViewType", "Detail"),
        ("SortOrder", "5"),
        ("CustReviewCount", "0"),
        ("CustReviewRank", "0"),
        ("SearchFieldEnable", "1"),
        ("KeyWord", ""),
        ("CategorySearch", ""),
        ("DetailSearch", "1"),
        ("chkKeyTitle", ""),
        ("chkKeyAuthor", ""),
        ("chkKeyPublisher", "on"),
        ("chkKeyISBN", ""),
        ("chkKeyTag", ""),
        ("chkKeyTOC", ""),
        ("chkKeySubject", ""),
        ("ViewRowCount", "50"),
        ("page", page)
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/search/wsearchresult.aspx?" + qrystr

    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')

    # 각 책 항목 처리
    for item in soup.select("div.ss_book_list > ul"):
        # exact_match인 경우 출판사 먼저 확인
        if exact_match:
            publisher_link = item.find("a", href=re.compile(r"PublisherSearch"))
            if not publisher_link:
                continue
            actual_publisher = publisher_link.text.strip()
            if actual_publisher != publisher:
                continue

        # book_id 추출 및 출력
        book_link = item.find("a", "bo3")
        if book_link:
            print(book_link.attrs["href"].split('=')[1])
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--publisher", default="위키북스", type=str)
    parser.add_argument("--page", default=1, type=int)
    parser.add_argument("--exact_match", action="store_true", help="출판사명과 완전히 일치하는 결과만 출력")
    args = parser.parse_args()
    main(args.publisher, args.page, args.exact_match)


