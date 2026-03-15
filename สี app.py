import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os # เพิ่มเพื่อเช็คไฟล์ภาพ

# --- 1. CONFIGURATION & LOGO SETUP (ตำแหน่ง B: Favicon) ---
# ตรวจสอบว่ามีไฟล์โลโก้ไหม ถ้ามีให้ใช้เป็น Favicon ในแถบ Browser
logo_path = "logo3.jpg"
logo_exists = os.path.exists(logo_path)

st.set_page_config(
    page_title="SYNAPSE IDENTITY",
    page_icon=logo_path if logo_exists else "🌐", # ใช้โลโก้เป็นไอคอน Browser ถ้ามี
    layout="wide"
)

# --- 2. INITIALIZE FIREBASE ---
@st.cache_resource
def init_firebase():
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
            # แก้ URL เป็น Region Singapore (asia-southeast1)
            target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
            firebase_admin.initialize_app(cred, {'databaseURL': target_url})
            return True
        except Exception as e:
            st.error(f"🚨 เชื่อมต่อ Firebase ไม่ได้: {e}")
            return False
    return True

init_firebase()

# --- 3. MULTI-LANGUAGE DATA (6 ภาษา) ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "sys": "🧹 ระบบ", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ", "manual": "คู่มือ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "sys": "🧹 SYSTEM", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME", "manual": "MANUAL"},
    "JP": {"welcome": "ようこそ", "core": "🚀 コア", "radar": "🛰️ レーダー", "comms": "💬 通信", "sys": "🧹 システム", "lat": "緯度", "lon": "経度", "time": "システム時間", "manual": "マニュアル"},
    "CN": {"welcome": "欢迎", "core": "🚀 核心", "radar": "🛰️ 雷达", "comms": "💬 通讯", "sys": "🧹 系统", "lat": "纬度", "lon": "经度", "time": "系统时间", "manual": "手册"},
    "MM": {"welcome": "ကြိုဆိုပါတယ်", "core": "🚀 အဓိက", "radar": "🛰️ ရေဒါ", "comms": "💬 ဆက်သွယ်ရေး", "sys": "🧹 စနစ်", "lat": "လတ္တီတွဒ်", "lon": "လောင်ဂျီတွဒ်", "time": "စနစ်အချိန်", "manual": "လမ်းညွှန်"},
    "LA": {"welcome": "ຍິນດີຕ້ອນຮັບ", "core": "🚀 ແກນຫຼັກ", "radar": "🛰️ ເຣດາ", "comms": "💬 ສື່ສານ", "login": "ເຂົ້າສູ່ລະບົບ", "sys": "🧹 ລະບົບ", "lat": "ລະຕິຈູด", "lon": "ລອງຕິຈູດ", "time": "ເວລາລະບົບ", "manual": "ຄູ່ມື"}
}

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 5. LOGIN UI (หน้าแรกที่มีป้ายบอกทาง และโลโก้ตำแหน่ง A) ---
def login_ui():
    # แสดงโลโก้ด้านบนสุดของหน้า Login
    if logo_exists:
        st.image(logo_path, width=200) 
    
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {st.session_state.theme_color}; border-radius: 15px; background: rgba(0,0,0,0.5);">
            <h1 style="color:{st.session_state.theme_color}; margin-bottom:0;">🌐 SYNAPSE IDENTITY</h1>
            <p style="color:#888;">NEURAL NETWORK INTERFACE SYSTEM</p>
            <hr style="border: 0.5px solid #333;">
            <div style="text-align: left; margin: 20px auto; max-width: 400px;">
                <p style="color:{st.session_state.theme_color};"><b>📥 ขั้นตอนการเข้าใช้งาน:</b></p>
                <ol style="color:#bbb; font-size: 0.9em;">
                    <li>กรอก <b>รหัสผ่านลับ</b> (Password) ในช่องด้านล่าง</li>
                    <li>กดปุ่ม <b>ENTER SYSTEM</b> เพื่อยืนยันตัวตน</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("SECURITY KEY REQUIRED", type="password", placeholder="กรุณาใส่รหัสผ่าน...")
        if st.button("🚀 ENTER SYSTEM"):
            if password == "notty101": 
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Access Denied")
    
    st.markdown(f"<p style='text-align:center; color:#444; margin-top:50px;'><i>{st.session_state.lang == 'TH' and 'อยู่นิ่งๆ ไม่เจ็บตัว' or 'Stay still, stay safe'}</i></p>", unsafe_allow_html=True)
    st.stop()

if not st.session_state.logged_in:
    login_ui()

# --- 6. MAIN UI SETUP ---
L = LANG_DATA[st.session_state.lang]

st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stButton>button {{ border: 1px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; background: transparent; width: 100%; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 7. SIDEBAR (โลโก้ตำแหน่ง A) ---
with st.sidebar:
    # แสดงโลโก้ด้านบนสุดของ Sidebar
    if logo_exists:
        st.image(logo_path, use_column_width=True)
        
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("ID", st.session_state.user_name)
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.markdown("---")
    st.write('**Slogan:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- 8. MAIN TABS ---
tabs = st.tabs([L["core"], L["radar"], L["comms"], L["sys"]])

# TAB 0: แกนหลัก
with tabs[0]:
    c1, c2 = st.columns([2,1])
    c1.header(f"{L['welcome']}, {st.session_state.user_name}")
    c2.metric(L["time"], time.strftime("%H:%M:%S"))
    if st.button("📢 BROADCAST SIGNAL"):
        try:
            db.reference('logs/activity').push({'user': st.session_state.user_name, 'ts': time.time()})
            st.toast("Signal Broadcasted!")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 1: เรดาร์
with tabs[1]:
    st.subheader(L["radar"])
    col_a, col_b = st.columns(2)
    lat_val = col_a.number_input(L["lat"], value=13.7500, format="%.4f")
    lon_val = col_b.number_input(L["lon"], value=100.5100, format="%.4f")
    map_data = pd.DataFrame({'lat': [lat_val], 'lon': [lon_val]})
    st.map(map_data, color=st.session_state.theme_color)

# TAB 3: ระบบ & คู่มือ
with tabs[3]:
    st.subheader(f"📖 {L['manual']}")
    with st.expander("เปิดอ่านคู่มือการใช้งาน"):
        st.write(f"1. ใส่รหัส 'notty101' เพื่อเข้าเครื่อง")
        st.write(f"2. หน้า {L['core']} ใช้ส่งสัญญาณยืนยันตัวตน")
        st.write(f"3. หน้า {L['radar']} ใช้ปักหมุดตำแหน่ง (สีหมุดเปลี่ยนตาม Theme)")
        st.write(f"4. หน้า {L['comms']} ใช้สำหรับติดต่อสื่อสาร")
    
    if st.button("REBOOT CORE"):
        st.cache_resource.clear()
        st.rerun()
