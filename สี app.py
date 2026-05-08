import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, timedelta
import base64
import time
import math

# --- 1. SET UP & THEME (Cyberpunk Style) ---
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #000; color: #39FF14; }
    .stButton>button { 
        border: 1px solid #39FF14 !important; color: #39FF14 !important;
        background: rgba(57, 255, 20, 0.1) !important; width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; }
    .stTabs [data-baseweb="tab"] { color: #888; }
    .stTabs [aria-selected="true"] { color: #39FF14 !important; border-bottom: 2px solid #39FF14 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE INIT ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except:
        st.error("⚠️ เชื่อมต่อ Firebase ไม่ได้ ตรวจสอบ Secrets ด้วยเพื่อน!")

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

# --- 4. UTILS ---
def get_base64_img(path):
    import os
    if os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- 5. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("🛡️ AGENT AUTHENTICATION")
    tab_l, tab_r = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    with tab_l:
        u = st.text_input("AGENT ID")
        p = st.text_input("PASSWORD", type="password")
        if st.button("ENTER SYSTEM"):
            res = db.reference(f'users/{u}').get()
            if res and res.get('password') == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied.")
    with tab_r:
        nu = st.text_input("NEW AGENT ID")
        np = st.text_input("SET PASSWORD", type="password")
        if st.button("CREATE PROFILE"):
            db.reference(f'users/{nu}').set({'password': np, 'ts': time.time()})
            st.success("Profile Created.")
    st.stop()

# --- 6. MAIN INTERFACE ---
st.sidebar.title(f"📟 AGENT: {st.session_state.user}")
st.sidebar.write('"อยู่นิ่งๆ ไม่เจ็บตัว"')
if st.sidebar.button("LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()

main_tabs = st.tabs(["💬 GLOBAL CHAT", "🛰️ RADAR", "🔢 COSMIC DECODER", "🎧 NEON MIXER"])

# --- TAB 1: GLOBAL CHAT ---
with main_tabs[0]:
    chat_html = f"""
    <div id="c-box" style="height:400px; overflow-y:auto; background:#050505; border:1px solid #39FF14; padding:10px; font-family:monospace;">
        <div id="m-area"></div>
    </div>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
        if(!firebase.apps.length) firebase.initializeApp(conf);
        firebase.database().ref('global_chat').limitToLast(20).on('child_added', (s) => {{
            const m = s.val();
            const area = document.getElementById('m-area');
            const d = document.createElement('div');
            d.style.color = m.user === "{st.session_state.user}" ? "#39FF14" : "#fff";
            d.innerHTML = `<b>[${{m.user}}]:</b> ${{m.text}}`;
            area.appendChild(d);
            document.getElementById('c-box').scrollTop = 9999;
        }});
    </script>
    """
    components.html(chat_html, height=420)
    msg = st.text_input("SEND SIGNAL", key="chat_in")
    if st.button("SEND ⚡"):
        if msg:
            db.reference('global_chat').push({'user': st.session_state.user, 'text': msg, 'ts': time.time()})
            st.rerun()

# --- TAB 2: RADAR ---
with main_tabs[1]:
    st.subheader("🛰️ AGENT LOCATOR")
    m = folium.Map(location=[13.7367, 100.5231], zoom_start=12, tiles="CartoDB dark_matter")
    try:
        agents = db.reference('users').get()
        for uid, data in agents.items():
            if 'lat' in data and 'lon' in data:
                folium.Marker([data['lat'], data['lon']], tooltip=uid, 
                              icon=folium.Icon(color='green' if uid != st.session_state.user else 'red')).add_to(m)
    except: pass
    st_folium(m, width="100%", height=400)
    if st.button("📡 BROADCAST MY LOCATION"):
        # ในใช้งานจริงต้องใช้ get_geolocation จาก streamlit_js_eval
        db.reference(f'users/{st.session_state.user}').update({'lat': 13.7367, 'lon': 100.5231}) 
        st.success("Location Broadcasted!")

# --- TAB 3: COSMIC DECODER ---
with main_tabs[2]:
    st.subheader("🔢 COSMIC BALANCE DECODER")
    target_dt = st.date_input("เลือกวันที่วิเคราะห์", date.today())
    # Logic ถอดรหัส (ตัวอย่างจาก Step-by-Step)
    day_val = target_dt.isoweekday()
    lunar_pos = ((target_dt - date(1900,1,1)).days - 0.5) % 29.53
    lunar_val = int(lunar_pos) if lunar_pos <= 14.7 else int(lunar_pos - 14.7)
    res = (day_val + target_dt.day + lunar_val) * 1.618
    
    st.metric("Cosmic Index", f"{res:.4f}")
    st.info(f"วันทางพลังงาน: {day_val} | ฐานจันทรคติ: {lunar_val} | ตัวเลขสั่นสะเทือน: {str(res)[2:4]}")

# --- TAB 4: NEON MIXER ---
with main_tabs[3]:
    st.subheader("🎧 NEON AUTO-MIXER")
    # โค้ด HTML Mixer แบบย่อ (ใช้งานจริงต้องโหลดไฟล์เสียง)
    mixer_html = """
    <div style="background:#111; padding:20px; border-radius:10px; border:1px solid #39FF14; text-align:center;">
        <p style="color:#39FF14;">SYSTEM READY: AWAITING AUDIO INPUT</p>
        <div style="display:flex; justify-content:space-around;">
            <div style="width:40%; border:1px dashed #555; padding:10px;">DECK A</div>
            <div style="width:40%; border:1px dashed #555; padding:10px;">DECK B</div>
        </div>
        <button style="margin-top:20px; padding:10px 30px; background:#39FF14; border:none; color:#000; font-weight:bold;">AUTO-SYNC</button>
    </div>
    """
    st.components.v1.html(mixer_html, height=300)
    st.write("💡 อัปโหลดไฟล์เสียงในระดับเครื่อง AGENT เพื่อเริ่มการ Mix")

st.markdown("---")
st.caption("SYNAPSE ULTIMATE SYSTEM v6.0 | © 2026")
