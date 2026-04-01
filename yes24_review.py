#!/usr/bin/python3

from urllib import parse
from bs4 import BeautifulSoup
import argparse
import sys

import yes24
import spider
import review_crawler
import yes24_bookinfo


def reviewlist(info, csv, order=None, showurl=None):
    return goodsReviewList(info, order, csv) + awordReviewList(info, order, csv)


def main(itemid_list, csv, noheader, order=None, showurl=None, output_json=False):
    review_crawler.mainloop(itemid_list, yes24_bookinfo.bookinfo, reviewlist, csv, noheader, order, showurl, output_json)


def goodsReviewList(info, order, csv):
    result = []

    sortorder = {
        "최근순": 1,
        "추천순": 2,
        "별점순": 3,
    }

    qrylist = [
        ("type", "ALL"),
        ("sort", sortorder[order]),
        ("PageNumber", 1)
    ]

    qrystr = parse.urlencode(qrylist)
    url = yes24.site + "/Product/communityModules/GoodsReviewList/" + info["goodsid"] + '?' + qrystr
    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')

    for review in soup.select('div.reviewInfoGrp'):
        buy = review.select_one("span.buy")
        result.append({
            "reviewdate": review.select_one("em.txt_date").text,
            "reviewerid": review.select_one("em.txt_id > a").text,
            "buy": buy.text.strip() if buy else '',
            "rating": review.select_one("span.review_rating").text,
            "content": ' '.join(review.select_one("div.review_cont").text.split())
        })
        
    return result
   

def awordReviewList(info, order, csv):
    result = []

    sortorder = {
        "최근순": 1,
        "추천순": 2,
        "별점순": 3,
    }

    qrylist = [
        ("type", "ALL"),
        ("sort", sortorder[order]),
        ("PageNumber", 1)
    ]

    qrystr = parse.urlencode(qrylist)
    url = yes24.site + "/Product/communityModules/AwordReviewList/" + info["goodsid"] + '?' + qrystr
    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')

    for review in soup.select('div.cmtInfoGrp'):
        buy = review.select_one("span.buy")
        result.append({
            "reviewdate": review.select_one("em.txt_date").text,
            "reviewerid": review.select_one("em.txt_id > a").text,
            "rating": review.select_one("span.rating").text.strip(),
            "buy": buy.text.strip() if buy else '',
            "content": review.select_one("div.cmt_cont").text.replace('\n', ' ').strip(),
        })
        
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""\
YES24 도서 리뷰 수집 스크립트.

YES24 상품 ID(숫자)를 받아 해당 도서의 리뷰를 수집한다.
상품 ID는 YES24 상품 URL의 마지막 숫자 부분이다.
  예: http://www.yes24.com/Product/Goods/97315227 → 97315227

수집 대상:
  - 상품리뷰 (긴 리뷰, goodsReview)
  - 한줄평 (짧은 한줄 리뷰, awordReview)
  두 종류를 합쳐서 출력한다.

출력 필드 (JSON/CSV):
  title       책 제목
  url         YES24 상품 페이지 URL
  author      저자/역자
  pubdate     발행일 (예: "2026-01-02")
  isbn13      ISBN13 (없으면 null)
  reviewdate  리뷰 작성일
  reviewerid  작성자 ID (마스킹됨)
  buy         "구매"이면 구매자 리뷰, 빈 문자열이면 비구매자
  rating      평점 (예: "평점10점")
  content     리뷰 본문

입력:
  상품 ID를 인자로 직접 지정하거나, 생략하면 stdin에서 줄바꿈 구분으로 읽는다.
  yes24.py --id_only의 출력을 파이프로 넘겨받을 수 있다.

제약:
  - 각 리뷰 종류별 첫 페이지만 조회한다 (각 최대 약 10건).
  - 상품 ID당 도서 정보 요청 1회 + 리뷰 요청 2회, 요청 간 1초 대기.""",
        epilog="""\
사용 예:
  echo 97315227 | %(prog)s --csv                  stdin으로 CSV 출력
  echo -e "97315227\\n90322497" | %(prog)s --csv   여러 상품
  %(prog)s --json 97315227                         JSON 출력
  %(prog)s --order 추천순 --csv 97315227           추천순 정렬

파이프라인 예 (검색 → 리뷰 수집):
  yes24.py --id_only 위키북스 | %(prog)s --csv > 리뷰.csv
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--order", default="최근순", choices=["최근순", "추천순", "별점순"],
                        help="리뷰 정렬 순서 (기본: 최근순)")
    parser.add_argument("--csv", action=argparse.BooleanOptionalAction,
                        help="CSV 형식 출력 (헤더 포함)")
    parser.add_argument("--json", dest="output_json", action=argparse.BooleanOptionalAction,
                        help="JSON 배열 출력")
    parser.add_argument("--noheader", action=argparse.BooleanOptionalAction,
                        help="CSV 헤더 행 생략 (여러 상품 결과를 이어붙일 때)")
    parser.add_argument("goodsid_list", nargs='?', type=str,
                        help="상품 ID (숫자). 생략 시 stdin에서 줄바꿈 구분으로 읽음")
    args = parser.parse_args()
    main(args.goodsid_list, args.csv, args.noheader, args.order, output_json=args.output_json)


