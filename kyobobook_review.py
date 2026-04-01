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


def main(itemid_list, csv, noheader, order=None, showurl=None, output_json=False):
    review_crawler.mainloop(itemid_list, bookinfo, reviewlist, csv, noheader, order, showurl, output_json)


def bookinfo(itemid, showurl):
    if itemid.startswith('E'):
        url = "https://ebook-product.kyobobook.co.kr/dig/epd/ebook//" + itemid
    else:
        url = "https://product.kyobobook.co.kr/detail/" + itemid
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    if showurl:
        print(url, file=sys.stderr)
    
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

    # ISBN 번호를 포함하는 td 태그 찾기
    isbn_tag = soup.find('th', string="ISBN").find_next_sibling('td')
    
    # ISBN 번호 추출
    isbn_number = isbn_tag.text.strip()

    return {
        "itemid": itemid,
        "title": title,
        "url": url,
        "author": authors,
        "pubdate": pubdate,
        "isbn13": isbn_number,
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
        print(url, file=sys.stderr)

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


def _cli():
    parser = argparse.ArgumentParser(
        description="""\
교보문고 도서 리뷰 수집 스크립트.

교보문고 상품 ID를 받아 해당 도서의 리뷰를 수집한다.
상품 ID는 교보문고 상품 URL의 마지막 부분이다.
  예: https://product.kyobobook.co.kr/detail/S000218736039 → S000218736039

출력 필드 (JSON/CSV):
  title       책 제목
  url         교보문고 상품 페이지 URL
  author      저자/역자
  pubdate     발행일 (예: "2024-01-02")
  isbn13      ISBN13
  reviewdate  리뷰 작성일
  reviewerid  작성자 ID (마스킹됨)
  buy         "구매자"이면 구매자 리뷰, 빈 문자열이면 비구매자
  rating      평점 (숫자)
  content     리뷰 본문

입력:
  상품 ID를 인자로 직접 지정하거나, 생략하면 stdin에서 줄바꿈 구분으로 읽는다.
  kyobobook_book_ids.py의 출력을 파이프로 넘겨받을 수 있다.

제약:
  - 첫 페이지(10건)만 조회한다.
  - 교보문고 리뷰 API(/api/review/list)를 사용한다.
  - 요청 간 1초 대기.""",
        epilog="""\
사용 예:
  echo S000218736039 | %(prog)s --csv                  stdin으로 CSV 출력
  %(prog)s --json S000218736039                         JSON 출력

파이프라인 예 (출판사 도서 목록 → 리뷰 수집):
  kyobobook-book-ids --publisher 위키북스 | %(prog)s --csv > 리뷰.csv
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--csv", action=argparse.BooleanOptionalAction,
                        help="CSV 형식 출력 (헤더 포함)")
    parser.add_argument("--json", dest="output_json", action=argparse.BooleanOptionalAction,
                        help="JSON 배열 출력")
    parser.add_argument("--noheader", action=argparse.BooleanOptionalAction,
                        help="CSV 헤더 행 생략 (여러 상품 결과를 이어붙일 때)")
    parser.add_argument("--showurl", action=argparse.BooleanOptionalAction,
                        help="요청 URL을 stderr에 출력 (디버깅용)")
    parser.add_argument("itemid_list", nargs='?', type=str,
                        help="상품 ID. 생략 시 stdin에서 줄바꿈 구분으로 읽음")
    args = parser.parse_args()
    main(args.itemid_list, args.csv, args.noheader, args.showurl, output_json=args.output_json)


if __name__ == '__main__':
    _cli()

