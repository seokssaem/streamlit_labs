# 0. 라이브러리 불러오기
import streamlit as st
import pandas as pd
import plotly.express as px 

# 1. 페이지 기본 설정 -------------------------------
st.set_page_config(
    page_title='코로나19 한국 대시보드',
    page_icon='🦠',
    layout='wide'  # 전체 화면 너비 사용
)
st.title('KR 코로나19 한국 감염자 대시보드')

# 2. 파일 업로더 -------------------------------------------
#       파일이 업로드 되지 않았다면 None반환
uploaded_confirmed = st.file_uploader('확진자 csv파일 업로드', type=['csv'])
uploaded_deaths = st.file_uploader('사망자 csv파일 업로드', type=['csv'])
uploaded_recovered = st.file_uploader('회복자 csv파일 업로드', type=['csv'])

# 3. 세 파일이 모두 업로드되었을 때만 분석 실행 ---------------------------
#       업로드 전 : 파일 객체가 None -> False -> 분석 실행 안함 -> 다시 업로드 유도
#       업로드 후 : 파일 객체가 있다 -> True -> 분석 실행 가능
if uploaded_confirmed and uploaded_deaths and uploaded_recovered:

    # 4. 데이터프레임으로 읽기 --------------------------------------------
    df_confirmed = pd.read_csv(uploaded_confirmed)
    df_deaths = pd.read_csv(uploaded_deaths)
    df_recovered = pd.read_csv(uploaded_recovered)

    # 5. 함수 정의 : 대한민국 데이터만 추출 --------------------------------
    def get_korea_data(df, value_name):
        """
        데이터프레임에서 대한민국 행만 추출 
        날짜-값 형태

        매개변수(parameters)
        df --> 전세계 원본 데이터프레임
        value_name --> 결과 열 이름 문자열 (ex. 'confirmed', 'deaths'..)
        """
        # "대한민국" 필터링
        korea_df = df[df['Country/Region'] == "Korea, South"]

        # 불필요한 컬럼 제거
        korea_df = korea_df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])

        # 날짜별 합산
        korea_series = korea_df.sum().reset_index()

        # 열 이름 지정
        korea_series.columns = ['date', value_name]

        # 날짜 문자열 --> datetime 형 변환
        korea_series['date'] = pd.to_datetime(korea_series['date'], format='%m/%d/%y')

        return korea_series

    # 6. 세 개의 데이터프레임을 각각 대한민국 데이터로 변환
    df_confirmed = get_korea_data(df_confirmed, 'confirmed') # 확진자
    df_deaths = get_korea_data(df_deaths, 'deaths') # 사망자
    df_recovered = get_korea_data(df_recovered, 'recovered') # 회복자

    # 7. 세 개의 데이터프레임을 하나로 병합 (merge)
    #   'date' 열을 기준으로 병합 --> on='date'
    df_merged = df_confirmed.merge(df_deaths, on='date').merge(df_recovered, on='date')

    # 8. 날짜만 나오게 변환
    df_merged['date'] = df_merged['date'].dt.date

    # 9. 일일 신규 수치 계산 --> 파생변수 생성
    # .diff()  --> fillna(0) --> .astype(int) 
    df_merged['new_confirmed'] = df_merged['confirmed'].diff().fillna(0).astype(int)
    df_merged['new_deaths'] = df_merged['deaths'].diff().fillna(0).astype(int)
    df_merged['new_recovered'] = df_merged['recovered'].diff().fillna(0).astype(int)

    # 10. 탭 UI 구성
    tab1, tab2, tab3 = st.tabs(['감염 추이', '통계 요약', '비율 분석'])

    # 11. tab1 : 감염 추이
    with tab1:
        # ① 누적 추이 (선 그래프) ─────────────────────────────
        st.subheader('누적 추이 그래프')

        # 누적 데이터용 매핑 사전
        label_map = {
            '확진자':'confirmed',
            '사망자':'deaths',
            '회복자':'recovered'
        }

        # 12. 다중 선택 위젯
        selected_labels = st.multiselect(
            label='표시할 항목을 선택하세요.',
            options=list(label_map.keys()),
            default=['확진자', '회복자']
        )

        # 13. 하나 이상 선택을 했다면 --> 그래프 출력
        if selected_labels:
            selected_cols = [label_map[label] for label in selected_labels]

            # 14. 선 그래프
            fig = px.line(
                data_frame=df_merged,
                x='date',
                y=selected_cols,
                markers=True,
                labels={col:kor for kor, col in label_map.items()}
            )
            st.plotly_chart(fig, width='stretch')

        # ② 일일 신규 수치 (막대 그래프) ─────────────────────
        st.subheader("🆕 일일 증가량 그래프")

        # 신규 데이터용 매핑 사전 (구조는 누적용과 동일)
        new_label_map = {
            '신규 확진자': 'new_confirmed',
            '신규 사망자': 'new_deaths',
            '신규 회복자': 'new_recovered'
        }

        selected_new_labels = st.multiselect(
            "표시할 항목 (신규)",
            options=list(new_label_map.keys()),
            default=['신규 확진자']
        )

        if selected_new_labels:
            # 선택된 한글 레이블 → 영어 열 이름으로 변환
            selected_new_cols = [new_label_map[label] for label in selected_new_labels]

            # px.bar : Plotly 막대 그래프
            # labels 파라미터로 범례·축 툴팁을 한글로 표시
            fig_new = px.bar(
                df_merged,
                x="date",
                y=selected_new_cols,
                labels={col: kor for kor, col in new_label_map.items()}
            )
            st.plotly_chart(fig_new, width='stretch')
          







# 파일 미업로드 시 상태 안내 메시지-----------------------------------------
else: # st.info() : 파란색 안내 박스로 사용자에게 보여준다!
    st.info('3개의 csv파일(확진자, 사망자, 회복자)을 모두 업로드 해주세요!')
