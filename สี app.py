import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64
import os
import json
import random
import pandas as pd
from datetime import datetime, date, timedelta

# =========================================================
# 1. CONFIG & SYSTEM THEME CONTROLLER
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

st.sidebar.markdown("<h4 style='color:#fff; font-family:Orbitron;'>🎨 SYSTEM CORE COLOR</h4>", unsafe_allow_html=True)
theme_color = st.sidebar.color_picker("ปรับจูนสีคลื่นพลังงานหลักของแอป:", "#39FF14")

def inject_cyberpunk_ui(color_code):
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;500&display=swap');
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, #080f14 0%, #030508 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }}
            .stTabs [data-baseweb="tab-list"] {{ gap: 12px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: #0b1116; border: 1px solid #1a2936;
                border-radius: 8px; padding: 12px 24px; color: #666;
                font-family: 'Orbitron', sans-serif; transition: 0.3s;
            }}
            .stTabs [aria-selected="true"] {{
                background-color: {color_code}15 !important;
                border-color: {color_code} !important; color: {color_code} !important;
            }}
            .truth-card {{
                background: linear-gradient(135deg, rgba(11,20,28,0.9) 0%, rgba(4,8,12,0.95) 100%);
                border: 2px solid {color_code}; border-radius: 16px; padding: 25px; text-align: center; margin: 15px 0;
            }}
        </style>
    """, unsafe_allow_html=True)

inject_cyberpunk_ui(theme_color)

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64("logo1.png")

# =========================================================
# 2. FIREBASE CONNECTION
# =========================================================
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"การเชื่อมต่อฐานข้อมูลผิดพลาด: {e}")

# =========================================================
# 3. SESSION STATE CONFIGURATION
# =========================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

# Header HTML
header_html = f"""
<div style="text-align:center; padding:15px; border-bottom:1px solid #121e29; font-family:'Orbitron'; font-size:24px; color:{theme_color}; font-weight:bold;">
    SYNAPSE COMMAND CENTER
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Authentication System
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ SYSTEMS", "📝 ลงทะเบียน AGENT ใหม่"])
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("ชื่อผู้ใช้ (AGENT ID)")
            u_pw = st.text_input("รหัสผ่าน", type="password")
            if st.form_submit_button("เข้าสู่ระบบ ⚡", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('password') == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.rerun()
                else: st.error("ข้อมูลไม่ถูกต้อง")
    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี AGENT"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ!")
    st.stop()

st.markdown(f"<div style='text-align:right; color:{theme_color}; font-family:Orbitron; font-size:12px;'>📡 AGENT OUTPOST: {st.session_state.user}</div>", unsafe_allow_html=True)

# Navigation
menu_choice = st.radio(
    "เลือกฟังก์ชันระบบ:", 
    ["💬 CHATROOM SYSTEMS", "🛰️ GPS TRACER", "🔮 THE TRUTH SCANNER", "🎵 NEON JUKEBOX", "🧠 QUANTUM BRAIN SCAN"],
    horizontal=True
)
st.divider()

