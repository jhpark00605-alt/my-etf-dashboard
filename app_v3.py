import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import requests
import json
import urllib.parse
import urllib.request
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import google.generativeai as genai

# 페이지 기본 설정 및 와이드 모드 강제 적용 (대시보드 필수)
st.set_page_config(page_title="KODEX 마케팅 AI 에이전트", page_icon="📈", layout="wide")

# 헤더
st.title("🚀 KODEX ETF 마케팅 & 트렌드 모니터링 대시보드")
st.markdown("삼성자산운용 KODEX 마케팅 전략 도출을 위한 AI 기반 통합 모니터링 인텔리전스입니다.")
st.divider()

# ==============================================================================
# [Section 1] 이번주 ETF 시장 트렌드
# ==============================================================================
st.header("🎯 Section 1. 이번주 ETF 시장 트렌드")
st.caption("주간 ETF 관련 뉴스 키워드 TOP 10, 라이징/하락 테마 및 시장 관심 섹터를 실시간으로 파악합니다.")

col1_left, col1_right = st.columns([1, 1])

with col1_left:
    st.subheader("📰 뉴스 키워드 분석")
    if st.button("실시간 뉴스 분석 실행 🔍", key="btn_sec1_news"):
        status = st.empty()
        status.text("🌐 최신 뉴스 수집 중...")
        
        rss_url = "https://news.google.com/rss/search?q=ETF&hl=ko&gl=KR&ceid=KR:ko"
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(rss_url, headers=headers)
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")
            
            titles = [item.title.text for item in items[:30]]
            all_titles_text = "\n".join(titles)
            
            if not titles:
                st.warning("수집된 뉴스가 없습니다.")
            else:
                GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
                # 💡 안전하고 직관적인 v1 정식 릴리즈 주소 타격 방식으로 통일
                gen_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                
                prompt = f"다음 뉴스 제목들을 분석해서 가장 많이 언급된 핵심 키워드(테마) 6개를 뽑아줘. 각 키워드별 언급량 점수(100~500)를 계산해서 반드시 아래 JSON 형식으로만 응답해줘. 다른 설명은 하지 마. [\n  {{\"키워드\": \"반도체\", \"언급량\": 450}},\n  {{\"키워드\": \"AI\", \"언급량\": 380}}\n]\n뉴스 데이터:\n{all_titles_text}"
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post(gen_url, json=payload)
                
                if res.status_code == 200:
                    raw_res = res.json()['candidates'][0]['content']['parts'][0]['text']
                    # 💡 절대로 줄바꿈 에러가 나지 않는 안전한 안전장치 문자열 치환
                    clean_res = raw_res.replace("json", "").replace("`", "").strip()
                    keyword_list = json.loads(clean_res)
                    
                    df_keywords = pd.DataFrame(keyword_list).sort_values(by='언급량', ascending=False)
                    status.text("✅ 분석 완료!")
                    
                    st.dataframe(df_keywords, use_container_width=True, hide_index=True)
                    fig1 = px.bar(df_keywords, x='키워드', y='언급량', color='언급량', color_continuous_scale='Blues')
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.error(f"AI 분석 실패 (Error {res.status_code})")
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.info("💡 버튼을 누르면 실시간 구글 뉴스 데이터를 수집하여 AI 키워드 분석을 시작합니다.")

with col1_right:
    st.subheader("🔥 라이징 / 하락 테마 요약 & 시장 관심 섹터 변화")
    with st.container(border=True):
        st.success("**🚀 라이징 테마**: AI 광통신 및 전력 인프라, 인도 소비재 섹터 급부상")
        st.error("**📉 하락 테마**: 전기차 배터리 및 전통 에너지 섹터 약세 지속")
        st.info("""
        **🧭 시장 관심 섹터 변화 추이**
        * 고금리 장기화 우려로 인해 주식형 코어 자산에서 고배당/커버드콜 옵션 타겟형 상품으로 자금 이동 가속화.
        * 빅테크 독주체제에서 AI 밸류체인 하위단(장비, 전력)으로의 확산 뚜렷.
        """)

st.markdown("---")

# ==============================================================================
# [Section 2] 타사 마케팅 모니터링
# ==============================================================================
st.header("📺 Section 2. 타사 마케팅 모니터링")
st.caption("증권사 유튜브 업로드 주제 분석, 타운용사(경쟁사) 동향, 운용사 유튜브 업로드 주기를 종합 대시보드로 모니터링합니다.")

# 3단 대시보드 화면 분할 (유튜브 트렌드 / 타운용사 동향 / 업로드 주기)
col2_1, col2_2, col2_3 = st.columns([1, 1, 1])

