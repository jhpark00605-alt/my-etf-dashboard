import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 대시보드", layout="wide")

# 1. API 설정
try:
    # Secrets에 새로 만든 키를 넣었는지 꼭 확인!
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 404를 피하기 위해 가장 최신 명칭인 'gemini-1.5-flash-latest' 사용
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    
except Exception as e:
    st.error(f"초기 설정 오류: {e}")
    st.stop()

st.title("📊 ETF 마케팅 대시보드")

# ... (사이드바 생략) ...

if st.button("분석 실행"):
    with st.spinner("분석 중..."):
        try:
            # 2. 아주 짧은 테스트 문장으로 먼저 확인
            response = model.generate_content("안녕? 너는 누구니?")
            st.write(response.text)
        except Exception as e:
            # 여기서 404가 뜨면 '키' 자체의 권한 문제입니다.
            st.error(f"분석 오류: {e}")
