import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="ETF 통합 마케팅 대시보드", layout="wide")

# 2. API 설정
try:
    # Secrets에서 키를 불러옵니다.
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 모델 정의: 404 에러를 방지하기 위해 'gemini-1.5-flash'를 사용합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"설정 중 오류가 발생했습니다: {e}")
    st.stop()

st.title("📊 ETF 시장 인텔리전스 & 마케팅 대시보드")

# 3. 사이드바 입력
st.sidebar.header("데이터 수집 대상")
target_corp = st.sidebar.multiselect("증권사 선택", ["삼성증권", "미래에셋증권", "키움증권", "한국투자증권"])
target_fund = st.sidebar.multiselect("운용사 선택", ["KODEX", "TIGER", "RISE", "ACE"])
query = st.text_input("검색할 ETF 키워드", "반도체 ETF")

# 4. 탭 구성
tab1, tab2, tab3 = st.tabs(["시장 뉴스 & 유튜브", "순매수 & 분석", "AI 마케팅 전략"])

with tab3:
    st.subheader("💡 Gemini AI 마케팅 인사이트")
    if st.button("인사이트 분석 실행"):
        prompt = f"""
        당신은 전문 ETF 마케터입니다.
        증권사: {target_corp}
        운용사: {target_fund}
        분석 키워드: {query}
        위 데이터를 바탕으로 투자자에게 어필할 마케팅 포인트 3가지를 제안해줘.
        """
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # 5. 콘텐츠 생성
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
                st.write("오류가 계속되면 API 키를 새로 발급받아 Secrets에 업데이트했는지 확인해주세요.")
