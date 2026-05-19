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
            
            /* พื้นหลังและฟอนต์หลัก ปรับตัวหนังสือให้หนาและชัดขึ้น */
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, #050a0f 0%, #010204 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #ffffff !important;
                font-weight: 400;
            }}
            
            /* ปรับแต่งข้อความทั่วไปให้เด่นชัด ไม่เบลอ */
            p, span, label, .stMarkdown {{
                color: #ffffff !important;
                font-weight: 500 !important;
                text-shadow: 0px 1px 2px rgba(0,0,0,0.5);
            }}
            
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .stApp {{ top: -60px; }}
            
            /* แท็บเมนู: เพิ่มความหนาเส้นขอบเป็น 4px และผสมผสานสีน้ำเงิน/แดง */
            .stTabs [data-baseweb="tab-list"] {{ gap: 14px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: #060d14; 
                border: 4px solid #1f3a52 !important; /* เส้นขอบหนา 4px สีน้ำเงินเข้ม */
                border-radius: 12px; padding: 14px 28px; 
                color: #00d2ff !important; /* ตัวหนังสือสีน้ำเงินสว่าง ชัดเจน */
                font-family: 'Orbitron', sans-serif; 
                font-weight: 700 !important;
                transition: 0.3s;
            }}
            
            /* แท็บที่เลือกใช้งาน: เปล่งประกายด้วยพลังสีแดงและสีหลัก */
            .stTabs [aria-selected="true"] {{
                background-color: rgba(255, 0, 60, 0.15) !important;
                border-color: {color_code} !important; /* เส้นขอบหนา 4px ตามสีที่เลือก */
                color: #ff003c !important; /* ตัวอักษรเปลี่ยนเป็นสีแดงนีออนเข้มข้น */
                box-shadow: 0 0 20px {color_code}55, inset 0 0 10px #ff003c;
            }}
            
            /* ช่องกรอกข้อมูล: เพิ่มความหนาเส้นขอบเป็น 4px สีน้ำเงินไซเบอร์ */
            .stTextInput>div>div>input, .stForm, .stTextArea>div>div>textarea {{
                background-color: #04080c !important;
                border: 4px solid #0055ff !important; /* เส้นขอบหนา 4px สีน้ำเงิน */
                color: #ffffff !important;
                border-radius: 10px !important;
                font-size: 16px !important;
                font-weight: bold !important;
            }}
            .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
                border-color: #ff003c !important; /* เวลาโฟกัสเปลี่ยนเป็นสีแดงแรงฤทธิ์ */
                box-shadow: 0 0 15px #ff003c !important;
            }}
            
            /* การ์ดแสดงความจริง: เพิ่มความหนาเส้นขอบเป็น 4px และไล่เฉดน้ำเงิน-แดง */
            .truth-card {{
                background: linear-gradient(135deg, rgba(4,12,24,0.95) 0%, rgba(20,4,8,0.95) 100%);
                border: 4px solid {color_code}; /* เส้นขอบหนา 4px */
                border-radius: 18px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 0 30px {color_code}40, inset 0 0 20px rgba(0,210,255,0.2);
                margin: 20px 0;
            }}
            
            /* กล่องสตรีมโลจิก: ขอบสีแดงนีออน */
            .logic-stream-box {{
                background-color: #03070a;
                border-left: 6px solid #ff003c; /* ขอบข้างหนาพิเศษสีแดง */
                padding: 18px;
                border-radius: 0 10px 10px 0;
                color: #00d2ff !important; /* ตัวอักษรสีน้ำเงินสว่าง */
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 18px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                border-top: 1px solid rgba(0,210,255,0.2);
                border-bottom: 1px solid rgba(0,210,255,0.2);
                border-right: 1px solid rgba(0,210,255,0.2);
            }}
            
            /* ปรับปุ่มกดของ Streamlit ให้หนาและชัดเจน */
            .stButton>button {{
                border: 4px solid #0055ff !important;
                border-radius: 10px !important;
                font-weight: bold !important;
                font-size: 16px !important;
                background: linear-gradient(135deg, #04080c 0%, #100408 100%) !important;
                color: #ffffff !important;
                transition: 0.3s;
            }}
            .stButton>button:hover {{
                border-color: #ff003c !important;
                box-shadow: 0 0 15px #ff003c;
                color: #ff003c !important;
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
audio_notif_data = get_base64("notification.mp3")

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
# 4. HEADER LOGO & SLOGAN WINKING (เอฟเฟกต์ไฟกระพริบผสมสีน้ำเงิน-แดง-สีธีม)
# =========================================================
header_html = f"""
<style>
    @keyframes dance {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(2px, -2px) rotate(1.5deg); }}
        50% {{ transform: translate(-2px, 2px) rotate(-1.5deg); }}
        75% {{ transform: translate(1px, 1px) rotate(0.5deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 15px {theme_color}, 0 0 30px #0055ff; }}
        33% {{ color: #00d2ff; text-shadow: 0 0 15px #0055ff, 0 0 30px #00d2ff; }}
        66% {{ color: #ff003c; text-shadow: 0 0 15px #ff003c, 0 0 30px #ff003c; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 15px 0; border-bottom: 4px solid #1f3a52; margin-bottom: 20px; }}
    .logo-img {{ width: 80px; height: 80px; animation: dance 0.8s infinite ease-in-out; filter: drop-shadow(0 0 12px {theme_color}); object-fit: contain; }}
    .slogan-txt {{ 
        font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 26px; letter-spacing: 4px;
        margin-left: 18px; animation: wink 3s infinite; 
    }}
</style>
<div class="logo-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else ''}
    <span class="slogan-txt">SYNAPSE COMMAND CENTER</span>
</div>
"""
components.html(header_html, height=120)

# =========================================================
# 5. AUTHENTICATION SYSTEM
# =========================================================
if not st.session_state.logged_in:
    st.markdown(f"<h2 style='text-align:center; color:#ff003c; font-family:Orbitron; font-weight:bold;'>🔒 SYSTEM AUTHENTICATION</h2>", unsafe_allow_html=True)
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
    
    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี AGENT"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ!")
    st.stop()

st.markdown(f"<div style='text-align:right; color:#00d2ff; font-family:Orbitron; font-size:14px; font-weight:bold; padding-right:10px;'>📡 AGENT OUTPOST: <span style='color:#ff003c;'>{st.session_state.user}</span></div>", unsafe_allow_html=True)

# =========================================================
# 6. NAVIGATION CONTROLLER
# =========================================================
menu_choice = st.radio(
    "เลือกฟังก์ชันระบบ:", 
    ["💬 CHATROOM SYSTEMS", "🛰️ GPS TRACER", "🔮 THE TRUTH SCANNER", "🎵 NEON JUKEBOX", "🧠 QUANTUM BRAIN SCAN"],
    horizontal=True, key="main_menu_navigator"
)
st.divider()

if st.sidebar.button("🔴 ออกจากระบบ (LOGOUT)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# Dummy blocks for navigation placeholders (Chat & GPS) เพื่อให้โค้ดรันได้ไม่พัง
if menu_choice == "💬 CHATROOM SYSTEMS":
    st.write("### 💬 ระบบห้องแชทเข้ารหัสความปลอดภัยสูง")
    st.info("ระบบกำลังเตรียมการสตรีมสัญญาณ...")

elif menu_choice == "🛰️ GPS TRACER":
    st.write("### 🛰️ ระบบติดตามพิกัดดาวเทียมเรียลไทม์")
    st.info("กำลังเรียกค้นสัญญาณ GPS ข้อมูลแกนพิกัด...")

# --- 7.3 ระบบคำนวณถอดรหัสวงรอบพลังงานจริง ---
elif menu_choice == "🔮 THE TRUTH SCANNER":
    st.markdown(f"<h2 style='color:#ff003c; text-align:center; font-family:Orbitron; font-weight:bold;'>🧬 QUANTUM TIME DECODER</h2>", unsafe_allow_html=True)
    
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
                <span style="color:#00d2ff; font-family:'Orbitron'; font-size:14px; font-weight:bold; letter-spacing:1px;">INDEX VALUE (ผลลัพธ์มวลตัวเลขจริง)</span>
                <h1 style="color:{theme_color}; font-family:'Orbitron'; font-size:60px; margin:10px 0; font-weight:bold; text-shadow: 0 0 20px {theme_color};">{res_index:.4f}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("### 🧮 อธิบายที่มาของมวลตัวเลขแกนวิทยาศาสตร์จริง:")
        st.latex(rf"Result = {formula_text} = {res_index:.4f}")
        
        st.markdown(f"""
        * <strong style='color:#00d2ff;'>{diff_days:,} (จำนวนวันสะสม):</strong> คือจำนวนวันรวมที่นับจริงห่างจากวันที่ 1 มกราคม ค.ศ. 1900 เพื่อใช้หาจุดตัดของช่วงเวลา
        * <strong style='color:#ff003c;'>{lunar_cycle} วัน (วงโคจรดวงจันทร์):</strong> ค่าเวลาเฉลี่ยตามจริงทางดาราศาสตร์ที่ดวงจันทร์โคจรรอบโลก 1 รอบ นำมาหารเพื่อหาช่วง <strong style='color:{theme_color};'>{'ข้างขึ้น' if is_waxing else 'ข้างแรม'} {lunar_num} ค่ำ</strong> โดยไม่มีการเดาสุ่ม
        * <strong style='color:#00d2ff;'>{day_val} (ลำดับวันประจำสัปดาห์):</strong> ลำดับแกนเวลาจริง (วันจันทร์=1 จนถึง วันอาทิตย์=7)
        * <strong style='color:#ff003c;'>1.618 (ค่าอัตราส่วนทองคำ / Golden Ratio):</strong> ค่าคงที่สากลทางคณิตศาสตร์ที่ใช้รักษาสมดุลแรงดันในโครงสร้างเลขฐานควอนตัมอดีตและอนาคต
        """)

# --- 7.4 ระบบเครื่องเล่นเพลงสุ่มต่อเนื่อง (ปรับปรุงใหม่ ป้องกัน Error 100%) ---
elif menu_choice == "🎵 NEON JUKEBOX":
    st.markdown(f"<h3 style='color:#00d2ff; font-family:Orbitron; text-align:center; font-weight:bold;'>🎵 AUTOLOOP RANDOM JUKEBOX</h3>", unsafe_allow_html=True)
    
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    
    if all_songs:
        st.markdown(f"<div style='color:#ffffff; font-weight:bold; font-size:16px; margin-bottom:10px;'>📁 ตรวจพบไฟล์เพลงในระบบทั้งหมดค้างอยู่ <span style='color:#ff003c;'>{len(all_songs)}</span> เพลง</div>", unsafe_allow_html=True)
        
        song_dict_js = {}
        for s in all_songs:
            b64 = get_base64(s)
            if b64: song_dict_js[s] = "data:audio/mp3;base64," + b64

        # ปรับขอบหนา 4px ไล่เฉดแดง-น้ำเงิน พร้อมปุ่มกดขนาดใหญ่ชัดเจน
        jukebox_html = f"""
        <div style="background:#04070a; border:4px solid #ff003c; border-radius:15px; padding:25px; text-align:center; box-shadow:0 0 25px rgba(255,0,60,0.35);">
            <div id="track-name" style="color:#ffffff; font-family:'Sarabun'; font-size:16px; font-weight:bold; margin-bottom:15px; text-shadow:0 0 5px #00d2ff;">เตรียมระบบขับเคลื่อนเสียง...</div>
            <audio id="core-player" controls style="width:100%; margin-bottom:20px;"></audio>
            <div>
                <button id="next-btn" style="background:linear-gradient(45deg, #ff003c, #0055ff); border:none; padding:12px 30px; border-radius:10px; color:#ffffff; font-weight:bold; font-size:15px; font-family:'Orbitron'; cursor:pointer; box-shadow: 0 0 15px #0055ff; transition: 0.2s;">⚡ NEXT RANDOM TRACK</button>
            </div>
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
                player.play().catch(e => console.log("รอการคลิกจากผู้ใช้ก่อนเริ่มเล่น"));
            }}

            btn.onclick = playRandom;
            player.onended = playRandom;

            // รันทันทีโดยไม่พึ่ง window.onload ป้องกันโครงสร้างย่อยตีกับ Streamlit
            playRandom();
        </script>
        """
        components.html(jukebox_html, height=220)
    else:
        st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์หลักของระบบแอปเลยครับบาส ลองอัปโหลดไฟล์เข้าไปดูก่อนนะ")

# --- 7.5 ระบบแปลงตัวอักษรเป็นความถี่จริง (ปรับปรุงลูปแอนิเมชันให้ปลอดภัย 100%) ---
elif menu_choice == "🧠 QUANTUM BRAIN SCAN":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron; font-weight:bold;'>🔮 QUANTUM CONSCIOUSNESS SCANNER</h3>", unsafe_allow_html=True)
    
    thought_input = st.text_input("กรอกข้อความหรือความคิดเพื่อสแกนถอดค่ามวลตัวเลข ($Hz$):", "อยู่นิ่งๆ ไม่เจ็บตัว")
    
    if thought_input:
        char_sum = sum(ord(c) for c in thought_input)
        calculated_hz = (char_sum % 700) + 120.0
        
        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#00d2ff; font-family:'Orbitron'; font-size:14px; font-weight:bold; letter-spacing:1px;">REAL-TIME FREQUENCY DETECTED</span>
                <h1 style="color:#ff003c; font-family:'Orbitron'; font-size:60px; margin:10px 0; font-weight:bold; text-shadow:0 0 20px #ff003c;">{calculated_hz:.2f} Hz</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("### 📊 คำอธิบายมวลตัวเลขของชุดคลื่นความถี่นี้:")
        st.markdown(f"""
        * <strong style='color:#00d2ff;'>{char_sum} (ผลรวมรหัสคลื่นอักขระออร์บิทัล):</strong> ได้มาจากการนำอักขระทีละตัวแปรในคำว่า `"{thought_input}"` ไปถอดค่าเลขฐานคอมพิวเตอร์จริงตัวต่อตัว (`ASCII unicode`) แล้วจับมาบวกกันทั้งหมดเพื่อหาค่ามวลหนาแน่นของข้อความ
        * <strong style='color:#ff003c;'>สูตรประมวลผลคำนวณ:</strong> ใช้รูปแบบสมการตัวเลขคณิตศาสตร์จริงด้านล่างนี้ โดยไม่มีการล็อกผลลัพธ์
        """)
        st.latex(rf"Hz = (TotalASCII \pmod{{700}}) + 120.0 = ({char_sum} \pmod{{700}}) + 120.0 = {calculated_hz:.2f} \, Hz")

        # หน้าจอแสดงเส้นกราฟิกเรืองแสงหนาและชัด ผสมสีแดงและน้ำเงินตามจังหวะคลื่นความถี่จริง
        canvas_html = f"""
        <canvas id="live-wave" style="width:100%; height:110px; background:#020508; border:4px solid #0055ff; border-radius:12px; box-shadow:0 0 15px rgba(0,85,255,0.3);"></canvas>
        <script>
            const canvas = document.getElementById('live-wave');
            const ctx = canvas.getContext('2d');
            let frame = 0;
            let animationFrameId;
            
            function drawWave() {{
                // ตรวจสอบความจริงของพิกัด Element เพื่อป้องกันข้อผิดพลาดเชิงโครงสร้างตอนสลับหน้าจอ
                if (!document.getElementById('live-wave')) {{
                    cancelAnimationFrame(animationFrameId);
                    return;
                }}
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // ใช้การไล่เฉดสีหนานุ่มของคลื่น (แดง ผสม น้ำเงิน และสีคอร์หลัก)
                let gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
                gradient.addColorStop(0, '#ff003c');   // เริ่มต้นที่แดงนีออน
                gradient.addColorStop(0.5, '{theme_color}'); // ตรงกลางเป็นสีหลักที่จูน
                gradient.addColorStop(1, '#00d2ff');   // ปลายสายเป็นสีน้ำเงินสว่าง
                
                ctx.strokeStyle = gradient;
                ctx.lineWidth = 4; // เส้นขอบความหนา 4 ตามที่ต้องการ
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#0055ff';
                
                ctx.beginPath();
                for(let x=0; x<canvas.width; x++) {{
                    let y = canvas.height/2 + Math.sin(x*0.03 + frame) * 25 * Math.cos(x*0.012);
                    if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                }}
                ctx.stroke();
                
                frame += {calculated_hz / 750};
                animationFrameId = requestAnimationFrame(drawWave);
            }}
            drawWave();
        </script>
        """
        components.html(canvas_html, height=130)

# =========================================================
# 8. GLOBAL SYSTEM FOOTER
# =========================================================
st.markdown("<div style='text-align:center; color:#00d2ff; font-size:13px; font-weight:bold; margin-top:40px; font-family:Orbitron; letter-spacing:2px;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.4.0</div>", unsafe_allow_html=True)
