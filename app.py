import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 마케팅 대시보드", layout="wide")

# 1. API 설정 (가장 보수적인 모델명 사용)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # [치트키] 1.5-flash 대신 가장 안정적인 'gemini-pro'를 사용합니다.
    # 404 에러를 방지하기 위해 별도의 경로 없이 이름만 넣습니다.
    model = genai.GenerativeModel('gemini-pro')
    
except Exception as e:
    st.error(f"연결 오류: {e}")
    st.stop()

st.title("📊 ETF 시장 인텔리전스 & 마케팅 대시보드")

# 2. UI 구성
target_corp = st.sidebar.multiselect("증권사 선택", ["삼성증권", "미래에셋증권", "키움증권", "한국투자증권"])
target_fund = st.sidebar.multiselect("운용사 선택", ["KODEX", "TIGER", "RISE", "ACE"])
query = st.text_input("검색할 ETF 키워드", "반도체 ETF")

if st.button("분석 실행"):
    prompt = f"키워드 '{query}'와 관련하여 {target_corp}와 {target_fund}를 위한 마케팅 전략을 제안해줘."
    with st.spinner("분석 중..."):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")
            st.write("---")
            st.write("이래도 안 된다면? 구글 AI Studio에서 API 키를 만들 때, 오른쪽 상단 설정에서 'Global' 또는 'US' 지역이 선택되었는지 확인해보세요.")