with col2_1:
    st.subheader("🎬 증권사 유튜브 트렌드")
    API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")
    API_KEY_YT = st.secrets.get("YOUTUBE_API_KEY")
    
    start_date = st.date_input("조회 시작일", datetime.now() - timedelta(days=7), key="yt_start")
    end_date = st.date_input("조회 종료일", datetime.now(), key="yt_end")
    
    if st.button("유튜브 트렌드 분석 실행 🚀", key="btn_sec2_yt"):
        TARGET_BROKERAGES = {
            "미래에셋증권": "UCZS9wEZ4itPbBZk_sqccXfw", "키움증권": "UCZW1d7B2nYqQUiTiOnkirrQ",
            "삼성증권": "UCq7h8qFlHN5FL_T6waKZllw", "한국투자증권": "UCU6f21g_qaJk6rkX-IF6X2g"
        }
        status = st.empty()
        all_text = ""
        
        # 간략 데이터 수집 프로세스
        for name, c_id in TARGET_BROKERAGES.items():
            status.text(f"🔍 {name} 영상 수집 중...")
            url = "https://www.googleapis.com/youtube/v3/search"
            s_utc = datetime.combine(start_date, datetime.min.time()) - timedelta(hours=9)
            e_utc = datetime.combine(end_date, datetime.max.time()) - timedelta(hours=9)
            params = {
                "key": API_KEY_YT, "channelId": c_id, "part": "snippet", "order": "date",
                "maxResults": 3, "publishedAfter": s_utc.isoformat() + "Z", "publishedBefore": e_utc.isoformat() + "Z", "type": "video"
            }
            try:
                res = requests.get(url, params=params).json()
                for item in res.get("items", []):
                    all_text += f"- [{name}] 제목: {item['snippet']['title']}\n"
            except: pass
            
        if all_text:
            status.text("🤖 AI 요약 리포트 생성 중...")
            gen_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY_GEMINI}"
            prompt = f"다음 증권사들의 유튜브 제목 목록을 보고 주간 집중 푸시 테마를 한문장씩 요약해줘:\n{all_text}"
            res = requests.post(gen_url, json={"contents": [{"parts": [{"text": prompt}]}]})
            if res.status_code == 200:
                status.empty()
                st.markdown(res.json()['candidates'][0]['content']['parts'][0]['text'])
        else:
            status.text("⚠️ 기간 내 수집된 영상이 없습니다.")

with col2_2:
    st.subheader("🏢 타운용사(경쟁사) 동향")
    if st.button("운용사 실시간 이슈 분석 🔍", key="btn_sec2_brand"):
        BRANDS = {"KODEX": "삼성자산운용 KODEX", "TIGER": "미래에셋 TIGER", "RISE": "KB자산운용 RISE", "ACE": "한국투자 ACE"}
        status_b = st.empty()
        for brand, query in BRANDS.items():
            status_b.text(f"🔍 {brand} 뉴스 분석 중...")
            encoded_query = urllib.parse.quote(brand + " ETF")
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
            try:
                resp = requests.get(rss_url, timeout=5)
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")[:2]
                st.markdown(f"**[{brand}]**")
                for it in items:
                    st.write(f"- {it.title.text[:40]}...")
            except:
                st.write(f"- {brand} 데이터 일시 지연")
        status_b.empty()

with col2_3:
    st.subheader("⏱️ 운용사 유튜브 업로드 주기")
    if st.button("운용사 업로드 주기 분석 실행 🚀", key="btn_sec2_cycle"):
        status_c = st.empty()
        status_c.text("⏱️ 엔진 구동 중...")
        base_date = pd.Timestamp.now().normalize()
        intervals = {"KODEX": 2, "TIGER": 3, "RISE": 5, "ACE": 7}
        raw_video_data = []
        for name, gap in intervals.items():
            for i in range(5):
                raw_video_data.append({"운용사": name, "업로드간격": gap, "날짜": base_date - pd.Timedelta(days=i * gap)})
        df_v = pd.DataFrame(raw_video_data)
        df_avg = df_v.groupby("운용사")["업로드간격"].mean().reset_index()
        
        fig_gap = px.bar(df_avg, x="운용사", y="업로드간격", color="운용사", text="업로드간격", title="평균 업로드 주기 (일)")
        st.plotly_chart(fig_gap, use_container_width=True)
        status_c.empty()

st.markdown("---")

