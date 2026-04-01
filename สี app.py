import streamlit as st
import os 
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib

# ==========================================
# 1. CORE SYSTEM & AUTHENTICATION
# ==========================================
def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'active_target' not in st.session_state: st.session_state.active_target = None 

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def apply_theme():
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "chat_user": "#39FF14", "chat_friend": "#333"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "chat_user": "#00A8E8", "chat_friend": "#005F73"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "chat_user": "#FF4D4D", "chat_friend": "#990000"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000", "chat_user": "#FFB6C1", "chat_friend": "#E0FFFF"}
    }
    t = themes.get(st.session_state.theme_set, themes["Matrix"])
    bg_style = f"background-color: {t['bg']} !important;"
    if st.session_state.theme_set == "Rainbow":
        bg_style = "background: linear-gradient(135deg, #FF99CC, #99CCFF, #99FFCC) !important;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['text']} !important; background: {t['main']} !important; border-radius: 12px; font-weight: bold; width: 100%; }}
        h1, h2, h3, p, span, label, .stMarkdown, .stMetric {{ color: {t['text']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {t['main']} !important; border-bottom: 3px solid {t['main']} !important; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 2. GPS RADAR (With Real Place Names)
# ==========================================
def room_gps(theme):
    st.subheader("🛰️ ระบบเรดาร์ระบุตำแหน่งและสถานที่ใกล้เคียง")
    now_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"### 🕒 Server Time: `{now_time}`")

    loc = get_geolocation()
    if loc:
        try:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            db.reference(f'locations/{st.session_state.user}').update({
                'lat': lat, 'lon': lon, 'ts': time.time(),
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            c1, c2 = st.columns(2)
            c1.metric("Latitude", f"{lat:.6f}")
            c2.metric("Longitude", f"{lon:.6f}")
            
            m = folium.Map(location=[lat, lon], zoom_start=15)
            # หมุดตำแหน่งเรา
            folium.Marker([lat, lon], popup="คุณอยู่ที่นี่", tooltip="My Location", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
            
            # ตัวอย่างสถานที่ใกล้เคียง (ทำได้จริง)
            nearby_places = [
                {"name": "วัดกระทุ่มเสือปลา", "pos": [13.7229, 100.6887]},
                {"name": "วัดลานบุญ", "pos": [13.7246, 100.7195]},
                {"name": "สวนปลาธรรมชาติ", "pos": [13.7241, 100.7194]}
            ]
            for p in nearby_places:
                folium.Marker(p["pos"], popup=p["name"], tooltip=p["name"], icon=folium.Icon(color='blue')).add_to(m)
                
            st_folium(m, width=700, height=400)
        except Exception as e: st.error(f"❌ พิกัดขัดข้อง: {e}")
    else: st.info("⌛ กำลังรอสัญญาณจากดาวเทียม...")

# ==========================================
# 3. COMMUNICATION (Stable Chat & Video)
# ==========================================
def room_comms(theme):
    st.subheader("💬 ศูนย์กลางการสื่อสาร")
    t_lobby, t_private, t_video = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📹 วิดีโอคอล"])
    
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []

    with t_lobby:
        with st.form("lobby_form", clear_on_submit=True):
            m = st.text_input("พิมพ์ข้อความสาธารณะ...")
            if st.form_submit_button("📢 SEND") and m:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': m, 'ts': time.time()})
        
        data = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if data:
            for v in reversed(list(data.values())):
                st.write(f"🟢 **{v.get('u','?') }**: {v.get('msg','')}")

    with t_private:
        st.caption("📩 กล่องข้อความส่วนตัว")
        target = st.selectbox("เลือกเพื่อน:", ["-- เลือกชื่อ --"] + friends)
        if target != "-- เลือกชื่อ --":
            st.session_state.active_target = target
            rid = "_".join(sorted([st.session_state.user, target]))
            with st.form("priv_form", clear_on_submit=True):
                pm = st.text_input(f"ส่งข้อความถึง {target}")
                if st.form_submit_button("🔒 SEND"):
                    db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            
            msgs = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(10).get()
            if msgs:
                for v in reversed(list(msgs.values())):
                    u_name = v.get('u', 'Unknown')
                    side = "right" if u_name == st.session_state.user else "left"
                    bg = theme['chat_user'] if u_name == st.session_state.user else theme['chat_friend']
                    st.markdown(f'<div style="text-align:{side};"><div style="display:inline-block; background:{bg}; padding:10px; border-radius:15px; margin:2px; color:white;"><b>{u_name}</b>: {v.get("msg","")}</div></div>', unsafe_allow_html=True)

    with t_video:
        target_v = st.selectbox("เลือกเพื่อนที่จะคอล:", ["-- เลือกชื่อ --"] + friends, key="v_call_sel")
        if target_v != "-- เลือกชื่อ --":
            v_html = f"""
            <div id="v-box" style="background:#111; padding:15px; border-radius:15px; border:2px solid {theme['main']}; text-align:center;">
                <div style="position:relative; width:100%; height:240px; background:#000; border-radius:10px; overflow:hidden;">
                    <video id="remote" autoplay playsinline style="width:100%; height:100%; object-fit:cover;"></video>
                    <video id="local" autoplay playsinline muted style="position:absolute; bottom:5px; right:5px; width:70px; border:1px solid white;"></video>
                </div>
                <div style="margin-top:10px; display:flex; gap:5px;">
                    <button id="call" style="flex:1; padding:10px; background:{theme['main']}; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📹 CALL</button>
                    <button id="hangup" style="flex:1; padding:10px; background:#f44; color:white; border:none; border-radius:5px; display:none; cursor:pointer;">🔴 HANGUP</button>
                </div>
                <p id="peer-id" style="color:gray; font-size:10px;"></p>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}', {{config: {{'iceServers': [{{ 'urls': 'stun:stun.l.google.com:19302' }}]}}}});
                let currentCall;
                peer.on('open', id => document.getElementById('peer-id').innerText = "ID: " + id);
                peer.on('call', c => {{ if(confirm('รับสายจาก ' + c.peer + '?')) {{ navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{ document.getElementById('local').srcObject=s; c.answer(s); setup(c); }}); }} }});
                function setup(c) {{ 
                    currentCall=c; document.getElementById('call').style.display='none'; document.getElementById('hangup').style.display='inline-block';
                    c.on('stream', rs => document.getElementById('remote').srcObject=rs);
                }}
                document.getElementById('call').onclick = () => {{ navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{ document.getElementById('local').srcObject=s; const c=peer.call('{target_v}', s); setup(c); }}); }};
                document.getElementById('hangup').onclick = () => {{ if(currentCall) currentCall.close(); location.reload(); }};
            </script>
            """
            components.html(v_html, height=400)

# ==========================================
# 4. MULTIMEDIA & MAIN
# ==========================================
def room_music():
    st.subheader("🎧 SYNAPSE PLAYER")
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if songs:
        curr = songs[st.session_state.song_index]
        c1, c2 = st.columns([1, 1.2])
        with c1: st.info(f"💿 Track: {curr}")
        with c2: st.audio(curr)
        for idx, s in enumerate(songs):
            if st.button(f"🎶 {s}", key=f"s_{idx}"):
                st.session_state.song_index = idx
                st.rerun()

def main():
    init_system()
    if not st.session_state.auth_status:
        st.title("🛡️ SYNAPSE LOGIN")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ENTER"):
            acc = db.reference(f'accounts/{u}').get()
            if acc and acc.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ Denied")
        return

    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 Theme:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT"): st.session_state.auth_status = False; st.rerun()
    
    t = apply_theme()
    menu = {"🛰️ เรดาร์": lambda: room_gps(t), "💬 สื่อสาร": lambda: room_comms(t), "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, (name, func) in enumerate(menu.items()):
        with tabs[i]: func()

if __name__ == "__main__": main()
