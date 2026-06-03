import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import requests
from google import genai
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi

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
    st.subheader("🎬 주요 증권사 유튜브 마케팅 모니터링")
    
    API_KEY_YT = st.secrets.get("YOUTUBE_API_KEY")
    API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")

    # ... (중략: 날짜 선택 및 데이터 수집 함수 부분은 동일) ...

    if st.button("유튜브 트렌드 분석 실행 🚀"):
        if not API_KEY_YT or not API_KEY_GEMINI:
            st.error("⚠️ API 키를 불러오지 못했습니다.")
        else:
            progress = st.progress(0)
            status = st.empty()
            all_text = ""
            
            # 1. 데이터 수집 루프
            for i, (name, c_id) in enumerate(TARGET_BROKERAGES.items()):
                status.text(f"🔍 {name} 수집 중...")
                all_text += get_yt_data(name, c_id, start_date, end_date, API_KEY_YT)
                progress.progress((i + 1) * 20)

            # 2. Gemini 분석 (최신 SDK 문법 적용)
            status.text("🤖 Gemini 분석 중...")
            try:
                # 💡 핵심 수정: configure 대신 Client 객체를 생성합니다.
                client = genai.Client(api_key=API_KEY_GEMINI)
                
                prompt = f"다음 데이터를 분석하여 증권사 마케팅 트렌드 리포트를 작성해줘:\n\n{all_text}"
                
                # 💡 핵심 수정: 호출 방식 변경
                response = client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt
                )
                
                progress.progress(100)
                status.text("✅ 분석 완료!")
                st.divider()
                st.markdown(response.text) # 최신 SDK는 response.text로 결과 확인 가능
                
            except Exception as e:
                st.error(f"Gemini 분석 중 오류 발생: {e}")

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
# ==========================================
# Tab 4: 투자자 & 순매수 데이터 (문법 오류 수정본)
# ==========================================
with tabs[3]:
    st.subheader("📊 주차별 순매수 강도 및 마케팅 실효성 분석")
    
    uploaded_file = st.file_uploader("ETF 순매수 데이터 엑셀 파일을 업로드해주세요", type=["xlsx"])

    if uploaded_file is not None:
        try: # 1. 여기서 try가 시작됩니다
            # 엑셀 파일 로드
            xls = pd.ExcelFile(uploaded_file)
            weeks = [s for s in xls.sheet_names if s != '참고사항']
            
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                prev_week = st.selectbox("1주차 (전주)", weeks, index=0)
            with col2:
                curr_week = st.selectbox("2주차 (금주)", weeks, index=min(1, len(weeks)-1))
            with col3:
                investor_opts = ['개인', '은행', '금융투자', '기관', '외국인', '투신', '연기금 등']
                target_investor = st.selectbox("분석 타겟", investor_opts, index=0)

            # 데이터 로드 및 전처리
            df_prev = pd.read_excel(uploaded_file, sheet_name=prev_week)
            df_curr = pd.read_excel(uploaded_file, sheet_name=curr_week)

            # '전체' 행 제외 및 숫자 변환 (하이픈 에러 방지)
            df_prev = df_prev[(df_prev['종목명'] != '전체') & (df_prev['종목명'].notna())]
            df_curr = df_curr[(df_curr['종목명'] != '전체') & (df_curr['종목명'].notna())]
            
            df_prev[target_investor] = pd.to_numeric(df_prev[target_investor], errors='coerce').fillna(0)
            df_curr[target_investor] = pd.to_numeric(df_curr[target_investor], errors='coerce').fillna(0)

            # 데이터 결합
            merged_df = pd.merge(
                df_prev[['종목명', target_investor]], 
                df_curr[['종목명', target_investor]], 
                on='종목명', 
                suffixes=('_전주', '_금주')
            )

            if st.button("분석 실행 🚀"):
                # 금주 비중(%)으로 계산
                total_curr = merged_df[f'{target_investor}_금주'].sum()
                merged_df['매수강도'] = (merged_df[f'{target_investor}_금주'] / total_curr) * 100
                
                result_df = merged_df.sort_values(by='매수강도', ascending=False).head(15)

                st.markdown(f"### 🏆 {curr_week} 주차 마케팅 성적표")
                fig = px.bar(result_df, x='종목명', y='매수강도', color='매수강도', text_auto='.1f')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(result_df, use_container_width=True)

        except Exception as e: # 2. try의 짝꿍인 except가 반드시 있어야 합니다!
            st.error(f"분석 중 오류가 발생했습니다: {e}")
            
    else:
        st.info("💡 엑셀 파일을 업로드하면 분석을 시작합니다.")

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
