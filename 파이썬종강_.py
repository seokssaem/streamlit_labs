import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

# 엑셀 워크북 만들기
wb = Workbook()
ws = wb.active
ws.title = '네이버 시가총액 상위'

# 제목 행 추가
ws.append(['N', '종목명', '현재가', '시가총액'])

# 네이버 시가총액 페이지 가져오기
url = 'https://finance.naver.com/sise/sise_market_sum.naver?sosok=0'
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

# 종목 정보 테이블 찾기
table = soup.find('table', {'class': 'type_2'})
if table:
    # 테이블 내의 모든 행 가져오기 (제목 행 제외)
    trs = table.find_all('tr')[2:]  # 처음 두 개 행은 필요 없는 정보

    for tr in trs:
        # 각 행에서 필요한 컬럼 데이터 추출
        tds = tr.find_all('td')
        if len(tds) >= 7:  # 필요한 데이터가 있는 최소한의 컬럼 수 확인
            n_element = tds[0].find('img')
            n = n_element['alt'] if n_element else tds[0].text.strip() # <img alt="N"> 또는 숫자 추출
            종목명 = tds[1].find('a').text.strip()
            현재가_element = tds[2].text.strip().replace(',', '')
            현재가 = int(현재가_element) if 현재가_element else ''
            시가총액_element = tds[6].text.strip().replace(',', '').replace('조', '')
            시가총액 = float(시가총액_element) if 시가총액_element else ''

            # 엑셀에 데이터 추가
            ws.append([n, 종목명, 현재가, 시가총액])

    # 열 너비 조정
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 20

    # 6. 엑셀 저장
    wb.save('네이버_시가총액상위_코스닥.xlsx')
    print('네이버 시가총액 상위 정보 엑셀 파일에 저장 완료! ^^')
else:
    print('시가총액 정보를 찾을 수 없습니다.')