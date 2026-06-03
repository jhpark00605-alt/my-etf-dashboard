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
    # ↓ 여기서부터는 모두 앞공백 4칸(들여쓰기)이 유지되어야 합니다.
    st.subheader("🎬 주요 증권사 유튜브 마케팅 모니터링")
    st.markdown("4대 증권사 채널의 영상을 전수 조사하여 **Gemini**가 마케팅 전략을 도출합니다.")

    # [설정] API 키와 기간 선택
    # 실제 배포 시에는 st.secrets를 사용하는 것이 안전합니다.
    MY_YT_KEY = st.secrets.get("YOUTUBE_API_KEY", "여기에_유튜브_키_입력")
    MY_GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "여기에_제미나이_키_입력")

    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("조회 시작일", datetime.now() - timedelta(days=7), key="yt_start")
    with col_date2:
        end_date = st.date_input("조회 종료일", datetime.now(), key="yt_end")

    # 분석 대상 (기존 설정 유지)
    TARGET_BROKERAGES = {
        "미래에셋증권": "UCZS9wEZ4itPbBZk_sqccXfw",
        "키움증권": "UCZW1d7B2nYqQUiTiOnkirrQ",
        "삼성증권": "UCq7h8qFlHN5FL_T6waKZllw",
        "한국투자증권": "UCU6f21g_qaJk6rkX-IF6X2g"
    }

    # 내부 함수: 자막 추출
    def fetch_transcript_safe(video_id):
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            return " ".join([item['text'] for item in transcript_list])[:1500] # 분석을 위해 1500자 제한
        except:
            return "자막 데이터 없음"

    # 내부 함수: 유튜브 데이터 수집
    def collect_youtube_data(name, channel_id, s_date, e_date, api_key):
        url = "https://www.googleapis.com/youtube/v3/search"
        p_after = (datetime.combine(s_date, datetime.min.time()) - timedelta(hours=9)).isoformat() + "Z"
        p_before = (datetime.combine(e_date, datetime.max.time()) - timedelta(hours=9)).isoformat() + "Z"
        
        params = {
            "key": api_key, "channelId": channel_id, "part": "snippet", "order": "date",
            "maxResults": 10, "publishedAfter": p_after, "publishedBefore": p_before, "type": "video"
        }
        
        try:
            res = requests.get(url, params=params).json()
            video_list = []
            for item in res.get("items", []):
                v_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                desc = item["snippet"]["description"]
                pub_date = item["snippet"]["publishedAt"][:10]
                transcript = fetch_transcript_safe(v_id)
                
                video_list.append(f"- [{pub_date}] 제목: {title}\n  설명: {desc}\n  내용: {transcript}")
            
            return f"\n### [{name}]\n" + "\n".join(video_list) if video_list else f"\n### [{name}]\n기간 내 영상 없음"
        except Exception as e:
            return f"\n### [{name}]\n데이터 수집 오류: {e}"

    # 2. 실행 버튼
    if st.button("유튜브 트렌드 분석 실행 🚀"):
        if not yt_api_key or not gemini_api_key:
            st.error("⚠️ YouTube 및 Gemini API 키를 모두 입력해 주세요.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_data_buffer = ""
            
    유튜브 자막(스크립트) 추출 함수
# ==========================================
def fetch_video_transcript(video_id):
    """
    영상 ID를 받아 자막을 추출합니다.
    공식 한국어 자막(ko)이 없으면 자동 생성된 한국어 자막(a.ko)을 우회 수집합니다.
    """
    try:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text[:2000]
        except Exception:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en']) 
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text[:2000]
            
    except Exception as e:
        return f"자막 데이터 추출 불가 (사유: {str(e)})"

# ==========================================
# 전수 수집 엔진 (시차 보정 탑재, 키워드 필터 제거)
# ==========================================
def fetch_all_youtube_data(channel_name, channel_id, start_date_str, end_date_str):
    print(f"\n-> {channel_name} 채널 기간 내 전수 스캔 시작 ({start_date_str} ~ {end_date_str})...")
    url = "https://www.googleapis.com/youtube/v3/search"
    
    # [시차 보정] 한국 시각(KST)을 입력받아 유튜브 서버 기준시(UTC)로 9시간 역산 변환
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    
    start_dt_utc = start_dt - timedelta(hours=9)
    end_dt_utc = end_dt - timedelta(hours=9)
    
    published_after = start_dt_utc.isoformat() + "Z"
    published_before = end_dt_utc.isoformat() + "Z"
    
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 15, # 해당 기간 내 최대 15개 영상 전수 조사
        "publishedAfter": published_after,
        "publishedBefore": published_before,
        "type": "video"
    }
    
    try:
        response = requests.get(url, params=params).json()
        video_entries = []
        
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            desc = item["snippet"]["description"]
            pub_at = item["snippet"]["publishedAt"][:10]
            
            print(f"   [수집 완료] {title[:25]}...")
            transcript = fetch_video_transcript(video_id)
            
            video_entry = (
                f"- [업로드일: {pub_at}] 제목: {title}\n"
                f"  설명: {desc}\n"
                f"  내용(자막): {transcript}\n"
            )
            video_entries.append(video_entry)
                
        # 구조화 데이터 패키징
        result_payload = f"■ 해당 기간 업로드 확인된 총 영상: {len(video_entries)}건\n\n"
        result_payload += "[전체 영상 세부 목록]\n" + "\n".join(video_entries) if video_entries else "[전체 영상 세부 목록] 없음\n"
        
        print(f"   [완료] 총 {len(video_entries)}건의 영상 데이터 및 자막 버퍼 적재 완료")
        return result_payload

    except Exception as e:
        return f"데이터 수집 중 치명적 오류 발생: {str(e)}"

