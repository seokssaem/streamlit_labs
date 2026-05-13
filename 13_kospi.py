# 0. 라이브러리 불러오기
import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import unicodedata
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title='주식 차트 대시보드',
    page_icon='💰',
    layout='wide'
)
st.title('💰 KOSPI 주식 차트 대시보드')

# 2. 한글 종목명 정규화 함수 정의
def normalize_str(s):
    return unicodedata.normalize('NFKC', s).strip()

# 3. KOSPI 전체 종목 불러오기(로드)
market = 'KOSPI'
df_market = fdr.StockListing(market)

# 실제 적용: df_market 종목명 전체 정규화
df_market['Name'] = df_market['Name'].apply(normalize_str)

# multiselect 위젯에 사용할 종목명 리스트 추출
stocks = df_market['Name'].tolist()

# 4. 시가총액 TOP 10 수평막대그래프
top10 = df_market.nlargest(10, 'Marcap').iloc[::-1]  # 반전

fig_top10 = go.Figure(go.Bar(
    x=top10['Marcap'] / 1e12,
    y=top10['Name'],
    orientation='h',  # 수평 막대그래프(가로)
    text=top10['Marcap'] / 1e12,
    texttemplate='%{text:.1f}조',  # 소수 첫째자리까지, + '조' 단위
    marker_color='steelblue'  # 막대 색상
))

fig_top10.update_layout(
    title=f'{market} 시가총액 TOP 10',
    xaxis_title='시가총액 (조)',
    yaxis_title='종목명',
    bargap=0.15,   # 막대 사이 간격 (0~1)
    height=450
)

st.plotly_chart(fig_top10, width='stretch')

# 5. 사이드바 : 종목 선택 (multiselect)
selected_stocks = st.sidebar.multiselect(
    '종목을 선택하세요 (최대 10개)',
    stocks,
    max_selections=10
)

# 종목명을 정규화 함수 적용
# 리스트 컴프리헨션(리스트 내포)
# --> [최종결과 for 변수명 in 리스트명]
selected_stocks = [normalize_str(s) for s in selected_stocks]

# 6. 선택된 종목명 -> 종목코드로 변환
codes = [] # 종목코드가 저장될 리스트
for name in selected_stocks:
    matched = df_market.loc[
        df_market['Name'] == name, # 행
        'Code' # 열
    ].values
    if len(matched) > 0:
        codes.append(matched[0])

# 선택된 종목이 없거나, 코드 변환에 실패한 경우
# 경고 후 실행 중단
if not codes:
    st.warning('종목 코드를 찾을 수 없습니다. 종목을 다시 선택해주세요.')
    st.stop()

# 7. 사이드바 : 날짜 범위 선택
start_date = st.sidebar.date_input('시작 날짜', datetime.date(2025, 1, 1))
end_date = st.sidebar.date_input('종료 날짜', datetime.datetime.now().date())

# 8. 주식 데이터 불러오는(로드하는) 함수 정의
def get_stock_data(code, start, end):
    """
    함수설명 : FinanceDataReader로 개별 종목의 주가 데이터 조회

    매개변수(Parameters) :
    code : 종목 코드 문자열
    start : 조회 시작일 문자열
    end : 조회 종료일 문자열

    반환값(Returns) :
    DataFrame 
    조회 실패 또는 데이터가 없을 시 None반환
    """
    try:
        df = fdr.DataReader(code, start, end)
        if df.empty:
            return None
        return df
    except Exception as e: # e->예외메시지
        st.error(f'{code} 데이터 로드 실패 : {e}')
        return None

# 9. 현재가 / 전일 대비 변동폭 카드 표시
for i, code in enumerate(codes):
    df = get_stock_data(
        code, 
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    if df is not None and len(df) >= 2:
        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        delta = current - prev # 전일대비 변동폭

        st.metric(
            label=selected_stocks[i],
            value=f'{current:,}원', # 천단위 구분기호 넣었다(,)
            delta=f'{delta:,}원'
        )
    else:
        st.warning(f'{selected_stocks[i]} 데이터가 충분하지 않습니다!')

# 10. 탭 기능 : 라인 차트 / 캔들스틱 차트
tab1, tab2 = st.tabs(['라인 차트', '캔들스틱 차트'])  

# 라인 차트
with tab1:
    if len(codes) == 1: # 종목을 하나만 선택했다면
        df = get_stock_data(
            codes[0],
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        if df is not None:
            # st.line_chart 위젯 : 스트림릿 기본 내장 라인 차트
            st.line_chart(df['Close'])
        else:
            st.warning('데이터를 불러올 수 없습니다.')
    else: # 종목을 여러개 선택했다면 
        dfs = []  # 병합할 데이터
        for code in codes:
            df = get_stock_data(
                code,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if df is not None: # 결과가 있다면
                df_temp = df[['Close']].rename(columns={'Close':code})
                dfs.append(df_temp)

        if dfs: # 병합할 데이터가 있다면
            merged_df = pd.concat(dfs, axis=1) # 수평병합
            merged_df.columns = selected_stocks # 열 이름을 종목명(한글)로
            st.line_chart(merged_df) # 합치고 난 다음 차트 생성
        else:
            st.warning('선택한 종목의 데이터를 불러올 수 없습니다.')

# 캔들스틱 차트
with tab2:
    for i, code in enumerate(codes):
        df = get_stock_data(
            code, 
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        if df is not None:  # df가 있다면
            # 캔들 차트
            fig_candle = go.Figure(data=[go.Candlestick(
                x=df.index,  # 날짜
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']
            )])

            # 캔들 차트 - 디자인
            fig_candle.update_layout(
                title=f'{selected_stocks[i]} 캔들스틱 차트(최근3개월)',
                xaxis_title='날짜',
                yaxis_title='가격 (원)',
                xaxis_rangeslider_visible=False, # 하단 범위 슬라이더 숨김,
                height=500
            )
            st.plotly_chart(fig_candle, width='stretch')
        else:
            st.warning(f'{selected_stocks[i]} 캔들스틱 차트를 불러올 수 없습니다.')




