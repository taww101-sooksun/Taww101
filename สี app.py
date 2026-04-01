import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from datetime import datetime

# --- 1. CONFIG & LOGO ---
logo_path = "logo3.jpg"
logo_exists = os.path.exists(logo_path)
st.set_page_config(
    page_title="SYNAPSE IDENTITY", 
    page_icon=logo_path if logo_exists else "🌐", 
    layout="wide"
)

# --- 2. INITIALIZE FIREBASE ---
if not firebase_admin._apps:
    try:
        fb_config = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["client_email"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        cred = credentials.Certificate(fb_config)
        target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app"
        firebase_admin.initialize_app(cred, {'databaseURL': target_url})
        st.toast("✅ SYNAPSE CORE CONNECTED")
    except Exception as e:
        st.error(f"🚨 Connection Error: {e}")

# --- 3. เพลง AUTO-PLAY ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)

# --- 4. LOGIC แชทส่วนตัว ---
def private_chat_logic(my_name, target_name, p_msg=None):
    try:
        pair = sorted([my_name, target_name])
        room_id = f"priv_{pair[0]}_{pair[1]}"
        ref = db.reference(f'private_rooms/{room_id}')
        if p_msg:
            ref.push({'name': my_name, 'msg': p_msg, 'ts': time.time()})
        raw_p_msgs = ref.get()
        if raw_p_msgs:
            msgs = list(raw_p_msgs.values()) if isinstance(raw_p_msgs, dict) else [m for m in raw_p_msgs if m]
            return sorted(msgs, key=lambda x: x.get('ts', 0))[-15:]
    except Exception as e:
        st.error(f"Chat Error: {e}")
    return []

# --- 5. MULTI-LANGUAGE DATA ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "sys": "🧹 ระบบ", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ", "manual": "คู่มือ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "sys": "🧹 SYSTEM", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME", "manual": "MANUAL"}
}

# --- 6. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 7. LOGIN UI ---
if not st.session_state.logged_in:
    if logo_exists: st.image(logo_path, width=400)
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>🌐 SYNAPSE IDENTITY</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pw = st.text_input("SECURITY KEY", type="password")
        if st.button("🚀 ENTER SYSTEM"):
            if pw == "notty101":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("❌ Access Denied")
    st.stop()

# --- 8. MAIN APP ---
L = LANG_DATA[st.session_state.lang]
play_audio()
st.markdown(f"<style>.stApp {{ background: #000; color: {st.session_state.theme_color}; }}</style>", unsafe_allow_html=True)

with st.sidebar:
    if logo_exists: st.image(logo_path, use_column_width=True)
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("ID", st.session_state.user_name)
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

tabs = st.tabs([L["core"], L["radar"], L["comms"], L["sys"]])

with tabs[0]: # แกนหลัก
    st.header(f"{L['welcome']}, {st.session_state.user_name}")
    st.info("System Ready. Monitoring active signals...")

with tabs[1]: # เรดาร์แบบอัปเกรด
    st.subheader(f"🛰️ {L['radar']} (Hybrid Satellite)")
    
    # ดึงพิกัดจริงจากเบราว์เซอร์
    loc = get_geolocation()
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        
        c1, c2 = st.columns(2)
        c1.metric(L["lat"], f"{lat:.6f}")
        c2.metric(L["lon"], f"{lon:.6f}")

        # ตั้งค่าแผนที่ Google Hybrid
        google_hybrid = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles=google_hybrid, attr='Google')
        
        # ปักหมุดตำแหน่งปัจจุบัน
        folium.Marker(
            [lat, lon], 
            popup=f"คุณอยู่ที่นี่: {st.session_state.user_name}",
            tooltip="Current Location",
            icon=folium.Icon(color='red', icon='user', prefix='fa')
        ).add_to(m)

        # เพิ่มจุดที่น่าสนใจ (ตัวอย่าง)
        nearby = [{"name": "วัดกระทุ่มเสือปลา", "pos": [13.7229, 100.6887]}]
        for p in nearby:
            folium.Marker(p["pos"], popup=p["name"], icon=folium.Icon(color='blue')).add_to(m)

        st_folium(m, width=1000, height=500)
    else:
        st.warning("⌛ กำลังดึงข้อมูลพิกัด GPS... (กรุณากดอนุญาตสิทธิ์ตำแหน่งในเบราว์เซอร์)")

with tabs[2]: # สื่อสาร
    st.subheader(L["comms"])
    target = st.text_input("แชทกับใคร:", value="User2")
    
    # ส่วนวิดีโอคอล
    if st.button("📹 OPEN CAMERA SIGNAL"):
        st.components.v1.html("<video id='v' autoplay playsinline style='width:100%; border:2px solid #39FF14; border-radius:10px;'></video><script>navigator.mediaDevices.getUserMedia({video:true,audio:true}).then(s=>document.getElementById('v').srcObject=s)</script>", height=250)
    
    # ส่วนแชท
    msgs = private_chat_logic(st.session_state.user_name, target)
    for m in msgs:
        st.write(f"**{m['name']}**: {m['msg']}")
    
    with st.form("chat_f", clear_on_submit=True):
        txt = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("ส่ง"):
            private_chat_logic(st.session_state.user_name, target, txt)
            st.rerun()

with tabs[3]: # ระบบ
    st.subheader(f"📖 {L['manual']}")
    st.code('Slogan: "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("REBOOT CORE"):
        st.cache_resource.clear()
        st.rerun()