# ==========================================
# Gemini 모니터링 대시보드 변환 엔진
# ==========================================
def generate_filtered_report(raw_data, start_date, end_date):
    print("\n[시스템] 전수 수집 데이터 취합 완료. Gemini가 이메일용 요약 대시보드를 구축합니다...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    당신은 자산운용사 ETF 전략실의 데이터 자동화 봇입니다. 
    출근하는 팀원들이 이메일 화면에서 3초 만에 핵심만 파악할 수 있도록, 불필요한 미사여구(서론, 결론, 공지사항)를 완전히 제외하고 아래 [출력 포맷]에 맞춰 데이터만 가공해 주세요.

    ⚠️ [주의] 수집된 데이터에는 웹드라마, 브이로그, 단순 예능, 이벤트 안내 등 ETF/투자 전략과 무관한 콘텐츠가 섞여 있을 수 있습니다. 데이터의 [제목], [설명], [자막]을 당신이 직접 판단하여 무관한 콘텐츠는 포맷의 '기타' 수치로 빼고, 오직 '진짜 투자/상품 관련 콘텐츠'만 추출하여 테마와 액션 플랜을 도출하세요.

    [수집된 데이터셋]
    {raw_data}

    [출력 포맷]
    ### 📊 주간 증권사 채널 요약 ({start_date} ~ {end_date})

    | 증권사 | 콘텐츠 현황 | 이번 주 핵심 테마 (TOP 1) | 운용사 즉시 대응 방향 (Action Plan) |
    | :--- | :--- | :--- | :--- |
    | 미래에셋 | 주식/투자 N건<br>기타(드라마/이벤트) N건 | **[핵심단어]** (예: 미국 배당성장) | - **타깃:** [MTS/PB/상품부 중 택1]<br>- **내용:** [제안할 자사 ETF 및 세일즈 명분 핵심 1줄] |
    | 키움증권 | 주식/투자 N건<br>기타(드라마/이벤트) N건 | **[핵심단어]** | - **타깃:** [MTS/PB/상품부 중 택1]<br>- **내용:** [제안할 자사 ETF 및 세일즈 명분 핵심 1줄] |
    | 삼성증권 | 주식/투자 N건<br>기타(드라마/이벤트) N건 | **[핵심단어]** | - **타깃:** [MTS/PB/상품부 중 택1]<br>- **내용:** [제안할 자사 ETF 및 세일즈 명분 핵심 1줄] |
    | 한국투자 | 주식/투자 N건<br>기타(드라마/이벤트) N건 | **[핵심단어]** | - **타깃:** [MTS/PB/상품부 중 택1]<br>- **내용:** [제안할 자사 ETF 및 세일즈 명분 핵심 1줄] |

    ---

    ### 💡 이번 주 원포인트 마켓 트렌드
    - **종합 동향:** (예: 이번 주 4대 증권사 모두 반도체 밸류에이션 재평가를 언급하며 테크 중심 마케팅으로 일제히 회귀함. 채권/금리형 소폭 둔화.)
    - **공략 기회:** (예: 키움이 배당 마케팅에 예산을 태우기 시작했으므로 당사 커버드콜 상품 매칭 제안 적기.)
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Gemini 리포트 생성 실패: {str(e)}"

# ==========================================
# 메인 제어문
# ==========================================
if __name__ == "__main__":
    print("==================================================")
    print("  자동 메일링 연동형 증권사 모니터링 시스템 가동   ")
    print("==================================================")
    
    # 💡 조회 및 분석을 원하시는 기간을 입력하세요 (YYYY-MM-DD)
    START_DATE = "2026-05-24"
    END_DATE = "2026-05-31"
    
    aggregated_payload = ""
    
    for name, channel_id in TARGET_BROKERAGES.items():
        # 전수 수집 함수 호출
        channel_result = fetch_all_youtube_data(name, channel_id, START_DATE, END_DATE)
        aggregated_payload += f"\n### [하우스 채널명: {name}]\n{channel_result}\n"
        aggregated_payload += "==================================================\n"
        
    # Gemini 분석 수행
    final_clean_report = generate_filtered_report(aggregated_payload, START_DATE, END_DATE)
    
    print("==================================================")
    print(final_clean_report)

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
