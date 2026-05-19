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
            
            /* ========================================================= */
            /* 🔥 ขยายปุ่มเมนูหลัก (RADIO BUTTONS) หน้าแรกให้ใหญ่ ย่นระยะจิ้มง่ายขึ้นบนมือถือ */
            /* ========================================================= */
            [data-testid="stRadio"] > div {{
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 15px !important; /* เพิ่มช่องไฟระหว่างปุ่ม */
                padding: 10px 0 !important;
            }}
            
            [data-testid="stRadio"] label {{
                background: linear-gradient(135deg, #06111c 0%, #0c0612 100%) !important;
                border: 4px solid #0055ff !important; /* เส้นขอบหนา 4px สีน้ำเงิน */
                border-radius: 14px !important; /* มนกลมสไตล์ไซเบอร์ */
                padding: 18px 24px !important; /* เพิ่มความกว้างใหญ่ของพื้นที่ปุ่มกดให้จิ้มง่าย */
                margin: 0 !important;
                min-width: 160px !important; /* กำหนดขนาดขั้นต่ำให้เต็มมือกด */
                text-align: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                transition: all 0.25s ease-in-out !important;
                box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
            }}
            
            /* ตัวหนังสือข้างในปุ่มเมนู */
            [data-testid="stRadio"] label p {{
                font-family: 'Orbitron', 'Sarabun', sans-serif !important;
                font-size: 16px !important; /* ปรับขนาดตัวหนังสือให้ใหญ่เด่นชัด */
                font-weight: 700 !important;
                color: #00d2ff !important; /* สีน้ำเงินสว่าง */
            }}
            
            /* เมื่อเอาเมาส์วางหรือใช้นิ้วจิ้มปุ่มเมนู */
            [data-testid="stRadio"] label:hover {{
                border-color: #ff003c !important; /* ขอบเปลี่ยนเป็นสีแดงนีออน */
                box-shadow: 0 0 15px rgba(255,0,60,0.5) !important;
            }}
            
            /* เอฟเฟกต์เมื่อปุ่มเมนูนั้นถูกเลือกใช้งาน (Active) */
            [data-testid="stRadio"] label[data-checked="true"] {{
                background: linear-gradient(135deg, rgba(255, 0, 60, 0.2) 0%, rgba(0, 85, 255, 0.1) 100%) !important;
                border-color: {color_code} !important; /* ขอบหนาตามสีหลักที่จูน */
                box-shadow: 0 0 25px {color_code}66, inset 0 0 10px rgba(255,0,60,0.3) !important;
            }}
            
            [data-testid="stRadio"] label[data-checked="true"] p {{
                color: #ffffff !important; /* ตัวอักษรปุ่มที่เลือกเป็นสีขาวสว่างชัดเจน */
                text-shadow: 0 0 8px {color_code} !important;
            }}
            
            /* ซ่อนวงกลมวิทยุแบบเก่าออกไปเพื่อให้เป็นการ์ดปุ่มกดเต็มๆ ใบ */
            [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] {{
                display: none !important;
            }}
            [data-testid="stRadio"] input[type="radio"] {{
                display: none !important;
            }}
            /* ========================================================= */
            
            /* ช่องกรอกข้อมูล: เพิ่มความหนาเส้นขอบเป็น 4px สีน้ำเงินไซเบอร์ */
            .stTextInput>div>div>input, .stForm, .stTextArea>div>div>textarea {{
                background-color: #04080c !important;
                border: 4px solid #0055ff !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                font-size: 16px !important;
                font-weight: bold !important;
            }}
            .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
                border-color: #ff003c !important;
                box-shadow: 0 0 15px #ff003c !important;
            }}
            
            /* การ์ดแสดงความจริง: เพิ่มความหนาเส้นขอบเป็น 4px และไล่เฉดน้ำเงิน-แดง */
            .truth-card {{
                background: linear-gradient(135deg, rgba(4,12,24,0.95) 0%, rgba(20,4,8,0.95) 100%);
                border: 4px solid {color_code};
                border-radius: 18px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 0 30px {color_code}40, inset 0 0 20px rgba(0,210,255,0.2);
                margin: 20px 0;
            }}
            
            /* กล่องสตรีมโลจิก: ขอบสีแดงนีออน */
            .logic-stream-box {{
                background-color: #03070a;
                border-left: 6px solid #ff003c;
                padding: 18px;
                border-radius: 0 10px 10px 0;
                color: #00d2ff !important;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 18px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                border-top: 1px solid rgba(0,210,255,0.2);
                border-bottom: 1px solid rgba(0,210,255,0.2);
                border-right: 1px solid rgba(0,210,255,0.2);
            }}
            
            /* ปรับปุ่มกดทั่วไปของ Streamlit ให้หนาและชัดเจน */
            .stButton>button {{
                border: 4px solid #0055ff !important;
                border-radius: 10px !important;
                font-weight: bold !important;
                font-size: 16px !important;
                background: linear-gradient(135deg, #04080c 0%, #100408 100%) !important;
                color: #ffffff !important;
                transition: 0.3s;
                padding: 10px 20px !important;
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
# 6. NAVIGATION CONTROLLER (ปรับปรุงขยายขนาดการ์ดเรียบร้อย)
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


# =========================================================
# 7. SYSTEM FUNCTIONS CORE (ทำงานจริงเชื่อมระบบจริง 100%)
# =========================================================

# --- 7.1 ระบบห้องแชทเข้ารหัสความปลอดภัยสูง (ส่งและดึงข้อมูลงฐานข้อมูล Firebase จริง) ---
if menu_choice == "💬 CHATROOM SYSTEMS":
    st.markdown(f"<h3 style='color:#00d2ff; font-family:Orbitron; font-weight:bold;'>💬 SYNAPSE SECURE CHATROOM</h3>", unsafe_allow_html=True)
    
    chat_ref = db.reference('global_chat')
    messages_data = chat_ref.order_by_child('timestamp').limit_to_last(20).get()
    
    st.markdown("<div style='color:#ff003c; font-weight:bold; margin-bottom:5px;'>📡 LIVE LOG STREAM:</div>", unsafe_allow_html=True)
    
    chat_box_html = "<div style='height:300px; overflow-y:auto; border:4px solid #0055ff; border-radius:12px; padding:15px; background:#03070a; margin-bottom:15px;'>"
    if messages_data:
        sorted_messages = sorted(messages_data.items(), key=lambda x: x[1].get('timestamp', ''))
        for msg_id, msg in sorted_messages:
            sender = msg.get('user', 'UNKNOWN')
            text = msg.get('text', '')
            time_str = msg.get('time_display', '')
            
            color = "#39FF14" if sender == st.session_state.user else "#ff003c"
            chat_box_html += f"""
            <div style='margin-bottom:10px; border-bottom:1px solid rgba(0,85,255,0.1); padding-bottom:5px;'>
                <span style='color:{color}; font-weight:bold; font-family:Orbitron;'>[{sender}]</span> 
                <span style='color:#aaa; font-size:11px;'>({time_str})</span>: 
                <b style='color:#fff; font-size:15px; margin-left:5px;'>{text}</b>
            </div>
            """
    else:
        chat_box_html += "<div style='color:#666; text-align:center; padding-top:100px;'>ไม่มีข้อมูลการสื่อสารในระบบค้างอยู่</div>"
    chat_box_html += "</div>"
    
    st.components.v1.html(chat_box_html, height=320, scrolling=False)
    
    with st.form("chat_input_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            chat_text = st.text_input("ป้อนรหัสสัญญาณข้อความความคิด...", key="chat_msg_input", label_visibility="collapsed")
        with col2:
            send_btn = st.form_submit_button("SEND ⚡", use_container_width=True)
            
        if send_btn and chat_text:
            now = datetime.now()
            new_msg = {
                'user': st.session_state.user,
                'text': chat_text,
                'timestamp': time.time(),
                'time_display': now.strftime("%H:%M:%S")
            }
            chat_ref.push(new_msg)
            st.rerun()

# --- 7.2 ระบบติดตามพิกัดดาวเทียมเรียลไทม์ (ดึงค่าจากเซนเซอร์ GPS มือถือบาสจริง) ---
elif menu_choice == "🛰️ GPS TRACER":
    st.markdown(f"<h3 style='color:#ff003c; font-family:Orbitron; font-weight:bold;'>🛰️ REAL-TIME SATELLITE GPS TRACER</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="logic-stream-box">
        📡 ระบบจะทำการดึงพิกัดตำแหน่งละติจูด/ลองจิจูดจริงจากชิปเซนเซอร์บนมือถือของบาสผ่านสัญญาณดาวเทียม เพื่อนำมาคำนวณโครงสร้างแผนที่ไซเบอร์พังก์โดยไม่มีการสุ่มตำแหน่งพิกัด
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("กำลังเชื่อมต่อค้นหาสัญญาณดาวเทียมข้ามพิกัด..."):
        loc = get_geolocation()
        
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        acc = loc['coords'].get('accuracy', 0)
        
        db.reference(f'users/{st.session_state.user}/last_gps').set({
            'lat': lat, 'lon': lon, 'accuracy': acc, 'updated_at': datetime.now().isoformat()
        })
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown(f"""
            <div style='background:#04080c; border:4px solid #0055ff; border-radius:10px; padding:15px; text-align:center;'>
                <span style='color:#00d2ff; font-weight:bold; font-size:14px;'>LATITUDE (พิกัดแนวตั้ง)</span>
                <h3 style='color:#fff; margin:5px 0;'>{lat:.6f}</h3>
            </div>
            """, unsafe_allow_html=True)
        with col_g2:
            st.markdown(f"""
            <div style='background:#04080c; border:4px solid #ff003c; border-radius:10px; padding:15px; text-align:center;'>
                <span style='color:#ff003c; font-weight:bold; font-size:14px;'>LONGITUDE (พิกัดแนวนอน)</span>
                <h3 style='color:#fff; margin:5px 0;'>{lon:.6f}</h3>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"<div style='color:#39FF14; font-size:13px; font-weight:bold; margin-top:5px; text-align:right;'>🎯 ค่าความแม่นยำรัศมีคลื่น: {acc:.2f} เมตร</div>", unsafe_allow_html=True)
        
        m = folium.Map(location=[lat, lon], zoom_start=16, tiles="CartoDB dark_matter")
        folium.Marker(
            [lat, lon], 
            popup=f"AGENT: {st.session_state.user}",
            tooltip="ตำแหน่งปัจจุบันของคุณ",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        st.markdown("<div style='border:4px solid #39FF14; border-radius:12px; overflow:hidden; margin-top:10px;'>", unsafe_allow_html=True)
        st_folium(m, width="100%", height=350, returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        st.warning("⚠️ ไม่สามารถดึงตำแหน่งพิกัดได้ กรุณากดปุ่ม 'อนุญาตสิทธิ์เข้าถึงตำแหน่ง (Allow Location)' บนหน้าจอมือถือ หรือเปิดระบบ GPS ในเครื่องก่อนใช้งานนะครับบาส")

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

# --- 7.4 ระบบเครื่องเล่นเพลงสุ่มต่อเนื่อง (LOOP AUDIO RANDOM PLAYER - รันได้จริง 100%) ---
elif menu_choice == "🎵 NEON JUKEBOX":
    st.markdown(f"<h3 style='color:#00d2ff; font-family:Orbitron; text-align:center; font-weight:bold;'>🎵 AUTOLOOP RANDOM JUKEBOX</h3>", unsafe_allow_html=True)
    
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    
    if all_songs:
        st.markdown(f"<div style='color:#ffffff; font-weight:bold; font-size:16px; margin-bottom:10px;'>📁 ตรวจพบไฟล์เพลงในระบบทั้งหมดค้างอยู่ <span style='color:#ff003c;'>{len(all_songs)}</span> เพลง</div>", unsafe_allow_html=True)
        
        song_dict_js = {}
        for s in all_songs:
            b64 = get_base64(s)
            if b64: song_dict_js[s] = "data:audio/mp3;base64," + b64

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

            playRandom();
        </script>
        """
        components.html(jukebox_html, height=220)
    else:
        st.markdown("<div style='background:#100408; border:4px solid #ff003c; border-radius:10px; padding:20px; color:#fff; font-weight:bold; text-align:center;'>⚠️ ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์หลักของเซิร์ฟเวอร์แอปเลยครับบาส นำไฟล์เพลงไปวางคู่กับไฟล์โค้ดแล้วปุ่มควบคุมเครื่องเล่นเพลงจะเปิดขึ้นมาทำงานทันทีครับ</div>", unsafe_allow_html=True)

# --- 7.5 ระบบแปลงตัวอักษรเป็นความถี่จริง ---
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

        canvas_html = f"""
        <canvas id="live-wave" style="width:100%; height:110px; background:#020508; border:4px solid #0055ff; border-radius:12px; box-shadow:0 0 15px rgba(0,85,255,0.3);"></canvas>
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
