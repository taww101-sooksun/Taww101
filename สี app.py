import streamlit as st
import os 
import base64
import random
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. SETUP & NEON COLORS
# ==========================================
N_GREEN = "#39FF14"  # เขียวนีออน
N_RED   = "#FF0000"  # แดงนีออน
N_BLUE  = "#0000FF"  # น้ำเงินนีออน
N_GOLD  = "#FFD700"  # ทองนีออน
N_WHITE = "#FFFFFF"  # ขาวนีออน
BG_BLACK = "#000000" # ดำสนิท

@st.cache_resource
def init_system():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass
    return True

init_system()

# Initialize Session States
if 'user' not in st.session_state: st.session_state.user = "Ta101"
if 'song_index' not in st.session_state: st.session_state.song_index = 0

# ==========================================
# 2. UI STYLING (THE NEON OS)
# ==========================================
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    /* ซ่อน Streamlit UI */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stApp {{ background-color: {BG_BLACK} !important; color: {N_WHITE} !important; font-family: 'Orbitron', sans-serif; top: -60px; }}
    
    /* สไตล์ Tab สีน้ำเงิน */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #111; border: 1px solid {N_BLUE}; border-radius: 5px; color: {N_BLUE}; padding: 10px;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {N_BLUE}33 !important; border-color: {N_BLUE} !important; color: {N_WHITE} !important; }}

    /* ปุ่มกดสีเขียว */
    .stButton>button {{ 
        border: 2px solid {N_GREEN} !important; color: {N_GREEN} !important; 
        background: transparent !important; box-shadow: 0 0 10px {N_GREEN}33;
    }}
    .stButton>button:hover {{ background: {N_GREEN} !important; color: black !important; box-shadow: 0 0 20px {N_GREEN}; }}

    /* กล่องนีออนน้ำเงิน */
    .neon-box {{ 
        border: 2px solid {N_BLUE}; padding: 20px; border-radius: 15px; 
        text-align: center; box-shadow: inset 0 0 15px {N_BLUE}44, 0 0 10px {N_BLUE}44;
        background: rgba(0,0,0,0.8);
    }}
    
    /* ตัวหนังสือทองวิ้งๆ */
    @keyframes wink {{ 0%, 100% {{ opacity: 1; text-shadow: 0 0 15px {N_GOLD}; }} 50% {{ opacity: 0.4; }} }}
    .slogan-gold {{ color: {N_GOLD}; animation: wink 1.5s infinite; font-weight: bold; font-size: 18px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. THE ROOMS (MODULAR)
# ==========================================

def room_core():
    # Header: โลโก้เต้น + สโลแกนทอง
    logo_b64 = ""
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <div style="text-align:center; padding: 20px;">
            <img src="data:image/png;base64,{logo_b64}" style="width:100px; animation: dance 0.6s infinite;">
            <div class="slogan-gold">SYNAPSE อยู่นิ้งๆไม่เจ็บตัว</div>
        </div>
        <style> @keyframes dance {{ 0%, 100% {{ transform:scale(1); }} 50% {{ transform:scale(1.1) rotate(3deg); }} }} </style>
    """, unsafe_allow_html=True)

    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{N_GREEN}; text-shadow: 0 0 10px {N_GREEN};">{now.strftime('%H:%M:%S')}</h1>
            <p style="color:{N_WHITE};">CORE AGENT: {st.session_state.user}</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar():
    st.markdown(f"<h3 style='color:{N_BLUE}; text-shadow: 0 0 10px {N_BLUE};'>🛰️ SATELLITE RADAR</h3>", unsafe_allow_html=True)
    loc = get_geolocation()
    # ป้องกัน Error บรรทัด 75: เช็คพิกัดก่อนใช้
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    else:
        lat, lon = 13.7367, 100.5231 # พิกัดสำรอง (กทม.)
    
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    st.markdown(f"<style>.stMap {{ border: 2px solid {N_BLUE}; border-radius: 15px; overflow: hidden; }}</style>", unsafe_allow_html=True)
    st_folium(m, width="100%", height=400, key="radar")
    
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        st.toast("📡 พิกัดถูกส่งเข้าดาวเทียมแล้ว!")

def room_comms():
    st.markdown(f"<h3 style='color:{N_GREEN};'>💬 COMMS HUB</h3>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        msg = col1.text_input("Enter Signal...", placeholder="ส่งข้อความ...")
        up_file = col2.file_uploader("📁", type=['jpg', 'png'], label_visibility="collapsed")
        if st.form_submit_button("SEND SIGNAL ⚡"):
            f_b64 = base64.b64encode(up_file.getvalue()).decode() if up_file else None
            if msg or f_b64:
                db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'f': f_b64, 'ts': time.time()})
                st.rerun()

    # แสดงแชท (เขียว-ขาว-แดง)
    msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
    if msgs:
        for v in reversed(list(msgs.values())):
            is_me = v.get('u') == st.session_state.user
            color = N_GREEN if is_me else N_WHITE
            align = "right" if is_me else "left"
            border = f"border-right: 4px solid {N_GREEN}" if is_me else f"border-left: 4px solid {N_WHITE}"
            
            st.markdown(f"""
                <div style="text-align:{align}; margin-bottom:10px;">
                    <div style="display:inline-block; background:#111; {border}; padding:10px; border-radius:10px; max-width:80%;">
                        <small style="color:{N_RED};">{v.get('u')}</small><br>
                        <span style="color:{color};">{v.get('m','')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if v.get('f'): st.image(base64.b64decode(v['f']), width=200)

def room_music():
    st.markdown(f"<h3 style='color:{N_GOLD}; text-align:center;'>🎧 HOLOGRAPHIC MUSIC</h3>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs:
        st.warning("⚠️ ไม่พบไฟล์ .mp3")
        return
    
    s_a = st.selectbox("🎯 SELECT SOURCE", songs, index=st.session_state.song_index)
    song_b64 = base64.b64encode(open(s_a, "rb").read()).decode()
    
    # วิชวลไลเซอร์สีน้ำเงิน-ทอง
    viz_html = f"""
    <div style="background:#000; border:2px solid {N_GOLD}; border-radius:15px; padding:15px; text-align:center;">
        <canvas id="cv" style="width:100%; height:150px;"></canvas>
        <button id="pb" style="width:100%; padding:10px; background:transparent; border:1px solid {N_GREEN}; color:{N_GREEN}; border-radius:10px;">[ SYNC AUDIO ]</button>
        <audio id="ad" src="data:audio/mp3;base64,{song_b64}"></audio>
    </div>
    <script>
        const audio = document.getElementById('ad');
        const btn = document.getElementById('pb');
        const cv = document.getElementById('cv');
        const ctx = cv.getContext('2d');
        let aCtx, ans, src, data;

        btn.onclick = () => {{
            if(!aCtx) {{
                aCtx = new AudioContext();
                ans = aCtx.createAnalyser();
                src = aCtx.createMediaElementSource(audio);
                src.connect(ans); ans.connect(aCtx.destination);
                data = new Uint8Array(ans.frequencyBinCount);
                render();
            }}
            audio.paused ? audio.play() : audio.pause();
            btn.innerText = audio.paused ? "[ PAUSED ]" : "[ ACTIVE ]";
        }};

        function render() {{
            requestAnimationFrame(render);
            ans.getByteFrequencyData(data);
            ctx.clearRect(0,0,cv.width,cv.height);
            ctx.fillStyle = '{N_GOLD}';
            for(let i=0; i<data.length; i++) {{
                ctx.fillRect(i*2, cv.height - data[i]/2, 1, data[i]/2);
            }}
        }}
    </script>
    """
    components.html(viz_html, height=300)

def room_sensor():
    st.markdown(f"<h3 style='color:{N_RED}; text-align:center;'>📟 SENSOR ARRAY</h3>", unsafe_allow_html=True)
    sensor_js = f"""
    <div style="background:#000; border:2px solid {N_RED}; border-radius:15px; padding:20px; text-align:center; font-family:Orbitron;">
        <div style="margin-bottom:20px;">
            <small style="color:{N_WHITE};">MOTION MAGNITUDE</small>
            <h1 id="m_v" style="color:{N_RED}; font-size:50px;">1.00</h1>
        </div>
        <button id="s_b" style="width:100%; padding:15px; background:transparent; border:2px solid {N_RED}; color:{N_RED}; border-radius:10px;">[ START SENSORS ]</button>
    </div>
    <script>
        document.getElementById('s_b').onclick = async () => {{
            if(typeof DeviceMotionEvent.requestPermission === 'function') await DeviceMotionEvent.requestPermission();
            window.addEventListener('devicemotion', (e) => {{
                let a = e.accelerationIncludingGravity;
                let m = Math.sqrt(a.x*a.x + a.y*a.y + a.z*a.z) / 9.8;
                document.getElementById('m_v').innerText = m.toFixed(2);
            }});
            document.getElementById('s_b').style.display = 'none';
        }};
    </script>
    """
    components.html(sensor_js, height=300)

# ==========================================
# 4. MAIN NAVIGATION
# ==========================================
def main():
    with st.sidebar:
        st.markdown(f"<h2 style='color:{N_GOLD};'>SYNAPSE X</h2>", unsafe_allow_html=True)
        st.session_state.user = st.text_input("AGENT ID", st.session_state.user)
        st.divider()
        st.caption("อยู่นิ่งๆ ไม่เจ็บตัว")

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR"])
    rooms = [room_core, room_radar, room_comms, room_music, room_sensor]
    for i, tab in enumerate(tabs):
        with tab: rooms[i]()

if __name__ == "__main__":
    main()
