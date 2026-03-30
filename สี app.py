import streamlit as st
import os 
import random
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    # ตัวแปรสถานะ Login
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 2. ระบบลงชื่อเข้าใช้ (Authentication)
# ==========================================
def login_page():
    st.title("🛡️ SYNAPSE AUTHENTICATION")
    tab1, tab2 = st.tabs(["🔐 เข้าสู่ระบบ", "📝 ลงทะเบียน"])
    
    with tab1:
        u_login = st.text_input("ชื่อผู้ใช้", key="u_log")
        p_login = st.text_input("รหัสผ่าน", type="password", key="p_log")
        if st.button("LOGIN", use_container_width=True):
            user_data = db.reference(f'accounts/{u_login}').get()
            if user_data and user_data.get('pw') == hash_pw(p_login):
                st.session_state.auth_status = True
                st.session_state.user = u_login
                st.success(f"ยินดีต้อนรับคุณ {u_login}")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    with tab2:
        u_reg = st.text_input("ตั้งชื่อผู้ใช้", key="u_reg")
        p_reg = st.text_input("ตั้งรหัสผ่าน", type="password", key="p_reg")
        p_conf = st.text_input("ยืนยันรหัสผ่าน", type="password", key="p_conf")
        if st.button("REGISTER", use_container_width=True):
            if u_reg and p_reg == p_conf:
                existing = db.reference(f'accounts/{u_reg}').get()
                if existing:
                    st.warning("⚠️ ชื่อนี้มีผู้ใช้แล้ว")
                else:
                    db.reference(f'accounts/{u_reg}').set({'pw': hash_pw(p_reg)})
                    st.success("✅ ลงทะเบียนสำเร็จ! กรุณาไปหน้า Login")
            else:
                st.error("❌ ข้อมูลไม่ถูกต้องหรือรหัสไม่ตรงกัน")

# ==========================================
# 3. พื้นที่เก็บห้อง (The Rooms / Modules)
# ==========================================
def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7) 
    day_percent = ((now.hour * 3600) + (now.minute * 60) + now.second) / 84600
    
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 5px; text-align: center;">
            <h3 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h3>
            <small style="color: {st.session_state.theme_color}; opacity: 0.8;">THAILAND TIME</small>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
    st.progress(min(day_percent, 1.0))
    st.markdown("---")
    st.info(f"สถานะระบบ: ONLINE | ผู้ใช้: {st.session_state.user}")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    start_lat, start_lon = 13.7367, 100.5231
    if loc:
        start_lat, start_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[start_lat, start_lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for user_id, data in all_users.items():
            u_lat, u_lon, u_ts = data.get('lat'), data.get('lon'), data.get('ts', 0)
            if u_lat and u_lon:
                color = 'red' if user_id == st.session_state.user else 'green'
                folium.Marker([u_lat, u_lon], tooltip=user_id, icon=folium.Icon(color=color)).add_to(m)

    st_folium(m, width="100%", height=400)
    if loc and st.button("📡 กระจายพิกัด", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': start_lat, 'lon': start_lon, 'ts': time.time()})

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t1, t2 = st.tabs(["🌐 Lobby", "📞 CALL"])
    with t1:
        with st.form("chat", clear_on_submit=True):
            msg = st.text_input("ส่งสัญญาณ...")
            if st.form_submit_button("SEND") and msg:
                db.reference('public_chat').push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
                st.rerun()
        msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")
    with t2:
        st.write("ระบบโทร Peer-to-Peer")
        friends = [uid for uid in (db.reference('users').get() or {}).keys() if uid != st.session_state.user]
        target = st.selectbox("เลือกเพื่อน:", [""] + friends)
        if target:
            call_js = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:15px; border:1px solid %s; border-radius:10px; color:white; text-align:center;">
                <p>ID: <b>%s</b> -> โทรหา: <b>%s</b></p>
                <button id="callBtn" style="width:100%%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px;">🟢 CALL</button>
                <audio id="remoteAudio" autoplay></audio>
            </div>
            <script>
                const peer = new Peer('%s');
                peer.on('call', c => { navigator.mediaDevices.getUserMedia({audio:true}).then(s => { c.answer(s); c.on('stream', rs => { document.getElementById('remoteAudio').srcObject = rs; }); }); });
                document.getElementById('callBtn').onclick = () => { navigator.mediaDevices.getUserMedia({audio:true}).then(s => { const c = peer.call('%s', s); c.on('stream', rs => { document.getElementById('remoteAudio').srcObject = rs; }); }); };
            </script>
            """ % (st.session_state.theme_color, st.session_state.user, target, st.session_state.user, target)
            components.html(call_js, height=200)

# ==========================================
# 4. แผงวงจรหลัก
# ==========================================
def main():
    init_system()
    
    # ถ้ายังไม่ Login ให้แสดงแค่หน้า Login เท่านั้น
    if not st.session_state.auth_status:
        login_page()
        return

    # ถ้า Login แล้ว แสดง UI หลัก
    st.markdown(f"""<style>.stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.auth_status = False
            st.session_state.user = None
            st.rerun()

    room_map = {"🚀 แกนหลัก": room_core, "🛰️ เรดาร์": room_radar, "💬 สื่อสาร": room_comms}
    tabs = st.tabs(list(room_map.keys()))
    for i, room_func in enumerate(room_map.values()):
        with tabs[i]: room_func()

if __name__ == "__main__":
    main()
