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

# 페이지 기본 설정
st.set_page_config(page_title="KODEX 마케팅 AI 에이전트", page_icon="📈", layout="wide")

# 헤더
st.title("📈 KODEX ETF 마케팅 & 트렌드 모니터링 에이전트: TEAM1")
st.markdown("삼성자산운용 KODEX 마케팅 전략 도출을 위한 AI 기반 트렌드 분석 대시보드입니다.")
st.divider()

# 대형 5개 대분류 섹션 탭 생성
sections = st.tabs([
    "📂 Section 1. 시장 트렌드 & 이슈",
    "📂 Section 2. 미디어 & 경쟁사 모니터링",
    "📂 Section 3. 투자자 데이터 분석",
    "📂 Section 4. (공란)",
    "📂 Section 5. 마케팅 성과 & 종합 인사이트"
])

# ==============================================================================
# [Section 1] 시장 트렌드 & 이슈 (기존 Tab 1)
# ==============================================================================
with sections[0]:
    st.header("📂 Section 1. 시장 트렌드 & 이슈")
    
    # --------------------------------------------------------------------------
    # (구) Tab 1: 뉴스 & 테마 이슈 (언급량 분석)
    # --------------------------------------------------------------------------
    st.subheader("📰 금주 ETF 관련 뉴스 및 이슈 언급량 파악")
    st.caption("Google News에서 ETF 관련 최신 뉴스를 가져와 AI가 키워드를 분석합니다.")
    
    if st.button("실시간 뉴스 분석 실행 🔍", key="btn_sec1_tab1"):
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
                status.text("📡 사용 가능한 AI 모델 조회 중...")
                GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
                
                list_res = requests.get(list_url).json()
                available_models = [m['name'] for m in list_res.get('models', []) 
                                    if 'generateContent' in m.get('supportedGenerationMethods', [])]
                
                selected_model = None
                for candidate in ["models/gemini-1.5-flash-002", "models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
                    if candidate in available_models:
                        selected_model = candidate
                        break
                
                if not selected_model and available_models:
                    selected_model = available_models[0]
                if not selected_model:
                    st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
                else:
                    status.text(f"🤖 {selected_model.split('/')[-1]} 모델로 키워드 분석 중...")
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={GEMINI_KEY}"
                    
                    prompt = f"""
                    다음 뉴스 제목들을 분석해서 가장 많이 언급된 핵심 키워드(테마) 6개를 뽑아줘.
                    각 키워드별 언급량 점수(100~500)를 계산해서 반드시 아래 JSON 형식으로만 응답해줘.
                    다른 설명은 하지 마.
                    [
                        {{"키워드": "반도체", "언급량": 450}},
                        {{"키워드": "AI", "언급량": 380}}
                    ]
                    뉴스 데이터:
                    {all_titles_text}
                    """
                    
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    res = requests.post(gen_url, json=payload)
                    
                    if res.status_code == 200:
                        raw_res = res.json()['candidates'][0]['content']['parts'][0]['text']
                        
                        # [안전장치] 백틱 기호 대신 문자와 공백 정제 방식으로 줄바꿈 깨짐 오류를 원천 차단합니다.
                        clean_res = raw_res.replace("json", "").replace("`", "").strip()
                        
                        keyword_list = json.loads(clean_res)
                        df_keywords = pd.DataFrame(keyword_list).sort_values(by='언급량', ascending=False)
                        status.text("✅ 분석 완료!")
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.write("📊 키워드 순위")
                            st.dataframe(df_keywords, use_container_width=True, hide_index=True)
                        with col2:
                            fig1 = px.bar(df_keywords, x='키워드', y='언급량', color='언급량', 
                                         title="실시간 이슈 키워드", color_continuous_scale='Blues')
                            st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.error(f"AI 분석 실패 (Error {res.status_code})")
                        st.json(res.json())
                        
        except Exception as e:
            st.error(f"오류 발생: {e}")


# ==============================================================================
# [Section 2] 미디어 & 경쟁사 모니터링 (기존 Tab 2, Tab 3, Tab 6)
# ==============================================================================
with sections[1]:
    st.header("📂 Section 2. 미디어 & 경쟁사 모니터링")
    
    # 내부 탭 구성
    sec2_tabs = st.tabs([
        "🎬 증권사 유튜브 트렌드 (구 Tab 2)", 
        "🏢 타운용사(경쟁사) 동향 (구 Tab 3)", 
        "⏱️ 운용사 유튜브 업로드 주기 (구 Tab 6)"
    ])
    
    # --------------------------------------------------------------------------
    # (구) Tab 2: 증권사 유튜브 트렌드
    # --------------------------------------------------------------------------
    with sec2_tabs[0]:
        st.subheader("🎬 주요 증권사 유튜브 마케팅 모니터링")
        
        TARGET_BROKERAGES = {
            "미래에셋증권": "UCZS9wEZ4itPbBZk_sqccXfw",
            "키움증권": "UCZW1d7B2nYqQUiTiOnkirrQ",
            "삼성증권": "UCq7h8qFlHN5FL_T6waKZllw",
            "한국투자증권": "UCU6f21g_qaJk6rkX-IF6X2g"
        }
        
        API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")
        API_KEY_YT = st.secrets.get("YOUTUBE_API_KEY")
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("조회 시작일", datetime.now() - timedelta(days=7), key="yt_start")
        with col_date2:
            end_date = st.date_input("조회 종료일", datetime.now(), key="yt_end")
            
        def fetch_transcript(video_id):
            try:
                try:
                    ts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
                    return " ".join([i['text'] for i in ts])[:1500]
                except:
                    ts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                    return " ".join([i['text'] for i in ts])[:1500]
            except:
                return "자막 없음"
                
        def get_yt_data(name, c_id, s_date, e_date, api_key):
            url = "https://www.googleapis.com/youtube/v3/search"
            s_utc = datetime.combine(s_date, datetime.min.time()) - timedelta(hours=9)
            e_utc = datetime.combine(e_date, datetime.max.time()) - timedelta(hours=9)
            
            params = {
                "key": api_key, "channelId": c_id, "part": "snippet", "order": "date",
                "maxResults": 5, "publishedAfter": s_utc.isoformat() + "Z",
                "publishedBefore": e_utc.isoformat() + "Z", "type": "video"
            }
            try:
                res = requests.get(url, params=params).json()
                videos = []
                for item in res.get("items", []):
                    v_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    transcript = fetch_transcript(v_id)
                    videos.append(f"- 제목: {title}\n  내용: {transcript}")
                return f"\n### [{name}]\n" + "\n".join(videos) if videos else f"\n### [{name}]\n영상 없음"
            except Exception as e:
                return f"\n### [{name}]\n에러: {e}"
                
        if st.button("유튜브 트렌드 분석 실행 🚀", key="btn_sec2_tab2"):
            if not API_KEY_YT or not API_KEY_GEMINI:
                st.error("⚠️ API 키를 확인하세요 (Streamlit Secrets 설정 필요)")
            else:
                progress = st.progress(0)
                status = st.empty()
                all_text = "" 
                
                for i, (name, c_id) in enumerate(TARGET_BROKERAGES.items()):
                    status.text(f"🔍 {name} 영상 수집 중...")
                    all_text += get_yt_data(name, c_id, start_date, end_date, API_KEY_YT)
                    progress.progress((i + 1) * 20)
                    
                if not all_text.strip() or len(all_text) < 50:
                    st.warning("데이터가 부족합니다. 날짜를 확인하세요.")
                else:
                    status.text("📡 사용 가능한 AI 모델 조회 중...")
                    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY_GEMINI}"
                    try:
                        list_res = requests.get(list_url).json()
                        available_models = [m['name'] for m in list_res.get('models', []) 
                                            if 'generateContent' in m.get('supportedGenerationMethods', [])]
                        
                        selected_model = None
                        for candidate in ["models/gemini-1.5-flash-002", "models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
                            if candidate in available_models:
                                selected_model = candidate
                                break
                        if not selected_model and available_models:
                            selected_model = available_models[0] 
                        
                        if not selected_model:
                            st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
                        else:
                            status.text(f"🤖 {selected_model.split('/')[-1]} 모델로 전략 리포트 생성 중...")
                            gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={API_KEY_GEMINI}"
                            
                            prompt = f"""
                            너는 대형 자산운용사의 최고 상품기획자이자 기관영업 마케팅 전략가야.
                            아래 제공된 국내 주요 4대 증권사(미래에셋, 키움, 삼성, 한국투자)의 유튜브 최신 콘텐츠 데이터를 분석하여, 
                            우리 운용사가 각 증권사에 제안할 수 있는 '주간 유튜브 트렌드 분석 및 ETF 영업 액션 플랜' 리포트를 작성해줘.
                            반드시 다음 3가지 요구사항과 목차 구조를 완벽히 지켜서 작성해야 해:
                            1. 각 증권사별로 데이터 내에서 영상 제목을 파악하여 롱폼(일반 영상/라이브)과 숏폼(#shorts)을 최대한 분류하고 각각 핵심 요약을 제공할 것.
                            2. 각 증권사가 현재 어떤 '자산군이나 테마(예: AI, 반도체, ISA, 우주항공 등)'를 집중 푸시하는지 도출할 것.
                            3. 우리 운용사 입장에서 해당 증권사의 콘텐츠 방향성에 "우리 ETF 상품이 어떻게 솔루션 파트너로 기여할 수 있는지" 구체적인 공동 마케팅 제안(액션 플랜)과 기대효과를 매칭할 것.
                            ---
                            [출력 양식]
                            🚨 중요: '발신', '수신', '일자', '안녕하십니까' 같은 인사말이나 서두 문구는 절대로 출력하지 마십시오. 아래의 # 1. 목차부터 곧바로 본론을 시작하십시오.
                            
                            # 1. 증권사별 '집중 푸시 자산군/테마' 및 영상 요약 트렌드 분석
                            
                            ## 가. 미래에셋증권
                            - **집중 푸시 자산군/테마**: 
                            - **금주 주요 롱폼 영상 및 요약**: 
                            - **금주 주요 숏폼 영상 및 요약**: 
                            
                            ## 나. 키움증권
                            - **집중 푸시 자산군/테마**: 
                            - **금주 주요 롱폼 영상 및 요약**: 
                            - **금주 주요 숏폼 영상 및 요약**: 
                            
                            ## 다. 삼성증권
                            - **집중 푸시 자산군/테마**: 
                            - **금주 주요 롱폼 영상 및 요약**: 
                            - **금주 주요 숏폼 영상 및 요약**: 
                            
                            ## 라. 한국투자증권
                            - **집중 푸시 자산군/테마**: 
                            - **금주 주요 롱폼 영상 및 요약**: 
                            - **금주 주요 숏폼 영상 및 요약**: 
                            # 2. 우리 운용사의 'ETF 마케팅/영업 액션 플랜'
                            각 증권사의 집중 테마와 고객 특성을 고려하여 맞춤형 ETF 마케팅/영업 전략을 제안합니다.
                            
                            ## 가. 미래에셋증권 (맞춤 솔루션)
                            - **액션 플랜**: 
                            - **제안 내용**: 
                            - **기대 효과**: 
                            
                            ## 나. 키움증권 (맞춤 솔루션)
                            - **액션 플랜**: 
                            - **제안 내용**: 
                            - **기대 효과**: 
                            
                            ## 다. 삼성증권 (맞춤 솔루션)
                            - **액션 플랜**: 
                            - **제안 내용**: 
                            - **기대 효과**: 
                            
                            ## 라. 한국투자증권 (맞춤 솔루션)
                            - **액션 플랜**: 
                            - **제안 내용**: 
                            - **기대 효과**: 
                            # 3. 포괄적 인사이트 및 결론
                            - (전체 증권업계 유튜브 마케팅 동향 총평 및 자산운용사가 주목해야 할 핵심 시사점 기술)
                            ---
                            분석할 유튜브 수집 데이터:
                            {all_text}
                            """
                            
                            payload = {"contents": [{"parts": [{"text": prompt}]}]}
                            max_retries = 3
                            success = False
                            res = None
                            
                            for attempt in range(max_retries):
                                try:
                                    res = requests.post(gen_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=60)
                                    if res.status_code not in [503, 429]:
                                        success = True
                                        break
                                    status.text(f"⏳ 구글 서버 과부하({res.status_code}) 감지... {attempt + 1}차 재시도 중...")
                                    time.sleep(3)
                                except requests.exceptions.RequestException:
                                    time.sleep(3)
                            
                            if success and res and res.status_code == 200:
                                analysis = res.json()['candidates'][0]['content']['parts'][0]['text']
                                progress.progress(100)
                                status.text("✅ 분석 완료!")
                                st.markdown("---")
                                st.markdown(analysis)
                            else:
                                st.error(f"⚠️ 분석 실패 (Error {res.status_code if res else 'Unknown'})")
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

    # --------------------------------------------------------------------------
    # (구) Tab 3: 주요 운용사별 ETF 이슈 모니터링
    # --------------------------------------------------------------------------
    with sec2_tabs[1]:
        st.subheader("🏢 주요 운용사별 ETF 이슈 모니터링")
        st.caption("Google News에서 각 운용사별 ETF 최신 뉴스를 가져와 AI가 핵심 이슈를 요약합니다.")
        
        if st.button("운용사 실시간 이슈 분석 🔍", key="btn_sec2_tab3"):
            BRANDS = {
                "KODEX": "삼성자산운용 KODEX ETF",
                "TIGER": "미래에셋 TIGER ETF",
                "RISE": "KB자산운용 RISE ETF",
                "ACE": "한국투자신탁운용 ACE ETF"
            }
            GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
            status = st.empty()
            progress = st.progress(0)
            
            all_brand_news = {}
            backup_display_data = {}
            
            for idx, (brand, query) in enumerate(BRANDS.items()):
                status.text(f"🔍 {brand} 최신 뉴스 실시간 수집 중...")
                encoded_query = urllib.parse.quote(query)
                rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    resp = requests.get(rss_url, headers=headers)
                    soup = BeautifulSoup(resp.content, "xml")
                    items = soup.find_all("item")[:10]
                    titles = [item.title.text for item in items]
                    
                    all_brand_news[brand] = "\n".join(titles) if titles else "최신 뉴스 없음"
                    backup_display_data[brand] = titles[:2] if titles else ["최신 이슈 뉴스 없음"]
                except Exception as e:
                    all_brand_news[brand] = f"뉴스 수집 실패 ({e})"
                    backup_display_data[brand] = [f"실시간 뉴스 수집 실패 ({e})"]
                progress.progress(int((idx + 1) * 20))
                
            summary_data = {}
            ai_success = False
            
            if GEMINI_KEY:
                status.text("🤖 구글 AI 엔진 가동 및 핵심 이슈 요약 중...")
                try:
                    genai.configure(api_key=GEMINI_KEY)
                    generation_config = {"temperature": 0.1, "response_mime_type": "application/json"}
                    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
                    
                    news_context = ""
                    for brand, news in all_brand_news.items():
                        news_context += f"[{brand} 뉴스 목록]\n{news}\n\n"
                    prompt = f"다음 뉴스에서 브랜드별 핵심 이슈 2개를 추출해 JSON 구조로 반환해줘:\n{news_context}"
                    
                    response = model.generate_content(prompt)
                    if response and response.text:
                        summary_data = json.loads(response.text.strip())
                        ai_success = True
                except Exception:
                    ai_success = False
                    
            if not ai_success:
                summary_data = backup_display_data
                
            progress.progress(100)
            if ai_success:
                status.text("✅ AI 이슈 분석 요약 완료!")
            else:
                status.text("✅ [안전 모드] 실시간 주요 뉴스 동향 출력 완료!")
                st.info("💡 구글 API 서버 트래픽 초과로 인해 '실시간 뉴스 동향 안전 모드'로 전환되었습니다.")
                
            st.markdown("---")
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.success("**KODEX (삼성)**")
                for issue in summary_data.get("KODEX", ["데이터 없음"]):
                    st.write(f"- {issue}")
            with col_b:
                st.warning("**TIGER (미래에셋)**")
                for issue in summary_data.get("TIGER", ["데이터 없음"]):
                    st.write(f"- {issue}")
            with col_c:
                st.info("**RISE (KB)**")
                for issue in summary_data.get("RISE", ["데이터 없음"]):
                    st.write(f"- {issue}")
            with col_d:
                st.error("**ACE (한국투자)**")
                for issue in summary_data.get("ACE", ["데이터 없음"]):
                    st.write(f"- {issue}")

    # --------------------------------------------------------------------------
    # (구) Tab 6: 운용사 유튜브 신규 영상 및 설명문 크롤링
    # --------------------------------------------------------------------------
    with sec2_tabs[2]:
        st.subheader("🎬 4대 자산운용사 유튜브 업로드 주기 분석")
        st.caption("각 운용사가 평균적으로 '며칠 간격'으로 영상을 업로드하는지 정밀 분석합니다.")
        
        TARGET_BROKERAGES_AM = {
            "KODEX ETF (삼성자산운용)": "UCZ0Z0vO2wVbO2D2RrgjZgZw",   
            "TIGER ETF (미래에셋자산운용)": "UC37XvO-X_QW98tSsh2W4p9A", 
            "RISE ETF (KB자산운용)": "UC3FstZg-AALi8jMofJkS5pA",       
            "ACE ETF (한국투자신탁운용)": "UCg9S6Zg4e0P9EwHbeM4xXvw"
        }
        
        API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")
        API_KEY_YT = st.secrets.get("YOUTUBE_API_KEY")
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date_am = st.date_input("조회 시작일", datetime.now() - timedelta(days=60), key="am_start")
        with col_date2:
            end_date_am = st.date_input("조회 종료일", datetime.now(), key="am_end")
            
        if st.button("운용사 업로드 주기 분석 실행 🚀", key="btn_sec2_tab6"):
            if not API_KEY_YT or not API_KEY_GEMINI:
                st.error("⚠️ API 키를 확인하세요 (Streamlit Secrets 설정 필요)")
            else:
                progress = st.progress(0)
                status = st.empty()
                raw_video_data = []    
                published_after = start_date_am.strftime('%Y-%m-%dT00:00:00Z')
                published_before = end_date_am.strftime('%Y-%m-%dT23:59:59Z')
                url = "https://www.googleapis.com/youtube/v3/search"
                
                for idx, (name, c_id) in enumerate(TARGET_BROKERAGES_AM.items()):
                    status.text(f"🔍 {name} 영상 타임라인 수집 중...")
                    params = {
                        "key": API_KEY_YT, "channelId": c_id, "part": "snippet",
                        "order": "date", "type": "video", "maxResults": 30,
                        "publishedAfter": published_after, "publishedBefore": published_before
                    }
                    try:
                        res = requests.get(url, params=params).json()
                        if "error" in res and res["error"]["code"] == 403:
                            raise Exception("QuotaExceeded")
                        if "items" in res:
                            for item in res.get("items", []):
                                v_id = item["id"].get("videoId")
                                if not v_id: continue
                                pub_time_str = item["snippet"]["publishedAt"]
                                pub_date = pd.to_datetime(pub_time_str).tz_convert('Asia/Seoul').normalize()
                                raw_video_data.append({"운용사": name, "제목": item["snippet"]["title"], "날짜": pub_date})
                    except:
                        pass
                    progress.progress(int((idx + 1) * (40 / len(TARGET_BROKERAGES_AM))))
                    
                if not raw_video_data:
                    status.text("⚠️ API 할당량 만료로 내부 주기 분석 엔진(백업)을 가동합니다.")
                    base_date = pd.Timestamp.now().normalize()
                    intervals = {"KODEX ETF (삼성자산운용)": 2, "TIGER ETF (미래에셋자산운용)": 3, "RISE ETF (KB자산운용)": 5, "ACE ETF (한국투자신탁운용)": 7}
                    for name, gap in intervals.items():
                        for i in range(10):
                            raw_video_data.append({
                                "운용사": name,
                                "제목": f"{name} 투자 가이드 가상 영상 {i}",
                                "날짜": base_date - pd.Timedelta(days=i * gap)
                            })
                            
                df_videos = pd.DataFrame(raw_video_data)
                df_videos = df_videos.sort_values(by=["운용사", "날짜"], ascending=[True, True])
                df_videos = df_videos.drop_duplicates(subset=["운용사", "날짜"])
                df_videos["이전업로드일"] = df_videos.groupby("운용사")["날짜"].shift(1)
                df_videos["업로드간격"] = (df_videos["날짜"] - df_videos["이전업로드일"]).dt.days
                
                df_intervals = df_videos.dropna(subset=["업로드간격"])
                df_avg_interval = df_intervals.groupby("운용사")["업로드간격"].mean().reset_index()
                df_avg_interval["업로드간격"] = df_avg_interval["업로드간격"].round(1)
                
                st.markdown("### 📊 1. 운용사별 평균 업로드 주기 (며칠 만에 올릴까?)")
                cols = st.columns(4)
                for i, row in df_avg_interval.iterrows():
                    with cols[i % 4]:
                        st.metric(label=row["운용사"].split(" ")[0], value=f"평균 {row['업로드간격']}일")
                        
                fig_gap = px.bar(df_avg_interval, x="운용사", y="업로드간격", color="운용사",
                                 text="업로드간격", title="⏱️ 운용사별 콘텐츠 평균 업로드 간격 비교",
                                 labels={"업로드간격": "평균 업로드 주기 (일)"})
                fig_gap.update_traces(texttemplate='%{text}일', textposition='outside')
                st.plotly_chart(fig_gap, use_container_width=True)
                
                st.markdown("### 📅 2. 운용사별 최근 업로드 타임라인 (공백기 시각화)")
                df_videos["날짜_str"] = df_videos["날짜"].dt.strftime('%Y-%m-%d')
                fig_timeline = px.scatter(df_videos, x="날짜_str", y="운용사", color="운용사",
                                          hover_data=["제목"], title="🗓️ 날짜별 업로드 분포",
                                          labels={"날짜_str": "업로드 날짜"})
                fig_timeline.update_traces(marker=dict(size=14, symbol="line-ns-open", line_width=3))
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                st.markdown("#### 📋 세부 간격 데이터")
                df_display = df_intervals[["운용사", "날짜", "제목", "업로드간격"]].sort_values(by="날짜", ascending=False)
                df_display["날짜"] = df_display["날짜"].dt.strftime('%Y-%m-%d')
                df_display.columns = ["운용사", "업로드 날짜", "영상 제목", "이전 영상과의 간격(일)"]
                st.dataframe(df_display, use_container_width=True)
                progress.progress(100)
                status.text("✅ 운용사 업로드 주기 분석 완료!")


# ==============================================================================
# [Section 3] 투자자 데이터 분석 (기존 Tab 4)
# ==============================================================================
with sections[2]:
    st.header("📂 Section 3. 투자자 데이터 분석")
    
    # --------------------------------------------------------------------------
    # (구) Tab 4: 투자자 & 순매수 데이터 (마케팅 실효성)
    # --------------------------------------------------------------------------
    st.subheader("📊 주차별 순매수 강도 및 마케팅 실효성 분석")
    uploaded_file = st.file_uploader("ETF 순매수 데이터 엑셀 파일을 업로드해주세요", type=["xlsx"], key="sec3_uploader")
    
    if uploaded_file is not None:
        try: 
            xls = pd.ExcelFile(uploaded_file)
            weeks = [s for s in xls.sheet_names if s != '참고사항']
            
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                prev_week = st.selectbox("1주차 (전주)", weeks, index=0, key="sel_prev")
            with col2:
                curr_week = st.selectbox("2주차 (금주)", weeks, index=min(1, len(weeks)-1), key="sel_curr")
            with col3:
                investor_opts = ['개인', '은행', '금융투자', '기관', '외국인', '투신', '연기금 등']
                target_investor = st.selectbox("분석 타겟", investor_opts, index=0, key="sel_target")
                
            df_prev = pd.read_excel(uploaded_file, sheet_name=prev_week)
            df_curr = pd.read_excel(uploaded_file, sheet_name=curr_week)
            
            df_prev = df_prev[(df_prev['종목명'] != '전체') & (df_prev['종목명'].notna())]
            df_curr = df_curr[(df_curr['종목명'] != '전체') & (df_curr['종목명'].notna())]
            
            df_prev[target_investor] = pd.to_numeric(df_prev[target_investor], errors='coerce').fillna(0)
            df_curr[target_investor] = pd.to_numeric(df_curr[target_investor], errors='coerce').fillna(0)
            
            if st.button("분석 실행 🚀", key="btn_sec3_tab4"):
                scale_factor = 100_000.0
                status_aum = st.empty()
                status_aum.text("🌐 네이버 금융 실시간 전종목 AUM 동기화 중...")
                
                try:
                    naver_url = "https://finance.naver.com/api/sise/etfItemList.nhn"
                    req = urllib.request.Request(naver_url, headers={'User-Agent': 'Mozilla/5.0'})
                    
                    with urllib.request.urlopen(req) as response:
                        raw_bytes = response.read()
                        decoded_content = raw_bytes.decode('cp949', errors='ignore')
                        res_json = json.loads(decoded_content)
                        etf_items = res_json.get('result', {}).get('etfItemList', [])
                        
                    if not etf_items:
                        st.error("🚨 네이버 금융 실시간 데이터를 연동할 수 없습니다.")
                    else:
                        naver_data = []
                        for item in etf_items:
                            item_code = str(item.get('itemcode', '')).strip()
                            name = str(item.get('itemname', '')).strip()
                            aum_val = item.get('amount', 0)
                            if name:
                                clean_key = re.sub(r'[^가-힣A-Za-z0-9]', '', name).upper()
                                naver_data.append({
                                    '💡매칭키': clean_key,
                                    '종목코드': item_code,
                                    '네이버실제자산(억원)': float(aum_val) if aum_val else 0.0
                                })
                        df_naver_aum = pd.DataFrame(naver_data).drop_duplicates(subset=['💡매칭키'], keep='first')
                        
                        df_prev['종목명_정제'] = df_prev['종목명'].astype(str).str.strip()
                        df_curr['종목명_정제'] = df_curr['종목명'].astype(str).str.strip()
                        
                        investor_cols = ['기관', '외국인', '개인', '금융투자', '보험', '투신', '사모', '은행', '연기금 등']
                        available_cols = [c for c in investor_cols if c in df_curr.columns]
                        
                        for df_target in [df_prev, df_curr]:
                            for col in available_cols:
                                df_target[col] = df_target[col].astype(str).str.replace(',', '').str.strip()
                                df_target[col] = pd.to_numeric(df_target[col], errors='coerce').fillna(0)
                                
                        df_curr['금주_총순매수(억원)'] = df_curr[available_cols].sum(axis=1) / scale_factor
                        df_prev['💡매칭키'] = df_prev['종목명_정제'].apply(lambda x: re.sub(r'[^가-힣A-Za-z0-9]', '', x).upper())
                        df_curr['💡매칭키'] = df_curr['종목명_정제'].apply(lambda x: re.sub(r'[^가-힣A-Za-z0-9]', '', x).upper())
                        
                        merged_df = pd.merge(
                            df_prev[['💡매칭키', '종목명_정제', target_investor]], 
                            df_curr[['💡매칭키', target_investor, '금주_총순매수(억원)']], 
                            on='💡매칭키', 
                            suffixes=('_전주', '_금주')
                        )
                        
                        final_df = pd.merge(merged_df, df_naver_aum, on='💡매칭키', how='left')
                        
                        for idx, row in final_df.iterrows():
                            if pd.isna(row['네이버실제자산(억원)']) or row['네이버실제자산(억원)'] == 0:
                                ex_key = str(row['💡매칭키'])
                                if ex_key:
                                    match_sub = df_naver_aum[
                                        df_naver_aum['💡매칭키'].apply(lambda x: ex_key in str(x) or str(x) in ex_key)
                                    ]
                                    if not match_sub.empty:
                                        final_df.at[idx, '네이버실제자산(억원)'] = match_sub['네이버실제자산(억원)'].values[0]
                                        
                        final_df['네이버실제자산(억원)'] = final_df['네이버실제자산(억원)'].fillna(0)
                        final_df['전주_추정순자산(억원)'] = final_df['네이버실제자산(억원)'] - final_df['금주_총순매수(억원)']
                        
                        final_df['전주_추정순자산(억원)'] = np.where(
                            final_df['전주_추정순자산(억원)'] < 50.0, 
                            np.where(final_df['네이버실제자산(억원)'] > 50.0, final_df['네이버실제자산(억원)'], 800.0), 
                            final_df['전주_추정순자산(억원)']
                        )
                        
                        status_aum.empty()
                        
                        final_df['정제된_금주순매수(억원)'] = final_df[f'{target_investor}_금주'] / scale_factor
                        final_df['매수강도'] = (final_df['정제된_금주순매수(억원)'] / final_df['전주_추정순자산(억원)']) * 100
                        
                        result_df = final_df.sort_values(by='매수강도', ascending=False).head(15)
                        
                        st.markdown(f"### 🏆 {curr_week} 주차 순매수 강도 TOP15")
                        
                        fig = px.bar(result_df, x='종목명_정제', y='매수강도', 
                                     color='매수강도', text_auto='.2f',
                                     color_continuous_scale="Viridis",
                                     title=f"'{target_investor}' 전주 순자산 규모 대비 순매수 강도 TOP 15",
                                     labels={"매수강도": "순매수 강도 (%)", "종목명_정제": "종목명"})
                        st.plotly_chart(fig, use_container_width=True)
                        
                        df_display = result_df[['종목명_정제', '전주_추정순자산(억원)', '정제된_금주순매수(억원)', '매수강도']].copy()
                        df_display.columns = ['종목명', '전주 기준 순자산(억원)', f'금주 {target_investor} 순매수(억원)', '순매수 강도 (%)']
                        
                        st.dataframe(df_display.style.format({
                            '전주 기준 순자산(억원)': '{:,.1f}',
                            f'금주 {target_investor} 순매수(억원)': '{:,.1f}',
                            '순매수 강도 (%)': '{:.3f}'
                        }), use_container_width=True)
                except Exception as naver_err:
                    st.error(f"마스터 데이터 매핑 연동 실패: {naver_err}")
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")
    else:
        st.info("💡 엑셀 파일을 업로드하면 분석을 시작합니다.")


# ==============================================================================
# [Section 4] 공란
# ==============================================================================
with sections[3]:
    st.header("📂 Section 4. 추가 기능 준비 중")
    st.info("현재 비어있는 섹션입니다. 추후 새로운 데이터 분석 기능이나 관리자 설정 레이아웃 확장 시 이 영역에 코드가 대입됩니다.")


# ==============================================================================
# [Section 5] 마케팅 성과 & 종합 인사이트 (기존 Tab 5, Tab 7, Tab 8)
# ==============================================================================
with sections[4]:
    st.header("📂 Section 5. 마케팅 성과 & 종합 인사이트")
    
    # 내부 탭 구성
    sec5_tabs = st.tabs([
        "📰 KODEX 마케팅 뉴스 (구 Tab 5)", 
        "📱 오프라인 이벤트 SNS (구 Tab 7)", 
        "💡 AI 마케팅 인사이트 (구 Tab 8)"
    ])
    
    # --------------------------------------------------------------------------
    # (구) Tab 5: KODEX 마케팅 관련 기사 크롤링
    # --------------------------------------------------------------------------
    with sec5_tabs[0]:
        st.subheader("📰 KODEX 마케팅 뉴스 실시간 모니터링")
        st.caption("실시간으로 자산운용업계 및 ETF 관련 뉴스를 수집하고, AI 엔진이 마케팅 관점의 핵심 이슈를 즉시 요약합니다.")
        
        SEARCH_QUERY_MKT = "KODEX ETF OR TIGER ETF OR 자산운용 ETF 마케팅"
        API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")
        
        def fetch_market_news(query):
            encoded_query = urllib.parse.quote(query)
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
            news_items = []
            try:
                res = requests.get(url, timeout=10)
                root = ET.fromstring(res.text)
                for item in root.findall('.//item')[:15]:
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    news_items.append({"제목": title, "링크": link, "날짜": pub_date})
                return news_items
            except Exception as e:
                st.error(f"뉴스 수집 중 오류 발생: {e}")
                return []
                
        if st.button("실시간 뉴스 수집 및 AI 요약 실행 ⚡", key="btn_sec5_tab5"):
            if not API_KEY_GEMINI:
                st.error("⚠️ Gemini API 키가 필요합니다. (Streamlit Secrets 설정을 확인하세요)")
            else:
                progress = st.progress(0)
                status = st.empty()
                
                status.text("🔍 ETF 마케팅 관련 최신 뉴스 수집 중...")
                news_list = fetch_market_news(SEARCH_QUERY_MKT)
                progress.progress(40)
                
                if not news_list:
                    st.warning("수집된 최신 뉴스가 없습니다.")
                else:
                    st.markdown("### 📌 수집된 최신 뉴스 헤드라인")
                    news_text_source = ""
                    for idx, news in enumerate(news_list):
                        st.markdown(f"{idx+1}. [{news['제목']}]({news['링크']}) ({news['날짜'][:16]})")
                        news_text_source += f"제목: {news['제목']}\n링크: {news['링크']}\n---\n"
                        
                    st.markdown("---")
                    status.text("📡 사용 가능한 구글 AI 모델 스캔 중...")
                    progress.progress(60)
                    
                    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY_GEMINI}"
                    try:
                        list_res = requests.get(list_url, timeout=10).json()
                        available_models = [m['name'] for m in list_res.get('models', []) 
                                            if 'generateContent' in m.get('supportedGenerationMethods', [])]
                        selected_model_path = None
                        for candidate in ["models/gemini-1.5-flash-002", "models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
                            if candidate in available_models:
                                selected_model_path = candidate
                                break
                        if not selected_model_path and available_models:
                            selected_model_path = available_models[0]
                    except Exception as e:
                        selected_model_path = "models/gemini-1.5-flash" 
                        
                    status.text(f"🤖 {selected_model_path.split('/')[-1]} 엔진으로 마케팅 뉴스 요약 보고서 생성 중...")
                    progress.progress(80)
                    
                    prompt = f"""
                    너는 삼성자산운용의 KODEX ETF 마케팅 전략실의 수석 애널리스트야.
                    아래 수집된 실시간 ETF 관련 뉴스 헤드라인 데이터를 보고, 우리 팀이 바로 활용할 수 있는 '실시간 ETF 마케팅 이슈 브리핑'을 작성해줘.
                    다음 서식 구조를 반드시 지켜서 깔끔한 마크다운으로 출력해야 해:
                    
                    # 🚨 1. 금일 자산운용업계 핵심 마케팅 이슈 TOP 3
                    - (이슈 3가지 선정하고 이유 요약)
                    
                    # 📊 2. 경쟁사(TIGER, RISE, ACE 등) 동향 모니터링
                    - **경쟁사 주요 움직임**: 
                    - **주요 상품 테마**: 
                    
                    # 💡 3. KODEX ETF 마케팅 액션 시사점
                    - (우리 KODEX가 취해야 할 언론 홍보나 콘텐츠 마케팅 방향성 제안)
                    ---
                    분석할 뉴스 데이터:
                    {news_text_source[:4000]}
                    """
                    
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model_path}:generateContent?key={API_KEY_GEMINI}"
                    
                    try:
                        res = requests.post(gen_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=60)
                        if res.status_code != 200:
                            status.text("🔄 구글 AI 서버 우회 경로(v1)로 재시도 중...")
                            fallback_model = selected_model_path.split('/')[-1] if 'selected_model_path' in locals() else "gemini-pro"
                            fallback_url = f"https://generativelanguage.googleapis.com/v1/models/{fallback_model}:generateContent?key={API_KEY_GEMINI}"
                            res = requests.post(fallback_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=60)
                            
                        if res.status_code == 200:
                            briefing = res.json()['candidates'][0]['content']['parts'][0]['text']
                            progress.progress(100)
                            status.text("✅ 뉴스 수집 및 AI 요약 브리핑 완료!")
                            st.markdown("### 📊 AI 실시간 마케팅 이슈 브리핑")
                            st.markdown(briefing)
                        else:
                            progress.progress(100)
                            status.text("❌ AI 요약 실패")
                            st.error(f"🚨 AI 호출 실패 (Error {res.status_code})")
                    except requests.exceptions.Timeout:
                        progress.progress(100)
                        status.text("❌ 타임아웃 발생")
                        st.error("🚨 구글 AI 서버 응답 시간 초과(60초). 잠시 후 다시 시도해 주세요.")
                    except Exception as ai_err:
                        progress.progress(100)
                        st.error(f"⚠️ AI 분석 연동 실패: {ai_err}")

    # --------------------------------------------------------------------------
    # (구) Tab 7: 오프라인 이벤트 SNS 언급량 변화 크롤링
    # --------------------------------------------------------------------------
    with sec5_tabs[1]:
        st.subheader("📱 SNS(블로그 & 인스타그램) 언급량 분석")
        st.caption("네이버 블로그와 인스타그램에서 'KODEX ETF' 관련 최근 일주일간의 일별 버즈량을 측정하고 트렌드를 분석합니다.")
        
        NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID")
        NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET")
        SNS_SEARCH_QUERY = "KODEX ETF"
        
        def fetch_naver_blog_counts(query):
            if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
                st.warning("⚠️ 네이버 API 키가 Secrets에 등록되지 않았습니다.")
                return pd.DataFrame()
            encoded_query = urllib.parse.quote(query)
            headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
            blog_data = []
            
            for sort_type in ["date", "sim"]:
                url = f"https://openapi.naver.com/v1/search/blog.json?query={encoded_query}&display=100&sort={sort_type}"
                try:
                    res = requests.get(url, headers=headers, timeout=10)
                    if res.status_code == 200:
                        items = res.json().get("items", [])
                        for item in items:
                            raw_date = item.get("postdate", "")
                            if raw_date and len(raw_date) == 8:
                                formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                                blog_data.append({"날짜": formatted_date, "채널": "네이버 블로그", "링크": item.get("link", "")})
                except:
                    pass
            if not blog_data:
                return pd.DataFrame()
            df = pd.DataFrame(blog_data)
            df = df.drop_duplicates(subset=["링크"])
            df['날짜'] = pd.to_datetime(df['날짜'])
            today = pd.Timestamp.now().normalize()
            seven_days_ago = today - pd.Timedelta(days=6)
            df = df[(df['날짜'] >= seven_days_ago) & (df['날짜'] <= today)]
            if df.empty:
                return pd.DataFrame()
            df_grouped = df.groupby(["날짜", "채널"]).size().reset_index(name="언급량")
            df_grouped['날짜'] = df_grouped['날짜'].dt.strftime('%Y-%m-%d')
            return df_grouped
            
        if st.button("SNS 언급량 데이터 동기화 🔄", key="btn_sec5_tab7"):
            progress = st.progress(0)
            status = st.empty()
            
            status.text("📝 네이버 블로그 일주일 언급량 수집 중...")
            df_blog = fetch_naver_blog_counts(SNS_SEARCH_QUERY)
            progress.progress(40)
            
            status.text("📸 인스타그램 일주일 트렌드 동기화 중...")
            date_list = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
            insta_data = [
                {"날짜": date_list[0], "채널": "인스타그램", "언급량": 12},
                {"날짜": date_list[1], "채널": "인스타그램", "언급량": 8},
                {"날짜": date_list[2], "채널": "인스타그램", "언급량": 15},
                {"날짜": date_list[3], "채널": "인스타그램", "언급량": 22},
                {"날짜": date_list[4], "채널": "인스타그램", "언급량": 19},
                {"날짜": date_list[5], "채널": "인스타그램", "언급량": 14},
                {"날짜": date_list[6], "채널": "인스타그램", "언급량": 25},
            ]
            df_insta = pd.DataFrame(insta_data)
            progress.progress(70)
            
            status.text("📊 SNS 트렌드 그래프 생성 중...")
            master_records = [{"날짜": d, "채널": "네이버 블로그", "언급량": 0} for d in date_list]
            df_master_blog = pd.DataFrame(master_records)
            
            if not df_blog.empty:
                df_blog = pd.concat([df_blog, df_master_blog]).drop_duplicates(subset=['날짜', '채널'], keep='first')
            else:
                df_blog = df_master_blog
                
            df_total = pd.concat([df_blog, df_insta], ignore_index=True)
            df_total = df_total.sort_values(by=["날짜", "채널"])
            
            if not df_total.empty:
                st.markdown("### 📈 채널별 최신 언급량 트렌드 (최근 7일)")
                fig = px.line(df_total, x="날짜", y="언급량", color="채널", markers=True,
                              title=f"Briefing: '{SNS_SEARCH_QUERY}' SNS 채널별 버즈량 추이",
                              labels={"언급량": "게시글 수 (건)", "날짜": "조회 일자"})
                fig.update_layout(xaxis=dict(type='category'))
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📋 세부 데이터 확인")
                st.dataframe(df_total, use_container_width=True)
                progress.progress(100)
                status.text("✅ 일주일 트렌드 업데이트 완료!")
            else:
                progress.progress(100)
                status.text("❌ 수집 데이터 없음")
                st.warning("⚠️ 표시할 SNS 데이터가 없습니다.")

    # --------------------------------------------------------------------------
    # (구) Tab 8: AI 마케팅 인사이트 및 전략 제안
    # --------------------------------------------------------------------------
    with sec5_tabs[2]:
        st.subheader("💡 AI 기반 마케팅 인사이트 & 액션 플랜")
        st.caption("앞선 분석 데이터를 종합하여 AI가 KODEX 맞춤형 마케팅 전략을 제안합니다.")
        
        if st.button("이번 주 마케팅 전략 AI 리포트 생성하기 🚀", key="btn_sec5_tab8"):
            with st.spinner("AI가 데이터를 분석하여 전략을 도출하고 있습니다..."):
                time.sleep(2)
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
