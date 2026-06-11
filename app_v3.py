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
            res = requests.post(gen_url, json={"contents
