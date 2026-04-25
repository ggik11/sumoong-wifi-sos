import streamlit as st
import time
import requests
import os

# --- 1. 설정 ---
TELEGRAM_TOKEN = "8249458560:AAF41U3OaJYKHyU-VCxMmzSR9B-tXgfLam8" ##텔레그램 봇 고유토큰값
CHAT_ID = "7320610053" ##개발자 고유 id
THRESHOLD = 15  # 임계치를 15로 변경
ALERT_COOLDOWN = 300  # 알림 간격 (5분)

# --- 2. 전역 데이터 및 사용자 식별 로직 ---
@st.cache_resource
def get_global_state():
    # clicks: [(timestamp, user_ip), ...] 형태의 튜플 리스트로 저장
    return {
        "clicks": [], 
        "last_alert_time": 0
    }

def get_remote_ip():
    """접속한 사용자의 IP를 가져오는 함수 (Streamlit 환경 전용)"""
    # Streamlit Cloud나 일반적인 배포 환경에서 작동하는 헤더 분석
    try:
        from streamlit.web.server.websocket_headers import _get_headers
        headers = _get_headers()
        if headers:
            return headers.get("X-Forwarded-For", "unknown").split(",")[0]
    except:
        return "unknown"
    return "unknown"

global_state = get_global_state()
user_ip = get_remote_ip()

# --- 3. 텔레그램 메시지 발송 함수 ---
def send_telegram_msg(count):
    message = f"🚨 [와이파이 비상] 서로 다른 {count}명의 학생이 장애를 신고했습니다! 즉시 확인 바랍니다."
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.get(url, params=params)
    except Exception as e:
        st.error(f"알림 전송 실패: {e}")

# --- 4. 웹 화면 구성 ---
st.set_page_config(page_title="클린 와이파이 신고 센터", page_icon="📶")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 120px;
        font-size: 26px !important;
        background-color: #007AFF;
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📶 와이파이 장애 공동 신고 센터")
st.info(f"정확한 집계를 위해 **1인당 1회(1분 기준)**만 신고가 반영됩니다. (현재 임계치: {THRESHOLD}명)")

# --- 5. 클릭 로직 (중복 방지) ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    image_path = "mascot.jpg" 
    if os.path.exists(image_path):
        st.image(image_path, caption="중복 신고는 시스템이 자동으로 제외합니다", use_container_width=True)
    
    # 버튼 클릭 처리
    if st.button("🚨 와이파이 장애 신고"):
        current_time = time.time()
        
        # 최근 1분 내에 동일 IP의 클릭 기록이 있는지 확인
        recent_user_clicks = [t for t, ip in global_state["clicks"] if ip == user_ip and current_time - t < 60]
        
        if not recent_user_clicks:
            global_state["clicks"].append((current_time, user_ip))
            st.balloons()
            st.success("신고가 정상 접수되었습니다.")
        else:
            st.warning("이미 신고하셨습니다. 잠시 후 다시 시도해주세요.")

# --- 6. 전역 데이터 처리 (중복 제거 및 카운팅) ---
current_time = time.time()

# 1) 1분 경과 데이터 제거
global_state["clicks"] = [(t, ip) for t, ip in global_state["clicks"] if current_time - t < 60]

# 2) 유니크한 IP 개수 파악 (중복 방지 논리의 핵심)
# 한 사람이 여러 번 기록되었더라도 set을 통해 고유한 인원수만 파악
unique_reporters = len(set(ip for t, ip in global_state["clicks"]))

# --- 7. dash 출력 ---
st.divider()
k1, k2 = st.columns(2)
k1.metric("현재 신고 인원", f"{unique_reporters}명")
k2.metric("통보 기준", f"{THRESHOLD}명")

# --- 8. 자동 통보 로직 ---
if unique_reporters >= THRESHOLD:
    time_since_last_alert = current_time - global_state["last_alert_time"]
    
    if time_since_last_alert > ALERT_COOLDOWN:
        send_telegram_msg(unique_reporters)
        global_state["last_alert_time"] = current_time
        st.error(f"⚠️ 임계치 도달! {unique_reporters}명의 신고 데이터를 기반으로 관리자 통보를 완료했습니다.")

st.caption("IP 기반 중복 제거 시스템이 적용 중입니다.")
