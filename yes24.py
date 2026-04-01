#!/usr/bin/python3

from urllib import parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import argparse
import json
import re
import sys


site = "http://www.yes24.com"

domainmap = {
    "전체": "ALL",
    "국내도서": "BOOK",
    "ebook": "EBOOK",
    "중고샵": "USED_GOODS",
}

basefilter = {
    "인기도순": "SINDEX_ONLY",
    "정확도순": "RELATION",
    "신상품순": "RECENT",
    "최저가순": "LOW_PRICE",
    "최고가순": "HIGH_PRICE",
    "평점순": "CONT_NT",
    "리뷰순": "REVIEW_CNT"
}

categorymap = {
    "art": "001001007",
    "biz": "001001025",
    "elementary": "001001044",
    "exam": "001001015",
    "humanity": "001001019",
    "it": "001001003",
    "kid": "001001016",
    "kids": "001001016",
    "literature": "001001046",
    "middle": "001001013",
    "sci": "001001002",
    "self": "001001026",
    "teen": "001001005",
    "test": "001001015",
    "univ": "001001014",
    "경영": "001001025",
    "경제": "001001025",
    "과학": "001001002",
    "대학교재": "001001014",
    "문학": "001001046",
    "수험서": "001001015",
    "어린이": "001001016",
    "예술": "001001007",
    "인문": "001001019",
    "자격증": "001001015",
    "자기개발": "001001026",
    "자기계발": "001001026",
    "자연과학": "001001002",
    "중고등": "001001013",
    "중고등참고서": "001001013",
    "청소년": "001001005",
    "초등": "001001044",
    "초등참고서": "001001044",
}

mkEntrNo = {
    "위키북스": "120040",
    "위키북스(eBook)": "284569"
}

def main(keyword, domain, order, category, publisher, page, showurl, csv, id_only, output_json):
    booklist = search(keyword, domain, order, category, publisher, page, showurl)
    display(booklist, order, csv, id_only, output_json)


def display(booklist, order, csv, id_only, output_json):
    if output_json:
        print(json.dumps(booklist, ensure_ascii=False, indent=2))
        return

    if csv:
        print(
            '"URL"',
            '"제목"',
            '"부제"',
            '"저자/역자"',
            '"출판사"',
            '"발행일"',
            '"판매지수"',
            sep=','
        )

    booklist = sorted(booklist, key=lambda x: int(x["saleNum"].replace(',', '')), reverse=True) if order == "판매지수순" else booklist

    for book in booklist:
        if id_only:
            print(re.search(r"(\d+)$", book["url"]).group())
        elif csv:
            quote = lambda s: '"' + s.replace('"', '\"') + '"' if csv else s
            print(
                quote(book["url"]),
                quote(book["gd_res"] + ' ' + book["title"]),
                quote(book["subtitle"]),
                quote(book["author"]),
                quote(book["publisher"]),
                quote(book["pubdate"]),
                quote(book["saleNum"]),
                sep=','
            )
        else:
            print(
                book["url"],
                book["gd_res"] + ' ' + (": ".join([book["title"], book["subtitle"]]) if book["subtitle"] else book["title"]),
                book["author"] + '|' + book["publisher"] + '|' + book["pubdate"],
                "판매지수 " + book["saleNum"],
                sep='\n',
                end='\n\n'
            )


