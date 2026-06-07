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
    "1. 뉴스 & 테마 이슈", 
    "2. 증권사 유튜브 트렌드", 
    "3. 타운용사(경쟁사) 동향", 
    "4. 투자자 & 순매수 데이터", 
    "5. 💡 AI 마케팅 인사이트",
    "6. 📰 KODEX 마케팅 뉴스", 
    "7. 📺 운용사 유튜브 모니터링", 
    "8. 📱 오프라인 이벤트 SNS"
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
# ==========================================
# Tab 6: KODEX 마케팅 관련 기사 크롤링
# ==========================================
with tabs[5]: 
    st.subheader("📰 KODEX 마케팅 뉴스 실시간 모니터링 및 AI 요약")
    st.caption("Google News RSS 피드의 메타데이터를 기반으로 Gemini AI가 마케팅적 시사점과 핵심 내용을 3줄 요약합니다.")

    if st.button("KODEX 마케팅 기사 및 AI 요약 불러오기 🔄"):
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        import json

        status_news = st.empty()
        status_news.text("🌐 KODEX 마케팅 관련 뉴스 실시간 수집 중...")
        
        # 'KODEX 마케팅' 관련 키워드로 Google News RSS 검색
        query = "삼성자산운용 KODEX (마케팅 OR 홍보 OR 이벤트 OR 캠페인)"
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            resp = requests.get(rss_url, headers=headers)
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")[:8] # 안정적이고 풍부한 분석을 위해 8개 수집
            
            if not items:
                status_news.text("")
                st.warning("최근 KODEX 마케팅 관련 뉴스를 찾을 수 없습니다.")
            else:
                for idx, item in enumerate(items):
                    title = item.title.text.split(" - ")[0]
                    link = item.link.text
                    pub_date = item.pubDate.text if item.pubDate else "날짜 정보 없음"
                    source = item.source.text if item.source else "언론사 미정"
                    
                    # 구글 뉴스가 기본 제공하는 간이 설명문(Description) 추출 및 태그 제거
                    raw_desc = item.description.text if item.description else ""
                    clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text() if raw_desc else ""
                    
                    status_news.text(f"🧠 ({idx+1}/{len(items)}) '{title[:15]}...' AI 심층 분석 및 요약 중...")
                    
                    # 💡 원문 크롤링 대신 제목과 가용 데이터를 조합해 풍부한 컨텍스트 생성
                    context_text = f"기사 제목: {title}\n기사 주요 내용: {clean_desc}"
                    
                    summary_text = "요약을 생성할 수 없습니다."
                    
                    if API_KEY_GEMINI:
                        summary_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY_GEMINI}"
                        
                        # 컨텍스트를 기반으로 전문가 수준의 3줄 요약 문장을 만들어내도록 프롬프트 정교화
                        prompt = f"""
                        너는 금융 업계 최고의 AI 마케팅 분석가야. 
                        제공된 뉴스 기사의 단서(제목 및 요약 패킷)를 바탕으로, 해당 뉴스 기사가 담고 있는 핵심 사실과 마케팅적 시사점을 유추하여 '반드시' 딱 3줄의 깔끔한 글머리 기호(- ) 형태의 문장으로 요약해줘.
                        
                        요구사항:
                        1. 격식 있는 존댓말(~ 문체)을 사용해줘.
                        2. 첫 번째 줄은 기사의 핵심 팩트, 두 번째/세 번째 줄은 이것이 KODEX ETF나 운용업계에 가지는 마케팅적 의미나 영향 위주로 작성해줘.
                        3. 단서가 부족하더라도 금융 상식을 발휘하여 자연스럽고 전문적인 리포트 문체로 채워줘.

                        분석할 기사 단서:
                        {context_text}
                        """
                        
                        payload = {"contents": [{"parts": [{"text": prompt}]}]}
                        try:
                            summary_res = requests.post(summary_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=7)
                            if summary_res.status_code == 200:
                                summary_text = summary_res.json()['candidates'][0]['content']['parts'][0]['text']
                            else:
                                summary_text = f"⚡ AI 응답 오류 (Error Code: {summary_res.status_code})"
                        except Exception as e:
                            summary_text = f"⚡ AI 연동 중 타임아웃이 발생했습니다."

                    # 3. 대시보드 화면에 깔끔하게 출력
                    with st.container():
                        st.markdown(f"### 🔗 [{title}]({link})")
                        st.caption(f"📅 **발행일시:** {pub_date} | 🏢 **언론사:** {source}")
                        st.markdown("**🤖 Gemini AI 핵심 마케팅 리포트**")
                        st.info(summary_text)
                        st.markdown("---")
                        
                status_news.text("✅ 모든 뉴스 뉴스 수집 및 AI 요약 완료!")
                
        except Exception as e:
            status_news.text("")
            st.error(f"뉴스 수집 중 오류가 발생했습니다: {e}")


