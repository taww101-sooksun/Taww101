import streamlit as st
import os 
import base64
import time
import math
from datetime import datetime, timedelta, date
import firebase_admin
from firebase_admin import credentials, firestore, db as realdb
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. INITIAL SETUP & FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        # พยายามดึงจาก Secrets (สำหรับ Streamlit Cloud)
        if "firebase" in st.secrets:
            fb_creds = dict(st.secrets["firebase"])
            # จัดการเรื่องขึ้นบรรทัดใหม่ใน Private Key
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.get("firebase_db_url", "")
            })
        else:
            # สำหรับรันในเครื่อง (Local)
            cred = credentials.Certificate("your-firebase-key.json")
            firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"🛰️ Firebase Connection Error: {e}")

# เชื่อมต่อ Firestore (สำหรับ Login) และ Realtime DB (สำหรับ Chat/Radar)
fs_db = firestore.client()

# ==========================================
# 2. LOGIC FUNCTIONS (Auth & System)
# ==========================================

def login_user(username, password):
    user_ref = fs_db.collection("users").document(username).get()
    if user_ref.exists:
        if user_ref.to_dict().get("password") == password:
            return True
    return False

def register_user(username, password):
    if not username or not password:
        return False, "กรุณากรอกข้อมูลให้ครบถ้วน"
    user_ref = fs_db.collection("users").document(username)
    if user_ref.get().exists:
        return False, f"AGENT ID '{username}' นี้ถูกใช้ไปแล้ว"
    else:
        user_ref.set({
            "password": password,
            "created_at": firestore.SERVER_TIMESTAMP,
            "status": "active"
        })
        return True, "ลงทะเบียนสำเร็จ! ตอนนี้คุณสามารถ Login ได้แล้ว"

# ==========================================
# 3. MODULES (The Rooms)
# ==========================================
# (ย้ายฟังก์ชัน room_core, room_radar, room_comms, room_music, room_sensor, room_logic มาไว้ตรงนี้)
# *หมายเหตุ: ผมย่อไว้เพื่อให้คุณเห็นโครงสร้างหลัก แต่ในโค้ดจริงคุณใส่เนื้อหาเดิมที่คุณเขียนมาได้เลย*

def room_core():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.now()
    st.write(f"AGENT: {st.session_state.user}")
    st.write(f"TIME: {now.strftime('%H:%M:%S')}")
def room_logic():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        # ปีนักษัตร
        thai_year = dt.year + 543
        zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
        zodiac = zodiacs[thai_year % 12]
        
        # ธาตุประจำวัน
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val)

        if pos <= 14.765:
            m_num = int(pos) + 1
            phase = f"ขึ้น {m_num} ค่ำ"
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดัน (Vector)"
        else:
            m_num = int(pos - 14.765) + 1
            phase = f"แรม {m_num} ค่ำ"
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำ (Phi)"
            
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff}

    st.subheader("🔍 วิเคราะห์พิกัดความจริง (อดีต-อนาคต)")
    target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
    
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3);">
                <small>รหัสพิกัดจักรวาล</small>
                <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0;">{d['res']}</h1>
                <p style="color:#888;">{d['type']}</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 **ฐานวัน ({d['day_num']}):** แรงดึงดูดโลก")
            st.info(f"🌙 **จันทรคติ ({d['phase']}):** แรงดึงดูดดวงจันทร์")
        with col2:
            st.success(f"🐎 **ปีนักษัตร:** ปี{d['zodiac']}")
            st.success(f"💎 **ธาตุประจำวัน:** ธาตุ{d['element']}")

        st.markdown(f"""
            <div style="background:#111; padding:15px; border-left:5px solid {st.session_state.theme_color}; border-radius:10px; margin-top:10px;">
                <p style="font-size:14px; color:#aaa; margin:0;">
                    <b>สูตรการคำนวณ:</b> {d['formula']}<br>
                    คำนวณจากวันที่สะสมตั้งแต่ปี 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                </p>
            </div>
        """, unsafe_allow_html=True)

        if target_date < date.today(): st.warning("⏪ ตรวจสอบรอยเท้าพลังงานใน **'อดีต'**")
        elif target_date > date.today(): st.error("🔮 ตรวจสอบพิกัดเป้าหมายใน **'อนาคต'**")
        else: st.success("🟢 พิกัดพลังงานใน **'ปัจจุบัน'**")

# ... (ใส่ room_radar, room_comms, room_music, room_sensor, room_logic ตามลำดับ) ...

# ==========================================
# 4. UI PAGES
# ==========================================

def auth_page():
    st.title("🛡️ SYNAPSE AUTHENTICATION")
    choice = st.radio("SELECT", ["LOGIN", "SIGN UP"], horizontal=True)
    
    if choice == "LOGIN":
        with st.form("login_form"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("ACCESS SYSTEM"):
                if login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Access Denied")
    else:
        with st.form("reg_form"):
            new_u = st.text_input("NEW AGENT ID")
            new_p = st.text_input("NEW PASSWORD", type="password")
            conf_p = st.text_input("CONFIRM", type="password")
            if st.form_submit_button("CREATE AGENT"):
                if new_p == conf_p:
                    success, msg = register_user(new_u, new_p)
                    if success: st.success(msg)
                    else: st.error(msg)
                else: st.error("Passwords do not match")

# ==========================================
# 5. MAIN EXECUTION (One Main to Rule Them All)
# ==========================================

def main():
    # --- A. Initialize Session State ---
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = ""
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    # --- B. Routing (Login Check) ---
    if not st.session_state.logged_in:
        auth_page()
    else:
        # --- C. Sidebar System ---
        with st.sidebar:
            st.title("⚙️ SYSTEM")
            # ใช้ key ที่ไม่ซ้ำเพื่อป้องกัน Error
            st.session_state.user = st.text_input("AGENT ID", st.session_state.user, key="sb_user_input")
            st.session_state.theme_color = st.color_picker("THEME", st.session_state.theme_color, key="sb_theme")
            st.session_state.bg_color = st.color_picker("BACKGROUND", st.session_state.bg_color, key="sb_bg")
            
            if st.button("🔴 LOGOUT"):
                st.session_state.logged_in = False
                st.rerun()
                
            st.markdown("---")
            st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

        # --- D. Tabs Layout ---
        tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR", "🧬 LOGIC"])
        
        with tabs[0]: room_core()
        # with tabs[1]: room_radar() 
        # (และอื่นๆ ต่อไปจนครบ)

if __name__ == "__main__":
    main()
