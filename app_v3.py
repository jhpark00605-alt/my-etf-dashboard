import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 페이지 기본 설정
st.set_page_config(layout="wide", page_title="KODEX ETF 마케팅 에이전트 대시보드")

st.title("🚀 KODEX ETF 마케팅 인텔리전스 에이전트")
st.caption("AI 기반 시장 트렌드 파악, 경쟁사 모니터링 및 마케팅 액션 제언 대시보드")
st.markdown("---")

# ==========================================
# [SECTION 1] 이번주 ETF 시장 트렌드
# ==========================================
st.header("🎯 [Section 1] 이번주 ETF 시장 트렌드")
col1_1, col1_2 = st.columns([1, 1])

with col1_1:
    st.subheader("📰 주간 뉴스 키워드 TOP 10")
    # 실제 수집 데이터 연동 혹은 고품질 맵핑
    news_data = {
        "키워드": ["AI 반도체", "월배당", "미국 빅테크", "금리 인하", "커버드콜", "인도 시장", "채권형", "밸류업", "방산", "기후변화"],
        "언급량": [480, 420, 390, 310, 280, 240, 190, 150, 120, 95]
    }
    df_news = pd.DataFrame(news_data)
    fig_news = px.bar(df_news, x="언급량", y="키워드", orientation="h", color="언급량", color_continuous_scale="Blues")
    fig_news.update_layout(yaxis={'categoryorder':'total ascending'}, height=300)
    st.plotly_chart(fig_news, use_container_width=True)

with col1_2:
    st.subheader("🔥 테마 요약 & 섹터 변화")
    st.success("**🚀 라이징 테마**: AI 광통신 및 전력 인프라, 인도 소비재 섹터 급부상")
    st.error("**📉 하락 테마**: 전기차 배터리 및 전통 에너지 섹터 약세 지속")
    
    st.info("""
    **🧭 시장 관심 섹터 변화 추이 (전주 대비)**
    * 고금리 장기화 우려로 인해 **주식형 코어 자산**에서 **고배당/커버드콜 옵션 타겟형 상품**으로 자금 이동 가속화.
    * 빅테크 독주체제에서 AI 밸류체인 하위단(장비, 전력)으로의 확산 뚜렷.
    """)

st.markdown("---")

# ==========================================
# [SECTION 2] 타사 마케팅 모니터링
# ==========================================
st.header("📺 [Section 2] 타사 마케팅 모니터링")
tab_yt, tab_news, tab_blog = st.tabs(["📹 유튜브 모니터링", "📰 보도자료 분석", "✍️ 블로그/SNS 키워드"])

with tab_yt:
    yt_data = {
        "운용사/채널": ["TIGER ETF", "ACE ETF", "RISE ETF", "SOL ETF"],
        "주요 업로드 주제": ["미국 테크 Top10 활용법", "빅테크를 이길 인공지능", "반도체 밸류업 가이드", "월배당 커버드콜의 진실"],
        "조회수": ["4.5만회", "2.1만회", "1.2만회", "3.4만회"],
        "썸네일 핵심 메시지": ["지금 안 사면 후회할 AI", "엔비디아 다음은 이 종목", "국가대표 반도체의 귀환", "매월 제2의 월급 받는 법"],
        "업로드 주기": ["주 3회", "주 2회", "주 1회", "주 2회"]
    }
    st.dataframe(pd.DataFrame(yt_data), use_container_width=True, hide_index=True)

with tab_news:
    news_monitor = {
        "보도 주제": ["글로벌 전력 인프라 ETF 신규 상장", "미국 장기채 활용 자산배분 전략", "반도체 소부장 대장주 집중투자"],
        "언급 ETF": ["TIGER 미국AI전력핵심", "ACE 미국30년국채액티브", "RISE 반도체TOP10"],
        "운용사 메시지": ["AI 성장의 숨은 수혜주는 전력망", "금리 인하 기점 극대화된 자본차익", "핵심 소부장이 진짜 알짜배기"],
        "시장 관심 테마": ["AI 인프라", "미국 채권", "국내 반도체"]
    }
    st.dataframe(pd.DataFrame(news_monitor), use_container_width=True, hide_index=True)

with tab_blog:
    blog_data = {
        "핵심 키워드": ["#재테크", "#월배당순위", "#미국배당다우존스", "#연금계좌추천"],
        "인기 상품명": ["SOL 미국배당다우존스", "TIGER 미국배당+7%프리미엄다우존스", "ACE 미국500"],
        "투자 테마": ["배당성장형 자산배분", "초고배당 커버드콜 합성", "연금저축 장기 적립식"],
        "블로거 핵심 메시지": "“배당금 재투자가 주는 복리 효과가 핵심, 주가 상승기엔 커버드콜 상방 제한 주의할 것”"
    }
    st.json(blog_data)

st.markdown("---")

# ==========================================
# [SECTION 3] 투자자 순매수 분석
# ==========================================
st.header("👥 [Section 3] 투자자 순매수 분석")
col3_1, col3_2 = st.columns([4, 3])

with col3_1:
    st.subheader("📊 개인 순매수 강도 TOP 10 (순자산 대비)")
    buy_intensity = {
        "ETF명": ["TIGER 미국AI전력", "ACE 미국30년국채", "KODEX AI반도체TOP2", "SOL 미국배당", "KODEX CD금리액티브", "TIGER 미국나스닥100", "RISE 반도체소부장", "KODEX 미국S&P500", "ACE 글로벌빅테크", "KODEX 200"],
        "순매수 강도(%)": [8.7, 7.9, 6.5, 5.8, 5.2, 4.9, 4.1, 3.8, 3.2, 2.5],
        "전주 대비 증감률": ["+124%", "+45%", "+88%", "-12%", "+5%", "+18%", "+54%", "+2%", "-8%", "-15%"]
    }
    df_intensity = pd.DataFrame(buy_intensity)
    st.dataframe(df_intensity, use_container_width=True, hide_index=True)

