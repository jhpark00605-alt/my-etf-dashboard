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
    st.subheader("📺 운용사 유튜브 신규 영상 감지 및 업로드 주기 분석")
    st.caption("증권사 탭의 성공 로직을 기반으로, 공식 핸들 네임을 추적하여 4대 운용사의 최신 영상 데이터를 실시간 수집합니다.")

    # 💡 [핸들 네임 세팅] 증권사 탭처럼 직관적이고 직결성이 높은 @핸들 구조로 변경
    YT_BRANDS = {
        "KODEX ETF (삼성자산운용)": "@KODEX_ETF",   
        "TIGER ETF (미래에셋자산운용)": "@TIGERETF", 
        "RISE ETF (KB자산운용)": "@RISE_ETF",       
        "ACE ETF (한국투자신탁운용)": "@ACE_ETF"  
    }
    
    my_yt_key = st.secrets.get("YOUTUBE_API_KEY")

    if st.button("운용사 유튜브 채널 업로드 현황 조회 📊"):
        if not my_yt_key:
            st.error("⚠️ Streamlit Secrets에 YOUTUBE_API_KEY가 등록되어 있는지 확인해 주세요.")
        else:
            import requests
            import datetime
            
            status_yt = st.empty()
            progress_yt = st.progress(0)
            
            for idx, (brand_name, handle) in enumerate(YT_BRANDS.items()):
                status_yt.text(f"🎥 {brand_name} ({handle}) 최신 영상 데이터 수집 중...")
                
                # 💡 [증권사 성공 로직 이식] 핸들 네임(@)을 검색어로 활용하여 
                # 해당 채널의 최신 동영상을 안전하게 긁어오는 구문입니다.
                search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&order=date&q={handle}&type=video&key={my_yt_key}"
                
                try:
                    res_raw = requests.get(search_url, timeout=10)
                    
                    if res_raw.status_code != 200:
                        st.error(f"❌ {brand_name} 데이터 통신 실패 (서버 코드: {res_raw.status_code})")
                        continue
                        
                    res = res_raw.json()
                    videos = res.get("items", [])
                    
                    st.markdown(f"### 🏢 {brand_name}")
                    
                    if not videos:
                        st.warning("💡 최신 공개 영상을 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.")
                    else:
                        dates = []
                        for v in videos:
                            v_id = v.get("id", {}).get("videoId")
                            if not v_id: continue
                            
                            snippet = v.get("snippet", {})
                            title = snippet.get("title", "제목 없음")
                            desc = snippet.get("description", "설명 없음")
                            pub_time_str = snippet.get("publishedAt")
                            
                            # 날짜 형식 파싱
                            pub_time = datetime.datetime.strptime(pub_time_str, "%Y-%m-%dT%H:%M:%SZ")
                            dates.append(pub_time)
                            
                            # 아코디언 메뉴 구성
                            with st.expander(f"🎬 {title} ({pub_time.strftime('%Y-%m-%d')})"):
                                st.markdown(f"**🔗 영상 링크:** [YouTube 영상 바로가기](https://www.youtube.com/watch?v={v_id})")
                                st.markdown(f"**📝 영상 설명문(Description):**")
                                st.code(desc if desc.strip() else "등록된 설명문이 없습니다.", language="text")
                        
                        # ⏱️ 업로드 주기 패턴 계산
                        if len(dates) >= 2:
                            intervals = [abs((dates[i-1] - dates[i]).days) for i in range(1, len(dates))]
                            avg_interval = sum(intervals) / len(intervals)
                            
                            if avg_interval <= 3:
                                status_txt = "🔥 콘텐츠 생산 속도 매우 빠름 (마케팅 집중기)"
                            elif avg_interval <= 7:
                                status_txt = "✅ 정기적인 템포 유지 중 (주 1회 수준)"
                            else:
                                status_txt = "⏳ 최근 업로드 텀이 길어짐"
                                
                            st.info(f"⏱️ **최근 생산 패턴:** 평균 **{avg_interval:.1f}일** 간격으로 업로드 중 ({status_txt})")
                        else:
                            st.info("⏱️ 주기 분석을 위한 데이터가 부족합니다.")
                            
                except Exception as e:
                    st.error(f"{brand_name} 시스템 연동 에러 발생: {e}")
                
                progress_yt.progress(int((idx + 1) * 25))
                st.markdown("---")
            
            status_yt.text("✅ 모든 자산운용사 유튜브 실시간 데이터 연동 완료!")
