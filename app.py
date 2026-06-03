import streamlit as st
import requests
import xml.etree.ElementTree as ET

# 1. 스타일링 및 화면 꾸미기
st.set_page_config(page_title="ETF 뉴스 대시보드", layout="wide")
st.title("📈 ETF 실시간 뉴스 대시보드")
st.markdown("---")

# 2. 검색창 추가
query = st.text_input("검색하고 싶은 키워드를 입력하세요", "ETF")

if st.button("뉴스 가져오기"):
    try:
        # RSS 주소에 검색어(query) 반영
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        root = ET.fromstring(res.content)
        items = root.findall('.//item')
        
        if not items:
            st.warning("뉴스를 찾지 못했습니다.")
        else:
            # 3. 링크 연결 및 깔끔한 출력
            for item in items[:10]:
                title = item.find('title').text
                link = item.find('link').text
                
                # 클릭하면 링크로 이동하는 박스 형태
                st.markdown(f"### [{title}]({link})")
                st.write(f"🔗 [기사 원문 보기]({link})")
                st.divider()
                
    except Exception as e:
        st.error(f"오류 발생: {e}")
