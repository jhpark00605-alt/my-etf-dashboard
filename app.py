import streamlit as st
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup

# 1. API 설정
st.set_page_config(page_title="ETF 통합 마케팅 대시보드", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 모델 자동 선택 로직
    # 지원되는 모델 중 generateContent가 가능한 첫 번째 모델을 자동으로 가져옵니다.
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_methods]
    if not models:
        st.error("사용 가능한 모델을 찾을 수 없습니다.")
        st.stop()
    model = genai.GenerativeModel(models[0].name) # 가장 적절한 모델 자동 할당
    
except Exception as e:
    st.error(f"설정 오류: {e}")
    st.stop()

# ... (이후 UI 코드는 동일)
