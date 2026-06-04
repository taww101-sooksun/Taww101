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
# 1. INITIAL SETUP (ระบบจัดการกุญแจความลับผ่าน Secrets)
# ==========================================
@st.cache_resource
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    if not firebase_admin._apps:
        try:
            # ดักจับอาการระบบขัดข้องหากยังไม่ได้ใส่ค่าในหน้าเว็บ Secrets บน Streamlit Cloud
            if "firebase_credentials" not in st.secrets or "firebase_db_url" not in st.secrets:
                st.error("🚨 ตรวจพบสัญญาณขัดข้อง: นายยังไม่ได้นำข้อมูลกุญแจแอดมินไปวางในช่อง Secrets บนหน้าเว็บ Streamlit Cloud ครับ")
                st.stop()
                
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                # ทำความสะอาดรหัสตัดคำขึ้นบรรทัดใหม่ให้เข้ากับโครงสร้างกูเกิล
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
                
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
            st.stop()
    return True

init_system()

# ==========================================
# 2. UI STYLING & NEON THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; border-radius: 10px; font-weight: bold; }}
    .stButton>button:hover {{ background: {st.session_state.theme_color} !important; color: black !important; }}
    .neon-box {{ border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {st.session_state.theme_color}; }}
    
    /* ซ่อนติ่งและเมนูดั้งเดิมของ Streamlit เพื่อความคลีน */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MODULES (The Rooms)
# ==========================================

def room_core():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:0;">AGENT: {st.session_state.user} | 'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
        </div>
    """, unsafe_allow_html=True)
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ System Uptime: {progress*100:.2f}%")
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🛰️ SATELLITE RADAR</h2>", unsafe_allow_html=True)
    
    # บล็อกแก้บั๊กสิทธิ์ Geolocation ป้องกันอาการหน่วงหน้ารันเว็บครั้งแรก
    loc = get_geolocation()
    lat, lon = 13.7367, 100.5231  # ค่าพิกัดสำรองตั้งต้นกรณีระบุตำแหน่งไม่ได้
    
    if loc and 'coords' in loc:
        try:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
        except Exception:
            pass
            
    all_users = db.reference('users').get()
    
    # สร้างแผนที่ดาวเทียม Google Hybrid ความแม่นยำสูง
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users and isinstance(all_users, dict):
        for uid, data in all_users.items():
            if uid != st.session_state.user and isinstance(data, dict) and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=uid, icon=folium.Icon(color='green')).add_to(m)
                
    st_folium(m, width="100%", height=450, key="radar")
    
    # ปุ่มส่งกระจายสัญญาณตำแหน่งพิกัดดาวเทียม
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': lat, 
            'lon': lon, 
            'ts': time.time()
        })
        st.toast("Intelligence Data Transmitted!")

def room_comms():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>💬 COMM CENTER</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌐 PUBLIC FEED", "📞 SECURE CALL"])
    
    with t1:
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            msg = col1.text_input("Enter Signal...")
            up_file = col2.file_uploader("📁", type=['jpg', 'png', 'mp4'], label_visibility="collapsed")
            submit_signal = st.form_submit_button("SEND")
            
            if submit_signal:
                f_b64, f_type = None, None
                if up_file:
                    f_b64 = base64.b64encode(up_file.getvalue()).decode()
                    f_type = up_file.type
                if msg or f_b64:
                    db.reference('public_chat').push({
                        'u': st.session_state.user, 
                        'm': msg, 
                        'f': f_b64, 
                        'ft': f_type, 
                        'ts': time.time()
                    })
                    st.rerun()
                    
        # ดึงประวัติฟีดข้อความ 15 ข้อความล่าสุด
        try:
            msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        except Exception:
            msgs = None
            
        if msgs and isinstance(msgs, dict):
            for v in reversed(list(msgs.values())):
                if isinstance(v, dict):
                    st.markdown(f"🟢 **{v.get('u')}**: {v.get('m','')}")
                    if v.get('f'):
                        raw = base64.b64decode(v['f'])
                        if "image" in v.get('ft', ''): st.image(raw, width=300)
                        elif "video" in v.get('ft', ''): st.video(raw)
                        
    with t2:
        all_u = db.reference('users').get()
        friends = []
        if all_u and isinstance(all_u, dict):
            friends = [uid for uid in all_u.keys() if uid != st.session_state.user]
            
        target = st.selectbox("🎯 Target Agent:", [""] + friends)
        if target:
            call_js = """
            <div style="background:#111; padding:15px; border:1px solid %s; border-radius:10px; text-align:center;">
                <button id="cBtn" style="width:100%%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px; font-family:monospace; font-weight:bold; cursor:pointer;">📞 CALL %s</button>
                <audio id="rAudio" autoplay></audio>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('%s');
                peer.on('call', c => { navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ c.answer(s); c.on('stream',rs=>{document.getElementById('rAudio').srcObject=rs;}); })});
                document.getElementById('cBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ const c=peer.call('%s',s); c.on('stream',rs=>{document.getElementById('rAudio').srcObject=rs;}); });
                };
            </script>
            """ % (st.session_state.theme_color, target, st.session_state.user, target)
            components.html(call_js, height=200)

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🎧 SYNAPSE HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    
    # ดึงไฟล์เพลง .mp3 ในเครื่อง
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs:
        st.warning("⚠️ ไม่พบสัญญาณเสียง