# ==========================================
# Tab 7: 오프라인 이벤트 SNS 언급량 변화 크롤링
# ==========================================
with tabs[6]: # 사용하시는 SNS 탭 번호에 맞게 조정하세요
    st.subheader("📱 SNS(블로그 & 인스타그램) 언급량 분석")
    st.caption("네이버 블로그와 인스타그램에서 'KODEX ETF' 관련 최신 버즈량을 측정하고 트렌드를 분석합니다.")

    # Streamlit Secrets에서 네이버 개발자 센터 API 키 가져오기
    NAVER_CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET")
    
    # 검색어 설정
    SNS_SEARCH_QUERY = "KODEX ETF"

    # 💡 [핵심 보완] 네이버 블로그 수집 함수
    def fetch_naver_blog_counts(query):
        import requests
        import pandas as pd
        import urllib.parse
        
        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            st.warning("⚠️ 네이버 API 키(CLIENT_ID / SECRET)가 Secrets에 등록되지 않았습니다.")
            return pd.DataFrame()
            
        encoded_query = urllib.parse.quote(query)
        # 유사도순(sim) 혹은 최신순(date)으로 최대 100개 수집
        url = f"https://openapi.naver.com/v1/search/blog.json?query={encoded_query}&display=100&sort=date"
        
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                
                if not items:
                    return pd.DataFrame()
                
                blog_data = []
                for item in items:
                    # 네이버는 'postdate' 필드에 '20260608' 형태로 날짜를 줍니다.
                    raw_date = item.get("postdate", "")
                    if raw_date and len(raw_date) == 8:
                        formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                    else:
                        formatted_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                        
                    blog_data.append({
                        "날짜": formatted_date,
                        "채널": "네이버 블로그",
                        "카운트": 1
                    })
                
                df = pd.DataFrame(blog_data)
                # 날짜별로 묶어서 언급량 계산
                df_grouped = df.groupby(["날짜", "채널"]).size().reset_index(name="언급량")
                return df_grouped
            else:
                st.error(f"🚨 네이버 API 호출 실패 (에러 코드: {res.status_code})")
                return pd.DataFrame()
        except Exception as e:
            st.error(f"⚠️ 네이버 블로그 데이터 가공 중 에러 발생: {e}")
            return pd.DataFrame()

    # 실행 버튼
    if st.button("SNS 언급량 데이터 동기화 🔄", key="btn_sns_monitor"):
        progress = st.progress(0)
        status = st.empty()
        
        # [Step 1] 네이버 블로그 데이터 수집
        status.text("📝 네이버 블로그 언급량 데이터 긁어오는 중...")
        df_blog = fetch_naver_blog_counts(SNS_SEARCH_QUERY)
        progress.progress(50)
        
        # [Step 2] 인스타그램 데이터 수집 (기존에 잘 되던 로직이 있다고 가정)
        status.text("📸 인스타그램 언급량 데이터 가져오는 중...")
        # (기존에 작성하셨던 인스타그램 데이터프레임 양식을 그대로 유지해 주세요)
        # 여기서는 예시용 빈 데이터프레임 처리를 해두었습니다. 기존 코드가 있다면 매칭해 주세요.
        df_insta = pd.DataFrame() 
        
        # 임시 인스타그램 더미 데이터 생성 (테스트용/기존 코드 있으면 대체 가능)
        if df_insta.empty:
            import pandas as pd
            df_insta = pd.DataFrame([
                {"날짜": pd.Timestamp.now().strftime('%Y-%m-%d'), "채널": "인스타그램", "언급량": 5}
            ])
        progress.progress(80)
        
        # [Step 3] 데이터 병합 및 시각화 차트 그리기
        status.text("📊 SNS 트렌드 차트 생성 중...")
        
        import pandas as pd
        import plotly.express as px
        
        # 데이터 통합
        frames = []
        if not df_blog.empty:
            frames.append(df_blog)
        if not df_insta.empty:
            frames.append(df_insta)
            
        if frames:
            df_total = pd.concat(frames, ignore_index=True)
            # 날짜순 정렬
            df_total = df_total.sort_values(by="날짜")
            
            st.markdown("### 📈 채널별 최신 언급량 트렌드")
            # 선그래프로 블로그와 인스타 트렌드 시각화
            fig = px.line(df_total, x="날짜", y="언급량", color="채널", markers=True,
                          title=f"'{SNS_SEARCH_QUERY}' SNS 채널별 버즈량 비교",
                          labels={"언급량": "게시글 수 (건)"})
            st.plotly_chart(fig, use_container_width=True)
            
            # 테이블로도 표기
            st.markdown("#### 📋 세부 데이터 확인")
            st.dataframe(df_total, use_container_width=True)
            
            progress.progress(100)
            status.text("✅ SNS 모니터링 데이터 업데이트 완료!")
        else:
            progress.progress(100)
            status.text("❌ 수집 실패")
            st.warning("수집된 SNS 데이터가 존재하지 않습니다. API 권한 및 검색어를 확인해 주세요.")

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
