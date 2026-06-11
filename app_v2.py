import streamlit as st

# 1. 페이지 전체를 넓게 쓰기 위한 설정 (★필수)
st.set_page_config(
    page_title="KODEX 마케팅 대시보드",
    layout="wide",  # 화면을 좌우로 넓게 채워줍니다.
    initial_sidebar_state="expanded"
)

# 2. 타이틀 및 헤더
st.title("📊 KODEX 마케팅 AI 에이전트 & 전략 대시보드")
st.caption("은행/증권사 채널 외적 확장 및 2030 세대 공략을 위한 실시간 마케팅 인텔리전스")
st.markdown("---")

# 3. 화면을 좌우 2개의 칼럼으로 쪼개기 (비율 5:5)
col1, col2 = st.columns(2)

# --- [왼쪽 칼럼: 마케팅 전략 및 SWOT] ---
with col1:
    # 섹션 1: 마케팅 필수 근거 (테두리가 있는 박스 형태로 감싸기)
    with st.container(border=True):
        st.subheader("🎯 채널 외적 마케팅 필수 근거")
        st.markdown("""
        * **구매 결정권 이동**: PB 권유 중심에서 개인의 자기주도형(MTS) 매매로 전환
        * **경쟁 구도 변화**: 상품 스펙 상향 평준화로 '브랜드 팬덤' 싸움 촉발
        * **미래 생존 지표**: 잠재적 연금 고래인 2030 세대의 조기 선점(전환비용 극대화)
        """)
        
    st.write("") # 간격 띄우기

    # 섹션 2: SWOT 분석
    with st.container(border=True):
        st.subheader("📊 KODEX 마케팅 SWOT 진단")
        st.markdown("""
        * 🟢 **강점(S)**: 최초(First-mover) 타이틀 브랜딩, 김도형 대표의 '강남역 8번출구' 휴먼터치 소통
        * 🔴 **보완점(W)**: Gen Z 타깃 라이트 콘텐츠 부족, 콘텐츠에서 매수로 이어지는 디지털 UX 퍼널 약세
        """)

    st.write("") 

    # 섹션 3: 핀테크 협업 아이디어
    with st.container(border=True):
        st.subheader("💡 토스증권 핵심 협업 아이디어")
        st.markdown("""
        1. **주주 대항전**: 밸런스 게임 투표 시 KODEX 소수점 주식(500원) 즉시 지급 바이럴
        2. **주식 모으기 챌린지**: 스타터 패키지 정기 구독 및 출석 퀘스트 달성 리워드
        3. **소비 연동형 팝업**: 카드 소비 내역 확인 시 잔돈을 KODEX ETF로 자동 전환
        """)


# --- [오른쪽 칼럼: AI Agent 실시간 모니터링 (실현 가능 항목)] ---
with col2:
    with st.container(border=True):
        st.subheader("🤖 AI Agent 실시간 크롤링 현황")
        
        # 상단에 상태 표시 배지처럼 표현하기
        c1, c2 = st.columns(2)
        c1.metric(label="시스템 상태", value="정상 작동 중")
        c2.metric(label="금일 KODEX 브랜드 긍정 여론", value="74%")
        st.markdown("---")
        
        # 모니터링 항목 1
        st.markdown("### 1. 토스증권 WTS 커뮤니티 여론 (퍼블릭 웹)")
        st.write("• 주요 테마(반도체, 배당) 관련 2030 투자자 감성 추출")
        st.write("• 긍정/부정 키워드 실시간 데이터 분류 파이프라인 작동")
        st.markdown("---")
        
        # 모니터링 항목 2
        st.markdown("### 2. 증권사 공식 리서치 센터 보고서 (PDF)")
        st.write("• 전체 공개 보고서 파싱을 통한 주간 유망 산업 트렌드 랩핑")
        st.write("• 팩트 기반 대안 제안서 제작용 소스 자동 분류")
        st.markdown("---")
        
        # 모니터링 항목 3
        st.markdown("### 3. '강남역 8번출구' 등 유튜브/블로그 댓글")
        st.write("• 마케팅 피드백 수집 및 대중의 '진성 질문' 필터링")
        st.write("• 차주 유튜브 콘텐츠 기획 및 창구 배포용 FAQ 제작 연계")
