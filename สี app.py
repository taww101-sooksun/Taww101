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
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;500&display=swap');
            
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, #080f14 0%, #030508 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }
            
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .stApp {{ top: -60px; }}
            
            .stTabs [data-baseweb="tab-list"] {{ gap: 12px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: #0b1116; border: 1px solid #1a2936;
                border-radius: 8px; padding: 12px 24px; color: #666;
                font-family: 'Orbitron', sans-serif; transition: 0.3s;
            }}
            .stTabs [aria-selected="true"] {{
                background-color: {color_code}15 !important;
                border-color: {color_code} !important; color: {color_code} !important;
                box-shadow: 0 0 15px {color_code}33;
            }}
            
            .stTextInput>div>div>input, .stForm, .stTextArea>div>div>textarea {{
                background-color: #090e12 !important;
                border: 1px solid #1a2936 !important;
                color: #fff !important;
                border-radius: 8px !important;
            }}
            .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
                border-color: {color_code} !important;
                box-shadow: 0 0 10px {color_code}80 !important;
            }}
            
            .truth-card {{
                background: linear-gradient(135deg, rgba(11,20,28,0.9) 0%, rgba(4,8,12,0.95) 100%);
                border: 2px solid {color_code};
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 0 25px {color_code}26, inset 0 0 15px {color_code}1a;
                margin: 15px 0;
            }}
            
            .logic-stream-box {{
                background-color: #060a0d;
                border-left: 4px solid #ff00de;
                padding: 15px;
                border-radius: 0 8px 8px 0;
                color: #a3b8cc;
                font-size: 13px;
                margin-bottom: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }}
            
            .stDataFrame {{
                border: 1px solid #1a2936 !important;
                border-radius: 10px !important;
                background-color: #05080b !important;
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
audio_data = get_base64("notification.mp3")

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
if 'user_lat' not in st.session_state: st.session_state.user_lat = None
if 'user_lon' not in st.session_state: st.session_state.user_lon = None

# =========================================================
# 4. HEADER LOGO & SLOGAN WINKING
# =========================================================
header_html = f"""
<style>
    @keyframes dance {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(1px, -1px) rotate(1deg); }}
        50% {{ transform: translate(-1px, 1px) rotate(-1deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 12px {theme_color}; }}
        50% {{ opacity: 0.3; color: #fff; text-shadow: none; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 15px 0; border-bottom: 1px solid #121e29; margin-bottom: 15px; }}
    .logo-img {{ width: 70px; height: 70px; animation: dance 1s infinite ease-in-out; object-fit: contain; }}
    .slogan-txt {{ 
        font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 20px; letter-spacing: 2px;
        margin-left: 15px; animation: wink 2s infinite; 
    }}
</style>
<div class="logo-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else ''}
    <span class="slogan-txt">SYNAPSE COMMAND CENTER</span>
</div>
"""
components.html(header_html, height=110)

# =========================================================
# 5. AUTHENTICATION SYSTEM (LOGIN / REGISTER)
# =========================================================
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color}; font-family:Orbitron;'>🔒 SYSTEM AUTHENTICATION</h3>", unsafe_allow_html=True)
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
                    st.success("ลงทะเบียนสำเร็จ! กรุณาสลับไปหน้าเข้าสู่ระบบเพื่อใช้งาน")
    st.stop()

st.markdown(f"<div style='text-align:right; color:{theme_color}; font-family:Orbitron; font-size:12px; padding-right:10px;'>📡 AGENT OUTPOST: {st.session_state.user}</div>", unsafe_allow_html=True)

# =========================================================
# 6. NAVIGATION CONTROLLER (เพิ่มฟังก์ชันพิเศษ)
# =========================================================
st.markdown("<h5 style='color:#6886a3; font-family:Orbitron; margin-bottom:5px;'>🎛️ NAVIGATION CONTROLLER</h5>", unsafe_allow_html=True)
menu_choice = st.radio(
    "เลือกฟังก์ชันระบบ:", 
    ["💬 GLOBAL CHATROOM", "🛰️ GPS TRACER", "🔮 THE TRUTH SCANNER", "🎵 NEON MIXER & LYRICS", "🧠 QUANTUM BRAIN SCAN"],
    horizontal=True,
    key="main_menu_navigator",
    label_visibility="collapsed"
)

st.divider()

if st.sidebar.button("🔴 ออกจากระบบ (LOGOUT)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# =========================================================
# 7. MODULE LOGIC APPLICATIONS
# =========================================================

# --- 7.1 ระบบแชทเรียลไทม์ ---
if menu_choice == "💬 GLOBAL CHATROOM":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>💬 GLOBAL CHATROOM</h3>", unsafe_allow_html=True)
    
    chat_display_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    #chat-screen {{
        background: rgba(4,8,12,0.95); border: 2px solid {theme_color}; border-radius: 12px;
        height: 380px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
        box-shadow: inset 0 0 15px {theme_color}22;
    }}
    .bubble {{ padding: 10px 15px; border-radius: 10px; margin: 6px 0; max-width: 85%; color: #fff; font-family: sans-serif; font-size: 14px; line-height: 1.4; }}
    .me {{ background: {theme_color}15; border-right: 4px solid {theme_color}; align-self: flex-end; }}
    .others {{ background: #111b24; border-left: 4px solid #ff00de; align-self: flex-start; }}
    .notif-box {{ background: #162533; color: #888; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-family: 'Orbitron'; }}
    .alert-red {{ background: #ff0055 !important; color: white; box-shadow: 0 0 10px #ff0055; font-weight: bold; }}
</style>

<div id="chat-screen">
    <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #1a2936; padding-bottom: 5px;">
        <span style="color:{theme_color}; font-family:'Orbitron'; font-size:10px; letter-spacing: 2px;">📡 LINK_ESTABLISHED</span>
        <span id="notif-box" class="notif-box">0 SIGNAL</span>
    </div>
    <div id="msg-area" style="display:flex; flex-direction:column;"></div>
</div>

<audio id="notif-sound" preload="auto">
    <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
</audio>

<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
<script>
    const fb_conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
    if(!firebase.apps.length) firebase.initializeApp(fb_conf);
    const database = firebase.database();
    let lastCount = -1;
    const beep = document.getElementById('notif-sound');

    function unlock() {{
        beep.play().then(() => {{ beep.pause(); beep.currentTime = 0; }});
        window.removeEventListener('click', unlock);
        window.removeEventListener('touchstart', unlock);
    }}
    window.addEventListener('click', unlock);
    window.addEventListener('touchstart', unlock);

    database.ref('global_chat').limitToLast(25).on('child_added', (snap) => {{
        const msg = snap.val();
        const area = document.getElementById('msg-area');
        const div = document.createElement('div');
        const isMe = msg.user === "{st.session_state.user}";
        div.className = "bubble " + (isMe ? "me" : "others");
        div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
        
        let html = `<div style="font-size:10px; color:#527394; font-family:'Orbitron'; margin-bottom:4px;">${{msg.user}}</div>`;
        if(msg.text) html += `<div>${{msg.text}}</div>`;
        if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:6px; margin-top:6px; border: 1px solid #1a2936;">`;
        
        div.innerHTML = html;
        area.appendChild(div);
        document.getElementById('chat-screen').scrollTop = 999999;
    }});

    database.ref('chat_notifications/unread_count').on('value', (snap) => {{
        const val = snap.val() || 0;
        const box = document.getElementById('notif-box');
        box.innerText = val + " NEW SIGNAL";
        if(val > 0) {{
            box.classList.add('alert-red');
            if(lastCount !== -1 && val > lastCount) {{
                beep.currentTime = 0;
                beep.play().catch(() => {{}});
            }}
        }} else {{
            box.classList.remove('alert-red');
        }}
        lastCount = val;
    }});
</script>
"""
    components.html(chat_display_html, height=410)

    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            m_txt = st.text_input("MESSAGE", placeholder="ส่งข้อความคลื่นวิทยุ...", label_visibility="collapsed", key="msg_input")
        with c2:
            m_img = st.file_uploader("IMAGE", type=['png','jpg','jpeg'], label_visibility="collapsed", key="img_upload")
        with c3:
            if st.button("ส่งสัญญาณ ⚡", use_container_width=True):
                if m_txt or m_img:
                    p_load = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                    if m_txt: p_load['text'] = m_txt
                    if m_img: p_load['img'] = base64.b64encode(m_img.read()).decode()
                    db.reference('global_chat').push(p_load)
                    
                    cur = db.reference('chat_notifications/unread_count').get() or 0
                    db.reference('chat_notifications').set({'unread_count': cur + 1})
                    st.rerun()

    st.divider()
    if st.button("🧼 RESET NOTIFICATION COUNT", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()

# --- 7.2 ระบบแผนที่ดาวเทียม GPS ---
elif menu_choice == "🛰️ GPS TRACER":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🛰️ GLOBAL GPS TARGET TRACER</h3>", unsafe_allow_html=True)
    
    loc = get_geolocation() 

    if loc and 'coords' in loc:
        st.session_state.user_lat = loc['coords']['latitude']
        st.session_state.user_lon = loc['coords']['longitude']
        accuracy = loc['coords'].get('accuracy', 0)
        st.success(f"🎯 ดาวเทียมล็อกเป้าพิกัดสำเร็จ! (ขอบเขตคลาดเคลื่อนต่ำสุด: {accuracy:.0f} เมตร)")
        
        my_lat = st.session_state.user_lat
        my_lon = st.session_state.user_lon

        m = folium.Map(
            location=[my_lat, my_lon], 
            zoom_start=18, 
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
            attr='Google Maps'
        )

        folium.Marker(
            [my_lat, my_lon], 
            icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
        ).add_to(m)

        st_folium(m, width="100%", height=450)

        if st.button("🛰️ ทำการซิงค์ข้อมูลส่งขึ้นระบบคลาวด์ Firebase", use_container_width=True):
            try:
                db.reference(f'users/{st.session_state.user}').update({
                    'lat': my_lat, 'lon': my_lon, 'ts': time.time()
                })
                st.toast("อัปเดตข้อมูลตำแหน่งเข้าเซิร์ฟเวอร์กลางแล้ว")
            except: 
                st.error("ไม่สามารถเชื่อมต่อฐานข้อมูลปลายทางได้")
    else:
        st.info("🛰️ กำลังตรวจสอบสัญญาณจีพีเอสจากเครื่องโทรศัพท์... โปรดกดยอมรับสิทธิ์การเข้าถึงตำแหน่งอุปกรณ์ด้วยครับ")

# --- 7.3 ระบบคำนวณถอดรหัสความจริง ---
elif menu_choice == "🔮 THE TRUTH SCANNER":
    st.markdown(f"<h2 style='color:{theme_color}; text-shadow: 0 0 15px {theme_color}66; text-align:center; font-family:Orbitron;'>🧬 THE QUANTUM TRUTH SCANNERS</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        if dt is None: return None
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        thai_year = dt.year + 543
        zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
        zodiac = zodiacs[thai_year % 12]
        
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val)

        is_waxing = pos <= 14.765
        m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
        phase = f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ"

        if is_waxing:
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดันเวกเตอร์ (Vector)"
        else:
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"
            
        if res < 2.5: freq_level = "🟢 ALPHA CONSTANT (สงบนิ่งเสถียร)"
        elif 2.5 <= res < 5.0: freq_level = "🔵 BETA WAVE (พลังงานปฏิสัมพันธ์สูง)"
        elif 5.0 <= res < 9.0: freq_level = "🟡 GAMMA RADIATION (แรงผลักดันเฉียบพลัน)"
        else: freq_level = "🔥 COSMIC DELTA (คลื่นขยายตัวไร้ขอบเขต)"

        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff, "level": freq_level}

    def run_time_scanner(target_res, base_date, total_days, mode="future"):
        scan_list = []
        for i in range(total_days + 1):
            current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
            d = decode_truth(current_date)
            gap = abs(target_res - d['res'])
            
            status = "เสถียร"
            if gap < 0.4: status = "💎 รหัสบรรจบ (ตรงจุดร่วม)"
            elif 3.8 <= gap <= 4.2: status = "🌀 สัญญาณสะท้อน (ขั้วดึงดูด)"
            elif gap > 11.0: status = "🚩 รหัสแยกตัว (พลังงานอิสระ)"
            
            if status != "เสถียร":
                scan_list.append({
                    "วันที่สแกน": current_date.strftime("%d/%m/%Y"),
                    "ฐานวันพิกัด": d['phase'],
                    "สถานะโครงสร้าง": status,
                    "ระยะห่าง (Gap)": round(gap, 4),
                    "ดัชนีวันนั้น": d['res']
                })
        return pd.DataFrame(scan_list)

    st.subheader("📊 ตรวจสอบรหัสความถี่และสแกนพิกัดเวลาแบบวงจร")
    user_dob = st.date_input("กรอกวันเดือนปีเกิดของตัวคุณเพื่อจับสัญญาณพิกัดถอดรหัส", value=None, min_value=date(1940,1,1))
    
    if user_dob:
        u_data = decode_truth(user_dob)
        
        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#6886a3; font-family:'Orbitron'; font-size:12px; letter-spacing:3px;">QUANTUM DECODED INDEX</span>
                <h1 style="color:{theme_color}; font-family:'Orbitron'; font-size:62px; margin:5px 0; font-weight:700; text-shadow:0 0 20px {theme_color}99;">{u_data['res']}</h1>
                <div style="color:#ff00de; font-size:14px; font-family:'Orbitron'; font-weight:bold; letter-spacing:1px; margin-bottom:10px;">{u_data['level']}</div>
                <p style="color:#88aaee; margin:0; font-size:13px;">โครงสร้างสมการ: {u_data['type']}</p>
            </div>
        """, unsafe_allow_html=True)

        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            st.markdown(f"""<div class="logic-stream-box"><b>📅 ฐานค่าวันเกิด:</b> วันสัปดาห์ลำดับที่ {u_data['day_num']}<br><b>🌙 พิกัดวงรอบดวงจันทร์:</b> สภาพดวงจันทร์แบบ {u_data['phase']}</div>""", unsafe_allow_html=True)
        with col_inf2:
            st.markdown(f"""<div class="logic-stream-box" style="border-left-color:{theme_color};"><b>🐎 ปีนักษัตรดั้งเดิม:</b> ปี{u_data['zodiac']}<br><b>💎 ธาตุฟลักซ์ประจำวัน:</b> แรงธาตุ{u_data['element']}</div>""", unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background:#090f14; padding:12px; border:1px solid #1a2936; border-radius:8px; margin: 10px 0 25px 0;">
                <span style="font-size:12px; color:#527394; font-family:'Orbitron';">MATHEMATICAL ROOT PROOF:</span><br>
                <code style="color:{theme_color}; font-size:13px;">{u_data['formula']}</code> (วิเคราะห์จากช่วงเวลารวบรวมรวมทั้งสิ้น {u_data['diff']:,} วัน จากจุดตั้งต้น)
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color:#fff; font-family:Orbitron;'>🛰️ AUTOMATIC TIME MATRIX SCANNER</h4>", unsafe_allow_html=True)
        st.write("ระบบจะทำค้นหาพิกัดวันเวลาที่คลื่นความถี่จักรวาลโคจรมาตรงกับค่าของคุณ เพื่อระบุสถานะชีวิตล่วงหน้าและย้อนหลัง")
        
        c_sc1, c_sc2 = st.columns(2)
        with c_sc1: past_days = st.slider("ขอบข่ายการสแกนถอยหลังไปในอดีต (วัน)", 10, 365, 180)
        with c_sc2: future_days = st.slider("ขอบข่ายการสแกนก้าวไปข้างหน้า (วัน)", 10, 365, 180)

        t_past, t_future = st.tabs([f"⏪ พิกัดอดีตย้อนรอย ({past_days} วัน)", f"🔮 พิกัดอนาคตพยากรณ์ ({future_days} วัน)"])
        
        with t_past:
            df_past_results = run_time_scanner(u_data['res'], date.today(), past_days, "past")
            if not df_past_results.empty:
                st.write(f"📡 พบพิกัดโครงสร้างพลังงานสะท้อนกลับในอดีตจำนวน **{len(df_past_results)}** วัน:")
                st.dataframe(df_past_results, use_container_width=True, hide_index=True)
            else:
                st.info("ไม่พบคลื่นแทรกแซงหรือจุดบรรจบพิเศษในขอบเขตวันที่เลือก")

        with t_future:
            df_future_results = run_time_scanner(u_data['res'], date.today(), future_days, "future")
            if not df_future_results.empty:
                st.write(f"📡 ตรวจพบจุดเลื่อนไหลรหัสที่สอดคล้องสัมพันธ์ล่วงหน้า **{len(df_future_results)}** วันสำคัญ:")
                st.dataframe(df_future_results, use_container_width=True, hide_index=True)
            else:
                st.info("โครงสร้างอนาคตไหลลื่นเป็นปกติ ไม่มีจุดแรงดันหนาแน่นในช่วงเวลานี้")
    else:
        st.info("💡 กรุณาระบุข้อมูลวันที่ต้องการตรวจสอบรหัสพิกัดควอนตัมด้านบนเพื่อสตาร์ทระบบ")

# --- 7.4 ระบบมิกเซอร์ครอสเฟดเพลง + ออฟชั่นเศษ SPECIAL LYRICS PAD ---
elif menu_choice == "🎵 NEON MIXER & LYRICS":
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    all_songs = sorted(all_songs)
    mixer_logo_b64 = get_base64("logo1.png")

    st.markdown(f"""
        <style>
        .neon-mixer-text {{
            font-family: 'Orbitron', sans-serif; color: #fff; text-align: center; font-size: 1.8rem; letter-spacing: 5px;
            text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 40px {theme_color}; margin-bottom: 20px;
        }}
        </style>
        <div class="neon-mixer-text">SYNAPSE MIXER ENGINE</div>
        """, unsafe_allow_html=True)

    if all_songs:
        col_mix1, col_mix2 = st.columns(2)
        with col_mix1: sA = st.selectbox("DECK A (เริ่มก่อน)", all_songs, key="mixer_sA")
        with col_mix2: sB = st.selectbox("DECK B (เล่นต่อ)", all_songs, key="mixer_sB")
        
        audio_a = get_audio_base64_local(sA) if 'get_audio_base64_local' in globals() else get_base64(sA)
        audio_b = get_audio_base64_local(sB) if 'get_audio_base64_local' in globals() else get_base64(sB)

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body {{ background: transparent; color: white; font-family: sans-serif; overflow: hidden; }}
                .neon-card {{ border: 2px solid #1a2936; background: rgba(5,9,14,0.95); box-shadow: 0 0 25px {theme_color}26; }}
                .logo-box {{ width: 60px; height: 60px; margin: 0 auto 15px auto; background: url('data:image/png;base64,{mixer_logo_b64}') no-repeat center; background-size: contain; filter: drop-shadow(0 0 8px {theme_color}); }}
                .visualizer {{ height: 80px; background: #020508; border-radius: 10px; border: 1px solid #101a24; }}
                .deck {{ padding: 10px; border-radius: 10px; border: 1px solid #101a24; margin-top: 10px; transition: 0.3s; opacity: 0.4; }}
                .active-a {{ border-color: #ff00de; box-shadow: 0 0 10px rgba(255,0,222,0.4); opacity: 1; }}
                .active-b {{ border-color: {theme_color}; box-shadow: 0 0 10px {theme_color}66; opacity: 1; }}
                .btn-mix {{ background: linear-gradient(45deg, #ff00de, {theme_color}); width: 100%; padding: 12px; border-radius: 10px; font-weight: bold; margin-top: 15px; cursor: pointer; letter-spacing: 1px; }}
                .progress {{ height: 4px; background: #111; margin-top: 5px; }}
                .bar {{ height: 100%; width: 0%; background: #ff00de; }}
            </style>
        </head>
        <body>
            <div class="max-w-md mx-auto p-4 neon-card rounded-3xl text-center">
                <div class="logo-box"></div>
                <canvas id="scope" class="visualizer w-full"></canvas>

                <div id="deckA" class="deck text-left">
                    <div class="flex justify-between text-[10px]"><span style="color:#ff00de">DECK A</span><span id="tA">00:00</span></div>
                    <div class="text-[11px] truncate">{sA}</div>
                    <div class="progress"><div id="barA" class="bar"></div></div>
                </div>

                <div id="deckB" class="deck text-left">
                    <div class="flex justify-between text-[10px]"><span style="color:{theme_color}">DECK B</span><span id="tB">00:00</span></div>
                    <div class="text-[11px] truncate">{sB}</div>
                    <div class="progress"><div id="barB" class="bar" style="background:{theme_color}"></div></div>
                </div>

                <button onclick="start()" class="btn-mix">🚀 START CORE ENGINE</button>
                <div id="status" class="text-[9px] mt-3 text-gray-500">DECK OPERATIONAL</div>
            </div>

            <script>
                let ctx, analyser, songA, songB, gA, gB, srcA, srcB;
                let isPlaying = false, active = 'A', data;
                let crossfadeTriggered = false;

                async function toBuf(b64) {{
                    const r = await fetch('data:audio/mp3;base64,' + b64);
                    const ab = await r.arrayBuffer();
                    return await ctx.decodeAudioData(ab);
                }}

                async function start() {{
                    if(isPlaying) return;
                    try {{
                        document.getElementById('status').innerText = "BOOTING SIGNAL...";
                        ctx = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = ctx.createAnalyser();
                        data = new Uint8Array(analyser.frequencyBinCount);

                        songA = await toBuf('{audio_a}');
                        songB = await toBuf('{audio_b}');

                        crossfadeTriggered = false;
                        playDeckA();
                        isPlaying = true;
                        render();
                    }} catch(e) {{ alert("Error: " + e); }}
                }}

                function playDeckA() {{
                    active = 'A';
                    srcA = ctx.createBufferSource(); srcA.buffer = songA; gA = ctx.createGain();
                    srcA.connect(gA).connect(analyser).connect(ctx.destination);
                    srcA.start(0); srcA.t0 = ctx.currentTime;
                    document.getElementById('deckA').classList.add('active-a');
                    document.getElementById('status').innerText = "PLAYING DECK A";
                }}

                function playDeckB() {{
                    active = 'B';
                    srcB = ctx.createBufferSource(); srcB.buffer = songB; gB = ctx.createGain();
                    srcB.connect(gB).connect(analyser).connect(ctx.destination);
                    gB.gain.value = 0; srcB.start(0); srcB.t0 = ctx.currentTime;
                    gB.gain.linearRampToValueAtTime(1, ctx.currentTime + 5);
                    document.getElementById('deckB').classList.add('active-b');
                    document.getElementById('deckA').classList.remove('active-a');
                }}

                function render() {{
                    requestAnimationFrame(render);
                    analyser.getByteFrequencyData(data);
                    const can = document.getElementById('scope'); const c = can.getContext('2d');
                    c.clearRect(0,0,can.width,can.height);
                    for(let i=0; i<data.length; i++) {{
                        c.fillStyle = 'hsl(' + (i*2 + (active=='A'?300:190)) + ', 100%, 50%)';
                        c.fillRect(i*3, can.height-(data[i]/2.5), 2, data[i]/2.5);
                    }}
                    updateProgress();
                }}

                function updateProgress() {{
                    if (active == 'A' && srcA) {{
                        let elapsed = ctx.currentTime - srcA.t0; let rem = songA.duration - elapsed;
                        if(rem < 0) rem = 0;
                        
                        document.getElementById('tA').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                        document.getElementById('barA').style.width = (elapsed/songA.duration*100) + "%";
                        
                        if (rem < 8 && !crossfadeTriggered) {{
                            crossfadeTriggered = true;
                            gA.gain.linearRampToValueAtTime(0, ctx.currentTime + 5);
                            playDeckB(); 
                            document.getElementById('status').innerText = "CROSSFADING...";
                        }}
                    }} else if (active == 'B' && srcB) {{
                        let elapsed = ctx.currentTime - srcB.t0; let rem = songB.duration - elapsed;
                        if(rem < 0) rem = 0;
                        
                        document.getElementById('tB').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                        document.getElementById('barB').style.width = (elapsed/songB.duration*100) + "%";
                        document.getElementById('status').innerText = "PLAYING DECK B";
                    }}
                }}
            </script>
        </body>
        </html>
        """
        components.html(html_code, height=480)
        
        # 💎 ออฟชั่นเสริมพิเศษ 1: สมุดจดเนื้อเพลงด่วน + จับจังหวะ Tap BPM (สำหรับสายทำเพลง R&B/HipHop บนมือถือ)
        st.markdown(f"<h4 style='color:{theme_color}; font-family:Orbitron; margin-top:20px;'>🎵 REAL-TIME MUSICIAN LYRICS PAD</h4>", unsafe_allow_html=True)
        st.write("เครื่องมือช่วยบาสเขียนเนื้อเพลงและคำนวณความเร็วบีทดนตรีแบบเคาะนิ้วสด")
        
        bpm_tap_html = f"""
        <div style="background:#090e12; border:1px solid #1a2936; padding:15px; border-radius:12px; text-align:center;">
            <span style="font-size:11px; color:#527394; font-family:'Orbitron';">BPM AUDIO COUNTER</span>
            <h2 id="bpm-display" style="color:#ff00de; font-family:'Orbitron'; font-size:32px; margin:5px 0;">0.0 BPM</h2>
            <button onclick="tapBPM()" style="background:{theme_color}; color:#000; font-weight:bold; padding:8px 20px; border-radius:6px; font-size:12px;">TAP HERE TO COMPOSING</button>
        </div>
        <script>
            let taps = [];
            function tapBPM() {{
                const now = Date.now();
                taps.push(now);
                if(taps.length > 4) taps.shift();
                if(taps.length > 1) {{
                    let diffs = [];
                    for(let i=1; i<taps.length; i++) {{ diffs.push(taps[i] - taps[i-1]); }}
                    let avg = diffs.reduce((a,b) => a+b) / diffs.length;
                    let bpm = Math.round(60000 / avg);
                    document.getElementById('bpm-display').innerText = bpm + " BPM";
                }}
            }}
        </script>
        """
        components.html(bpm_tap_html, height=130)
        st.text_area("✍️ เขียน/วางท่อนแร็ป ท่อนร้องของคุณตรงนี้ได้เลยเพื่อน:", placeholder="คิดไอเดียเพลงออกปุ๊บ พิมพ์ล็อกลงตรงนี้ทันที...", height=150)
        
    else:
        st.error("ไม่พบไฟล์เพลงนามสกุล .mp3 ในโฟลเดอร์หลัก")

# --- 7.5 ออฟชั่นเสริมพิเศษ 2: ระบบจำลองคลื่นวิเคราะห์ความคิดและระดับจิตใต้สำนึก ---
elif menu_choice == "🧠 QUANTUM BRAIN SCAN":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🔮 QUANTUM CONSCIOUSNESS SCANNER</h3>", unsafe_allow_html=True)
    st.write("ระบบถอดสมการแปลงค่าข้อความหรือปรัชญาความคิดให้กลายเป็นระดับคลื่นความถี่พลังงานจิตสำนึก ($Hz$)")
    
    thought_input = st.text_input("ป้อนวลี ความคิด หรือสโลแกนที่คุณต้องการสแกนความถี่:", "อยู่นิ่งๆ ไม่เจ็บตัว")
    
    if thought_input:
        # ใช้หลักการทางคณิตศาสตร์แปลงรหัสอักขระเป็นระดับตัวเลขจำลองความถี่จริง ไม่มีการล็อคผลลัพธ์ล่วงหน้า
        char_sum = sum(ord(c) for c in thought_input)
        calculated_hz = (char_sum % 800) + 150.5
        
        if calculated_hz < 250: state_desc = "🟢 THETA WAVE - สภาวะจิตสงบนิ่ง เข้าใจสัจธรรม ลึกซึ้งสูงสุด"
        elif 250 <= calculated_hz < 500: state_desc = "🔵 ALPHA WAVE - สภาวะสมองแล่น ไอเดียสร้างสรรค์ ค้นหาความจริง"
        else: state_desc = "🔥 HIGH GAMMA - สภาวะจดจ่อขั้นเด็ดขาด พลังงานแรงขับเคลื่อนสูง"
        
        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#6886a3; font-family:'Orbitron'; font-size:11px; letter-spacing:2px;">CONSCIOUSNESS FREQUENCY LEVEL</span>
                <h1 style="color:#ff00de; font-family:'Orbitron'; font-size:54px; margin:5px 0;">{calculated_hz:.2f} Hz</h1>
                <div style="color:{theme_color}; font-size:13px; font-weight:bold;">{state_desc}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # แสดงอนิเมชั่นกราฟประมวลผลคลื่นสมองจำลองแบบเรียลไทม์
        canvas_html = f"""
        <canvas id="brain-wave" style="width:100%; height:100px; background:#04070a; border:1px solid #1a2936; border-radius:8px;"></canvas>
        <script>
            const cv = document.getElementById('brain-wave');
            const cx = cv.getContext('2d');
            let offset = 0;
            function draw() {{
                cx.clearRect(0,0,cv.width,cv.height);
                cx.strokeStyle = "{theme_color}";
                cx.lineWidth = 2;
                cx.beginPath();
                for(let x=0; x<cv.width; x++) {{
                    let y = cv.height/2 + Math.sin(x*0.05 + offset) * 20 * Math.sin(x*0.01);
                    if(x==0) cx.moveTo(x,y); else cx.lineTo(x,y);
                }}
                cx.stroke();
                offset += {calculated_hz / 1000};
                requestAnimationFrame(draw);
            }}
            draw();
        </script>
        """
        components.html(canvas_html, height=120)

# =========================================================
# 8. GLOBAL SYSTEM FOOTER
# =========================================================
st.markdown("<div style='text-align:center; color:#3b566e; font-size:11px; margin-top:30px; font-family:Orbitron;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.3.5</div>", unsafe_allow_html=True)
