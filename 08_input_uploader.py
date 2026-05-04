import streamlit as st

# 1. 텍스트 입력창
string1 = st.text_input(
    '좋아하는 포켓몬은???',  # 입력 레이블
    placeholder='당신이 가장 좋아하는 포켓몬 이름을 적어주세요!', # 안내글
    max_chars=32  # 최대 입력 글자 개수 제한
)
# 입력값이 있으면 화면에 출력 (값이 채워져 있으면 참, 비어있으면 거짓)
if string1:
    st.text(f'Your answer is {string1}.')

# 2. 비밀번호 입력창
string2 = st.text_input(
    '싫어하는 음식은???',  #  입력창 레이블
    placeholder='당신이 가장 싫어하는 음식을 하나 적어주세요!', # 안내문구
    max_chars=32,
    type='password'  # 입력값이 비밀번호 형태로 
)

if string2:
    st.text(f'Your answer is {string2}.')

st.divider()

# 3. 파일 업로더 
file = st.file_uploader(
    'Choose a file',  # 업로드 문구 레이블
    type='csv', #  확장자 제한 (csv만)
    accept_multiple_files=False  # 한번에 하나의 파일만 업로드 가능
)

# 판다스의 데이터프레임 형태로 읽어 표 출력
import pandas as pd

if file is not None:
    df = pd.read_csv(file)
    st.write(df)