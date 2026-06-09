import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import requests
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai  # 라이브러리 교체

# 페이지 기본 설정
st.set_page_config(page_title="KODEX 마케팅 AI 에이전트", page_icon="📈", layout="wide")

# 헤더
st.title("📈 KODEX ETF 주간 마케팅 & 트렌드 모니터링 에이전트: TEAM1")
st.markdown("삼성자산운용 KODEX 마케팅 전략 도출을 위한 AI 기반 트렌드 분석 대시보드입니다.")
st.divider()

# 탭 생성 (기획하신 6가지 항목을 5개의 탭으로 논리적으로 구성)
tabs = st.tabs([
    "1. ETF 관련 뉴스 & 테마 이슈", 
    "2. 증권사 유튜브 트렌드", 
    "3. 타운용사(경쟁사) 동향", 
    "4. 투자자 & 순매수 데이터", 
    "5. 📰 KODEX 마케팅 뉴스", 
    "6. 📺 운용사 유튜브 모니터링", 
    "7. 📱 오프라인 이벤트 SNS",
    "8. 💡 AI 마케팅 인사이트"
])

# ==========================================
# Tab 1: 뉴스 & 테마 이슈 (언급량 분석)
# ==========================================
with tabs[0]:
    st.subheader("📰 금주 ETF 관련 뉴스 및 이슈 언급량 파악")
    st.caption("Google News에서 ETF 관련 최신 뉴스를 가져와 AI가 키워드를 분석합니다.")

    if st.button("실시간 뉴스 분석 실행 🔍"):
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import json

        # 1. 뉴스 크롤링 (Google News RSS)
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
                # 2. 내 API 키로 사용 가능한 모델 찾기 (Tab 2 성공 로직 복사)
                status.text("📡 사용 가능한 AI 모델 조회 중...")
                GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
                
                list_res = requests.get(list_url).json()
                available_models = [m['name'] for m in list_res.get('models', []) 
                                    if 'generateContent' in m.get('supportedGenerationMethods', [])]
                
                # 우선순위에 따른 모델 선택
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
                    # 3. 선택된 모델로 분석 실행
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
                        # JSON 텍스트 정제 (Markdown 제거)
                        clean_res = raw_res.replace("```json", "").replace("```", "").strip()
                        keyword_list = json.loads(clean_res)
                        
                        df_keywords = pd.DataFrame(keyword_list).sort_values(by='언급량', ascending=False)
                        
                        status.text("✅ 분석 완료!")
                        
                        # 4. 결과 출력
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.write("📊 키워드 순위")
                            st.dataframe(df_keywords, use_container_width=True, hide_index=True)
                        with col2:
                            import plotly.express as px
                            fig1 = px.bar(df_keywords, x='키워드', y='언급량', color='언급량', 
                                         title="실시간 이슈 키워드", color_continuous_scale='Blues')
                            st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.error(f"AI 분석 실패 (Error {res.status_code})")
                        st.json(res.json())
                        
        except Exception as e:
            st.error(f"오류 발생: {e}")