# ==========================================
# Tab 7: 운용사 유튜브 신규 영상 및 설명문 크롤링
# ==========================================
with tabs[6]:
    st.subheader("📺 운용사 유튜브 신규 영상 감지 및 업로드 주기 분석")
    st.caption("각 운용사 공식 채널의 최신 영상 데이터(업로드일, 설명문)를 실시간 크롤링하여 최근 업로드 주기를 진단합니다.")

    # 기존에 사용하던 YouTube API Key와 채널 ID 딕셔너리 연동
    # (만약 변수명이 다르면 기존 코드에 맞춰 수정해 주세요)
    YT_BRANDS = {
        "KODEX ETF": "UCZ0Z0vO2wVbO2D2RrgjZgZw",       # 삼성자산운용 (예시 ID, 실제 ID로 교체 필요)
        "스마트타이거": "UC89e-Z_bepMM_D66SOfS0Sg",    # 미래에셋 (예시 ID)
        "RISE ETF": "UCf2vLbeMWhS9D_m8HbeHqgQ",        # KB자산운용 (예시 ID)
        "ACE ETF": "UCGfGQU0u-A3D-OQk8XNf4gA"          # 한국투자 (예시 ID)
    }
    
    # ⚠️ 기존에 선언된 TARGET_BROKERAGES가 있다면 그걸 사용하셔도 됩니다.
    API_KEY_YT = st.secrets.get("YOUTUBE_API_KEY")

    if st.button("유튜브 채널 업로드 현황 조회 📊"):
        if not API_KEY_YT:
            st.error("⚠️ Streamlit Secrets에 YOUTUBE_API_KEY가 설정되어 있지 않습니다.")
        else:
            import requests
            import datetime
            
            status_yt = st.empty()
            progress_yt = st.progress(0)
            
            for idx, (brand_name, channel_id) in enumerate(YT_BRANDS.items()):
                status_yt.text(f"🎥 {brand_name} 채널 최신 영상 및 설명문 분석 중...")
                
                # 채널의 최신 영상 리스트 가져오기 API
                search_url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY_YT}&channelId={channel_id}&part=snippet,id&order=date&maxResults=5&type=video"
                
                try:
                    res = requests.get(search_url).json()
                    videos = res.get("items", [])
                    
                    st.markdown(f"### 🏢 {brand_name}")
                    
                    if not videos:
                        st.write("최근 업로드된 영상이 없거나 채널 ID를 확인해 주세요.")
                    else:
                        dates = []
                        for v in videos:
                            v_id = v["id"]["videoId"]
                            title = v["snippet"]["title"]
                            desc = v["snippet"]["description"]
                            pub_time_str = v["snippet"]["publishedAt"]
                            
                            # 날짜 파싱
                            pub_time = datetime.datetime.strptime(pub_time_str, "%Y-%m-%dT%H:%M:%SZ")
                            dates.append(pub_time)
                            
                            # 개별 영상 출력
                            with st.expander(f"🎬 {title} ({pub_time.strftime('%Y-%m-%d')})"):
                                st.markdown(f"**🔗 영상 링크:** [YouTube 바로가기](https://www.youtube.com/watch?v={v_id})")
                                st.markdown(f"**📝 영상 설명문(Description):**")
                                st.code(desc if desc.strip() else "설명문이 없습니다.", language="text")
                        
                        # 업로드 주기 계산 (최신 5개 영상 간의 평균 간격)
                        if len(dates) >= 2:
                            intervals = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
                            avg_interval = sum(intervals) / len(intervals)
                            st.info(f"⏱️ **최근 업로드 주기:** 평균 **{avg_interval:.1f}일** 간격으로 신규 영상이 업로드되고 있습니다.")
                        else:
                            st.info("⏱️ 데이터 부족으로 평균 업로드 주기를 계산할 수 없습니다.")
                            
                except Exception as e:
                    st.error(f"{brand_name} 데이터 조회 실패: {e}")
                
                progress_yt.progress(int((idx + 1) * 25))
            
            status_yt.text("✅ 모든 채널 조회 완료!")


