import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 마케팅 대시보드", layout="wide")

# [중요] API 키 설정
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 1.5-flash 대신 1.5-flash-latest를 사용하여 경로 문제를 우회합니다.
# 이 명칭은 v1beta와 v1 모든 버전에서 인식률이 가장 높습니다.
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"모델 로드 실패: {e}")
    st.stop()

st.title("📊 ETF 마케팅 대시보드")

# UI 구성
target_corp = st.sidebar.multiselect("증권사", ["삼성", "미래", "키움", "한투"])
target_fund = st.sidebar.multiselect("운용사", ["KODEX", "TIGER", "RISE", "ACE"])
query = st.text_input("검색 키워드", "반도체 ETF")

if st.button("AI 분석 실행"):
    if not query:
        st.warning("키워드를 입력해주세요.")
    else:
        with st.spinner("AI가 전략을 짜고 있습니다..."):
            try:
                # 콘텐츠 생성
                response = model.generate_content(f"{query} 관련 {target_corp}, {target_fund} 마케팅 전략 3가지 제안해줘.")
                st.success("분석 완료!")
                st.markdown(response.text)
            except Exception as e:
                # 만약 또 404가 뜨면 에러 내용을 상세히 출력합니다.
                st.error("데이터 통신 중 오류가 발생했습니다.")
                st.info(f"상세 에러 내용: {e}")
