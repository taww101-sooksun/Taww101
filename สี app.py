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
# 1. CORE SYSTEM & DATABASE INITIALIZATION
# ==========================================
def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None

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
    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['text']} !important; background: {t['main']} !important; border-radius: 12px; font-weight: bold; width: 100%; }}
        h1, h2, h3, p, span, label, .stMarkdown, .stMetric {{ color: {t['text']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 2. GPS RADAR (พร้อมป้ายชื่ออักษรลอย)
# ==========================================
def room_gps(theme):
    st.subheader("🛰️ เรดาร์ระบุพิกัดพร้อมป้ายชื่อ")
    loc = get_geolocation()
    if loc:
        try:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            db.reference(f'locations/{st.session_state.user}').update({
                'lat': lat, 'lon': lon, 'ts': time.time(),
                'last_update': datetime.now().strftime("%H:%M:%S")
            })

            m = folium.Map(location=[lat, lon], zoom_start=16)
            # ปักหมุดตัวคุณ
            folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
            # ป้ายชื่อลอยบนหัว (YOU)
            folium.map.Marker([lat, lon], icon=folium.features.DivIcon(
                icon_size=(150,36), icon_anchor=(7,25),
                html=f'<div style="font-size: 11pt; color: red; font-weight: bold; background: white; padding: 2px; border-radius: 5px; border: 1px solid red; width: fit-content;">📍 {st.session_state.user} (YOU)</div>',
            )).add_to(m)

            # สถานที่ใกล้เคียง (ตัวอย่างตามภาพจริง)
            places = [
                {"name": "วัดกระทุ่มเสือปลา", "pos": [13.7198, 100.6888], "color": "blue"},
                {"name": "Golden Nakara", "pos": [13.7175, 100.6890], "color": "green"},
                {"name": "ร้านนัวคิมเฮง", "pos": [13.7258, 100.6875], "color": "orange"}
            ]
            for p in places:
                folium.Marker(p["pos"], icon=folium.Icon(color=p['color'])).add_to(m)
                folium.map.Marker(p["pos"], icon=folium.features.DivIcon(
                    icon_size=(200,36), icon_anchor=(0,0),
                    html=f'<div style="font-size: 10pt; color: black; background: #ffffffcc; padding: 2px; border: 1px solid {p["color"]}; border-radius: 3px; font-weight: bold; width: fit-content;">{p["name"]}</div>',
                )).add_to(m)

            st_folium(m, width=700, height=500)
        except Exception as e: st.error(f"🛰️ Error: {e}")
    else: st.info("🛰️ กำลังรอสัญญาณพิกัด...")

# ==========================================
# 3. CHAT & VIDEO CALL
# ==========================================
def room_comms(theme):
    st.subheader("💬 ศูนย์กลางการสื่อสาร")
    t_lobby, t_video = st.tabs(["🌐 Lobby Chat", "📹 Video Call"])
    
    with t_lobby:
        with st.form("lobby_form", clear_on_submit=True):
            m = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("📢 SEND") and m:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': m, 'ts': time.time()})
        data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if data:
            for v in reversed(list(data.values())):
                st.write(f"🟢 **{v.get('u','?')}**: {v.get('msg','')}")

    with t_video:
        all_users = db.reference('accounts').get()
        friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []
        target_v = st.selectbox("เลือกเพื่อนที่จะคอล:", ["-- เลือกชื่อ --"] + friends)
        if target_v != "-- เลือกชื่อ --":
            v_html = f"""
            <div style="background:#111; padding:10px; border-radius:10px; border:2px solid {theme['main']}; text-align:center;">
                <video id="remote" autoplay playsinline style="width:100%; height:200px; background:#000;"></video>
                <button id="call" style="width:100%; padding:10px; background:{theme['main']}; border-radius:5px; font-weight:bold;">📹 CALL {target_v}</button>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', c => {{ if(confirm('รับสาย?')) {{ navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{ c.answer(s); c.on('stream', rs => document.getElementById('remote').srcObject=rs); }}); }} }});
                document.getElementById('call').onclick = () => {{ navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{ const c=peer.call('{target_v}', s); c.on('stream', rs => document.getElementById('remote').srcObject=rs); }}); }};
            </script>
            """
            components.html(v_html, height=300)

# ==========================================
# 4. MAIN FLOW (Login & Register)
# ==========================================
def main():
    init_system()
    
    if not st.session_state.auth_status:
        st.title("🛡️ SYNAPSE ACCESS")
        tab_login, tab_reg = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab_login:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("LOGIN"):
                acc = db.reference(f'accounts/{u}').get()
                if acc and acc.get('pw') == hash_pw(p):
                    st.session_state.auth_status, st.session_state.user = True, u
                    st.rerun()
                else: st.error("❌ ข้อมูลไม่ถูกต้อง")
        
        with tab_reg:
            new_u = st.text_input("ตั้งชื่อผู้ใช้ (ภาษาอังกฤษ)")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.button("CREATE ACCOUNT"):
                if new_u and new_p:
                    if db.reference(f'accounts/{new_u}').get(): st.warning("⚠️ ชื่อนี้มีคนใช้แล้ว")
                    else:
                        db.reference(f'accounts/{new_u}').set({'pw': hash_pw(new_p)})
                        st.success("✅ สมัครสำเร็จ! ไปที่หน้า Login ได้เลย")
        return

    # Sidebar & App Content
    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 Theme:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT"): st.session_state.auth_status = False; st.rerun()
    
    t = apply_theme()
    menu = {"🛰️ เรดาร์": lambda: room_gps(t), "💬 สื่อสาร": lambda: room_comms(t)}
    tabs = st.tabs(list(menu.keys()))
    for i, (name, func) in enumerate(menu.items()):
        with tabs[i]: func()

if __name__ == "__main__": main()
