import streamlit as st
import os 
import base64
import time
import requests
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ==========================================
# 1. INITIAL SETUP & CONFIG (ต้องเอาตั้งค่าเพจขึ้นก่อนเสมอ!)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="wide")

try:
    FB_API_KEY = st.secrets["firebase"]["api_key"]
    FB_URL = st.secrets["firebase"]["firebase_url"]
    PROJECT_ID = st.secrets["firebase"]["project_id"]
except Exception:
    FB_API_KEY = "MOCK_API_KEY"
    FB_URL = "https://mock-synapse-default-rtdb.firebaseio.com"
    PROJECT_ID = "SYNAPSE-LOCAL-MODE"

@st.cache_resource
def init_system():
    # ฟังก์ชันนี้เอาไว้แคชทรัพยากรระบบหลัก
    return True

init_system()

# ทำการตรวจสอบและสร้างค่ากำหนดใน Session State ให้ปลอดภัยแบบ 100%
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00E5FF" 
if 'accent_color' not in st.session_state: st.session_state.accent_color = "#FF0055" 
if 'success_color' not in st.session_state: st.session_state.success_color = "#39FF14" 
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"     
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_phone' not in st.session_state: st.session_state.user_phone = ""
if 'song_index' not in st.session_state: st.session_state.song_index = 0

# ==========================================
# 2. FIREBASE REALTIME DATABASE FUNCTIONS
# ==========================================
def get_firebase_data(path):
    try:
        response = requests.get(f"{FB_URL}/{path}.json", timeout=5)
        if response.status_code == 200 and response.json():
            return response.json()
    except Exception:
        pass
    return {}

def push_firebase_data(path, data):
    try:
        requests.post(f"{FB_URL}/{path}.json", json=data, timeout=5)
        return True
    except Exception:
        return False