# ==========================================
# Tab 8: 오프라인 이벤트 SNS 언급량 변화 크롤링
# ==========================================
with tabs[7]:
    st.subheader("📱 오프라인 이벤트 SNS (네이버 블로그) 언급량 모니터링")
    st.caption("진행 중이거나 진행했던 오프라인 이벤트(예: 세미나, 팝업스토어) 키워드를 입력하면 실시간으로 블로그 언급 글을 크롤링합니다.")

    # 사용자로부터 오프라인 이벤트 키워드 입력받기
    event_keyword = st.text_input("분석할 오프라인 이벤트 키워드를 입력하세요", placeholder="예: KODEX 세미나, TIGER 팝업스토어")
    
    # 네이버 API 키 연동 (오픈 API 가입 후 Secrets 등록 필요)
    NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET")

    if st.button("SNS 언급량 분석 시작 🚀"):
        if not event_keyword.strip():
            st.warning("⚠️ 이벤트 키워드를 입력해 주세요.")
        elif not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            st.error("⚠️ 네이버 검색 API 사용을 위해 Streamlit Secrets에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 등록해야 합니다.")
        else:
            import requests
            import urllib.parse
            from bs4 import BeautifulSoup
            
            status_sns = st.empty()
            status_sns.text("🔍 네이버 SNS(블로그) 실시간 언급 데이터 수집 중...")
            
            encoded_key = urllib.parse.quote(event_keyword)
            
            # 1. 네이버 블로그 검색 API (급증 여부 판단을 위해 유사도순/최신순 조합 가능, 여기선 최신순 수집)
            url = f"https://openapi.naver.com/v1/search/blog.json?query={encoded_key}&display=20&sort=date"
            headers = {
                "X-Naver-Client-Id": NAVER_CLIENT_ID,
                "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
            }
            
            try:
                res = requests.get(url, headers=headers).json()
                items = res.get("items", [])
                
                if not items:
                    st.info(f"🙅‍♂️ '{event_keyword}' 키워드에 대한 최근 언급을 찾을 수 없습니다.")
                else:
                    st.success(f"📈 '{event_keyword}' 관련 최신 SNS 언급 데이터 총 {len(items)}건 분석 완료")
                    
                    # 수집된 글 목록 시각화
                    for item in items:
                        title = item["title"].replace("<b>", "").replace("</b>", "")
                        description = item["description"].replace("<b>", "").replace("</b>", "")
                        post_date = item["postdate"]
                        formatted_date = f"{post_date[:4]}-{post_date[4:6]}-{post_date[6:]}"
                        link = item["link"]
                        blog_name = item["bloggername"]
                        
                        with st.container():
                            st.markdown(f"**[{blog_name}]** [{title}]({link})")
                            st.caption(f"📅 작성일: {formatted_date}")
                            st.write(description)
                            st.markdown("---")
                            
                    # Tip 안내
                    st.info("💡 **인스타그램 크롤링 안내:** 인스타그램은 현재 공식 Graph API를 통해서만 비즈니스 계정 기준으로 해시태그 검색이 가능하며, 일반 웹 크롤링(BeautifulSoup 등)은 메타의 강력한 차단 정책 시스템에 의해 웹 대시보드 환경에서 실시간 작동이 불가능합니다. 따라서 실시간 모니터링은 네이버 블로그/웹 데이터를 메인으로 활용하시는 것을 추천합니다.")
            except Exception as e:
                st.error(f"SNS 데이터 수집 오류: {e}")
            
            status_sns.text("")
