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
import random
import pandas as pd
from datetime import datetime, date, timedelta

# =========================================================
# 1. CONFIG & SYSTEM THEME CONTROLLER (DYNAMIC NEON UI)
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

st.sidebar.markdown("<h4 style='color:#fff; font-family:Orbitron;'>🎨 SYSTEM CORE COLOR</h4>", unsafe_allow_html=True)
theme_color = st.sidebar.color_picker("ปรับจูนสีคลื่นพลังงานหลักของแอป:", "#39FF14")

def inject_cyberpunk_ui(color_code):
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@400;700&display=swap');
            
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, #050a0f 0%, #010204 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #ffffff !important;
            }}
            
            p, span, label, .stMarkdown {{
                color: #ffffff !important;
                font-weight: 500 !important;
            }}
            
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .stApp {{ top: -60px; }}
            
            /* ========================================================= */
            /* 🎯 ปรับปุ่มเมนูใหม่: ขนาดกลางพอดีนิ้ว ไม่ใหญ่เกินไป ใส่ข้อมูลชัดเจน */
            /* ========================================================= */
            [data-testid="stRadio"] > div {{
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 10px !important; /* เว้นช่องไฟกำลังสวย */
                padding: 5px 0 !important;
            }}
            
            [data-testid="stRadio"] label {{
                background: linear-gradient(135deg, #06111c 0%, #0c0612 100%) !important;
                border: 4px solid #0055ff !important; /* ขอบหนา 4px สีน้ำเงิน */
                border-radius: 10px !important;
                padding: 10px 15px !important; /* ขนาดลดลงมาพอดีๆ ไม่ใหญ่เกินไป */
                margin: 0 !important;
                min-width: 140px !important; /* ขนาดการ์ดกำลังดีสำหรับหน้าจอมือถือ */
                text-align: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                transition: all 0.2s ease-in-out !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.4) !important;
            }}
            
            [data-testid="stRadio"] label p {{
                font-family: 'Sarabun', sans-serif !important;
                font-size: 14px !important; /* ตัวอักษรขนาดพอดีตา */
                font-weight: bold !important;
                color: #00d2ff !important;
            }}
            
            [data-testid="stRadio"] label:hover {{
                border-color: #ff003c !important;
                box-shadow: 0 0 10px rgba(255,0,60,0.5) !important;
            }}
            
            [data-testid="stRadio"] label[data-checked="true"] {{
                background: linear-gradient(135deg, rgba(255, 0, 60, 0.2) 0%, rgba(0, 85, 255, 0.1) 100%) !important;
                border-color: {color_code} !important; /* ไฮไลต์ตามสีแกนหลัก */
                box-shadow: 0 0 15px {color_code}55 !important;
            }}
            
            [data-testid="stRadio"] label[data-checked="true"] p {{
                color: #ffffff !important;
                text-shadow: 0 0 5px {color_code} !important;
            }}
            
            /* ซ่อนวิทยุแบบเก่า */
            [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] {{ display: none !important; }}
            [data-testid="stRadio"] input[type="radio"] {{ display: none !important; }}
            /* ========================================================= */
            
            .stTextInput>div>div>input, .stForm, .stTextArea>div>div>textarea {{
                background-color: #04080c !important;
                border: 4px solid #0055ff !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                font-size: 16px !important;
                font-weight: bold !important;
            }}
            
            .truth-card {{
                background: linear-gradient(135deg, rgba(4,12,24,0.95) 0%, rgba(20,4,8,0.95) 100%);
                border: 4px solid {color_code};
                border-radius: 18px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 0 20px {color_code}40;
                margin: 15px 0;
            }}
            
            .logic-stream-box {{
                background-color: #03070a;
                border-left: 6px solid #ff003c;
                padding: 15px;
                border-radius: 0 10px 10px 0;
                color: #00d2ff !important;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 15px;
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

# =========================================================
# 4. HEADER LOGO & SLOGAN
# =========================================================
header_html = f"""
<style>
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 15px {theme_color}; }}
        50% {{ color: #ff003c; text-shadow: 0 0 15px #ff003c; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 10px 0; border-bottom: 4px solid #1f3a52; margin-bottom: 15px; }}
    .slogan-txt {{ font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 22px; letter-spacing: 3px; animation: wink 3s infinite; }}
</style>
<div class="logo-container">
    <span class="slogan-txt">SYNAPSE COMMAND CENTER</span>
</div>
"""
components.html(header_html, height=70)

# =========================================================
# 5. AUTHENTICATION SYSTEM
# =========================================================
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#ff003c; font-family:Orbitron;'>🔒 SYSTEM AUTHENTICATION</h2>", unsafe_allow_html=True)
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
                else:
                    st.error("ข้อมูลตรวจสอบความปลอดภัยไม่ถูกต้อง")
    st.stop()

st.markdown(f"<div style='text-align:right; color:#00d2ff; font-family:Orbitron; font-size:14px; font-weight:bold;'>📡 AGENT: <span style='color:#ff003c;'>{st.session_state.user}</span></div>", unsafe_allow_html=True)

# =========================================================
# 6. NAVIGATION CONTROLLER (เขียนหัวข้อชัดเจน เล็กลงพอดีนิ้วกด)
# =========================================================
menu_choice = st.radio(
    "เลือกฟังก์ชันระบบ:", 
    [
        "💬 ห้องแชทระบบ", 
        "🛰️ แผนที่ GPS", 
        "🔮 ถอดรหัสเวลาควอนตัม", 
        "🎵 กล่องเครื่องเล่นเพลง", 
        "🧠 สแกนคลื่นความถี่สมอง"
    ],
    horizontal=True, key="main_menu_navigator"
)
st.divider()

if st.sidebar.button("🔴 ออกจากระบบ (LOGOUT)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


# =========================================================
# 7. SYSTEM FUNCTIONS CORE (แก้ไขโครงสร้างแยก Iframe ป้องกัน RemoveChild Error)
# =========================================================

# --- 7.1 ระบบห้องแชท ---
if menu_choice == "💬 ห้องแชทระบบ":
    st.markdown("### 💬 SYNAPSE SECURE CHATROOM")
    chat_ref = db.reference('global_chat')
    messages_data = chat_ref.order_by_child('timestamp').limit_to_last(15).get()
    
    chat_box_html = "<div style='height:250px; overflow-y:auto; border:4px solid #0055ff; border-radius:12px; padding:12px; background:#03070a; color:#fff; font-family:sans-serif;'>"
    if messages_data:
        sorted_messages = sorted(messages_data.items(), key=lambda x: x[1].get('timestamp', ''))
        for msg_id, msg in sorted_messages:
            sender = msg.get('user', 'UNKNOWN')
            text = msg.get('text', '')
            time_str = msg.get('time_display', '')
            color = "#39FF14" if sender == st.session_state.user else "#ff003c"
            chat_box_html += f"<div><b style='color:{color};'>[{sender}]</b> <span style='color:#666; font-size:11px;'>({time_str})</span>: {text}</div>"
    else:
        chat_box_html += "<div style='color:#666; text-align:center; padding-top:90px;'>ไม่มีข้อมูลสื่อสาร</div>"
    chat_box_html += "</div>"
    
    st.components.v1.html(chat_box_html, height=270, scrolling=False)
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            chat_text = st.text_input("พิมพ์ข้อความ...", label_visibility="collapsed")
        with col2:
            if st.form_submit_button("ส่ง ⚡", use_container_width=True) and chat_text:
                chat_ref.push({
                    'user': st.session_state.user, 'text': chat_text,
                    'timestamp': time.time(), 'time_display': datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()

# --- 7.2 ระบบติดตามพิกัด GPS (แก้บั๊ก RemoveChild: เปลี่ยนมาใช้ปุ่มกดดึงค่าแมนนวล ไม่รันออโต้) ---
elif menu_choice == "🛰️ แผนที่ GPS":
    st.markdown("### 🛰️ REAL-TIME SATELLITE GPS TRACER")
    
    # สร้างปุ่มให้กดดึงพิกัดตามจริง แทนการใช้สคริปต์โหลดออโต้ เพื่อไม่ให้สคริปต์ไปทำลาย Node บราวเซอร์
    if st.button("📡 คลิกเพื่อเชื่อมต่อสัญญาณดาวเทียมและค้นหาพิกัดจริง", use_container_width=True):
        with st.spinner("กำลังดึงค่าพิกัดความแม่นยำจริงจากเซนเซอร์..."):
            loc = get_geolocation()
            
        if loc and 'coords' in loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            acc = loc['coords'].get('accuracy', 0)
            
            db.reference(f'users/{st.session_state.user}/last_gps').set({
                'lat': lat, 'lon': lon, 'accuracy': acc, 'updated_at': datetime.now().isoformat()
            })
            
            st.success(f"🎯 ค้นพบพิกัดสัญญาณ: ละติจูด {lat:.6f} / ลองจิจูด {lon:.6f} (ความแม่นยำรัศมี {acc:.2f} เมตร)")
            
            m = folium.Map(location=[lat, lon], zoom_start=16, tiles="CartoDB dark_matter")
            folium.Marker([lat, lon], popup=st.session_state.user).add_to(m)
            
            st.markdown("<div style='border:4px solid #39FF14; border-radius:12px; overflow:hidden;'>", unsafe_allow_html=True)
            st_folium(m, width="100%", height=300, returned_objects=[])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("⚠️ ไม่สามารถดึงพิกัดได้ กรุณาเปิดสิทธิ์เปิดตำแหน่ง GPS บนบราวเซอร์โทรศัพท์มือถือด้วยนะครับบาส")

# --- 7.3 ระบบถอดรหัสวงรอบพลังงานจริง ---
elif menu_choice == "🔮 ถอดรหัสเวลาควอนตัม":
    st.markdown("### 🧬 QUANTUM TIME DECODER")
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

        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#00d2ff; font-size:14px; font-weight:bold;">INDEX VALUE (ผลลัพธ์มวลตัวเลขจริง)</span>
                <h1 style="color:{theme_color}; font-size:50px; margin:10px 0; font-weight:bold;">{res_index:.4f}</h1>
            </div>
        """, unsafe_allow_html=True)
        st.latex(rf"Result = {formula_text} = {res_index:.4f}")

# --- 7.4 ระบบเครื่องเล่นเพลงสุ่มต่อเนื่อง ---
elif menu_choice == "🎵 กล่องเครื่องเล่นเพลง":
    st.markdown("### 🎵 AUTOLOOP RANDOM JUKEBOX")
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    
    if all_songs:
        song_dict_js = {}
        for s in all_songs:
            b64 = get_base64(s)
            if b64: song_dict_js[s] = "data:audio/mp3;base64," + b64

        jukebox_html = f"""
        <div style="background:#04070a; border:4px solid #ff003c; border-radius:15px; padding:20px; text-align:center;">
            <div id="track-name" style="color:#ffffff; font-size:15px; font-weight:bold; margin-bottom:15px;">เตรียมระบบขับเคลื่อนเสียง...</div>
            <audio id="core-player" controls style="width:100%; margin-bottom:15px;"></audio>
            <button id="next-btn" style="background:linear-gradient(45deg, #ff003c, #0055ff); border:none; padding:10px 25px; border-radius:8px; color:#fff; font-weight:bold; cursor:pointer;">⚡ NEXT RANDOM TRACK</button>
        </div>
        <script>
            const songData = {str(song_dict_js)};
            const playlist = Object.keys(songData);
            const player = document.getElementById('core-player');
            const txt = document.getElementById('track-name');
            const btn = document.getElementById('next-btn');

            function playRandom() {{
                if(playlist.length === 0) return;
                const randomIndex = Math.floor(Math.random() * playlist.length);
                const chosenSong = playlist[randomIndex];
                txt.innerHTML = "กำลังเล่นสุ่มวนลูป 🔄: <span style='color:#39FF14;'>" + chosenSong + "</span>";
                player.src = songData[chosenSong];
                player.play().catch(e => console.log("รอการคลิก"));
            }}
            btn.onclick = playRandom;
            player.onended = playRandom;
            playRandom();
        </script>
        """
        components.html(jukebox_html, height=200)
    else:
        st.markdown("<div style='background:#100408; border:4px solid #ff003c; border-radius:10px; padding:20px; text-align:center;'>⚠️ ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์หลัก นำไฟล์เพลงไปวางคู่กับโค้ดเพื่อเริ่มใช้งานครับบาส</div>", unsafe_allow_html=True)

# --- 7.5 ระบบแปลงตัวอักษรเป็นความถี่จริง ---
elif menu_choice == "🧠 สแกนคลื่นความถี่สมอง":
    st.markdown("### 🔮 QUANTUM CONSCIOUSNESS SCANNER")
    thought_input = st.text_input("กรอกข้อความหรือความคิดเพื่อสแกนถอดค่ามวลตัวเลข ($Hz$):", "อยู่นิ่งๆ ไม่เจ็บตัว")
    
    if thought_input:
        char_sum = sum(ord(c) for c in thought_input)
        calculated_hz = (char_sum % 700) + 120.0
        
        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#00d2ff; font-size:14px; font-weight:bold;">REAL-TIME FREQUENCY DETECTED</span>
                <h1 style="color:#ff003c; font-size:50px; margin:10px 0; font-weight:bold;">{calculated_hz:.2f} Hz</h1>
            </div>
        """, unsafe_allow_html=True)
        st.latex(rf"Hz = (TotalASCII \pmod{{700}}) + 120.0 = {calculated_hz:.2f} \, Hz")

        canvas_html = f"""
        <canvas id="live-wave" style="width:100%; height:90px; background:#020508; border:4px solid #0055ff; border-radius:12px;"></canvas>
        <script>
            const canvas = document.getElementById('live-wave');
            const ctx = canvas.getContext('2d');
            let frame = 0;
            let animationFrameId;
            function drawWave() {{
                if (!document.getElementById('live-wave')) {{
                    cancelAnimationFrame(animationFrameId);
                    return;
                }}
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                let gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
                gradient.addColorStop(0, '#ff003c');
                gradient.addColorStop(0.5, '{theme_color}');
                gradient.addColorStop(1, '#00d2ff');
                ctx.strokeStyle = gradient;
                ctx.lineWidth = 4;
                ctx.beginPath();
                for(let x=0; x<canvas.width; x++) {{
                    let y = canvas.height/2 + Math.sin(x*0.03 + frame) * 20 * Math.cos(x*0.012);
                    if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                }}
                ctx.stroke();
                frame += {calculated_hz / 750};
                animationFrameId = requestAnimationFrame(drawWave);
            }}
            drawWave();
        </script>
        """
        components.html(canvas_html, height=110)

# =========================================================
# 8. GLOBAL SYSTEM FOOTER
# =========================================================
st.markdown("<div style='text-align:center; color:#00d2ff; font-size:13px; font-weight:bold; margin-top:30px; font-family:Orbitron;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.4.0</div>", unsafe_allow_html=True)