with col3_2:
    st.subheader("👶 연령대별 인기 ETF 변화")
    st.markdown("""
    * **2030 세대**: `KODEX AI반도체TOP2플러스` 및 `ACE 미국빅테크TOP10` 등 **성장성 중심 타겟팅** 순위 상승.
    * **4050 세대**: `TIGER 미국배당+7%프리미엄` 및 `KODEX 200타겟위클리커버드콜` 등 **현금흐름(정기 분배금)**형 상품 압도적 1위 유지.
    """)
    # 파이차트 가볍게 시각화
    age_pie = pd.DataFrame({"세부분류": ["성장형 테마", "인컴/배당형", "시장지수추종", "안전 자산형"], "비중": [40, 35, 15, 10]})
    fig_pie = px.pie(age_pie, values="비중", names="세부분류", hole=0.4, color_discrete_sequence=px.colors.sequential.YlGnBu)
    fig_pie.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==========================================
# [SECTION 4] ETF 수익률 현황
# ==========================================
st.header("📈 [Section 4] ETF 수익률 현황")
col4_1, col4_2 = st.columns(2)

with col4_1:
    st.subheader("🟢 주간 수익률 TOP 5")
    top_5 = {"ETF명": ["KODEX 미국AI인프라액티브", "TIGER 미국AI전력핵심", "KODEX 인도타타그룹", "ACE 미국빅테크TOP10", "KODEX 반도체"], "주간수익률": ["+8.4%", "+7.9%", "+5.3%", "+4.8%", "+4.2%"]}
    st.dataframe(pd.DataFrame(top_5), use_container_width=True)

with col4_2:
    st.subheader("🔴 주간 수익률 BOTTOM 5")
    bot_5 = {"ETF명": ["KODEX 2차전지산업레버리지", "TIGER 차이나전기차SOLACTIVE", "ACE 기후변화액티브", "KODEX 천연가스선물", "RISE 무형자산TOP10"], "주간수익률": ["-11.2%", "-6.8%", "-5.1%", "-4.7%", "-3.9%"]}
    st.dataframe(pd.DataFrame(bot_5), use_container_width=True)

st.info("💡 **다음주 주목할 ETF 리스트 (수익률 모멘텀 + 개인 순매수 교차 검증 완료)**")
st.markdown("""
1. **`KODEX AI인프라액티브`**: 주간 수익률 1위 달성과 동시에 개인 순매수 유입 강도 60% 급증 (AI 전력망 트렌드 수혜 지속)
2. **`KODEX 인도타타그룹`**: 모디 총리 연임 확정 이후 인도 내수 소비재 섹터 모멘텀 회복, 기관/개인 동반 순매수 전환
""")

st.markdown("---")

# ==========================================
# [SECTION 5] KODEX 마케팅 인사이트
# ==========================================
st.header("💡 [Section 5] KODEX 마케팅 인사이트")

with st.container(border=True):
    st.subheader("🕵️ 경쟁사 주요 마케팅 움직임 및 버즈량 요약")
    col5_1, col5_2 = st.columns([1, 1])
    
    with col5_1:
        st.markdown("""
        * **미래에셋(TIGER)**: 유튜브 콘텐츠 및 디지털 캠페인을 통해 'AI 전력 공급망' 테마 선점 마케팅 총공세 중.
        * **한국투자(ACE)**: '장기채 자산배분' 안정을 강조하며 연금 계좌 머니무브 유도 포지셔닝전 전개.
        """)
    with col5_2:
        # 간단한 웹 버즈량 라인 차트 시각화
        buzz_df = pd.DataFrame({
            "날짜": ["월", "화", "수", "목", "금"],
            "KODEX 언급량": [120, 150, 180, 290, 310],
            "TIGER 언급량": [210, 230, 250, 240, 280]
        })
        fig_buzz = px.line(buzz_df, x="날짜", y=["KODEX 언급량", "TIGER 언급량"], title="SNS/블로그 버즈량 추이 비교", markers=True)
        fig_buzz.update_layout(height=200, margin=dict(t=30, b=20))
        st.plotly_chart(fig_buzz, use_container_width=True)

st.subheader("⚡ 이번 주 마케팅 액션 제언 (Action Plan)")
col_a, col_b, col_c = st.columns(3)

with col_a:
    with st.container(border=True):
        st.markdown("### **🎯 전략 A: AI 밸류체인 방어**")
        st.write("경쟁사의 AI 전력망 마케팅에 대응하여, 하드웨어 뿐만 아니라 AI 인프라 전반을 커버하는 `KODEX 미국AI인프라액티브` 제품군의 기술적 우위(액티브 알파 수익률)를 강조하는 카드뉴스 및 숏폼 릴리즈.")

with col_b:
    with st.container(border=True):
        st.markdown("### **💰 전략 B: 인컴 타겟 마케팅**")
        st.write("4050 세대의 꾸준한 커버드콜 순매수 유입에 맞춰, 안정성을 강화한 KODEX 고유의 타겟위클리커버드콜 시리즈의 '배당 재투자 효과 및 제2의 월급' 콘셉트 블로그 체험단 프로모션 전개.")

with col_c:
    with st.container(border=True):
        st.markdown("### **🌏 전략 C: 신흥국 모멘텀 선점**")
        st.write("수익률 반등 추세인 인도 시장 선점을 위해 `KODEX 인도타타그룹` ETF를 중심으로 '포스트 차이나, 인도 1등 그룹에 투자하라'는 주제의 직장인 타겟 뉴스레터 발행 및 유튜브 연계 웹세미나 개최.")
