import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 통합 마케팅 대시보드", layout="wide")

# 1. API 설정
try:
    # Secrets에서 키 불러오기
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 2. 모델 직접 지정 (가장 안전한 방식)
    # 404 에러를 방지하기 위해 'gemini-1.5-flash'를 사용합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"API 초기화 오류: {e}")
    st.stop()

st.title("📊 ETF 시장 인텔리전스 & 마케팅 대시보드")

# 3. 사이드바 및 탭 구성
target_corp = st.sidebar.multiselect("증권사 선택", ["삼성증권", "미래에셋증권", "키움증권", "한국투자증권"])
target_fund = st.sidebar.multiselect("운용사 선택", ["KODEX", "TIGER", "RISE", "ACE"])
query = st.text_input("검색할 ETF 키워드", "반도체 ETF")

tab1, tab2, tab3 = st.tabs(["시장 뉴스 & 유튜브", "순매수 & 분석", "AI 마케팅 전략"])

with tab3:
    st.subheader("💡 Gemini AI 마케팅 인사이트")
    if st.button("인사이트 분석 실행"):
        prompt = f"키워드 '{query}'와 관련하여 {target_corp}와 {target_fund}를 위한 마케팅 전략을 제안해줘."
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # 4. 모델 호출
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
