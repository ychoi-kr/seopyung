# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

한국 온라인 서점(알라딘, YES24, 교보문고) 도서 리뷰 크롤러 모음. Python CLI 스크립트들로 구성되며, 상품 ID를 stdin 또는 인자로 받아 리뷰를 텍스트/CSV로 출력한다.

## Dependencies

```
pip install beautifulsoup4 requests html2text
```

## Usage Examples

```bash
# 알라딘 리뷰 수집 (CSV)
echo "320211724" | python aladin_review.py --csv

# YES24 도서 검색 → 리뷰 수집 파이프라인
python yes24.py --order 신상품순 --id_only 위키북스 | python yes24_review.py --csv > 리뷰.csv

# 교보문고 리뷰 수집
echo "S000001234567" | python kyobobook_review.py --csv

# 출판사별 알라딘 도서 ID 목록
python aladin_book_ids.py --publisher 위키북스 --exact_match
```

## Architecture

공통 패턴: 각 서점별 `*_review.py`는 `bookinfo()` + `reviewlist()` 함수를 구현하고, `review_crawler.mainloop()`에 위임한다.

- **spider.py** — HTTP 요청 래퍼 (`readurl`). User-Agent/Referer 헤더 포함.
- **review_crawler.py** — 리뷰 수집 메인루프 및 CSV/텍스트 출력 공통 로직. `bookinfo`/`reviewlist` 콜백을 받아 동작.
- **aladin_review.py** — 알라딘 리뷰 (마이리뷰 + 100자평, 구매자/비구매자 구분)
- **yes24_review.py** — YES24 리뷰 (상품리뷰 + 한줄평). `yes24_bookinfo.py`에서 도서 정보 조회.
- **kyobobook_review.py** — 교보문고 리뷰. API(`/api/review/list`) 사용.
- **yes24.py** — YES24 도서 검색 (카테고리/정렬/출판사 필터). `--id_only`로 리뷰 스크립트에 파이프 가능.
- **aladin_book_ids.py** / **kyobobook_book_ids.py** — 출판사 키워드로 도서 ID 목록 추출
- **yes24_toc.py** — YES24 도서 목차 추출 (html2text 변환)
- **yesblog.py** — YES 블로그 본문 추출

## Notes

- 모든 리뷰 스크립트의 CSV 출력 컬럼: 책 제목, URL, 저자/역자, 발행일, 작성일, 작성자, 구매, 평점, 리뷰, ISBN13
- 서점 사이트 HTML 구조 변경 시 BeautifulSoup 셀렉터 업데이트 필요
- `review_crawler.mainloop`은 요청 간 `time.sleep(1)` 포함
- 교보문고는 `spider.py` 대신 `requests`를 직접 사용 (별도 헤더 필요)
