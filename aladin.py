#!/usr/bin/python3

from urllib import parse
from bs4 import BeautifulSoup
import argparse
import json
import re
import sys

import spider


site = "https://www.aladin.co.kr"

sortmap = {
    "관련도순": "2",
    "판매량순": "1",
    "신상품순": "7",
    "최저가순": "3",
    "최고가순": "4",
    "평점순": "6",
    "리뷰순": "5",
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
        ("SearchTarget", "Book"),
        ("KeyWord", keyword),
        ("ViewType", "Detail"),
        ("SortOrder", sortmap.get(order, "2")),
        ("ViewRowCount", "25"),
        ("page", page),
    ]

    qrystr = parse.urlencode(qrylist)
    url = site + "/search/wsearchresult.aspx?" + qrystr

    if showurl:
        print("Opening", url, "...\n", file=sys.stderr)

    html = spider.readurl(url)
    soup = BeautifulSoup(html, 'html.parser')

    for item in soup.select("div.ss_book_list > ul"):
        book_link = item.find("a", "bo3")
        if not book_link:
            continue

        href = book_link.attrs.get("href", "")
        m = re.search(r"ItemId=(\d+)", href)
        if not m:
            continue
        item_id = m.group(1)

        title = book_link.text.strip()

        publisher_link = item.find("a", href=re.compile(r"PublisherSearch"))
        publisher = publisher_link.text.strip() if publisher_link else ''

        # 저자: AuthorSearch 링크들
        author_links = item.find_all("a", href=re.compile(r"AuthorSearch"))
        author = ','.join(a.text.strip() for a in author_links) if author_links else ''

        # 발행일: "YYYY년 M월" 패턴
        pubdate_match = re.search(r'(\d{4}년\s*\d{1,2}월)', item.get_text())
        pubdate = pubdate_match.group(1) if pubdate_match else ''

        result.append({
            "itemid": item_id,
            "url": site + "/shop/wproduct.aspx?ItemId=" + item_id,
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
알라딘 도서 검색 스크립트.

알라딘 서점 웹사이트에서 키워드로 도서를 검색한다.

출력 필드 (JSON/CSV):
  itemid      알라딘 상품 ID
  url         알라딘 상품 페이지 URL
  title       제목
  author      저자/역자
  publisher   출판사
  pubdate     발행일

제약:
  - 페이지당 최대 25건. 한 번에 한 페이지만 조회한다.""",
        epilog=f"""\
사용 예:
  %(prog)s 파이썬                                 기본 검색 (관련도순)
  %(prog)s --order 신상품순 파이썬                 정렬 변경
  %(prog)s --id_only 파이썬                        상품 ID만 출력
  %(prog)s --json 파이썬                           JSON 출력

파이프라인 예 (검색 → 리뷰 수집):
  %(prog)s --id_only 파이썬 | python aladin_review.py --csv > 리뷰.csv

정렬 순서 (--order):
  {', '.join(sort_names)}
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("keyword", type=str,
                        help="검색 키워드")
    parser.add_argument("--order", default="관련도순",
                        choices=sort_names,
                        help="정렬 순서 (기본: 관련도순)")
    parser.add_argument("--page", default=1, type=int,
                        help="결과 페이지 번호 (기본: 1)")
    parser.add_argument("--showurl", action=argparse.BooleanOptionalAction,
                        help="검색 URL을 stderr에 표시")
    parser.add_argument("--csv", action=argparse.BooleanOptionalAction,
                        help="CSV 형식 출력 (헤더 포함)")
    parser.add_argument("--json", dest="output_json", action=argparse.BooleanOptionalAction,
                        help="JSON 배열 출력")
    parser.add_argument("--id_only", action=argparse.BooleanOptionalAction,
                        help="상품 ID(숫자)만 출력. 줄바꿈 구분")
    args = parser.parse_args()
    main(args.keyword, args.order, args.page, args.showurl, args.csv, args.id_only, args.output_json)