def search(keyword, domain, order, category, publisher, page, showurl):
    result = []

    inckey = [k for k in keyword.split() if not k.startswith('-')]
    exckey = [k[1:] for k in keyword.split() if k.startswith('-')]

    qrylist = [
        ("domain", domainmap[domain.lower()]),
        ("query", ' '.join(inckey)),
        ("page", page),
    ]

    if order in ["인기도순", "정확도순", "신상품순", "최저가순", "평점순", "리뷰순"]:
        qrylist.append(("order", basefilter[order]))
    elif order == "판매지수순":
        pass  # implemented by sorting because it's not provided by Yes24

    if category and category.lower() != "all":
        if category.startswith('0'):
            qrylist.append(("dispno2", category))
        elif category.lower() in categorymap:
            qrylist.append(("dispno2", categorymap[category.lower()]))
        else:
            print(f"오류: 알 수 없는 카테고리 '{category}'", file=sys.stderr)
            print(f"사용 가능: all, {', '.join(sorted(set(categorymap.keys())))}", file=sys.stderr)
            sys.exit(1)

    if publisher:
        codes = []
        for name in publisher.split(','):
            name = name.strip()
            if name not in mkEntrNo:
                print(f"오류: 알 수 없는 출판사 '{name}'", file=sys.stderr)
                print(f"사용 가능: {', '.join(sorted(mkEntrNo.keys()))}", file=sys.stderr)
                sys.exit(1)
            codes.append(mkEntrNo[name])
        qrylist.append(("mkEntrNo", ','.join(codes)))

    qrystr = parse.urlencode(qrylist)
    url = site + "/Product/Search?" + qrystr

    if showurl:
        print("Opening", url, "...\n", file=sys.stderr)

    with urlopen(url) as f:
        html = f.read().decode('utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    yesSchList = soup.select('#yesSchList > li')

    for item in yesSchList:
        saleNum = item.select_one("span.saleNum").text.replace("판매지수", '').strip() if item.select_one("span.saleNum") else None

        title = dict()
        title["gd_res"] = item.select_one("span.gd_res").text
        title["title"] = item.select_one("div.info_row.info_name > a.gd_name").text.strip()
        title["subtitle"] = item.select_one("span.gd_nameE").text if item.select_one("span.gd_nameE") else ''
        title["url"] = site + item.select_one("div.info_row.info_name > a")['href']
        title["author"] = item.select_one("span.authPub.info_auth").text.split('\n')[1].strip()
        title["publisher"] = item.select_one("span.authPub.info_pub > a").text
        title["pubdate"] = item.select_one("span.authPub.info_date").text
        title["saleNum"] = saleNum if saleNum else ''

        skip = False
        for k in exckey:
            if any(map(lambda x: k in x, title.values())):
                skip = True

        if order == "판매지수순" and title["saleNum"] == '':
            skip = True

        if not skip:
            result.append(title)
    return result


if __name__ == '__main__':
    category_names = sorted(set(categorymap.keys()))
    publisher_names = sorted(mkEntrNo.keys())

    parser = argparse.ArgumentParser(
        description="""\
YES24 도서 검색 스크립트.

YES24 서점 웹사이트에서 키워드로 도서를 검색한다.
검색은 YES24의 상품 검색 기능을 사용하며, 제목·저자·출판사 등을 대상으로 한다.

검색 동작:
  - 키워드에 포함된 단어는 AND 조건으로 검색된다.
    예: "파이썬 위키북스" → '파이썬'과 '위키북스'가 모두 포함된 결과
  - -접두사를 붙인 단어는 결과에서 제외한다 (클라이언트 필터링).
    제외 대상은 제목, 부제, 저자, 출판사 등 모든 필드이다.
    예: "Rust -일러스트 -애니" → 'Rust' 검색 후 '일러스트', '애니' 포함 결과 제거
  - --publisher는 YES24에 등록된 출판사 코드로 서버 필터링한다.
    키워드 검색과 다르며, 등록된 출판사 이름만 사용 가능하다.

출력 필드 (JSON/CSV):
  gd_res      상품 유형 ("[도서]", "[eBook]" 등)
  title       제목
  subtitle    부제 (없으면 빈 문자열)
  url         YES24 상품 페이지 URL (상품 ID 포함)
  author      저자/역자
  publisher   출판사
  pubdate     발행일 (예: "2026년 03월")
  saleNum     판매지수 (예: "16,821", 없으면 빈 문자열)

제약:
  - 페이지당 약 20~40건. 한 번에 한 페이지만 조회한다.
  - --id_only는 URL에서 숫자 상품 ID만 추출한다. yes24_review.py에 파이프 가능.""",
        epilog=f"""\
사용 예:
  %(prog)s 파이썬                                 전체 카테고리에서 인기도순 검색
  %(prog)s "파이썬 위키북스"                       복수 키워드 AND 검색
  %(prog)s "Rust -일러스트 -애니"                  제외 키워드
  %(prog)s --order 신상품순 --category it AWS      IT 카테고리, 신상품순
  %(prog)s --id_only 위키북스                      상품 ID만 출력 (파이프라인용)
  %(prog)s --json 파이썬                           JSON 출력

파이프라인 예 (검색 → 리뷰 수집):
  %(prog)s --id_only 위키북스 | yes24_review.py --csv > 리뷰.csv

카테고리 이름 (--category):
  {', '.join(category_names)}
  'all'이면 카테고리 필터 없이 검색. 코드 직접 지정도 가능 (예: 001001003)

등록된 출판사 (--publisher):
  {', '.join(publisher_names)}
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("keyword", type=str,
                        help="검색 키워드. 공백으로 AND 검색, -접두사로 제외")
    parser.add_argument("--domain", default="국내도서",
                        choices=sorted(domainmap.keys()),
                        help="검색 도메인 (기본: 국내도서)")
    parser.add_argument("--order", default="인기도순",
                        choices=["인기도순", "정확도순", "신상품순", "최저가순", "최고가순", "평점순", "리뷰순", "판매지수순"],
                        help="정렬 순서 (기본: 인기도순). 판매지수순은 클라이언트 정렬")
    parser.add_argument("--category", default="all", type=str,
                        help="카테고리 이름 또는 코드 (기본: all)")
    parser.add_argument("--publisher", type=str,
                        help="출판사 서버 필터. 등록된 이름만 가능, 쉼표 구분")
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
    main(args.keyword, args.domain, args.order, args.category, args.publisher, args.page, args.showurl, args.csv, args.id_only, args.output_json)


