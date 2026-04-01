import json
import sys
import time


def print_csv_header():
    print(
        '"책 제목"',
        '"URL"',
        '"저자/역자"',
        '"발행일"',
        '"작성일"',
        '"작성자"',
        '"구매"',
        '"평점"',
        '"리뷰"',
        '"ISBN13"',
        sep=','
    )


def display(info, reviewlist, csv):
    for review in reviewlist:
        if csv:
            quote = lambda s: '"' + s.replace('"', '\'') + '"' if csv else s
            print(
                quote(info["title"]),
                quote(info["url"]),
                quote(info["author"]),
                quote(info["pubdate"]),
                quote(review["reviewdate"]),
                quote(review["reviewerid"]),
                quote(review["buy"]),
                quote(review["rating"]),
                quote(review["content"]),
                quote(info["isbn13"]),
                sep=','
            )
            sys.stdout.flush()
        else:
            print(
                review["reviewdate"] + ' ' + review["reviewerid"] + ' ' + review["buy"],
                review["rating"],
                review["content"],
                sep='\n',
                end='\n\n'
            )


def mainloop(itemid_list, bookinfo, reviewlist, csv, noheader=False, order=None, showurl=None, output_json=False):
    if not itemid_list:
        itemid_list = sys.stdin
    elif isinstance(itemid_list, str):
        itemid_list = [itemid_list]

    if output_json:
        results = []
        for itemid in itemid_list:
            info = bookinfo(itemid.strip(), showurl)
            time.sleep(1)
            reviews = reviewlist(info, csv, order, showurl)
            for review in reviews:
                results.append({
                    "title": info["title"],
                    "url": info["url"],
                    "author": info["author"],
                    "pubdate": info["pubdate"],
                    "isbn13": info.get("isbn13"),
                    "reviewdate": review["reviewdate"],
                    "reviewerid": review["reviewerid"],
                    "buy": review["buy"],
                    "rating": review["rating"],
                    "content": review["content"],
                })
            time.sleep(1)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if csv and not noheader:
        print_csv_header()

    for itemid in itemid_list:
        info = bookinfo(itemid.strip(), showurl)
        time.sleep(1)
        display(
            info,
            reviewlist(info, csv, order, showurl),
            csv
        )
        time.sleep(1)

