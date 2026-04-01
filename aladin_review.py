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


def main(itemid_list, csv, noheader, order=None, showurl=None, output_json=False):
    review_crawler.mainloop(itemid_list, bookinfo, reviewlist, csv, noheader, order, showurl, output_json)


def bookinfo(itemid, showurl):
    url = site + "/shop/wproduct.aspx?ItemId=" + itemid
    if showurl:
        print(url, file=sys.stderr)

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

    # 'conts_info_list1' 클래스를 가진 div 태그 찾기
    info_list_div = soup.find('div', class_='conts_info_list1')
    
    # 해당 div 내부의 모든 li 태그 찾기
    li_tags = info_list_div.find_all('li')
    
    # 각 li 태그의 텍스트를 검사하여 ISBN 정보 추출
    isbn_number = None
    for li in li_tags:
        if 'ISBN' in li.text:
            isbn_number = li.text.split(':')[-1].strip()  # ISBN 번호 추출
            break

    return {
        "itemid": itemid,
        "title": title,
        "url": url,
        "author": authors,
        "pubdate": pubdate,
        "isbn13": isbn_number,
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
        print(url, file=sys.stderr)

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
        print(url, file=sys.stderr)

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


def _cli():
    parser = argparse.ArgumentParser(
        description="""\
알라딘 도서 리뷰 수집 스크립트.

알라딘 상품 ID(숫자)를 받아 해당 도서의 리뷰를 수집한다.
상품 ID는 알라딘 상품 URL의 ItemId 파라미터 값이다.
  예: https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=320211724 → 320211724

수집 대상:
  - 마이리뷰 (긴 리뷰, 구매자/비구매자)
  - 100자평 (짧은 리뷰, 구매자/비구매자)
  네 종류를 합쳐서 출력한다.

출력 필드 (JSON/CSV):
  title       책 제목
  url         알라딘 상품 페이지 URL
  author      저자/역자
  pubdate     발행일 (예: "2024-01-02")
  isbn13      ISBN13 (없으면 null)
  reviewdate  리뷰 작성일
  reviewerid  작성자 ID
  buy         "구매"이면 구매자 리뷰, 빈 문자열이면 비구매자
  rating      평점 (예: "5점")
  content     리뷰 본문

입력:
  상품 ID를 인자로 직접 지정하거나, 생략하면 stdin에서 줄바꿈 구분으로 읽는다.
  aladin_book_ids.py의 출력을 파이프로 넘겨받을 수 있다.

제약:
  - 각 리뷰 종류별 첫 페이지만 조회한다 (각 최대 약 10건).
  - 요청 간 1초 대기.""",
        epilog="""\
사용 예:
  echo 320211724 | %(prog)s --csv                  stdin으로 CSV 출력
  echo -e "320211724\\n319225685" | %(prog)s --csv  여러 상품
  %(prog)s --json 320211724                         JSON 출력

파이프라인 예 (출판사 도서 목록 → 리뷰 수집):
  aladin-book-ids --publisher 위키북스 --exact_match | %(prog)s --csv > 리뷰.csv
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
                        help="상품 ID (숫자). 생략 시 stdin에서 줄바꿈 구분으로 읽음")
    args = parser.parse_args()
    main(args.itemid_list, args.csv, args.noheader, args.showurl, output_json=args.output_json)


if __name__ == '__main__':
    _cli()

