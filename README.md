## 주요 파일

* [aladin_review.py](#aladin_reviewpy): 알라딘 서평 조회
* [yes24.py](#yes24py) : 예스24 도서 검색
* [yes24_review.py](#yes24_reviewpy) : 예스24 서평 조회
* [yesblog.py](#yesblogpy) : YES 블로그 본문 추출

## 요구사항

```
pip install beautifulsoup4
````

## aladin_review.py

사용 예:

```
$ echo -e "320211724" | aladin_review.py --csv
"책 제목","URL","저자/역자","발행일","작성일","작성자","구매","평점","리뷰"
"실전! 컴퓨터비전을 위한 머신러닝","https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=320211724","발리아파 락슈마난,마틴 괴르너,라이언 길라드,최용","2023-07-18","2023-07-28","황승규","구매","1점","진짜 뭘 위한 책일까요 내가 이걸 왜 샀을까요? 맨 처음 실습코드 따라치다가 뭔가 생략된 부분이 많은 것 같아서 책을 확인해보니 전체 코드는 깃허브에서 확인하라네요.그것까진 참을게요 근데 깃허브에 있는 코드랑 책에 있는 코드랑 내용이 왜 다르냐고요심지어 책에서는 짧은코드 살짝 설명해놓고 깃허브에는 전체코드 분량 엄청납니다. 전체코드는 당연히 설명도 없고요.걍 최악이요. 이걸 잠깐이라도 들여다 본 내 시간이 아까워요"
```

## yes24.py

예스24에서 국내 도서 목록을 검색합니다(e북 제외).

사용법:

```
yes24.py [-h] [--order {인기도순,정확도순,신상품순,최저가순,최고가순,평점순,리뷰순}] [--category CATEGORY] keyword
```

두 개 이상의 키워드로 찾고 싶을 때는 따옴표로 감싸면 됩니다.

```
$ yes24.py "파이썬 위키북스"
Opening http://www.yes24.com/Product/Search?domain=BOOK&query=%ED%8C%8C%EC%9D%B4%EC%8D%AC+%EC%9C%84%ED%82%A4%EB%B6%81%EC%8A%A4&order=SINDEX_ONLY&dispno2=001001003 ...

파이썬 머신러닝 완벽 가이드: 다양한 캐글 예제와 함께 기초 알고리즘부터 최신 기법까지 배우는
http://www.yes24.com/Product/Goods/108824557
권철민 저 | 위키북스 | 2022년 04월
판매지수 4,401

손가락 하나 까딱하지 않는 주식 거래 시스템 구축: 파이썬을 이용한 데이터 수집과 차트 분석, 매매 자동화까지
http://www.yes24.com/Product/Goods/89999945
장용준 저 | 위키북스 | 2020년 04월
판매지수 3,900

일 잘하는 직장인을 위한 엑셀 자동화 with 파이썬: 복잡하고 지루한 반복 업무를 쉽고 빠르게 해치우는 방법
http://www.yes24.com/Product/Goods/94483920
최은석 저 | 위키북스 | 2020년 11월
판매지수 3,654

...
```

검색어에서 제외하고 싶은 키워드는 마이너스를 붙이면 됩니다.

```
$ yes24.py "Rust -일러스트 -애니 -웹툰"
Opening http://www.yes24.com/Product/Search?domain=BOOK&query=Rust&order=SINDEX_ONLY&dispno2=001001003 ...

15단계로 배우는 도커와 쿠버네티스
http://www.yes24.com/Product/Goods/93317828
타카라 마호 저/이동규 역 | 제이펍 | 2020년 10월
판매지수 3,990

쿠버네티스 모범 사례: 쿠버네티스 창시자가 알려주는 최신 쿠버네티스 개발 및 배포 기법 
http://www.yes24.com/Product/Goods/95560470
브렌던 번스, 에디 비얄바, 데이브 스트레벨, 라클런 이븐슨 저/장정호 역 | 한빛미디어 | 2020년 12월
판매지수 2,622

동시성 프로그래밍: Rust, C, 어셈블리어로 구현하며 배우는 동시성 프로그래밍 A to Z
http://www.yes24.com/Product/Goods/108570426
다카노 유키 저/김모세 역 | 한빛미디어 | 2022년 04월
판매지수 2,310
```

정렬 순서를 지정할 수 있습니다.

```
$ yes24.py --order 신상품순 AWS | head -16
Opening http://www.yes24.com/Product/Search?domain=BOOK&query=AWS&order=RECENT&dispno2=001001003 ...

Must Have 코로나보드로 배우는 실전 웹 서비스 개발: Node.js와 AWS를 활용한 설계부터 크롤링, 개발, 운영, 수익화까지
http://www.yes24.com/Product/Goods/108903274
권영재, 주은진 저 | 골든래빗 | 2022년 05월
판매지수 2,673

쉽게 배우는 AWS AI 서비스: 챗봇, 음성비서, 크롤러 프로젝트를 구현하며 만나는 서비스형 AI
http://www.yes24.com/Product/Goods/108685145
피터 엘거, 오언 셔너히 저/맹윤호, 임지순 역/곽근봉 감수 | 한빛미디어 | 2022년 04월
판매지수 576

MLFlow를 활용한 MLOps: AWS, Azure, GCP에서 MLOps 시작하기
http://www.yes24.com/Product/Goods/106709982
스리다르 알라, 수만 칼리안 아다리 저/정이현 역 | 에이콘출판사 | 2022년 02월
판매지수 1,938
```

검색 카테고리를 지정할 수 있습니다.

```
$ yes24.py --category 대학교재 통계 | head -16
Opening http://www.yes24.com/Product/Search?domain=BOOK&query=%ED%86%B5%EA%B3%84&order=SINDEX_ONLY&dispno2=001001014 ...

제대로 알고 쓰는 논문 통계분석: SPSS & AMOS
http://www.yes24.com/Product/Goods/70748357
노경섭 저 | 한빛아카데미 | 2019년 02월
판매지수 12,564

SPSS 결과표 작성과 해석 방법: 한번에 통과하는 논문
http://www.yes24.com/Product/Goods/59577796
히든그레이스 논문통계팀, 김성은, 정규형, 우종훈, 허영회 저 | 한빛아카데미 | 2018년 03월
판매지수 9,768

정신질환의 진단 및 통계편람: DSM-5
http://www.yes24.com/Product/Goods/17843603
APA 저/권준수, 김재진, 남궁기, 박원명 역 | 학지사 | 2015년 04월
판매지수 8,274
```

카테고리는 URL의 `dispno2` 값을 넣어도 되고, 한글로 지정할 수도 있습니다. 사용 가능한 카테고리 이름을 확인하려면 다음과 같이 하면 됩니다(제가 임의로 정한 것이므로 예스24의 카테고리명과는 차이가 있습니다).

```
$ python -c "import yes24; print(yes24.categorymap)"
{'art': '001001007', 'biz': '001001025', 'elementary': '001001044', 'exam': '001001015', 'humanity': '001001019', 'it': '001001003', 'kid': '001001016', 'kids': '001001016', 'literature': '001001046', 'middle': '001001013', 'sci': '001001002', 'self': '001001026', 'teen': '001001005', 'test': '001001015', 'univ': '001001014', '경영': '001001025', '경제': '001001025', '과학': '001001002', '대학교재': '001001014', '문학': '001001046', '수험서': '001001015', '어린이': '001001016', '예술': '001001007', '인문': '001001019', '자격증': '001001015', '자기개발': '001001026', '자기계발': '001001026', '자연과학': '001001002', '중고등': '001001013', '중고등참고서': '001001013', '청소년': '001001005', '초등': '001001044', '초등참고서': '001001044'}
``` 

기능 제한:

- 페이징 기능이 없어 상품 목록의 첫 번째 페이지만 조회합니다.

## yes24_review.py

예스24의 상품 번호를 입력해 리뷰를 조회할 수 있습니다.

```
$ echo -e "97315227\n90322497" | yes24_review.py
2021-03-22 밍*이 
내용 평점5점  편집/디자인 평점5점
어렸을때 준비했던 정보보안전문가가 다시 기억나는 책요즘 들어, 웹 개발, 반응형을 포함한 모바일 웹앱까지 개발하다 보니 웹 보안에 대해 더 신경을 많이 쓰게 되었는데 마침 좋은 기회가 있어                    더보기찰, 공격, 방어 세 단계로 배우는 웹 애플리케이션 보안의 모든 것'이 문장만 들어도 나로선, 어렸을 때부터 정보보안에 관심이 많았던...

2021-03-22 z****n 
내용 평점5점  편집/디자인 평점5점
2021년 올해의 책리뷰 / 웹 애플리케이션 보안 / 한빛미디어드디어 출시된 웹 애플리케이션 보안!!이 책은 정말 해킹과 보안에 관심있는 사람들에게는 필독인 책이다. 해커로부터 웹 애플리케이션                    더보기웹 애플리케이션을 조사하고 침입하는 방법을 다루는 책이다. 취약점을 식별하며 애플리케이션 데이터를 공격에 악용하는 페이로드를...

...

2020-10-13 출*****4 구매
평점5점
칼리,네트워크 설정 및 서버 구축에 있어서 어느정도에 지식이 있는 사람이 읽어야 한다.
```

CSV 형식으로 출력할 수 있습니다.

```
$ echo -e "97315227\n90322497" | yes24_review.py --csv
"책 제목","URL","저자/역자","발행일","작성일","작성자","구매","평점","리뷰"
"웹 애플리케이션 보안","http://www.yes24.com/Product/Goods/97315227","앤드루 호프먼 저/최용 역","2021년 02월 19일","2021-03-22","밍*이","","내용 평점5점  편집/디자인 평점5점","어렸을때 준비했던 정보보안전문가가 다시 기억나는 책요즘 들어, 웹 개발, 반응형을 포함한 모바일 웹앱까지 개발하다 보니 웹 보안에 대해 더 신경을 많이 쓰게 되었는데 마침 좋은 기회가 있어서 이                     더보기" , 방어 세 단계로 배우는 웹 애플리케이션 보안의 모든 것'이 문장만 들어도 나로선, 어렸을 때부터 정보보안에 관심이 많았던...
"웹 애플리케이션 보안","http://www.yes24.com/Product/Goods/97315227","앤드루 호프먼 저/최용 역","2021년 02월 19일","2021-03-22","z****n","","내용 평점5점  편집/디자인 평점5점","2021년 올해의 책리뷰 / 웹 애플리케이션 보안 / 한빛미디어드디어 출시된 웹 애플리케이션 보안!!이 책은 정말 해킹과 보안에 관심있는 사람들에게는 필독인 책이다. 해커로부터 웹 애플리케이션을 보호                    더보기" 케이션을 조사하고 침입하는 방법을 다루는 책이다. 취약점을 식별하며 애플리케이션 데이터를 공격에 악용하는 페이로드를...

...

"침투 본능, 해커의 기술","http://www.yes24.com/Product/Goods/90322497","아드리안 프루티아누 저/최용 역","2020년 05월 28일","2020-10-13","출*****4","구매","평점5점","칼리,네트워크 설정 및 서버 구축에 있어서 어느정도에 지식이 있는 사람이 읽어야 한다."
```

`yes24.py`로 조회한 상품 ID 목록을 파이프로 넘겨받아 리뷰를 수집하고 CSV 파일로 저장할 수 있습니다.

```
$ yes24.py --order 신상품순 --id_only 위키북스 | yes24_review.py --csv > 리뷰.csv
```

기능 제한:

- 페이징 기능이 없어 최근 리뷰만 조회됩니다.

팁:

- Excel에서 글자가 깨져 보이는 경우, 리본 메뉴에서 ‘데이터’ - ‘텍스트/CSV에서’를 선택해 CSV 파일을 열어 보세요.


## yesblog.py

사용 예:

```
$ yesblog.py 15801308

파이썬은 데이터과학자들에게 필수적인 프로그래밍 언어이다. C, 자바 같은 언어에 비해 배우기가 쉬운 언어로 알려져 있지만 막상 혼자 배워보려 하면 생각만큼 쉽지 않다. 인터넷에 관련 자료들이 많이 있기는 하지만 체계적으로 정리되어 있지 않은 경우가 많다. 하지만 이 책은 데이터 과학과 관련된 파이썬 문법 및 기능들을 잘 정리했기 때문에 데이터 과학 입문서로서 손색이 없다. 그리고 적절한 실습 예제들이 많이 포함되어 있어 이해하기가 용이했다.
```