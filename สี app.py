import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# กำหนดสี Neon ตามสไตล์ที่พี่ชอบ
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 

# --- 2. INITIALIZE FIREBASE (ดึงค่าจาก Secrets เท่านั้น ปลอดภัย 100%) ---
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
        # URL ฐานข้อมูลจริงจากรูปที่พี่ส่งมา (sooksun1)
        database_url = "https://sooksun1-default-rtdb.firebaseio.com/"
        
        firebase_admin.initialize_app(cred, {'databaseURL': database_url})
        st.toast("✅ SYNAPSE CORE: SOOKSUN1 ONLINE")
    except Exception as e:
        st.error(f"🚨 Connection Error: {e}")

# --- 3. CSS STYLE (Dark Mode & Glow Effect) ---
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

# --- 4. SIDEBAR (เมนูควบคุม) ---
with st.sidebar:
    st.title("🌐 CONTROL")
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 5. MAIN INTERFACE ---
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "📞 COMMS"])

with tabs[0]: 
    st.header("SYNAPSE COMMAND CENTER")
    # เพลงยักษ์ในตัวฉัน (Auto Play ตามไฟล์ที่พี่มี)
    music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.audio(music_url, format="audio/mpeg", loop=True)
    
    # ระบบ DATABASE STATUS (ยิงข้อมูลเข้า Firebase)
    st.subheader("📡 DATABASE STATUS")
    test_msg = st.text_input("ส่งข้อความเข้าฐานข้อมูล:", value="ทัก", key="db_msg")
    if st.button("🚀 UPDATE STATUS"):
        if test_msg:
            try:
                db.reference('logs').push({
                    'msg': test_msg, 
                    'user': 'Ta101',
                    'time': '7 ชั่วโมงตามเวลา'
                })
                st.success(f"บันทึกข้อมูล '{test_msg}' สำเร็จ!")
            except Exception as e:
                st.error(f"เขียนข้อมูลไม่ได้: {e}")

with tabs[1]: # แผนที่ดาวเทียม
    st.subheader("🛰️ STRATEGIC RADAR")
    # ใช้ Google Hybrid (ดาวเทียมผสมถนน)
    m = folium.Map(location=[13.7563, 100.5018], zoom_start=16, 
                   tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                   attr='Google Satellite')
    st_folium(m, width="100%", height=500)

with tabs[2]: # ระบบสื่อสาร (Jitsi Meet)
    st.subheader("💬 SECURE CALL")
    components.html(f"""
        <div id="meet" style="height:500px; width:100%; border:2px solid {st.session_state.theme_color}; border-radius:15px;"></div>
        <script src="https://meet.jit.si/external_api.js"></script>
        <script>
            const options = {{
                roomName: 'SYNAPSE_SOOKSUN1_ROOM',
                width: '100%', height: 500,
                parentNode: document.querySelector('#meet'),
                configOverwrite: {{ prejoinPageEnabled: false }},
                interfaceConfigOverwrite: {{ SHOW_JITSI_WATERMARK: false }}
            }};
            new JitsiMeetExternalAPI('meet.jit.si', options);
        </script>
    """, height=520)
