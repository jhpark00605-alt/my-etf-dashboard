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

# 3. 사이드바: 데이터 수집 대상 선택
st.sidebar.header("데이터 수집 대상")
target_corp = st.sidebar.multiselect("증권사 선택", ["삼성증권", "미래에셋증권", "키움증권", "한국투자증권"])
target_fund = st.sidebar.multiselect("운용사 선택", ["KODEX", "TIGER", "RISE", "ACE"])

# 4. 탭 구성
tab1, tab2, tab3 = st.tabs(["시장 뉴스 & 유튜브", "순매수 & 분석", "AI 마케팅 전략"])

with tab1:
    st.subheader("📰 시장 이슈 및 유튜브 테마")
    query = st.text_input("검색할 ETF 키워드", "반도체 ETF")
    if st.button("데이터 수집"):
        st.write(f"'{query}' 관련 데이터를 수집 중입니다...")
        st.success("데이터 수집 로직이 연결되었습니다.")

with tab2:
    st.subheader("📈 순매수 강도 및 연령별 데이터")
    st.info("향후 데이터 API를 연동하여 시각화할 영역입니다.")

with tab3:
    st.subheader("💡 Gemini AI 마케팅 인사이트")
    if st.button("인사이트 분석 실행"):
        prompt = f"""
        당신은 전문 ETF 마케터입니다. 
        사용자가 선택한 증권사: {target_corp}
        사용자가 선택한 운용사: {target_fund}
        분석 키워드: {query}
        
        이 데이터를 기반으로 마케팅 전략을 제안해줘.
        """
        with st.spinner("Gemini가 시장을 분석 중입니다..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
