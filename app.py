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
    st.subheader("📊 주차별 순매수 강도 및 마케팅 실효성 분석")
    st.markdown("""
    업로드하신 `ETF 순매수 데이터_260529.xlsx` 파일의 시트(주차)를 비교하여 마케팅 강도를 분석합니다.
    * **분석 방식:** 전주(베이스) 데이터 대비 금주 데이터의 성장세 및 비중 파악
    """)

    # 1. 파일 업로드
    uploaded_file = st.file_uploader("ETF 순매수 데이터 엑셀 파일을 업로드해주세요", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # 엑셀 파일의 모든 시트 이름 가져오기
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            
            # '참고사항' 시트는 분석에서 제외
            weeks = [s for s in sheet_names if s != '참고사항']
            
            st.success(f"엑셀 로드 완료! 총 {len(weeks)}개의 주차 데이터가 확인되었습니다.")

            st.divider()
            st.markdown("#### ⚙️ 분석 주차 및 마케팅 타겟 설정")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                prev_week = st.selectbox("1주차 (기준이 될 전주 선택)", weeks, index=0)
            with col2:
                curr_week = st.selectbox("2주차 (비교할 금주 선택)", weeks, index=min(1, len(weeks)-1))
            with col3:
                # 엑셀에 있는 실제 투자주체 컬럼들 목록
                investor_opts = ['개인', '은행', '금융투자', '기관', '외국인', '투신', '연기금 등']
                target_investor = st.selectbox("마케팅 타겟 주체 선택", investor_opts, index=0)

           # 데이터를 읽어온 후
df_prev = pd.read_excel(uploaded_file, sheet_name=prev_week)
df_curr = pd.read_excel(uploaded_file, sheet_name=curr_week)

# 🔥 에러 해결 코드: 선택한 투자 주체 컬럼의 하이픈(-)이나 문자를 숫자 0으로 변환
df_prev[target_investor] = pd.to_numeric(df_prev[target_investor], errors='coerce').fillna(0)
df_curr[target_investor] = pd.to_numeric(df_curr[target_investor], errors='coerce').fillna(0)

            # 중요! 데이터 첫 줄에 있는 '전체' 총합 행 및 NaN 종목 제거 (시각화 왜곡 방지)
            df_prev = df_prev[(df_prev['종목명'] != '전체') & (df_prev['종목명'].notna())]
            df_curr = df_curr[(df_curr['종목명'] != '전체') & (df_curr['종목명'].notna())]

            # 두 주차 데이터 종목명 기준으로 결합 (inner join)
            merged_df = pd.merge(
                df_prev[['종목명', target_investor]], 
                df_curr[['종목명', target_investor]], 
                on='종목명', 
                suffixes=('_전주', '_금주')
            )

            # 2. 강도 계산 로직 선택
            st.markdown("#### ⚡ 강도 계산 방식 선택")
            formula_type = st.radio(
                "분석에 사용할 공식을 선택하세요:",
                (
                    "금주 순매수 금액 / 전주 순매수 금액 (단순 성장 강도)", 
                    "금주 순매수 금액 자체로 상품 간 백분율 비교 (금주 마케팅 집중도)"
                )
            )

            if st.button("순매수 강도 분석 실행 🚀"):
                if formula_type == "금주 순매수 금액 / 전주 순매수 금액 (단순 성장 강도)":
                    # 0으로 나누기 및 마이너스 금액 분모 처리 방지 (절대값 혹은 replace 적용)
                    merged_df['매수강도'] = (merged_df[f'{target_investor}_금주'] / merged_df[f'{target_investor}_전주'].replace(0, np.nan)) * 100
                    title_text = f"[{target_investor}] 전주 대비 금주 순매수 성장 강도 (%)"
                else:
                    # 금주 순매수 총합 중 각 상품이 차지하는 백분율 비중
                    total_curr = merged_df[f'{target_investor}_금주'].sum()
                    merged_df['매수강도'] = (merged_df[f'{target_investor}_금주'] / total_curr) * 100
                    title_text = f"[{target_investor}] 금주 총 순매수 중 상품별 비중 (%)"

                # 결과 정렬 (상위 15개만 정렬해서 차트 가독성 확보)
                result_df = merged_df.sort_values(by='매수강도', ascending=False).head(15)

                # 3. 결과 시각화
                st.markdown(f"### 🏆 {curr_week} 주차 마케팅 성적표")
                
                fig = px.bar(
                    result_df, 
                    x='종목명', 
                    y='매수강도', 
                    color='매수강도',
                    text_auto='.1f',
                    title=title_text,
                    color_continuous_scale='Viridis',
                    labels={'매수강도': '강도 (%)'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

                # 상세 데이터 테이블 제공
                st.markdown("##### 📋 상위 종목 상세 데이터")
                st.dataframe(
                    result_df[['종목명', f'{target_investor}_전주', f'{target_investor}_금주', '매수강도']].style.format({
                        f'{target_investor}_전주': '{:,.0f}',
                        f'{target_investor}_금주': '{:,.0f}',
                        '매수강도': '{:.2f}%'
                    }), 
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error(f"파일 분석 중 에러가 발생했습니다. 데이터 형식을 확인해주세요. 에러 내용: {e}")
    else:
        st.info("💡 오른쪽 사이드바 혹은 파일 업로더에 파일을 드래그해 올려주세요.")

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
