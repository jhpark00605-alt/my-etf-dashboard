import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ETF 통합 마케팅 대시보드", layout="wide")

# API 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 1. 사용 가능한 모델 리스트를 강제로 불러옵니다.
    models = genai.list_models()
    
    # 2. 'generateContent'가 가능한 모델 중 이름에 'flash'가 들어가는 것을 찾습니다.
    selected_model = None
    for m in models:
        if "generateContent" in m.supported_methods and "flash" in m.name:
            selected_model = m.name
            break
    
    # 3. 모델이 없으면 리스트의 첫 번째 모델이라도 사용합니다.
    if not selected_model:
        selected_model = [m.name for m in models if "generateContent" in m.supported_methods][0]
    
    model = genai.GenerativeModel(selected_model)
    st.sidebar.write(f"사용 중인 모델: {selected_model}") # 디버깅용 확인창

except Exception as e:
    st.error(f"API 설정 및 모델 연결 오류: {e}")
    st.stop()

# ... (이후 UI 코드 생략, 동일하게 유지)
