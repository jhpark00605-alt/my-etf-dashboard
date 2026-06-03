import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 통합 마케팅 대시보드", layout="wide")

# 1. API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 404 에러를 방지하는 최후의 수단: 경로를 포함한 명칭 사용
    # 모델명 앞에 'models/'를 붙이는 것이 핵심입니다.
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    
except Exception as e:
    st.error(f"초기화 오류: {e}")
    st.stop()

st.title("📊 ETF 시장 인텔리전스 & 마케팅 대시보드")

# 2. 사이드바 및 탭
target_corp = st.sidebar.multiselect("증권사 선택", ["삼성증권", "미래에셋증권", "키움증권", "한국투자증권"])
target_fund = st.sidebar.multiselect("운용사 선택", ["KODEX", "TIGER", "RISE", "ACE"])
query = st.text_input("검색할 ETF 키워드", "반도체 ETF")

if st.button("분석 실행"):
    prompt = f"키워드 '{query}' 관련 {target_corp}, {target_fund} 마케팅 전략 제안해줘."
    with st.spinner("분석 중..."):
        try:
            # 콘텐츠 생성
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")
            st.write("---")
            st.write("만약 404가 계속된다면, 사용 중인 Google AI Studio 프로젝트가 '베타' 상태이거나 제한된 권역일 수 있습니다.")
