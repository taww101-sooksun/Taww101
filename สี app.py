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
# 1. SETUP & NEON DEFINITION
# ==========================================
N_GREEN = "#39FF14"  # เขียว (Active/Me)
N_RED   = "#FF0000"  # แดง (Alert/Danger)
N_BLUE  = "#0000FF"  # น้ำเงิน (Border/Radar)
N_GOLD  = "#FFD700"  # ทอง (Slogan/Title)
N_WHITE = "#FFFFFF"  # ขาว (Others/Text)
BG_BLACK = "#000000"

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

if 'user' not in st.session_state: st.session_state.user = "Ta101"
if 'song_index' not in st.session_state: st.session_state.song_index = 0

# ==========================================
# 2. GLOBAL CSS (ลูกเล่นนีออน)
# ==========================================
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stApp {{ background-color: {BG_BLACK} !important; color: {N_WHITE} !important; font-family: 'Orbitron', sans-serif; top: -60px; }}
    
    /* Tabs สไตล์น้ำเงินนีออน */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #050505; border: 1px solid {N_BLUE}; border-radius: 5px; color: {N_BLUE}; padding: 8px 15px;
    }}
    .stTabs [aria-selected="true"] {{ 
        background-color: {N_BLUE}33 !important; border-color: {N_BLUE} !important; 
        color: {N_WHITE} !important; box-shadow: 0 0 10px {N_BLUE};
    }}

    /* ปุ่มเขียวนีออนเต้นได้ */
    .stButton>button {{ 
        border: 2px solid {N_GREEN} !important; color: {N_GREEN} !important; 
        background: transparent !important; transition: 0.3s;
    }}
    .stButton>button:hover {{ 
        background: {N_GREEN} !important; color: black !important; 
        box-shadow: 0 0 20px {N_GREEN}; transform: scale(1.02);
    }}

    /* Animation สโลแกนทอง */
    @keyframes wink {{ 0%, 100% {{ opacity: 1; text-shadow: 0 0 15px {N_GOLD}; }} 50% {{ opacity: 0.3; }} }}
    .slogan-gold {{ color: {N_GOLD}; animation: wink 1.2s infinite; font-weight: bold; font-size: 22px; text-align:center; }}
    
    @keyframes dance {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px) rotate(2deg); }} }}
    .dancing-logo {{ animation: dance 0.8s infinite ease-in-out; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. ROOMS
# ==========================================

def room_core():
    logo_b64 = ""
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <div style="text-align:center; padding: 30px 0;">
            <img src="data:image/png;base64,{logo_b64}" class="dancing-logo" style="width:120px;">
            <div class="slogan-gold" style="margin-top:15px;">SYNAPSE อยู่นิ้งๆไม่เจ็บตัว</div>
        </div>
    """, unsafe_allow_html=True)

    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border:2px solid {N_GREEN}; padding:20px; border-radius:15px; text-align:center; box-shadow: 0 0 20px {N_GREEN}44;">
            <h1 style="margin:0; color:{N_GREEN}; font-size:60px; text-shadow: 0 0 15px {N_GREEN};">{now.strftime('%H:%M:%S')}</h1>
            <p style="color:{N_WHITE}; letter-spacing: 3px;">SYSTEM ACTIVE | AGENT: {st.session_state.user}</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar():
    st.markdown(f"<h3 style='color:{N_BLUE}; text-shadow: 0 0 10px {N_BLUE};'>🛰️ RADAR SCANNER</h3>", unsafe_allow_html=True)
    loc = get_geolocation()
    # แก้บั๊ก Error บรรทัด 75
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if (loc and 'coords' in loc) else (13.7367, 100.5231)
    
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.CircleMarker([lat, lon], radius=10, color=N_RED, fill=True, popup="YOU").add_to(m)
    
    st.markdown(f"<style>.stMap {{ border: 2px solid {N_BLUE}; border-radius: 15px; box-shadow: 0 0 15px {N_BLUE}66; }}</style>", unsafe_allow_html=True)
    st_folium(m, width="100%", height=450, key="radar_map")
    
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        st.toast("📡 พิกัดถูกส่งเข้าดาวเทียมแล้ว!")

def room_comms():
    st.markdown(f"<h3 style='color:{N_GREEN};'>💬 SECURE COMMS</h3>", unsafe_allow_html=True)
    
    with st.form("chat_f", clear_on_submit=True):
        c1, c2 = st.columns([4, 1])
        msg = c1.text_input("Signal...", placeholder="พิมพ์ข้อความที่นี่...")
        file = c2.file_uploader("📸", type=['jpg','png'], label_visibility="collapsed")
        if st.form_submit_button("SEND ⚡"):
            f_b64 = base64.b64encode(file.getvalue()).decode() if file else None
            if msg or f_b64:
                db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'f': f_b64, 'ts': time.time()})
                st.rerun()

    # Chat Display แบบลูกเล่นเดิม
    msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
    if msgs:
        for v in reversed(list(msgs.values())):
            me = v.get('u') == st.session_state.user
            bg = f"{N_GREEN}11" if me else "#111"
            brd = f"2px solid {N_GREEN}" if me else f"1px solid {N_WHITE}33"
            align = "flex-end" if me else "flex-start"
            
            st.markdown(f"""
                <div style="display:flex; flex-direction:column; align-items:{align}; margin-bottom:10px;">
                    <div style="background:{bg}; border:{brd}; padding:10px 15px; border-radius:15px; max-width:80%; box-shadow: 0 0 10px {bg if me else '#000'};">
                        <small style="color:{N_GOLD if not me else N_WHITE}; font-size:10px;">{v.get('u')}</small><br>
                        <span style="color:{N_WHITE};">{v.get('m','')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if v.get('f'): st.image(base64.b64decode(v['f']), width=250)

def room_music():
    st.markdown(f"<h3 style='color:{N_GOLD}; text-align:center;'>🎧 RAINBOW VISUALIZER</h3>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs: return st.warning("No MP3 found")
    
    s_sel = st.selectbox("🎯 SELECT SIGNAL", songs, index=st.session_state.song_index)
    song_data = base64.b64encode(open(s_sel, "rb").read()).decode()
    
    # Visualizer ลูกเล่นเดิมที่เต้นตามจังหวะสีรุ้ง
    viz_js = f"""
    <div style="background:#000; border:2px solid {N_GOLD}; border-radius:20px; padding:20px; box-shadow: 0 0 20px {N_GOLD}44;">
        <canvas id="canvas" style="width:100%; height:200px;"></canvas>
        <button id="btn" style="width:100%; padding:15px; background:transparent; border:2px solid {N_GREEN}; color:{N_GREEN}; border-radius:10px; font-family:Orbitron; cursor:pointer;">[ SYNC AUDIO SOURCE ]</button>
        <audio id="audio" src="data:audio/mp3;base64,{song_data}"></audio>
    </div>
    <script>
        const audio = document.getElementById('audio');
        const btn = document.getElementById('btn');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let aCtx, ans, src, data;

        btn.onclick = () => {{
            if(!aCtx) {{
                aCtx = new AudioContext();
                ans = aCtx.createAnalyser();
                src = aCtx.createMediaElementSource(audio);
                src.connect(ans); ans.connect(aCtx.destination);
                ans.fftSize = 128;
                data = new Uint8Array(ans.frequencyBinCount);
                draw();
            }}
            audio.paused ? audio.play() : audio.pause();
            btn.innerText = audio.paused ? "[ PAUSED ]" : "[ ACTIVE ]";
        }};

        function draw() {{
            requestAnimationFrame(draw);
            ans.getByteFrequencyData(data);
            ctx.clearRect(0,0,canvas.width,canvas.height);
            let barW = (canvas.width / data.length) * 2.5;
            let x = 0;
            for(let i=0; i<data.length; i++) {{
                let barH = data[i] * 0.8;
                let hue = (i / data.length) * 360;
                ctx.fillStyle = `hsl(${{hue}}, 100%, 50%)`;
                ctx.fillRect(x, canvas.height - barH, barW - 2, barH);
                x += barW;
            }}
        }}
    </script>
    """
    components.html(viz_js, height=350)

def room_sensor():
    st.markdown(f"<h3 style='color:{N_RED}; text-align:center;'>📟 MOTION ANALYZER</h3>", unsafe_allow_html=True)
    sensor_html = f"""
    <div style="background:#000; border:2px solid {N_RED}; border-radius:20px; padding:30px; text-align:center;">
        <h1 id="val" style="color:{N_RED}; font-size:80px; text-shadow: 0 0 20px {N_RED};">1.00</h1>
        <p style="color:{N_WHITE};">GRAVITY FORCE (G)</p>
        <button id="sBtn" style="width:100%; padding:15px; border:2px solid {N_RED}; color:{N_RED}; background:transparent; border-radius:10px; cursor:pointer;">[ INITIALIZE SENSOR ]</button>
    </div>
    <script>
        document.getElementById('sBtn').onclick = async () => {{
            if(typeof DeviceMotionEvent.requestPermission === 'function') await DeviceMotionEvent.requestPermission();
            window.addEventListener('devicemotion', (e) => {{
                let acc = e.accelerationIncludingGravity;
                let m = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.8;
                const el = document.getElementById('val');
                el.innerText = m.toFixed(2);
                el.style.textShadow = m > 1.2 ? '0 0 40px #FF0000' : '0 0 20px #FF0000';
            }});
            document.getElementById('sBtn').style.display = 'none';
        }};
    </script>
    """
    components.html(sensor_html, height=350)

# ==========================================
# 4. EXECUTION
# ==========================================
def main():
    with st.sidebar:
        st.markdown(f"<h2 style='color:{N_GOLD};'>COMMAND</h2>", unsafe_allow_html=True)
        st.session_state.user = st.text_input("AGENT ID", st.session_state.user)
        st.divider()
        st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR"])
    rooms = [room_core, room_radar, room_comms, room_music, room_sensor]
    for i, tab in enumerate(tabs):
        with tab: rooms[i]()

if __name__ == "__main__":
    main()
