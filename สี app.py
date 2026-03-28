import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import os
import streamlit.components.v1 as components

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 

# --- 2. INITIALIZE FIREBASE (ข้อมูลจริงจาก JSON ของพี่) ---
if not firebase_admin._apps:
    try:
        fb_config = {
            "type": "service_account",
            "project_id": "sooksun1",
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": "firebase-adminsdk-fbsvc@sooksun1.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        cred = credentials.Certificate(fb_config)
        # URL ฐานข้อมูลจริงจากรูปที่พี่ส่งมา
        database_url = "https://sooksun1-default-rtdb.firebaseio.com/"
        
        firebase_admin.initialize_app(cred, {'databaseURL': database_url})
        st.toast("✅ SYNAPSE CORE: SOOKSUN1 ONLINE")
    except Exception as e:
        st.error(f"🚨 Connection Error: {e}")

# --- 3. DYNAMIC CSS (สไตล์นีออน) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background-color: #000 !important; color: {st.session_state.theme_color} !important; }}
    .stButton>button {{
        width: 100%; background-color: transparent !important; color: {st.session_state.theme_color} !important;
        border: 2px solid {st.session_state.theme_color} !important; border-radius: 10px;
        font-family: 'Orbitron';
    }}
    h1, h2, h3, p, span, label {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌐 CONTROL")
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 5. MAIN INTERFACE ---
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "📞 COMMS"])

with tabs[0]: 
    st.header("SYNAPSE COMMAND CENTER")
    # เพลง (ยักษ์ในตัวฉัน - Auto Play)
    music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.audio(music_url, format="audio/mpeg", loop=True)
    
    # ระบบเขียนข้อมูลทดสอบลง Firebase
    st.subheader("📡 DATABASE STATUS")
    test_msg = st.text_input("ส่งข้อความเข้าฐานข้อมูล:", value="System Online")
    if st.button("🚀 UPDATE STATUS"):
        try:
            db.reference('system_log').push({'msg': test_msg, 'user': 'Ta101'})
            st.success("บันทึกข้อมูลเรียบร้อย!")
        except: st.error("เขียนข้อมูลไม่ได้ (เช็ค Rules ใน Firebase)")

with tabs[1]: # เรดาร์ดาวเทียม (Google Hybrid)
    st.subheader("🛰️ STRATEGIC RADAR")
    # พิกัดกรุงเทพฯ (พี่แก้เป็นพิกัดตัวเองได้)
    m = folium.Map(location=[13.7563, 100.5018], zoom_start=16, 
                   tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                   attr='Google')
    folium.Marker([13.7563, 100.5018], popup="CENTER").add_to(m)
    st_folium(m, width="100%", height=500)

with tabs[2]: # Video Call (ฆ่าติ่ง Join)
    st.subheader("💬 SECURE CALL")
    components.html(f"""
        <div id="meet" style="height:500px; width:100%; border:2px solid {st.session_state.theme_color}; border-radius:15px;"></div>
        <script src="https://meet.jit.si/external_api.js"></script>
        <script>
            const options = {{
                roomName: 'SYNAPSE_SOOKSUN1',
                width: '100%', height: 500,
                parentNode: document.querySelector('#meet'),
                configOverwrite: {{
                    prejoinPageEnabled: false,
                    disableDeepLinking: true,
                    startWithAudioMuted: false,
                    startWithVideoMuted: false
                }},
                interfaceConfigOverwrite: {{ SHOW_JITSI_WATERMARK: false }}
            }};
            new JitsiMeetExternalAPI('meet.jit.si', options);
        </script>
    """, height=520)
