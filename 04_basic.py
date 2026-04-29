import streamlit as st
from PIL import Image

image = Image.open('input/egg.png')

# 이미지 불러오기
st.image(image, caption='egg_image')
st.image(image, caption='너비100픽셀', width=100)
st.image(image, caption='너비200픽셀', width=200)

# 화면 채우기
st.image(image, caption='전체 너비', width='stretch')

# 이미지 원본 크기
st.image(image, caption='원본 너비', width='content')

# 이미지 작게 새로운 변수에 저장
small_image = image.resize((200, 200))

st.image(small_image, caption='stretch', width='stretch')
st.image(small_image, caption='content', width='content')