# ==========================================
# 3. UI STYLING & GLOBAL LOGO (กรอบนีออนหมุนกระดุกะดิก)
# ==========================================
current_bg = st.session_state.get('bg_color', '#000000')
current_theme = st.session_state.get('theme_color', '#00E5FF')
current_accent = st.session_state.get('accent_color', '#FF0055')
current_success = st.session_state.get('success_color', '#39FF14')

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {{ background-color: {current_bg} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {current_theme} !important; color: #FFFFFF !important; background: linear-gradient(45deg, {current_theme}33, {current_accent}33) !important; border-radius: 10px; box-shadow: 0 0 10px {current_theme}55; }}
    .stButton>button:hover {{ background: linear-gradient(45deg, {current_theme}, {current_accent}) !important; color: black !important; box-shadow: 0 0 20px {current_theme}; }}
    .neon-box {{ border: 1px solid {current_theme}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 15px {current_accent}; background-color: #050505; }}
    
    .stTabs [data-baseweb="tab"] {{ color: #FFFFFF !important; font-weight: bold; font-family: 'Orbitron', sans-serif; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {current_success} !important; border-bottom-color: {current_success} !important; }}
    h1, h2, h3, p, label, span {{ font-family: 'Orbitron', sans-serif; }}
    
    .neon-logo-container {{
        width: 150px; height: 150px; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center;
        position: relative; border-radius: 50%; padding: 5px; background: #000; overflow: hidden;
    }}
    .neon-logo-container::before {{
        content: ''; position: absolute; width: 250px; height: 250px;
        background: conic-gradient({current_theme}, {current_accent}, {current_success}, {current_theme});
        animation: spinLogoBorder 4s linear infinite; z-index: 1;
    }}
    .neon-logo-container::after {{
        content: ''; position: absolute; inset: 4px; background: #000; border-radius: 50%; z-index: 2;
    }}
    .neon-logo-img {{
        width: 138px; height: 138px; border-radius: 50%; object-fit: cover; z-index: 3; position: relative;
    }}
    @keyframes spinLogoBorder {{
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def show_neon_logo():
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    logo_path = os.path.join(current_dir, "logo1.png")
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        st.markdown(f"""
            <div class="neon-logo-container">
                <img src="data:image/png;base64,{b64}" class="neon-logo-img">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="neon-logo-container">
                <div style="z-index:3; color:{current_success}; font-weight:bold; font-size:20px; text-shadow: 0 0 10px {current_success};">SYNAPSE</div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. MODULES (แต่ละห้องควบคุม)
# ==========================================

def room_core():
    st.markdown(f"<h2 style='color:{current_theme}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    user_phone_display = st.session_state.get('user_phone', 'Unknown')
    st.markdown(f"""
        <div class="neon-box" style="border-color:{current_accent};">
            <h1 style="margin:0; color:{current_success}; text-shadow: 0 0 15px {current_success};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:5px 0 0 0; font-size:16px; color:#FFFFFF;">AGENT: {user_phone_display}</p>
            <p style="margin:5px 0 0 0; color:{current_theme}; font-style:italic;">'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
        </div>
    """, unsafe_allow_html=True)
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ System Day-Uptime: {progress*100:.2f}%")
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown(f"<h2 style='color:{current_theme};'>🛰️ SATELLITE RADAR & GPS แปลงนา</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {current_success};'>🚜 คำนวณพื้นที่จริงด้วยดาวเทียมไฮบริด ลากเส้นรอบคันนาเพื่อวัดขนาด ไร่-งาน ป้องกันการโกง!</p>", unsafe_allow_html=True)
    
    default_lat, default_lng = 15.9513057, 103.5796196
    map_html_code = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
    <script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>
    
    <div id="map" style="width: 100%; height: 350px; border-radius: 12px; border: 2px solid {current_theme}; box-shadow: 0 0 15px {current_accent};"></div>
    <script>
        var map = L.map('map').setView([{default_lat}, {default_lng}], 15);
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
    </script>
    """
    with st.container():
        components.html(map_html_code, height=380)

def room_comms():
    st.markdown(f"<h2 style='color:{current_theme};'>💬 COMM CENTER</h2>", unsafe_allow_html=True)
    chats = get_firebase_data("global_chat")
    chat_box = ""
    if chats:
        for key in sorted(chats.keys())[-10:]:
            chat_box += f"🔵 **{chats[key].get('user', 'Unknown')}**: {chats[key].get('msg', '')}\n\n"
        st.markdown(chat_box)
    
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("กรอกสัญญาณข้อความ:")
        if st.form_submit_button("SEND SIGNAL") and msg:
            user_phone_current = st.session_state.get('user_phone', 'Unknown')
            push_firebase_data("global_chat", {'user': user_phone_current, 'msg': msg, 'ts': time.time()})
            st.rerun()

def room_music():
    st.markdown(f"<h2 style='color:{current_theme}; text-shadow: 0 0 20px {current_theme}; text-align:center;'>🎧 SYNAPSE CONTINUOUS PLAYER</h2>", unsafe_allow_html=True)
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    try:
        songs = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")])
    except Exception:
        songs = []
        
    if not songs:
        st.warning("⚠️ ไม่พบไฟล์เสียงสัจจะ (.mp3) ในระบบ")
        return
        
    song_data_list = []
    for s in songs:
        try:
            with open(os.path.join(current_dir, s), "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                song_data_list.append({"name": s, "b64": b64})
        except:
            pass

    import json
    songs_json = json.dumps(song_data_list)
    current_song_idx = st.session_state.get('song_index', 0)

    player_html = f"""
    <div style="background: #000; border: 3px solid {current_accent}; border-radius: 20px; padding: 20px; box-shadow: 0 0 25px {current_theme};">
        <div style="background: #050505; border: 1px solid {current_theme}; border-radius: 8px; margin-bottom: 15px; padding: 10px; text-align:center;">
            <span style="color:{current_success}; font-weight:bold;">🛸 NOW STREAMING:</span>
            <h3 id="track-title" style="color:white; margin:5px 0; font-family:sans-serif;">กำลังเตรียมช่องสัญญาณ...</h3>
        </div>
        
        <div style="margin-bottom:15px;">
            <label style="color:white; font-size:12px;">เลือกช่องสัญญาณเพลงโดยตรง:</label>
            <select id="track-select" style="width:100%; padding:10px; background:#111; color:white; border:1px solid {current_theme}; border-radius:5px;"></select>
        </div>

        <audio id="main-player" controls style="width:100%; margin-top:5px;"></audio>
        
        <div style="margin-top:15px; display:flex; justify-content:space-between;">
            <button id="btn-prev" style="flex:1; margin-right:5px; padding:10px; background:transparent; border:1px solid {current_theme}; color:white; border-radius:5px; cursor:pointer;">⏮️ PREV</button>
            <button id="btn-next" style="flex:1; margin-left:5px; padding:10px; background:transparent; border:1px solid {current_theme}; color:white; border-radius:5px; cursor:pointer;">NEXT ⏭️</button>
        </div>
    </div>

    <script>
        const playlist = {songs_json};
        let currentIndex = {current_song_idx};
        
        const player = document.getElementById('main-player');
        const title = document.getElementById('track-title');
        const selector = document.getElementById('track-select');
        
        if (playlist.length > 0) {{
            playlist.forEach((song, idx) => {{
                let opt = document.createElement('option');
                opt.value = idx;
                opt.innerText = song.name;
                if(idx === currentIndex) opt.selected = true;
                selector.appendChild(opt);
            }});

            function loadTrack(index) {{
                if(index < 0) index = playlist.length - 1;
                if(index >= playlist.length) index = 0;
                currentIndex = index;
                selector.value = index;
                
                title.innerText = playlist[currentIndex].name;
                player.src = "data:audio/mp3;base64," + playlist[currentIndex].b64;
                player.play().catch(e => console.log("สัจจะของเบราว์เซอร์: รอผู้ใช้กดอนุญาตสัญญาณเสียงก่อน"));
            }}

            player.onended = function() {{
                loadTrack(currentIndex + 1);
            }};

            selector.onchange = function() {{
                loadTrack(parseInt(this.value));
            }};

            document.getElementById('btn-next').onclick = function() {{ loadTrack(currentIndex + 1); }};
            document.getElementById('btn-prev').onclick = function() {{ loadTrack(currentIndex - 1); }};

            loadTrack(currentIndex);
        }}
    </script>
    """
    with st.container():
        components.html(player_html, height=320)

def room_sensor():
    st.markdown(f"<h2 style='color:{current_theme}; text-align:center;'>📟 SYNAPSE SENSOR HUB</h2>", unsafe_allow_html=True)
    st.caption("ระบบดักจับความเคลื่อนไหวทางกายภาพเรียลไทม์")

# ==========================================
# 5. MAIN CONTROL FLOW
# ==========================================
def main():
    # 🌟 แก้ไขจุดตาย: ใช้การดึงข้อมูลแบบปลอดภัย .get() ป้องกันการระเบิดของเซสชันเมื่อรันหน้าเซิร์ฟเวอร์คลาวด์
    is_logged_in = st.session_state.get('logged_in', False)
    
    if not is_logged_in:
        show_neon_logo()
        st.markdown(f"<h1 style='text-align:center; color:{current_theme}; margin-top:0;'>SYNAPSE AUTH</h1>", unsafe_allow_html=True)
        
        with st.container():
            phone_input = st.text_input("เบอร์โทรศัพท์ส่วนบุคคล (ของจริง):", value="+66970801941", key="login_phone")
            otp_input = st.text_input("กรอกรหัสล็อกอินผ่านระบบ OTP:", value="753275", type="password", key="login_otp")
            
            if st.button("🔓 เปิดสัญญาณสัจจะความปลอดภัยเข้าแอป", use_container_width=True, key="login_btn"):
                if phone_input in ["+66970801941", "+66800924262"] and otp_input == "753275":
                    st.session_state.logged_in = True
                    st.session_state.user_phone = phone_input
                    st.rerun()
                else:
                    st.error("❌ สัญญาณรหัสสัจจะผิดพลาด กรุณากรอกใหม่")

    else:
        with st.sidebar:
            show_neon_logo()
            user_phone_current = st.session_state.get('user_phone', 'Unknown')
            st.markdown(f"<h3 style='text-align:center; color:{current_success}; margin-top:0;'>🛸 ONLINE</h3>", unsafe_allow_html=True)
            st.write(f"AGENT: `{user_phone_current}`")
            
            st.markdown("---")
            st.write("⚙️ **ส่วนผู้ใช้ปรับแต่งโทนสีเอง (Realtime-Custom)**")
            st.session_state.theme_color = st.color_picker("น้ำเงิน/ฟ้า นีออนหลัก", st.session_state.get('theme_color', '#00E5FF'), key="cp_theme")
            st.session_state.accent_color = st.color_picker("แดง/ชมพู นีออนตัดขอบ", st.session_state.get('accent_color', '#FF0055'), key="cp_accent")
            st.session_state.success_color = st.color_picker("เขียวนีออนสถานะ", st.session_state.get('success_color', '#39FF14'), key="cp_success")
            st.session_state.bg_color = st.color_picker("สีพื้นหลังหน้าจอแอป", st.session_state.get('bg_color', '#000000'), key="cp_bg")
            
            st.markdown("---")
            if st.button("🚪 LOGOUT (ตัดการเชื่อมต่อ)", key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.user_phone = ""
                st.rerun()
            st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

        tabs = st.tabs(["🚀 CORE COMMAND", "🛰️ RADAR / GPS", "💬 COMMS FEED", "🎧 NON-STOP MUSIC", "📟 SENSOR HUB"])
        with tabs[0]: room_core()
        with tabs[1]: room_radar()
        with tabs[2]: room_comms()
        with tabs[3]: room_music()
        with tabs[4]: room_sensor()

if __name__ == "__main__":
    main()
