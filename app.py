import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 페이지 기본 설정
st.set_page_config(page_title="KODEX 마케팅 AI 에이전트", page_icon="📈", layout="wide")

# 헤더
st.title("📈 KODEX ETF 주간 마케팅 & 트렌드 모니터링 에이전트")
st.markdown("삼성자산운용 KODEX 마케팅 전략 도출을 위한 AI 기반 트렌드 분석 대시보드입니다.")
st.divider()

# 탭 생성 (기획하신 6가지 항목을 5개의 탭으로 논리적으로 구성)
tabs = st.tabs([
    "1. 뉴스 & 테마 이슈", 
    "2. 증권사 유튜브 트렌드", 
    "3. 타운용사(경쟁사) 동향", 
    "4. 투자자 & 순매수 데이터", 
    "5. 💡 AI 마케팅 인사이트"
])

# ==========================================
# Tab 1: 뉴스 & 테마 이슈 (언급량 분석)
# ==========================================
with tabs[0]:
    st.subheader("📰 금주 ETF 관련 뉴스 및 이슈 언급량 파악")
    st.caption("주요 경제 뉴스를 크롤링하여 가장 많이 언급된 키워드와 테마를 분석합니다.")
    
    # [TODO] 실제 뉴스 크롤링 및 형태소 분석(KoNLPy 등) 데이터 연동 필요
    mock_keywords = pd.DataFrame({
        '키워드': ['반도체', 'AI', '배당금', '이차전지', '미국채', 'S&P500'],
        '언급량': [450, 380, 290, 210, 150, 310]
    }).sort_values(by='언급량', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.dataframe(mock_keywords, use_container_width=True, hide_index=True)
    with col2:
        fig1 = px.bar(mock_keywords, x='키워드', y='언급량', color='언급량', title="금주 주요 키워드 언급량")
        st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# Tab 2: 증권사 유튜브 트렌드
# ==========================================
with tabs[1]:
    st.subheader("▶️ 주요 증권사 유튜브 콘텐츠 트렌드")
    st.caption("삼성, 미래에셋, 한국투자, 키움증권의 최신 유튜브 영상을 분석하여 미는 테마를 파악합니다.")
    
    # [TODO] YouTube Data API v3를 활용하여 각 채널의 최신 영상 제목/조회수/설명 추출 필요
    mock_youtube_data = pd.DataFrame({
        '증권사': ['삼성증권', '미래에셋증권', '한국투자증권', '키움증권'],
        '주요 강조 테마': ['온디바이스 AI', '인도 주식시장', '월배당 ETF', '미국 빅테크'],
        '최다 조회수 영상 제목': ['이제는 온디바이스 AI다! 관련주는?', '넥스트 차이나, 인도에 투자하는 법', '매월 현금이 꽂히는 마법', '엔비디아, 애플 지금 사도 될까?'],
        '조회수': [15000, 22000, 18000, 31000]
    })
    
    st.dataframe(mock_youtube_data, use_container_width=True, hide_index=True)
    
    st.info("💡 **트렌드 요약:** 금주 주요 증권사들은 대체로 'AI/빅테크'와 '현금흐름(월배당)' 테마를 강조하고 있습니다.")

# ==========================================
# Tab 3: 타운용사(경쟁사) 동향
# ==========================================
with tabs[2]:
    st.subheader("🏢 주요 운용사별 ETF 이슈 모니터링")
    st.caption("KODEX, TIGER, RISE, ACE의 주요 상장 소식, 보수 인하 등 핵심 이슈를 정리합니다.")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    # [TODO] 각 운용사 보도자료 크롤링 또는 네이버 금융 뉴스 필터링 데이터 연동
    with col_a:
        st.success("**KODEX (삼성)**")
        st.write("- 신규 월배당 ETF 상장 이벤트")
        st.write("- 미국 장기채 ETF 거래량 1위 달성 홍보")
        
    with col_b:
        st.warning("**TIGER (미래에셋)**")
        st.write("- 인도 Nifty50 ETF 마케팅 강화")
        st.write("- AI 반도체 세미나 개최")
        
    with col_c:
        st.info("**RISE (KB)**")
        st.write("- ETF 브랜드명 'RISE' 리뉴얼 대대적 홍보")
        st.write("- 배당왕 ETF 수수료 인하")
        
    with col_d:
        st.error("**ACE (한국투자)**")
        st.write("- 빅테크 밸류체인 액티브 ETF 출시")
        st.write("- 유튜브 쇼츠를 활용한 2030 타겟 마케팅")

# ==========================================
# Tab 4: 투자자 & 순매수 데이터 (마케팅 실효성)
# ==========================================
with tabs[3]:
    st.subheader("📊 데이터 기반 마케팅 실효성 분석")
    st.markdown("""
    업로드하신 순매수 데이터를 바탕으로 **상품별 매수 강도**를 분석합니다.
    * **공식:** (2주차 순매수 금액 / 1주차 순자산 금액) × 100
    """)

    # 1. 파일 업로드 UI
    uploaded_file = st.file_uploader("순매수 데이터 엑셀 파일(.xlsx)을 업로드해주세요", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # 엑셀 읽기
            df = pd.read_excel(uploaded_file)
            st.success("파일 업로드 성공!")
            
            # 데이터 미리보기
            with st.expander("데이터 미리보기"):
                st.dataframe(df.head())

            st.divider()
            st.markdown("#### ⚙️ 분석 설정")
            st.caption("분석에 사용할 컬럼을 매칭해주세요.")

            # 2. 컬럼 매칭 (사용자가 직접 선택하도록 하여 오류 방지)
            cols = df.columns.tolist()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                prod_col = st.selectbox("상품명(ETF명) 컬럼", cols)
            with col2:
                buy_col = st.selectbox("2주차 순매수 금액 컬럼", cols)
            with col3:
                aum_col = st.selectbox("1주차 순자산 금액 컬럼", cols)

            # 3. 계산 버튼
            if st.button("매수 강도 분석 실행 📈"):
                # 계산 로직 (0으로 나누기 방지 처리)
                df['매수강도(%)'] = (df[buy_col] / df[aum_col].replace(0, np.nan)) * 100
                
                # 결과 데이터 정리
                result_df = df[[prod_col, buy_col, aum_col, '매수강도(%)']].sort_values(by='매수강도(%)', ascending=False)
                
                # 4. 결과 시각화
                st.markdown("#### 🏆 상품별 매수 강도 결과")
                
                # 지표 요약
                top_product = result_df.iloc[0]
                st.metric(label=f"이번 주 최고 강도 상품: {top_product[prod_col]}", 
                          value=f"{top_product['매수강도(%)']:.2f}%")

                # 차트 출력
                fig = px.bar(result_df, 
                             x=prod_col, 
                             y='매수강도(%)', 
                             color='매수강도(%)',
                             text_auto='.2f',
                             title="상품별 매수 강도 비교 (%)",
                             color_continuous_scale='Blues',
                             labels={'매수강도(%)': '강도 (%)', prod_col: '상품명'})
                
                st.plotly_chart(fig, use_container_width=True)

                # 데이터 테이블 출력
                st.dataframe(result_df.style.highlight_max(axis=0, subset=['매수강도(%)']), use_container_width=True)

        except Exception as e:
            st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")
    else:
        st.info("데이터 분석을 위해 엑셀 파일을 업로드해주세요.")

# ==========================================
# Tab 5: AI 마케팅 인사이트 및 전략 제안
# ==========================================
with tabs[4]:
    st.subheader("💡 AI 기반 마케팅 인사이트 & 액션 플랜")
    st.caption("앞선 분석(1~4번) 데이터를 종합하여 AI가 KODEX 맞춤형 마케팅 전략을 제안합니다.")
    
    # [TODO] Google Gemini API 등을 연결하여 앞선 데이터 프레임들을 텍스트로 변환해 프롬프트로 전달하고 답변을 받는 로직 구성
    if st.button("이번 주 마케팅 전략 AI 리포트 생성하기 🚀"):
        with st.spinner("AI가 데이터를 분석하여 전략을 도출하고 있습니다..."):
            import time
            time.sleep(2) # API 호출 대기 시간 시뮬레이션
            
            st.markdown("""
            ### 🤖 **금주 마케팅 전략 제안 (AI Generated)**
            
            **1. 핵심 인사이트 (Findings)**
            * **트렌드:** 현재 유튜브와 뉴스 모두 'AI/반도체'와 지속적인 '월배당' 수요에 집중되어 있습니다.
            * **경쟁사 동향:** TIGER는 '인도' 테마를, RISE는 '브랜드 리뉴얼'에 마케팅 비용을 집중하고 있습니다.
            * **실효성 분석:** 미디어 언급량이 높은 'AI 반도체' 테마가 실제 2030 세대의 순매수 강도와 강한 양의 상관관계를 보입니다.

            **2. KODEX 마케팅 액션 플랜 (Actionable Strategies)**
            * **전략 A (상품 방어 & 공격):** 타사가 밀고 있는 '인도' 관련 테마에 대응하기 위해, KODEX의 대표 인도 ETF(예: KODEX 인도Nifty50)의 수익률 우위 또는 보수 차별점을 강조하는 카드뉴스를 이번 주 내에 배포하십시오.
            * **전략 B (타겟 마케팅):** 3040 타겟으로 'KODEX 미국 배당 다우존스' 등 월배당 상품의 복리 효과를 보여주는 시뮬레이션 웹페이지를 유튜브 쇼츠 하단 링크로 연계하여 트래픽을 유도하세요.
            * **전략 C (키워드 선점):** 다음 주 예상 이슈인 '온디바이스 AI' 관련하여, 증권사 PB들을 대상으로 한 세일즈 피치(Sales Pitch) 자료를 선제적으로 제공하여 창구 추천을 유도하십시오.
            """)
    else:
        st.info("버튼을 눌러 AI 인사이트를 생성하세요.")
