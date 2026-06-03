import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="ETF 마케팅 대시보드", layout="wide")

# API 설정
try:
    # 1. 키 설정 (사용자님의 AQ.로 시작하는 키가 여기 들어갑니다)
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 2. 모델 설정 (404 방지를 위해 경로를 포함한 최신 명칭 사용)
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    
except Exception as e:
    st.error(f"설정 오류: {e}")
    st.stop()

st.title("📊 ETF 마케팅 대시보드")

if st.button("AI 분석 시작"):
    with st.spinner("분석 중..."):
        try:
            # 테스트용 간단한 질문
            response = model.generate_content("안녕하세요, 마케팅 전문가로서 인사해주세요.")
            st.success("연결 성공!")
            st.markdown(response.text)
        except Exception as e:
            # 여기서 또 404가 뜨면 '앱 재배포'가 유일한 답입니다.
            st.error(f"오류 발생: {e}")
