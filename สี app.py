import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh # อย่าลืมเพิ่มในชื่อนี้ใน requirements.txt

# --- 1. CONFIG & LOGO ---
logo_path = "logo3.jpg"
logo_exists = os.path.exists(logo_path)
st.set_page_config(page_title="SYNAPSE IDENTITY", page_icon="🌐", layout="wide")

# --- 2. INITIALIZE FIREBASE (ใช้ค่าจาก Secrets) ---
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
        target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
        firebase_admin.initialize_app(cred, {'databaseURL': target_url})
    except Exception as e:
        st.error(f"🚨 Firebase Error: {e}")

# --- 3. SESSION STATE (ระบบจำค่า) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"
if 'my_lat' not in st.session_state: st.session_state.my_lat = 13.7563
if 'my_lon' not in st.session_state: st.session_state.my_lon = 100.5018

# --- 4. LOGIN UI ---
if not st.session_state.logged_in:
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

# --- 5. MAIN APP ---
st.markdown(f"<style>.stApp {{ background: #000; color: {st.session_state.theme_color}; }}</style>", unsafe_allow_html=True)

# แถบด้านข้าง
with st.sidebar:
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("ID", st.session_state.user_name)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🧹 SYS"])

# --- TAB 0: แกนหลัก (ดึงพิกัดจริง) ---
with tabs[0]:
    st.header(f"Welcome, {st.session_state.user_name}")
    st.components.v1.html(f"""
        <script>
            navigator.geolocation.getCurrentPosition(p => {{
                window.parent.postMessage({{
                    type: 'location',
                    lat: p.coords.latitude,
                    lon: p.coords.longitude
                }}, '*');
            }});
        </script>
    """, height=0)
    
    # ส่วนโชว์พิกัดบนหน้าจอ
    st.info(f"📍 CURRENT LOCATION: {st.session_state.my_lat}, {st.session_state.my_lon}")

# --- TAB 1: เรดาร์ (มุดให้ตรง) ---
with tabs[1]:
    st.subheader("🛰️ GOOGLE HYBRID RADAR")
    # ใช้พิกัดที่ดึงมาจริงจาก Tab 0
    m = folium.Map(
        location=[st.session_state.my_lat, st.session_state.my_lon], 
        zoom_start=18, 
        tiles='https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', 
        attr='Google'
    )
    folium.Marker(
        [st.session_state.my_lat, st.session_state.my_lon], 
        popup="YOU ARE HERE", 
        icon=folium.Icon(color='red', icon='screenshot')
    ).add_to(m)
    st_folium(m, width="100%", height=450, key="radar_map")

# --- TAB 2: สื่อสาร (แชต & คอลไร้ติ่ง) ---
with tabs[2]:
    # ระบบ Auto Refresh สำหรับแชต (ทุก 2 วินาที)
    st_autorefresh(interval=2000, key="chat_refresh")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a: # ระบบแชต
        st.write("💬 MESSENGER")
        target = st.text_input("แชตกับใคร:", value="User2")
        pair = sorted([st.session_state.user_name, target])
        room_id = f"chat_{pair[0]}_{pair[1]}"
        
        # ดึงข้อความ
        ref = db.reference(f'chats/{room_id}')
        msgs = ref.order_by_child('ts').limit_to_last(10).get()
        
        chat_box = st.container(height=300)
        with chat_box:
            if msgs:
                for k, v in msgs.items():
                    st.markdown(f"**{v['name']}**: {v['msg']}")
        
        with st.form("send_form", clear_on_submit=True):
            txt = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                ref.push({'name': st.session_state.user_name, 'msg': txt, 'ts': time.time()})
                st.rerun()

    with col_b: # วิดีโอคอล
        st.write("📹 VIDEO CALL")
        if st.button("🚀 START CALL"):
            st.components.v1.html(f"""
                <div id="meet" style="height:400px; width:100%; border:2px solid {st.session_state.theme_color}; border-radius:10px;"></div>
                <script src="https://meet.jit.si/external_api.js"></script>
                <script>
                    const options = {{
                        roomName: 'SYNAPSE_{room_id}',
                        width: '100%', height: 400,
                        parentNode: document.querySelector('#meet'),
                        configOverwrite: {{
                            prejoinPageEnabled: false, disableDeepLinking: true,
                            startWithAudioMuted: false, startWithVideoMuted: false
                        }},
                        interfaceConfigOverwrite: {{
                            SHOW_JITSI_WATERMARK: false,
                            TOOLBAR_BUTTONS: ['microphone', 'camera', 'hangup']
                        }}
                    }};
                    new JitsiMeetExternalAPI('meet.jit.si', options);
                </script>
            """, height=420)

# --- TAB 3: ระบบ ---
with tabs[3]:
    st.write('Slogan: "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("REBOOT CORE"): st.rerun()
