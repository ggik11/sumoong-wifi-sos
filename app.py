import streamlit as st
import time
import requests
import os

# --- 1. 개인 설정 ---
TELEGRAM_TOKEN = "8249458560:AAF41U3OaJYKHyU-VCxMmzSR9B-tXgfLam8"
CHAT_ID = "7320610053"
THRESHOLD = 50  # 테스트가 끝났다면 다시 50으로 설정!

# --- 2. 텔레그램 메시지 발송 함수 ---
def send_telegram_msg(count):
    message = f"🚨 [와이파이 비상] 현재 1분당 신고 수 {count}회 돌파! 즉시 점검 바랍니다."
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.get(url, params=params)
    except Exception as e:
        st.error(f"알림 전송 실패: {e}")

# --- 3. 웹 화면 구성 ---
st.set_page_config(page_title="와이파이 신고 센터", page_icon="📶")

# 버튼 디자인 커스텀
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 24px !important;
        background-color: #FF4B4B;
        color: white;
        border-radius: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 학교 와이파이 민원 센터")
st.info("와이파이가 자주 끊기나요? 아래 마스코트를 클릭해 실시간 상황을 알리세요!")

# 클릭 데이터 관리
if 'clicks' not in st.session_state:
    st.session_state.clicks = []
if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = 0

# --- 4. 마스코트 이미지 및 클릭 버튼 ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 파일명이 mascot.jpg인지 확인하세요!
    image_path = "mascot.jpg" 
    
    if os.path.exists(image_path):
        st.image(image_path, caption="와이파이 때문에 화난 마스코트", use_container_width=True)
    else:
        st.warning("⚠️ mascot.jpg 파일을 찾을 수 없습니다. (폴더에 이미지를 넣어주세요)")
    
    if st.button("🚨 지금 바로 신고하기"):
        st.session_state.clicks.append(time.time())
        st.balloons()

# --- 5. 데이터 처리 ---
current_time = time.time()
st.session_state.clicks = [t for t in st.session_state.clicks if current_time - t < 60]
click_count = len(st.session_state.clicks)

# --- 6. 실시간 현황 대시보드 ---
st.divider()
c1, c2 = st.columns(2)
c1.metric("최근 1분간 신고 수", f"{click_count}회")
c2.metric("통보 기준치", f"{THRESHOLD}회")

# --- 7. 자동 통보 로직 (5분 간격 제한) ---
if click_count >= THRESHOLD and (current_time - st.session_state.last_alert_time > 300):
    send_telegram_msg(click_count)
    st.session_state.last_alert_time = current_time
    st.error("⚠️ 신고 폭주! 학교 전산소(관리자)에 상황을 자동 전달했습니다.")

st.caption("본 서비스는 학생들의 학습권 보장을 위한 자발적 민원 수집 도구입니다.")