#!/usr/bin/python3

from urllib import parse
from bs4 import BeautifulSoup
import argparse
import json
import re
import sys

import spider


site = "https://search.kyobobook.co.kr"

sortmap = {
    "정확도순": "accuracy",
    "신상품순": "date",
    "판매량순": "sale",
    "평점순": "rating",
    "리뷰순": "review",
    "최저가순": "low_price",
    "최고가순": "high_price",
}


def main(keyword, order, page, showurl, csv, id_only, output_json):
    booklist = search(keyword, order, page, showurl)
    display(booklist, csv, id_only, output_json)


def display(booklist, csv, id_only, output_json):
    if output_json:
        print(json.dumps(booklist, ensure_ascii=False, indent=2))
        return

    if csv:
        print(
            '"URL"',
            '"제목"',
            '"저자/역자"',
            '"출판사"',
            '"발행일"',
            sep=','
        )

    for book in booklist:
        if id_only:
            print(book["itemid"])
        elif csv:
            quote = lambda s: '"' + s.replace('"', '\'') + '"'
            print(
                quote(book["url"]),
                quote(book["title"]),
                quote(book["author"]),
                quote(book["publisher"]),
                quote(book["pubdate"]),
                sep=','
            )
        else:
            print(
                book["url"],
                book["title"],
                book["author"] + '|' + book["publisher"] + '|' + book["pubdate"],
                sep='\n',
                end='\n\n'
            )


def search(keyword, order, page, showurl):
    result = []

    qrylist = [
        ("keyword", keyword),
        ("target", "total"),
        ("gbCode", "TOT"),
        ("ra", sortmap.get(order, "accuracy")),
        ("len", "20"),
        ("page", page),
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/search?" + qrystr

    if showurl:
        print("Opening", url, "...\n", file=sys.stderr)

    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')

    prod_list = soup.select_one('ul.prod_list')
    if not prod_list:
        return result

    for item in prod_list.find_all("li", recursive=False):
        prod_link = item.select_one("a.prod_info")
        if not prod_link:
            continue

        href = prod_link["href"]
        item_id = href.split('/')[-1]
        if item_id.startswith('E'):
            continue

        title_el = item.select_one(f"span#cmdtName_{item_id}")
        title = title_el.text.strip() if title_el else ''

        author_el = item.select_one("a.author")
        author = author_el.text.strip() if author_el else ''

        publish_el = item.select_one("div.prod_publish")
        if publish_el:
            pub_link = publish_el.find("a")
            publisher = pub_link.text.strip() if pub_link else ''
        else:
            publisher = ''

        date_el = item.select_one("span.date")
        pubdate = date_el.text.strip() if date_el else ''

        product_url = "https://product.kyobobook.co.kr/detail/" + item_id

        result.append({
            "itemid": item_id,
            "url": product_url,
            "title": title,
            "author": author,
            "publisher": publisher,
            "pubdate": pubdate,
        })

    return result


if __name__ == '__main__':
    sort_names = sorted(sortmap.keys())

    parser = argparse.ArgumentParser(
        description="""\
교보문고 도서 검색 스크립트.

교보문고 웹사이트에서 키워드로 도서를 검색한다.

출력 필드 (JSON/CSV):
  itemid      교보문고 상품 ID
  url         교보문고 상품 페이지 URL
  title       제목
  author      저자/역자
  publisher   출판사
  pubdate     발행일

제약:
  - 페이지당 최대 20건. 한 번에 한 페이지만 조회한다.
  - ebook(E로 시작하는 ID)은 제외한다.""",
        epilog=f"""\
사용 예:
  %(prog)s 파이썬                                 기본 검색 (정확도순)
  %(prog)s --order 신상품순 파이썬                 정렬 변경
  %(prog)s --id_only 파이썬                        상품 ID만 출력
  %(prog)s --json 파이썬                           JSON 출력

파이프라인 예 (검색 → 리뷰 수집):
  %(prog)s --id_only 파이썬 | python kyobobook_review.py --csv > 리뷰.csv

정렬 순서 (--order):
  {', '.join(sort_names)}
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("keyword", type=str,
                        help="검색 키워드")
    parser.add_argument("--order", default="정확도순",
                        choices=sort_names,
                        help="정렬 순서 (기본: 정확도순)")
    parser.add_argument("--page", default=1, type=int,
                        help="결과 페이지 번호 (기본: 1)")
    parser.add_argument("--showurl", action=argparse.BooleanOptionalAction,
                        help="검색 URL을 stderr에 표시")
    parser.add_argument("--csv", action=argparse.BooleanOptionalAction,
                        help="CSV 형식 출력 (헤더 포함)")
    parser.add_argument("--json", dest="output_json", action=argparse.BooleanOptionalAction,
                        help="JSON 배열 출력")
    parser.add_argument("--id_only", action=argparse.BooleanOptionalAction,
                        help="상품 ID만 출력. 줄바꿈 구분")
    args = parser.parse_args()
    main(args.keyword, args.order, args.page, args.showurl, args.csv, args.id_only, args.output_json)