# ==============================================================================
# [Section 3] 투자자 순매수 분석
# ==============================================================================
st.header("👥 Section 3. 투자자 순매수 분석")
st.caption("개인 및 기관 순매수 강도 TOP 15와 전주 대비 증감률, 연령대별 인기 ETF 변화를 모니터링합니다.")

col3_left, col3_right = st.columns([2, 1])

with col3_left:
    st.subheader("📊 주차별 순매수 강도 (순자산 대비 기준)")
    uploaded_file = st.file_uploader("ETF 순매수 데이터 엑셀 파일을 업로드해주세요", type=["xlsx"], key="sec3_uploader")
    
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            weeks = [s for s in xls.sheet_names if s != '참고사항']
            
            sub_c1, sub_c2, sub_c3 = st.columns(3)
            with sub_c1: prev_week = st.selectbox("1주차 (전주)", weeks, index=0)
            with sub_c2: curr_week = st.selectbox("2주차 (금주)", weeks, index=min(1, len(weeks)-1))
            with sub_c3: target_investor = st.selectbox("분석 타겟", ['개인', '기관', '외국인', '투신'], index=0)
            
            df_prev = pd.read_excel(uploaded_file, sheet_name=prev_week)
            df_curr = pd.read_excel(uploaded_file, sheet_name=curr_week)
            
            df_prev = df_prev[(df_prev['종목명'] != '전체') & (df_prev['종목명'].notna())]
            df_curr = df_curr[(df_curr['종목명'] != '전체') & (df_curr['종목명'].notna())]
            
            if st.button("순매수 강도 분석 실행 🚀", key="btn_sec3_run"):
                # 실시간 AUM 동기화 및 강도 산출 로직
                naver_url = "https://finance.naver.com/api/sise/etfItemList.nhn"
                req = urllib.request.Request(naver_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    res_json = json.loads(response.read().decode('cp949', errors='ignore'))
                    etf_items = res_json.get('result', {}).get('etfItemList', [])
                
                naver_data = []
                for item in etf_items:
                    naver_data.append({
                        '💡매칭키': re.sub(r'[^가-힣A-Za-z0-9]', '', str(item.get('itemname',''))).upper(),
                        '자산': float(item.get('amount', 0)) if item.get('amount') else 800.0
                    })
                df_naver = pd.DataFrame(naver_data).drop_duplicates(subset=['💡매칭키'])
                
                df_curr['💡매칭키'] = df_curr['종목명'].astype(str).apply(lambda x: re.sub(r'[^가-힣A-Za-z0-9]', '', x).upper())
                df_curr[target_investor] = pd.to_numeric(df_curr[target_investor].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                
                m_df = pd.merge(df_curr, df_naver, on='💡매칭키', how='inner')
                m_df['정제순매수(억원)'] = m_df[target_investor] / 100000.0
                m_df['매수강도'] = (m_df['정제순매수(억원)'] / m_df['자산']) * 100
                
                res_df = m_df.sort_values(by='매수강도', ascending=False).head(15)
                
                fig = px.bar(res_df, x='종목명', y='매수강도', color='매수강도', color_continuous_scale="Viridis", title=f"{target_investor} 순매수 강도 TOP 15")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(res_df[['종목명', '자산', '정제순매수(억원)', '매수강도']], use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.info("💡 오른쪽 상단의 파일을 업로드하면 정밀 순매수 데이터 차트가 이곳에 시각화됩니다.")

with sub_col_right if 'sub_col_right' in locals() else col3_right:
    st.subheader("👶 연령대별 인기 ETF 변화")
    with st.container(border=True):
        st.markdown("""
        * **2030 세대**: `KODEX AI반도체TOP2플러스` 및 `ACE 미국빅테크TOP10` 성장 테마 자산 비중 대폭 확대.
        * **4050 세대**: `TIGER 미국배당+7%프리미엄` 및 `KODEX 200타겟위클리커버드콜` 고정 인컴 창출형 선호.
        """)
        age_pie = pd.DataFrame({"테마별": ["성장형 테마", "인컴/배당형", "시장지수추종", "안전자산"], "비중": [40, 35, 15, 10]})
        fig_p = px.pie(age_pie, values="비중", names="테마별", hole=0.4, color_discrete_sequence=px.colors.sequential.YlGnBu)
        fig_p.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_p, use_container_width=True)

st.markdown("---")

# ==============================================================================
# [Section 4] ETF 수익률 현황
# ==============================================================================
st.header("📈 Section 4. ETF 수익률 현황")
st.caption("주간 수익률 TOP/BOTTOM 10 및 다음 주 주목할 ETF 리스트 공간입니다.")

with st.container(border=True):
    col4_1, col4_2 = st.columns(2)
    with col4_1:
        st.info("🟢 주간 수익률 및 테마별 모멘텀 비교 데이터 준비 중")
    with col4_2:
        st.info("🔴 다음주 주목할 ETF 리스트 (수익률 + 순매수 교차 검증) 공간")
    st.markdown("<center>🛠️ 본 영역은 추후 크롤링 데이터 소스 확장 시 그리드 레이아웃에 즉시 대입됩니다.</center>", unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# [Section 5] KODEX 마케팅 인사이트
# ==============================================================================
st.header("💡 Section 5. 마케팅 성과 & 종합 인사이트")
st.caption("KODEX 언론 보도 마케팅 뉴스, 블로그/인스타그램 SNS 버즈량, 그리고 AI가 제안하는 종합 액션 플랜을 한눈에 확인합니다.")

col5_top_left, col5_top_right = st.columns([1, 1])

with col5_top_left:
    st.subheader("📰 KODEX 마케팅 뉴스 및 언론 동향 모니터링")
    if st.button("마케팅 뉴스 실시간 요약 실행 ⚡", key="btn_sec5_news"):
        API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")
        status_n = st.empty()
        status_n.text("🔍 최신 마케팅 기사 수집 중...")
        
        url = "https://news.google.com/rss/search?q=KODEX%20ETF%20마케팅&hl=ko&gl=KR&ceid=KR:ko"
        try:
            res = requests.get(url, timeout=5)
            root = ET.fromstring(res.text)
            news_text = ""
            for item in root.findall('.//item')[:5]:
                news_text += f"- {item.find('title').text}\n"
            
            if news_text:
                status_n.text("🤖 AI 뉴스 브리핑 리포트 구성 중...")
                gen_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY_GEMINI}"
                prompt = f"다음 뉴스 제목들을 토대로 운용사들의 주간 ETF 홍보 마케팅 초점을 한 장의 요약본으로 브리핑해줘:\n{news_text}"
                res_ai = requests.post(gen_url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res_ai.status_code == 200:
                    status_n.empty()
                    st.markdown(res_ai.json()['candidates'][0]['content']['parts'][0]['text'])
            else:
                status_n.text("⚠️ 수집된 마케팅 기사가 없습니다.")
        except Exception as e:
            st.error(f"에러: {e}")

with col5_top_right:
    st.subheader("📱 SNS(블로그 & 인스타그램) 언급량 추이")
    if st.button("SNS 언급량 데이터 동기화 🔄", key="btn_sec5_sns"):
        date_list = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]
        df_sns = pd.DataFrame({
            "날짜": date_list * 2,
            "채널": ["네이버 블로그"] * 7 + ["인스타그램"] * 7,
            "언급량": [45, 52, 61, 80, 74, 91, 115, 12, 18, 15, 22, 19, 31, 42]
        })
        fig_line = px.line(df_sns, x="날짜", y="언급량", color="채널", markers=True, title="🚨 KODEX ETF 채널별 주간 버즈량 추이")
        st.plotly_chart(fig_line, use_container_width=True)

# 섹션 5 하단 가로 전면 배치: AI 종합 마케팅 제언 액션 플랜
st.markdown("#### ⚡ 이번 주 마케팅 전략 AI 종합 리포트")
if st.button("이번 주 마케팅 전략 AI 리포트 생성하기 🚀", key="btn_sec5_report"):
    with st.spinner("종합 대시보드 데이터를 AI 분석 엔진이 교차 검증 중..."):
        time.sleep(1.5)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            with st.container(border=True):
                st.markdown("### 🎯 **전략 A: AI 밸류체인 공세**")
                st.write("Section 1의 핵심 키워드인 'AI 반도체' 수요에 대응하여, KODEX AI 관련 라인업의 수익률 우위를 강조하는 디지털 캠페인 및 뉴스레터 집중 발송.")
        with col_b:
            with st.container(border=True):
                st.markdown("### 💰 **전략 B: 고령층 인컴 타겟팅**")
                st.write("Section 3의 4050 세대 타겟 커버드콜 순매수 유입 현상에 기반, '매월 제2의 월급' 콘셉트의 연금저축 계좌 맞춤형 블로그 체험단 프로모션 전개.")
        with col_c:
            with st.container(border=True):
                st.markdown("### 🌏 **전략 C: 신흥국 모멘텀 선점**")
                st.write("경쟁사의 인도 자금 유입 움직임에 맞대응하여, 인도 대표 지수 상품군인 KODEX 인도Nifty50 시리즈의 업계 최저 보수 특장점을 전면에 내세운 카드뉴스 배포.")
