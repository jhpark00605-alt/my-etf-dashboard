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

    # 3. 실행 로직
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
                # [Step 2] 내 키로 사용 가능한 모델 자동 찾기 (진단 및 해결)
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
                        selected_model = available_models[0] # 아무거나 첫 번째 모델 선택
                    
                    if not selected_model:
                        st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키 설정을 확인하세요.")
                        st.write("조회된 모델 목록:", available_models)
                    else:
                        # [Step 3] 선택된 모델로 분석 실행
                        status.text(f"🤖 {selected_model.split('/')[-1]} 모델로 분석 중...")
                        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={API_KEY_GEMINI}"
                        
                        payload = {
                            "contents": [{"parts": [{"text": f"국내 증권사 유튜브 마케팅 트렌드 분석 리포트 작성해줘:\n\n{all_text}"}]}]
                        }
                        
                        res = requests.post(gen_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                        
                        if res.status_code == 200:
                            analysis = res.json()['candidates'][0]['content']['parts'][0]['text']
                            progress.progress(100)
                            status.text("✅ 분석 완료!")
                            st.markdown("---")
                            st.markdown(analysis)
                        else:
                            st.error(f"⚠️ 분석 실패 (Error {res.status_code})")
                            st.json(res.json())
                            
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                
# ==========================================
# Tab 3: 타운용사(경쟁사) 동향
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
            status.text(f"🌐 {brand} 관련 최신 뉴스 수집 중...")
            encoded_query = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
            
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(rss_url, headers=headers)
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")[:10]  # 상위 10개 추출
                titles = [item.title.text for item in items]
                all_brand_news[brand] = "\n".join(titles) if titles else "최신 뉴스 없음"
            except Exception as e:
                all_brand_news[brand] = f"뉴스 수집 실패 ({e})"
            
            progress.progress(int((idx + 1) * 15)) # 진행 바 업데이트

        # 3. 내 API 키로 사용 가능한 Gemini 모델 자동 탐색 (앞서 검증된 성공 로직!)
        status.text("📡 사용 가능한 AI 모델 조회 중...")
        try:
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
                # 4. 선택된 AI 모델로 데이터 분석
                status.text(f"🤖 {selected_model.split('/')[-1]} 모델로 브랜드별 핵심 이슈 요약 중...")
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={GEMINI_KEY}"
                
                # AI에게 넘겨줄 텍스트 구조화
                news_context = ""
                for brand, news in all_brand_news.items():
                    news_context += f"[{brand} 뉴스 목록]\n{news}\n\n"
                    
                prompt = f"""
                제공된 운용사별 뉴스 데이터를 기반으로, 각 운용사(KODEX, TIGER, RISE, ACE)의 가장 중요한 최근 핵심 이슈, 신규 상장 소식, 또는 마케팅 포인트를 딱 2개씩만 명확하게 요약해줘.
                반드시 아래 지정된 JSON 형식으로만 응답해야 해. 앞뒤로 다른 설명이나 텍스트는 절대 붙이지 마.

                [응답 형식 JSON]
                {{
                    "KODEX": ["첫 번째 이슈 요약 문장", "두 번째 이슈 요약 문장"],
                    "TIGER": ["첫 번째 이슈 요약 문장", "두 번째 이슈 요약 문장"],
                    "RISE": ["첫 번째 이슈 요약 문장", "두 번째 이슈 요약 문장"],
                    "ACE": ["첫 번째 이슈 요약 문장", "두 번째 이슈 요약 문장"]
                }}

                데이터:
                {news_context}
                """
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post(gen_url, json=payload)
                
                if res.status_code == 200:
                    raw_res = res.json()['candidates'][0]['content']['parts'][0]['text']
                    clean_res = raw_res.replace("```json", "").replace("
```", "").strip()
                    summary_data = json.loads(clean_res)
                    
                    progress.progress(100)
                    status.text("✅ 운용사별 실시간 이슈 업데이트 완료!")
                    st.markdown("---")
                    
                    # 5. 기존 4단 레이아웃(컬럼 및 색상 박스) 구조에 데이터 바인딩
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.success("**KODEX (삼성)**")
                        issues = summary_data.get("KODEX", ["이슈 요약 실패", "데이터를 확인하세요."])
                        for issue in issues:
                            st.write(f"- {issue}")
                            
                    with col_b:
                        st.warning("**TIGER (미래에셋)**")
                        issues = summary_data.get("TIGER", ["이슈 요약 실패", "데이터를 확인하세요."])
                        for issue in issues:
                            st.write(f"- {issue}")
                            
                    with col_c:
                        st.info("**RISE (KB)**")
                        issues = summary_data.get("RISE", ["이슈 요약 실패", "데이터를 확인하세요."])
                        for issue in issues:
                            st.write(f"- {issue}")
                            
                    with col_d:
                        st.error("**ACE (한국투자)**")
                        issues = summary_data.get("ACE", ["이슈 요약 실패", "데이터를 확인하세요."])
                        for issue in issues:
                            st.write(f"- {issue}")
                else:
                    st.error(f"AI 분석 실패 (Error {res.status_code})")
                    st.json(res.json())
        except Exception as e:
            st.error(f"오류 발생: {e}")

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
