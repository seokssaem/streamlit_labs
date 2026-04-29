import streamlit as st

# 파이썬 코드
code = '''
import seaborn as sns

iris = sns.load_dataset('iris')
sns.pairplot(data=iris, hue='species', corner=True)
plt.show()
'''
st.code(code, language='python')

# 버튼
def button_write():
    """버튼을 클릭하면 실행되는 함수"""
    st.write('button activated!')

st.button('activate', on_click=button_write)    
st.button('Reset', type='primary')

st.divider()

# 버튼이 눌러진 상태 --> True 
if st.button('Reset', type='primary', key='btn1'):
    st.write('Reset clicked!')

if st.button('Cancel', type='secondary', key='btn2'):
    st.write('Cancel clicked!')

if st.button('Ignore', type='tertiary', key='btn3'):
    st.write('Ignore clicked!')