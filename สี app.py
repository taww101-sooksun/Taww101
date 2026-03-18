import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os
import folium
from streamlit_folium import st_folium

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
        target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
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
    except: pass
    return []

# --- 5. MULTI-LANGUAGE DATA ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "sys": "🧹 ระบบ", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ", "manual": "คู่มือ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "sys": "🧹 SYSTEM", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME", "manual": "MANUAL"}
} # (ลดทอนภาษาลงเพื่อความกระชับในตัวอย่าง)

# --- 6. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
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
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("ID", st.session_state.user_name)
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)

tabs = st.tabs([L["core"], L["radar"], L["comms"], L["sys"]])

with tabs[0]: # แกนหลัก
    st.header(f"{L['welcome']}, {st.session_state.user_name}")
    # แสดงพิกัดเรียลไทม์ (JS)
    st.components.v1.html(f"""
        <div style="background:rgba(0,0,0,0.8); color:{st.session_state.theme_color}; padding:15px; border-radius:10px; border:1px solid {st.session_state.theme_color}; font-family:monospace;">
            📍 LIVE GPS: <span id="g">กำลังดึงพิกัด...</span>
        </div>
        <script>
            setInterval(() => {{
                navigator.geolocation.getCurrentPosition(p => {{
                    document.getElementById('g').innerText = p.coords.latitude.toFixed(6) + ", " + p.coords.longitude.toFixed(6);
                }});
            }}, 2000);
        </script>
    """, height=70)

with tabs[1]: # เรดาร์ (Google Hybrid Maps)
    st.subheader(L["radar"])
    c1, c2 = st.columns(2)
    lat_v = c1.number_input(L["lat"], value=13.7563, format="%.6f")
    lon_v = c2.number_input(L["lon"], value=100.5018, format="%.6f")
    
    # สูตรลับ Google Hybrid: ดาวเทียม + ชื่อถนนไทย
    google_hybrid = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    
    m = folium.Map(location=[lat_v, lon_v], zoom_start=17, tiles=google_hybrid, attr='Google')
    folium.Marker([lat_v, lon_v], popup="TARGET", icon=folium.Icon(color='red')).add_to(m)
    
    st_folium(m, width="100%", height=450)

with tabs[2]: # สื่อสาร (Video Call ไร้ติ่ง)
    st.subheader("SYNAPSE PRIVATE CALL")
    call_id = st.text_input("รหัสช่องสัญญาณ:", value="SYNAPSE_SECURE")
    
    if st.button("📞 เริ่มการเชื่อมต่อ"):
        st.components.v1.html(f"""
            <div id="meet" style="height:450px; width:100%; border:2px solid {st.session_state.theme_color}; border-radius:10px;"></div>
            <script src="https://meet.jit.si/external_api.js"></script>
            <script>
                const options = {{
                    roomName: '{call_id}',
                    width: '100%', height: 450,
                    parentNode: document.querySelector('#meet'),
                    configOverwrite: {{
                        prejoinPageEnabled: false,    // ❌ ข้ามหน้า Join
                        disableDeepLinking: true,     // ❌ ปิดการชวนโหลดแอป
                        startWithAudioMuted: false,
                        startWithVideoMuted: false,
                        enableWelcomePage: false
                    }},
                    interfaceConfigOverwrite: {{
                        SHOW_JITSI_WATERMARK: false,  // ❌ ลบโลโก้
                        TOOLBAR_BUTTONS: ['microphone', 'camera', 'hangup', 'tileview']
                    }}
                }};
                new JitsiMeetExternalAPI('meet.jit.si', options);
            </script>
        """, height=470)

with tabs[3]: # ระบบ
    st.write(f'Slogan: "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("REBOOT"): st.rerun()