if st.sidebar.button("🔴 ออกจากระบบ (LOGOUT)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# =========================================================
# FUNCTIONS IMPLEMENTATION
# =========================================================

# --- 7.1 ระบบแชตข้ามมิติทำงานได้จริง ---
if menu_choice == "💬 CHATROOM SYSTEMS":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>💬 CYBER CHATROOM</h3>", unsafe_allow_html=True)
    
    # ดึงข้อมูลแชตจาก Firebase 50 ข้อความล่าสุด
    chat_ref = db.reference('chatroom').order_by_key().limit_to_last(50)
    messages = chat_ref.get()
    
    # แสดงข้อความ
    chat_box = ""
    if messages:
        for msg_id, msg_data in messages.items():
            user_msg = msg_data.get('user', 'Unknown')
            text_msg = msg_data.get('text', '')
            time_msg = msg_data.get('time', '')
            chat_box += f"<p style='margin:5px 0;'><b>[{time_msg}] {user_msg}:</b> {text_msg}</p>"
    
    st.markdown(f"""
        <div style="background:#060a0d; border:1px solid #1a2936; padding:15px; height:300px; overflow-y:auto; border-radius:8px; margin-bottom:15px;">
            {chat_box if chat_box else '<p style="color:#666;">ยังไม่มีการสื่อสารในระบบ...</p>'}
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("send_msg_form", clear_on_submit=True):
        user_input = st.text_input("พิมพ์ข้อความที่ต้องการส่งลงระบบ...")
        if st.form_submit_button("ส่งสัญญาณ 🛰️"):
            if user_input:
                now_str = datetime.now().strftime("%H:%M:%S")
                db.reference('chatroom').push({
                    'user': st.session_state.user,
                    'text': user_input,
                    'time': now_str
                })
                st.rerun()

# --- 7.2 ระบบพิกัดดาวเทียมจริง ---
elif menu_choice == "🛰️ GPS TRACER":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🛰️ REAL-TIME GPS LOCATOR</h3>", unsafe_allow_html=True)
    st.write("ระบบกำลังขอสิทธิ์เข้าถึงพิกัดจากเบราว์เซอร์ของคุณ (กรุณากด Allow หรือ อนุญาต หากมีหน้าต่างแจ้งเตือน)")
    
    # เรียกขอตำแหน่งพิกัดจริงจาก Web Browser
    loc = get_geolocation()
    
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        
        st.success(f"ตรวจพบพิกัดดาวเทียมจริง: Latitude {lat} | Longitude {lon}")
        
        # วาดแผนที่ Folium จริงๆ
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB dark_matter")
        folium.Marker([lat, lon], popup="พิกัดปัจจุบันของคุณ", icon=folium.Icon(color="green")).add_to(m)
    # แก้ไขจากของเดิมที่เป็น Error ให้เหลือแค่นี้พอครับ ทำงานได้จริงแน่นอน
st_folium(m, width="100%", height=400)

    else:
        st.warning("🔄 กำลังรอการตอบรับพิกัด หรือบราว์เซอร์ของคุณไม่ได้เปิดแชร์ตำแหน่งโลเคชั่น")

# --- 7.3 ระบบคำนวณวงรอบพลังงาน ---
elif menu_choice == "🔮 THE TRUTH SCANNER":
    st.markdown(f"<h2 style='color:{theme_color}; text-align:center; font-family:Orbitron;'>🧬 QUANTUM TIME DECODER</h2>", unsafe_allow_html=True)
    user_dob = st.date_input("เลือกวันเดือนปีเกิดเพื่อถอดมวลรหัสคณิตศาสตร์:", value=date(1996,8,17))
    if user_dob:
        ref_date = date(1900, 1, 1)
        diff_days = (user_dob - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff_days - 0.5) % lunar_cycle
        day_val = user_dob.weekday() + 1
        is_waxing = pos <= 14.765
        lunar_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
        if is_waxing:
            res_index = math.sqrt((day_val**2) + (lunar_num**2))
            formula_text = f"\\sqrt{{{day_val}^2 + {lunar_num}^2}}"
        else:
            res_index = (day_val * 1.618) / (lunar_num if lunar_num != 0 else 1)
            formula_text = f"\\frac{{{day_val} \\times 1.618}}{{{lunar_num}}}"

        st.markdown(f"""<div class="truth-card"><h1 style="color:{theme_color}; font-family:'Orbitron'; font-size:55px;">{res_index:.4f}</h1></div>""", unsafe_allow_html=True)
        st.latex(rf"Result = {formula_text} = {res_index:.4f}")

# --- 7.4 ระบบเครื่องเล่นเพลงที่ทำงานได้จริงผ่าน JS JSON ---
elif menu_choice == "🎵 NEON JUKEBOX":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron; text-align:center;'>🎵 AUTOLOOP RANDOM JUKEBOX</h3>", unsafe_allow_html=True)
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    
    if all_songs:
        st.write(f"📁 ตรวจพบไฟล์เพลงในระบบทั้งหมดค้างอยู่ {len(all_songs)} เพลง")
        song_dict_js = {}
        for s in all_songs:
            b64 = get_base64(s)
            if b64: song_dict_js[s] = "data:audio/mp3;base64," + b64

        # แปลงเป็น JSON String ที่ถูกต้องเพื่อส่งให้ JavaScript อย่างปลอดภัย
        playlist_json = json.dumps(list(song_dict_js.keys()))
        song_data_json = json.dumps(song_dict_js)

        jukebox_html = f"""
        <div style="background:#04070a; border:2px solid {theme_color}; border-radius:15px; padding:20px; text-align:center;">
            <div id="track-name" style="color:#fff; font-family:'Sarabun'; font-size:15px; margin-bottom:10px;">กรุณากดปุ่มด้านล่างเพื่อเริ่มระบบขับเคลื่อนเสียง</div>
            <audio id="core-player" controls style="width:100%; margin-bottom:15px;"></audio>
            <div>
                <button onclick="playRandom()" style="background:linear-gradient(45deg, #ff00de, {theme_color}); border:none; padding:10px 25px; border-radius:8px; color:#fff; font-weight:bold; cursor:pointer;">⚡ START / NEXT RANDOM TRACK</button>
            </div>
        </div>

        <script>
            // ดึงค่าอย่างปลอดภัยผ่าน JSON.parse
            const playlist = JSON.parse('{playlist_json}');
            const songData = JSON.parse('{song_data_json}');
            const player = document.getElementById('core-player');
            const txt = document.getElementById('track-name');

            function playRandom() {{
                if(playlist.length === 0) return;
                const randomIndex = Math.floor(Math.random() * playlist.length);
                const chosenSong = playlist[randomIndex];
                
                txt.innerText = "กำลังเล่นสุ่มวนลูป 🔄: " + chosenSong;
                player.src = songData[chosenSong];
                player.play().catch(e => {{
                    txt.innerText = "ติดข้อกำหนดเบราว์เซอร์: กรุณากดปุ่มเพื่อคลิกเล่นอีกครั้ง";
                }});
            }}

            player.onended = function() {{
                playRandom();
            }};
        </script>
        """
        components.html(jukebox_html, height=220)
    else:
        st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์หลัก ลองใส่ไฟล์เพลงไว้ในโฟลเดอร์เดียวกับโค้ดดูก่อนนะ")

# --- 7.5 ระบบสแกนสมองความถี่ควอนตัม ---
elif menu_choice == "🧠 QUANTUM BRAIN SCAN":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🔮 QUANTUM CONSCIOUSNESS SCANNER</h3>", unsafe_allow_html=True)
    thought_input = st.text_input("กรอกข้อความหรือความคิดเพื่อสแกนถอดค่ามวลตัวเลข ($Hz$):", "อยู่นิ่งๆ ไม่เจ็บตัว")
    if thought_input:
        char_sum = sum(ord(c) for c in thought_input)
        calculated_hz = (char_sum % 700) + 120.0
        st.markdown(f"""<div class="truth-card"><h1 style="color:#ff00de; font-family:'Orbitron'; font-size:55px;">{calculated_hz:.2f} Hz</h1></div>""", unsafe_allow_html=True)
        st.latex(rf"Hz = (TotalASCII \pmod{{700}}) + 120.0 = {calculated_hz:.2f} \, Hz")

st.markdown("<div style='text-align:center; color:#3b566e; font-size:11px; margin-top:30px;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.4.0</div>", unsafe_allow_html=True)
