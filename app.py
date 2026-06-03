import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 통합 마케팅 대시보드", layout="wide")

# API 설정
try:
    # 1. 시크릿에서 키를 안전하게 불러오기
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 2. 모델명을 직접 지정 (가장 안전한 방식)
    # 리스트를 조회하지 않고 직접 생성자를 호출합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"API 설정 오류: {e}")
    st.stop()

st.title("📊 ETF 시장 인텔리전스 & 마케팅 대시보드")

# ... (사이드바 및 탭 구성 코드는 동일하게 유지)