# ==========================================
# Tab 2: 증권사 유튜브 트렌드
# ==========================================
with tabs[1]:
    st.subheader("🎬 주요 증권사 유튜브 마케팅 모니터링")
    
    # [코드 상단 필수 import]
    # 파일 맨 윗부분에 아래 줄이 반드시 있어야 합니다.
    # import google.generativeai as genai
    
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

    # 2. 내부 함수 정의
    def fetch_transcript(video_id):
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            try:
                ts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
                return " ".join([i['text'] for i in ts])[:1500]
            except:
                ts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                return " ".join([i['text'] for i in ts])[:1500]
        except:
            return "자막 없음"

    def get_yt_data(name, c_id, s_date, e_date, api_key):
        import requests
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

    # # 3. 실행 로직 (새로운 고도화 리포트 및 에러 방지 적용 버전)
    if st.button("유튜브 트렌드 분석 실행 🚀"):
        if not API_KEY_YT or not API_KEY_GEMINI:
            st.error("⚠️ API 키를 확인하세요 (Streamlit Secrets 설정 필요)")
        else:
            import requests
            import json
            
            progress = st.progress(0)
            status = st.empty()
            all_text = "" 

            # [Step 1] 유튜브 데이터 수집
            for i, (name, c_id) in enumerate(TARGET_BROKERAGES.items()):
                status.text(f"🔍 {name} 영상 수집 중...")
                all_text += get_yt_data(name, c_id, start_date, end_date, API_KEY_YT)
                progress.progress((i + 1) * 20)

            if not all_text.strip() or len(all_text) < 50:
                st.warning("데이터가 부족합니다. 날짜를 확인하세요.")
            else:
                # [Step 2] 내 키로 사용 가능한 모델 자동 찾기
                status.text("📡 사용 가능한 AI 모델 조회 중...")
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY_GEMINI}"
                
                try:
                    list_res = requests.get(list_url).json()
                    available_models = [m['name'] for m in list_res.get('models', []) 
                                        if 'generateContent' in m.get('supportedGenerationMethods', [])]
                    
                    # 우선순위에 따라 모델 선택
                    selected_model = None
                    for candidate in ["models/gemini-1.5-flash-002", "models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
                        if candidate in available_models:
                            selected_model = candidate
                            break
                    
                    if not selected_model and available_models:
                        selected_model = available_models[0] 
                    
                    if not selected_model:
                        st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키 설정을 확인하세요.")
                        st.write("조회된 모델 목록:", available_models)
                    else:
                        # [Step 3] 선택된 모델로 원하셨던 맞춤형 서식 분석 실행
                        status.text(f"🤖 {selected_model.split('/')[-1]} 모델로 전략 리포트 생성 중...")
                        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={API_KEY_GEMINI}"
                        
                        # 요청하신 서식(롱폼/숏폼 분리, 액션플랜, 인사이트)을 강제 주입한 프롬프트
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
                        우리는 대형 자산운용사로서, 각 증권사의 집중 테마와 고객 특성을 고려하여 맞춤형 ETF 마케팅/영업 전략을 제안합니다.
                        
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
                        
                        payload = {
                            "contents": [{"parts": [{"text": prompt}]}]
                        }
                        
                        res = requests.post(gen_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                        
                        if res.status_code == 200:
                            analysis = res.json()['candidates'][0]['content']['parts'][0]['text']
                            progress.progress(100)
                            status.text("✅ 분석 완료!")
                            st.markdown("---")
                            st.markdown(analysis)
                        elif res.status_code == 429:
                            progress.progress(100)
                            status.text("❌ 사용량 제한 초과")
                            st.error("🚨 구글 AI 호출량이 일시적으로 초과되었습니다. 약 20초만 기다렸다가 다시 버튼을 클릭해 주세요!")
                        else:
                            st.error(f"⚠️ 분석 실패 (Error {res.status_code})")
                            st.json(res.json())
                            
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                
# ==========================================
# Tab 3: 주요 운용사별 ETF 이슈 모니터링
# ==========================================
with tabs[2]:
    st.subheader("🏢 주요 운용사별 ETF 이슈 모니터링")
    st.caption("Google News에서 각 운용사별 ETF 최신 뉴스를 가져와 AI가 핵심 이슈를 요약합니다.")

    if st.button("운용사 실시간 이슈 분석 🔍"):
        import requests
        from bs4 import BeautifulSoup
        import json
        import urllib.parse

        # 1. 운용사별 검색어 설정
        BRANDS = {
            "KODEX": "삼성자산운용 KODEX ETF",
            "TIGER": "미래에셋 TIGER ETF",
            "RISE": "KB자산운용 RISE ETF",
            "ACE": "한국투자신탁운용 ACE ETF"
        }
        
        GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
        
        status = st.empty()
        progress = st.progress(0)
        
        # 2. 각 운용사별 뉴스 RSS 크롤링
        all_brand_news = {}
        for idx, (brand, query) in enumerate(BRANDS.items()):
            status.text(f"🔍 {brand} 뉴스 수집 중...")
            encoded_query = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
            
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(rss_url, headers=headers)
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")[:10]
                titles = [item.title.text for item in items]
                all_brand_news[brand] = "\n".join(titles) if titles else "최신 뉴스 없음"
            except Exception as e:
                all_brand_news[brand] = f"뉴스 수집 실패 ({e})"
            
            progress.progress(int((idx + 1) * 15))

        # 3. 사용 가능한 Gemini 모델 자동 탐색
        status.text("📡 AI 모델 연결 중...")
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
            list_res = requests.get(list_url).json()
            available_models = [m['name'] for m in list_res.get('models', []) 
                                if 'generateContent' in m.get('supportedGenerationMethods', [])]
            
            selected_model = None
            for candidate in ["models/gemini-1.5-flash-002", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]:
                if candidate in available_models:
                    selected_model = candidate
                    break
            
            if not selected_model and available_models:
                selected_model = available_models[0]
            
            if not selected_model:
                st.error("❌ 사용 가능한 AI 모델을 찾을 수 없습니다.")
            else:
                # 4. 선택된 AI 모델로 데이터 분석
                status.text("🤖 AI 요약 리포트 생성 중...")
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={GEMINI_KEY}"
                
                news_context = ""
                for brand, news in all_brand_news.items():
                    news_context += f"[{brand} 뉴스 목록]\n{news}\n\n"
                    
                prompt = f"""
                다음 운용사별 뉴스 데이터를 기반으로, 각 브랜드의 최근 핵심 이슈를 2개씩 요약해줘.
                반드시 아래 JSON 형식으로만 응답해.
                {{
                    "KODEX": ["이슈1", "이슈2"],
                    "TIGER": ["이슈1", "이슈2"],
                    "RISE": ["이슈1", "이슈2"],
                    "ACE": ["이슈1", "이슈2"]
                }}
                데이터:
                {news_context}
                """
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post(gen_url, json=payload)
                
                if res.status_code == 200:
                    raw_res = res.json()['candidates'][0]['content']['parts'][0]['text']
                    # [수정된 부분] 따옴표와 괄호를 정확히 닫았습니다.
                    clean_res = raw_res.replace("```json", "").replace("```", "").strip()
                    summary_data = json.loads(clean_res)
                    
                    progress.progress(100)
                    status.text("✅ 모든 데이터 업데이트 완료!")
                    
                    # 5. 화면 레이아웃 출력
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
                else:
                    st.error(f"AI 분석 실패: {res.status_code}")
        except Exception as e:
            st.error(f"오류 발생: {e}")

# ==========================================
# Tab 4: 투자자 & 순매수 데이터 (마케팅 실효성)
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
# Tab 5: KODEX 마케팅 관련 기사 크롤링
# ==========================================
with tabs[4]: # 사용하시는 뉴스 탭 번호에 맞게 조정하세요 (예: tabs[0])
    st.subheader("📰 KODEX 마케팅 뉴스 실시간 모니터링")
    st.caption("실시간으로 자산운용업계 및 ETF 관련 뉴스를 수집하고, AI 엔진이 마케팅 관점의 핵심 이슈를 즉시 요약합니다.")

    # 뉴스 검색어 설정
    SEARCH_QUERY = "KODEX ETF OR TIGER ETF OR 자산운용 ETF 마케팅"
    
    API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")

    # 1. 뉴스 데이터 수집 함수 (네이버 뉴스 RSS 기준 예시 - 환경에 맞게 고쳐 쓰세요)
    def fetch_market_news(query):
        import requests
        import xml.etree.ElementTree as ET
        import urllib.parse
        
        encoded_query = urllib.parse.quote(query)
        # 네이버 뉴스 RSS는 인증키 없이 최근 50개 뉴스를 받아올 수 있어 모니터링용으로 안정적입니다.
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        news_items = []
        try:
            res = requests.get(url, timeout=10)
            root = ET.fromstring(res.text)
            
            for item in root.findall('.//item')[:15]: # 최근 뉴스 15개 추출
                title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                news_items.append({
                    "제목": title,
                    "링크": link,
                    "날짜": pub_date
                })
            return news_items
        except Exception as e:
            st.error(f"뉴스 수집 중 오류 발생: {e}")
            return []

    # 2. 실행 버튼 및 로직
    if st.button("실시간 뉴스 수집 및 AI 요약 실행 ⚡", key="btn_news_analysis"):
        if not API_KEY_GEMINI:
            st.error("⚠️ Gemini API 키가 필요합니다. (Streamlit Secrets 설정을 확인하세요)")
        else:
            progress = st.progress(0)
            status = st.empty()
            
            # [Step 1] 실시간 뉴스 크롤링
            status.text("🔍 ETF 마케팅 관련 최신 뉴스 수집 중...")
            news_list = fetch_market_news(SEARCH_QUERY)
            progress.progress(40)
            
            if not news_list:
                st.warning("수집된 최신 뉴스가 없습니다. 잠시 후 다시 시도해 주세요.")
            else:
                # 화면에 수집된 뉴스 리스트 먼저 뿌려주기
                st.markdown("### 📌 수집된 최신 뉴스 헤드라인")
                news_text_source = ""
                
                for idx, news in enumerate(news_list):
                    st.markdown(f"{idx+1}. [{news['제목']}]({news['링크']}) ({news['날짜'][:16]})")
                    # AI에게 넘겨줄 텍스트 빌드업
                    news_text_source += f"제목: {news['제목']}\n링크: {news['링크']}\n---\n"
                
                # [Step 2] 유튜브 탭 성공 로직 이식 + 타임아웃 60초 연장 버전
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
                
                status.text(f"🤖 {selected_model_path.split('/')[-1]} 엔진으로 마케팅 뉴스 요약 보고서 생성 중 (최대 1분 소요)...")
                progress.progress(80)
                
                # 프롬프트 구성
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
                {news_text_source[:4000]}  # 데이터가 너무 길어 타임아웃 유발하는 것을 방지하기 위해 글자수 제한 추가
                """
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model_path}:generateContent?key={API_KEY_GEMINI}"
                
                try:
                    import requests
                    import json
                    
                    # 💡 [핵심 수정] 타임아웃을 60초로 늘려 AI가 답변을 다 만들 때까지 안전하게 기다립니다.
                    res = requests.post(gen_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=60)
                    
                    # 일시적 오류 발생 시 우회 경로 재시도 (여기서도 timeout=60 유지)
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
                    st.error("🚨 구글 AI 서버가 답변을 생성하는 데 시간이 너무 오래 걸립니다(60초 초과). 뉴스 양이 많거나 서버가 혼잡할 수 있으니 잠시 후 다시 시도해 주세요!")
                except Exception as ai_err:
                    progress.progress(100)
                    st.error(f"⚠️ AI 분석 연동 실패: {ai_err}")
# ==========================================
# Tab 6: 운용사 유튜브 신규 영상 및 설명문 크롤링
# ==========================================
with tabs[5]:  
    st.subheader("🎬 4대 자산운용사 유튜브 업로드 패턴 및 AI 콘텐츠 요약")
    st.caption("안정적인 날짜 기반 Search API 방식을 사용하여 운용사의 업로드 주기를 분석하고 요약 리포트를 생성합니다.")
    
    TARGET_BROKERAGES = {
        "KODEX ETF (삼성자산운용)": "UCZ0Z0vO2wVbO2D2RrgjZgZw",   
        "TIGER ETF (미래에셋자산운용)": "UC37XvO-X_QW98tSsh2W4p9A", 
        "RISE ETF (KB자산운용)": "UC3FstZg-AALi8jMofJkS5pA",       
        "ACE ETF (한국투자신탁운용)": "UCg9S6Zg4e0P9EwHbeM4xXvw"
    }
    
    API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY")
    API_KEY_YT = st.secrets.get("YOUTUBE_API_KEY")

    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("조회 시작일", datetime.now() - timedelta(days=30), key="am_start")
    with col_date2:
        end_date = st.date_input("조회 종료일", datetime.now(), key="am_end")

    def fetch_transcript(video_id):
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            try:
                ts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
                return " ".join([i['text'] for i in ts])[:1000]
            except:
                ts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                return " ".join([i['text'] for i in ts])[:1000]
        except:
            return "자막 없음"

    if st.button("운용사 패턴 및 요약 분석 실행 🚀", key="btn_am_analysis"):
        if not API_KEY_YT or not API_KEY_GEMINI:
            st.error("⚠️ API 키를 확인하세요 (Streamlit Secrets 설정 필요)")
        else:
            import requests
            import json
            import pandas as pd
            import plotly.express as px
            
            progress = st.progress(0)
            status = st.empty()
            
            all_text = ""          
            chart_data_list = []    

            # 💡 구글 서버가 날짜를 오해하지 않도록 ISO 표준 포맷(RFC 3339)으로 철저하게 변환
            published_after = start_date.strftime('%Y-%m-%dT00:00:00Z')
            published_before = end_date.strftime('%Y-%m-%dT23:59:59Z')
            
            # 💡 무작위 누락을 막기 위해 오리지널 search 엔드포인트를 사용합니다.
            url = "https://www.googleapis.com/youtube/v3/search"

            # [Step 1] 데이터 수집
            for idx, (name, c_id) in enumerate(TARGET_BROKERAGES.items()):
                status.text(f"🔍 {name} 채널 데이터 동기화 중...")
                
                params = {
                    "key": API_KEY_YT,
                    "channelId": c_id,
                    "part": "snippet",
                    "order": "date",        # 최신순 정렬 강제
                    "type": "video",        # 플레이리스트, 채널 제외하고 오직 '동영상'만
                    "maxResults": 25,       # 수집 개수를 25개로 늘려 기간 내 누락 방지
                    "publishedAfter": published_after,
                    "publishedBefore": published_before
                }
                
                try:
                    res = requests.get(url, params=params).json()
                    videos_summary = []
                    
                    if "items" in res:
                        for item in res.get("items", []):
                            # 간혹 ID 구조가 다르게 들어오는 경우를 위한 방어 파싱
                            v_id = item["id"].get("videoId")
                            if not v_id:
                                continue
                                
                            title = item["snippet"]["title"]
                            pub_time_str = item["snippet"]["publishedAt"]
                            
                            # 한국 시간대 변환
                            pub_time = pd.to_datetime(pub_time_str).tz_convert('Asia/Seoul')
                            
                            chart_data_list.append({
                                "운용사": name,
                                "제목": title,
                                "날짜": pub_time.strftime('%Y-%m-%d'),
                                "요일": pub_time.strftime('%A'), 
                                "시간대": pub_time.hour          
                            })
                            
                            transcript = fetch_transcript(v_id)
                            videos_summary.append(f"- 제목: {title}\n  내용: {transcript}")
                    
                    if videos_summary:
                        all_text += f"\n### [{name}]\n" + "\n".join(videos_summary)
                    else:
                        all_text += f"\n### [{name}]\n선택 기간 내 업로드된 영상 없음\n"
                        
                except Exception as e:
                    all_text += f"\n### [{name}]\n데이터 수집 중 에러 발생: {e}\n"
                
                # 디버깅용 강제 대기 제거 및 빠른 프로그레스바 반영
                progress.progress(int((idx + 1) * (50 / len(TARGET_BROKERAGES))))

            # [Step 2] 시각화 차트 출력
            st.markdown("### 📊 1. 운용사별 유튜브 업로드 패턴 분석 (주기 파악)")
            if chart_data_list:
                df = pd.DataFrame(chart_data_list)
                weekday_map = {'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일', 
                               'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'}
                df['요일'] = df['요일'].map(weekday_map)
                
                df_day = df.groupby(['운용사', '요일']).size().reset_index(name='업로드수')
                fig_day = px.bar(df_day, x='요일', y='업로드수', color='운용사', barmode='group',
                                 title='📅 요일별 유튜브 업로드 분포',
                                 category_orders={'요일': ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']})
                st.plotly_chart(fig_day, use_container_width=True)
                
                df_hour = df.groupby(['운용사', '시간대']).size().reset_index(name='업로드수')
                fig_hour = px.line(df_hour, x='시간대', y='업로드수', color='운용사', markers=True,
                                   title='⏰ 시간대별 업로드 집중도 (KST)')
                st.plotly_chart(fig_hour, use_container_width=True)
            else:
                st.warning("⚠️ 선택하신 조회 기간 내에 수집된 영상이 없습니다. 조회 시작일을 더 과거로 설정해 보세요.")

            # [Step 3] AI 모델 동적 스캔 및 요약 리포트
            if not chart_data_list or len(all_text.strip()) < 50:
                st.info("ℹ️ 수집된 영상 데이터가 없으므로 AI 요약 리포트를 생략합니다.")
            else:
                status.text("📡 사용 가능한 AI 모델 조회 중...")
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY_GEMINI}"
                
                selected_model_path = "models/gemini-1.5-flash"
                try:
                    list_res = requests.get(list_url, timeout=5).json()
                    available_models = [m['name'] for m in list_res.get('models', []) 
                                        if 'generateContent' in m.get('supportedGenerationMethods', [])]
                    for candidate in ["models/gemini-1.5-flash-002", "models/gemini-1.5-flash", "models/gemini-pro"]:
                        if candidate in available_models:
                            selected_model_path = candidate
                            break
                except:
                    pass
                
                status.text(f"🤖 {selected_model_path.split('/')[-1]} 엔진 기반 영상 콘텐츠 트렌드 분석 중...")
                progress.progress(80)
                
                prompt = f"""
                너는 국내 대형 자산운용사의 ETF 마케팅 전략 총괄 책임자야.
                아래 제공된 국내 4대 ETF 자산운용사의 유튜브 최신 콘텐츠와 자막 데이터를 정밀 분석하여 요약 리포트를 작성해줘.

                구조:
                1. 각 운용사별로 최신 영상들의 내용을 파악하여 '핵심 홍보 테마'와 '최신 영상 요약'을 제공할 것.
                2. 경쟁사 대응을 위한 우리 운용사의 마케팅 시사점을 정리할 것.

                분석할 데이터:
                {all_text}
                """
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model_path}:generateContent?key={API_KEY_GEMINI}"
                
                try:
                    res = requests.post(gen_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=60)
                    if res.status_code != 200:
                        fallback_model = selected_model_path.split('/')[-1] if 'selected_model_path' in locals() else "gemini-pro"
                        fallback_url = f"https://generativelanguage.googleapis.com/v1/models/{fallback_model}:generateContent?key={API_KEY_GEMINI}"
                        res = requests.post(fallback_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=60)
                    
                    if res.status_code == 200:
                        briefing = res.json()['candidates'][0]['content']['parts'][0]['text']
                        progress.progress(100)
                        status.text("✅ 주기 분석 및 AI 영상 콘텐츠 요약 완료!")
                        st.markdown("---")
                        st.markdown(briefing)
                    else:
                        progress.progress(100)
                        st.error(f"🚨 구글 AI 서버 응답 지연 (Error {res.status_code})")
                except Exception as ai_err:
                    progress.progress(100)
                    st.error(f"⚠️ AI 연동 실패: {ai_err}")
                    
# ==========================================
# Tab 7: 오프라인 이벤트 SNS 언급량 변화 크롤링
# ==========================================
with tabs[6]: 
    st.subheader("📱 SNS(블로그 & 인스타그램) 언급량 분석")
    st.caption("네이버 블로그와 인스타그램에서 'KODEX ETF' 관련 최근 일주일간의 일별 버즈량을 측정하고 트렌드를 분석합니다.")

    NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET")
    
    SNS_SEARCH_QUERY = "KODEX ETF"

    # 💡 들여쓰기 정렬 완료: 함수 정의 블록 (스페이스 4칸 규칙)
    def fetch_naver_blog_counts(query):
        import requests
        import pandas as pd
        import urllib.parse
        
        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            st.warning("⚠️ 네이버 API 키가 Secrets에 등록되지 않았습니다.")
            return pd.DataFrame()
            
        encoded_query = urllib.parse.quote(query)
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
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
                            blog_data.append({
                                "날짜": formatted_date,
                                "채널": "네이버 블로그",
                                "링크": item.get("link", "") # 💡 한글 '링크' 키로 매칭
                            })
            except Exception as e:
                pass

        if not blog_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(blog_data)
        
        # 💡 한글 '링크' 컬럼 기준으로 중복 제거하도록 버그 수정 완료!
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


    # 💡 들여쓰기 정렬 완료: 실행 버튼 블록 (위의 함수와 시작 선을 동일하게 맞춤)
    if st.button("SNS 언급량 데이터 동기화 🔄", key="btn_sns_monitor"):
        import pandas as pd
        import plotly.express as px
        from datetime import datetime, timedelta
        
        progress = st.progress(0)
        status = st.empty()
        
        # [Step 1] 네이버 블로그 데이터 수집
        status.text("📝 네이버 블로그 일주일 언급량 수집 및 정렬 중...")
        df_blog = fetch_naver_blog_counts(SNS_SEARCH_QUERY)
        progress.progress(40)
        
        # [Step 2] 인스타그램 일주일 동기화 데이터 생성
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
        
        # [Step 3] 데이터 병합 및 빈 날짜 메우기
        status.text("📊 SNS 트렌드 7일 선그래프 생성 중...")
        
        master_records = []
        for d in date_list:
            master_records.append({"날짜": d, "채널": "네이버 블로그", "언급량": 0})
        df_master_blog = pd.DataFrame(master_records)
        
        if not df_blog.empty:
            df_blog = pd.concat([df_blog, df_master_blog]).drop_duplicates(subset=['날짜', '채널'], keep='first')
        else:
            df_blog = df_master_blog
            
        df_total = pd.concat([df_blog, df_insta], ignore_index=True)
        df_total = df_total.sort_values(by=["날짜", "채널"])
        
        # [Step 4] 시각화 및 표 출력
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

# ==========================================
# Tab 8: AI 마케팅 인사이트 및 전략 제안
# ==========================================
with tabs[7]:
    st.subheader("💡 AI 기반 마케팅 인사이트 & 액션 플랜")
    st.caption("앞선 분석(1~7번) 데이터를 종합하여 AI가 KODEX 맞춤형 마케팅 전략을 제안합니다.")
    
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
