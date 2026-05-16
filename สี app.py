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
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;500&display=swap');
            
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, #080f14 0%, #030508 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }}
            
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
# 4. HEADER LOGO & SLOGAN WINKING (โลโก้เต้นเรืองแสงตามธีมสีสีสรรค์)
# =========================================================
header_html = f"""
<style>
    @keyframes dance {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(2px, -2px) rotate(2deg); }}
        50% {{ transform: translate(-2px, 2px) rotate(-2deg); }}
        75% {{ transform: translate(1px, 1px) rotate(1deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 15px {theme_color}, 0 0 30px {theme_color}; }}
        50% {{ opacity: 0.4; color: #fff; text-shadow: 0 0 5px #fff; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 15px 0; border-bottom: 1px solid #121e29; margin-bottom: 15px; }}
    .logo-img {{ width: 75px; height: 75px; animation: dance 0.8s infinite ease-in-out; filter: drop-shadow(0 0 12px {theme_color}); object-fit: contain; }}
    .slogan-txt {{ 
        font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 22px; letter-spacing: 3px;
        margin-left: 15px; animation: wink 1.5s infinite; 
    }}
</style>
<div class="logo-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else ''}
    <span class="slogan-txt">SYNAPSE COMMAND CENTER</span>
</div>
"""
components.html(header_html, height=110)

# =========================================================
# 5. AUTHENTICATION SYSTEM
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
                    st.success("ลงทะเบียนสำเร็จ!")
    st.stop()

st.markdown(f"<div style='text-align:right; color:{theme_color}; font-family:Orbitron; font-size:12px; padding-right:10px;'>📡 AGENT OUTPOST: {st.session_state.user}</div>", unsafe_allow_html=True)

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

# =========================================================
# 7. MODULE LOGIC APPLICATIONS
# =========================================================

# --- 7.1 ระบบแชทรวม และ แชทส่วนตัวแยกคน (PRIVATE CHATROOM) ---
if menu_choice == "💬 CHATROOM SYSTEMS":
    chat_type = st.tabs(["🌍 GLOBAL CHAT (แชทรวม)", "🔒 PRIVATE CHAT (แชทส่วนตัว)"])
    
    with chat_type[0]:
        st.markdown(f"<h4 style='color:{theme_color}; font-family:Orbitron;'>🌍 GLOBAL CHATROOM</h4>", unsafe_allow_html=True)
        # โค้ด JavaScript จัดการเสียงและดึงข้อมูล Firebase อัตโนมัติเหมือนเวอร์ชันเดิม
        chat_display_html = f"""
        <style>
            #chat-screen-global {{ background: #04080c; border: 2px solid {theme_color}; border-radius: 12px; height: 300px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; }}
            .bubble {{ padding: 10px; border-radius: 8px; margin: 5px 0; color: #fff; font-size: 13px; max-width: 80%; }}
            .me {{ background: {theme_color}20; border-right: 4px solid {theme_color}; align-self: flex-end; }}
            .others {{ background: #111; border-left: 4px solid #ff00de; align-self: flex-start; }}
        </style>
        <div id="chat-screen-global"><div id="msg-area-global"></div></div>
        <audio id="notif-sound-g" preload="auto"><source src="data:audio/mp3;base64,{audio_notif_data}" type="audio/mp3"></audio>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            const confG = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
            if(!firebase.apps.length) firebase.initializeApp(confG);
            const dbG = firebase.database();
            const beepG = document.getElementById('notif-sound-g');
            let initialLoad = true;

            dbG.ref('global_chat').limitToLast(15).on('child_added', (snap) => {{
                const msg = snap.val();
                const div = document.createElement('div');
                const isMe = msg.user === "{st.session_state.user}";
                div.className = "bubble " + (isMe ? "me" : "others");
                div.innerHTML = `<b style="font-size:10px; color:#aaa;">${{msg.user}}</b><div>${{msg.text || ''}}</div>`;
                document.getElementById('msg-area-global').appendChild(div);
                document.getElementById('chat-screen-global').scrollTop = 99999;
                if(!initialLoad && !isMe) {{ beepG.currentTime = 0; beepG.play().catch(() => {{}}); }}
            }});
            setTimeout(() => {{ initialLoad = false; }}, 2000);
        </script>
        """
        components.html(chat_display_html, height=320)
        
        with st.form("global_send_form", clear_on_submit=True):
            g_msg = st.text_input("พิมพ์ข้อความกลาง:")
            if st.form_submit_button("ส่งสัญญาณแชทรวม ⚡"):
                if g_msg:
                    db.reference('global_chat').push({'user': st.session_state.user, 'text': g_msg, 'ts': time.time()})
                    st.rerun()

    with chat_type[1]:
        st.markdown(f"<h4 style='color:{theme_color}; font-family:Orbitron;'>🔒 PRIVATE AGENT CHATROOM</h4>", unsafe_allow_html=True)
        # ดึงรายชื่อผู้ใช้ทั้งหมดในระบบมาให้เลือกคุยตัวต่อตัว
        all_users = db.reference('users').get()
        if all_users:
            user_list = [u for u in all_users.keys() if u != st.session_state.user]
            target_user = st.selectbox("เลือกสายลับ AGENT ที่คุณต้องการติดต่อ:", user_list)
            
            if target_user:
                # เรียงชื่อคู่สนทนาตามตัวอักษรเพื่อสร้าง Path ห้องคุยที่เป็นคีย์เดียวกันเสมอ
                room_id = "_".join(sorted([st.session_state.user, target_user]))
                
                priv_chat_html = f"""
                <style>
                    #chat-screen-priv {{ background: #050a0f; border: 2px solid #ff00de; border-radius: 12px; height: 300px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; }}
                </style>
                <div id="chat-screen-priv"><div id="msg-area-priv"></div></div>
                <audio id="notif-sound-p" preload="auto"><source src="data:audio/mp3;base64,{audio_notif_data}" type="audio/mp3"></audio>
                <script>
                    if(!firebase.apps.length) firebase.initializeApp(confG);
                    const dbP = firebase.database();
                    const beepP = document.getElementById('notif-sound-p');
                    let initialLoadP = true;

                    dbP.ref('private_chats/{room_id}').limitToLast(15).on('child_added', (snap) => {{
                        const msg = snap.val();
                        const div = document.createElement('div');
                        const isMe = msg.user === "{st.session_state.user}";
                        div.className = "bubble " + (isMe ? "me" : "others");
                        div.innerHTML = `<b style="font-size:10px; color:#ff00de;">${{msg.user}}</b><div>${{msg.text || ''}}</div>`;
                        document.getElementById('msg-area-priv').appendChild(div);
                        document.getElementById('chat-screen-priv').scrollTop = 99999;
                        if(!initialLoadP && !isMe) {{ beepP.currentTime = 0; beepP.play().catch(() => {{}}); }}
                    }});
                    setTimeout(() => {{ initialLoadP = false; }}, 2000);
                </script>
                """
                components.html(priv_chat_html, height=320)
                
                with st.form("priv_send_form", clear_on_submit=True):
                    p_msg = st.text_input(f"ข้อความลับถึง {target_user}:")
                    if st.form_submit_button("ส่งรหัสแชทส่วนตัว 🔒"):
                        if p_msg:
                            db.reference(f'private_chats/{room_id}').push({'user': st.session_state.user, 'text': p_msg, 'ts': time.time()})
                            st.rerun()

# --- 7.2 ระบบแผนที่ดาวเทียม GPS พิกัดเป๊ะขยายวงกว้างตามใจสั่ง ---
elif menu_choice == "🛰️ GPS TRACER":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🛰️ REAL-TIME GPS TARGET TRACER</h3>", unsafe_allow_html=True)
    loc = get_geolocation() 

    if loc and 'coords' in loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
        acc = loc['coords'].get('accuracy', 0)
        
        # กล่องมวลตัวเลขของพิกัดจริง
        st.markdown(f"""
            <div style="background:#090e12; border:1px solid {theme_color}; padding:10px; border-radius:8px; font-family:'Orbitron'; font-size:13px; color:#fff;">
                📍 LATITUDE: <span style="color:{theme_color};">{my_lat}</span> | LONGITUDE: <span style="color:{theme_color};">{my_lon}</span> | ACCURACY: {acc:.2f} m.
            </div>
        """, unsafe_allow_html=True)

        m = folium.Map(location=[my_lat, my_lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellites')
        folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)
        st_folium(m, width="100%", height=400)

        if st.button("📡 บันทึกและแชร์พิกัดปัจจุบันลง Firebase บอร์ดกลาง", use_container_width=True):
            db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
            st.toast("อัปโหลดพิกัดตรงเป๊ะเรียบร้อย!")
    else:
        st.info("🛰️ กำลังดึงสัญญาณดาวเทียมจากโทรศัพท์มือถือ... กรุณาเปิดระบบระบุตำแหน่ง (Location) ที่ตัวเครื่องด้วยครับบาส")

# --- 7.3 ระบบคำนวณถอดรหัสวงรอบพลังงานจริง ---
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

        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#aaa; font-family:'Orbitron'; font-size:12px;">INDEX VALUE (ผลลัพธ์มวลตัวเลขจริง)</span>
                <h1 style="color:{theme_color}; font-family:'Orbitron'; font-size:55px; margin:5px 0;">{res_index:.4f}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("### 🧮 อธิบายที่มาของมวลตัวเลขแกนวิทยาศาสตร์จริง:")
        st.latex(rf"Result = {formula_text} = {res_index:.4f}")
        
        st.markdown(f"""
        * **{diff_days:,} (จำนวนวันสะสม):** คือจำนวนวันรวมที่นับจริงห่างจากวันที่ 1 มกราคม ค.ศ. 1900 เพื่อใช้หาจุดตัดของช่วงเวลา
        * **{lunar_cycle} วัน (วงโคจรดวงจันทร์):** ค่าเวลาเฉลี่ยตามจริงทางดาราศาสตร์ที่ดวงจันทร์โคจรรอบโลก 1 รอบ นำมาหารเพื่อหาช่วง **{'ข้างขึ้น' if is_waxing else 'ข้างแรม'} {lunar_num} ค่ำ** โดยไม่มีการเดาสุ่ม
        * **{day_val} (ลำดับวันประจำสัปดาห์):** ลำดับแกนเวลาจริง (วันจันทร์=1 จนถึง วันอาทิตย์=7)
        * **1.618 (ค่าอัตราส่วนทองคำ / Golden Ratio):** ค่าคงที่สากลทางคณิตศาสตร์ที่ใช้รักษาสมดุลแรงดันในโครงสร้างเลขฐานควอนตัมอดีตและอนาคต
        """)

# --- 7.4 ระบบเครื่องเล่นเพลงสุ่มต่อเนื่อง (LOOP AUDIO RANDOM PLAYER) ---
elif menu_choice == "🎵 NEON JUKEBOX":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron; text-align:center;'>🎵 AUTOLOOP RANDOM JUKEBOX</h3>", unsafe_allow_html=True)
    
    # ดึงไฟล์ mp3 ทั้งหมดที่มีในไดเรกทอรีแอป
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    
    if all_songs:
        st.write(f"📁 ตรวจพบไฟล์เพลงในระบบทั้งหมดค้างอยู่ {len(all_songs)} เพลง")
        
        # เข้ารหัส base64 ของทุกเพลงเพื่อส่งเข้าไปรอใน JavaScript Player
        song_dict_js = {}
        for s in all_songs:
            b64 = get_base64(s)
            if b64: song_dict_js[s] = "data:audio/mp3;base64," + b64

        # ฟังก์ชัน JavaScript เล่นเพลงแบบสุ่มต่อเนื่องสีสันกราฟิกไม่ขาดช่วง
        jukebox_html = f"""
        <div style="background:#04070a; border:2px solid {theme_color}; border-radius:15px; padding:20px; text-align:center; box-shadow:0 0 20px {theme_color}30;">
            <div id="track-name" style="color:#fff; font-family:'Sarabun'; font-size:15px; font-weight:bold; margin-bottom:10px;">เตรียมระบบขับเคลื่อนเสียง...</div>
            <audio id="core-player" controls style="width:100%; margin-bottom:15px;"></audio>
            <div>
                <button onclick="playRandom()" style="background:linear-gradient(45deg, #ff00de, {theme_color}); border:none; padding:10px 25px; border-radius:8px; color:#fff; font-weight:bold; font-family:'Orbitron'; cursor:pointer;">⚡ NEXT RANDOM TRACK</button>
            </div>
        </div>

        <script>
            const playlist = {str(list(song_dict_js.keys()))};
            const songData = {str(song_dict_js)};
            const player = document.getElementById('core-player');
            const txt = document.getElementById('track-name');

            function playRandom() {{
                if(playlist.length === 0) return;
                const randomIndex = Math.floor(Math.random() * playlist.length);
                const chosenSong = playlist[randomIndex];
                
                txt.innerText = "กำลังเล่นสุ่มวนลูป 🔄: " + chosenSong;
                player.src = songData[chosenSong];
                player.play().catch(e => console.log("รอปฏิสัมพันธ์จากผู้ใช้"));
            }}

            // ออฟชั่นสำคัญ: เมื่อเพลงเล่นจบ ให้ทำการสุ่มเพลงถัดไปเล่นต่อเนื่องทันทีโดยที่สีสันกราฟิกไม่ขาดช่วง
            player.onended = function() {{
                playRandom();
            }};

            // เริ่มสตาร์ทเพลงแรกตอนเปิดหน้าจอทันที
            window.onload = function() {{
                playRandom();
            }};
        </script>
        """
        components.html(jukebox_html, height=200)
    else:
        st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์หลักของระบบแอปเลยครับบาส ลองอัปโหลดไฟล์เข้าไปดูก่อนนะ")

# --- 7.5 ระบบแปลงตัวอักษรเป็นความถี่จริง (QUANTUM BRAIN SCAN) ---
elif menu_choice == "🧠 QUANTUM BRAIN SCAN":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🔮 QUANTUM CONSCIOUSNESS SCANNER</h3>", unsafe_allow_html=True)
    
    thought_input = st.text_input("กรอกข้อความหรือความคิดเพื่อสแกนถอดค่ามวลตัวเลข ($Hz$):", "อยู่นิ่งๆ ไม่เจ็บตัว")
    
    if thought_input:
        # ถอดค่ารหัส ASCII จริงๆ จากตัวอักษรทุกตัวมาประมวลผล ไม่มีล็อกค่าล่วงหน้า
        char_sum = sum(ord(c) for c in thought_input)
        calculated_hz = (char_sum % 700) + 120.0
        
        st.markdown(f"""
            <div class="truth-card">
                <span style="color:#aaa; font-family:'Orbitron'; font-size:11px;">REAL-TIME FREQUENCY DETECTED</span>
                <h1 style="color:#ff00de; font-family:'Orbitron'; font-size:55px; margin:5px 0;">{calculated_hz:.2f} Hz</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("### 📊 คำอธิบายมวลตัวเลขของชุดคลื่นความถี่นี้:")
        st.markdown(f"""
        * **{char_sum} (ผลรวมรหัสคลื่นอักขระออร์บิทัล):** ได้มาจากการนำอักขระทีละตัวแปรในคำว่า `"{thought_input}"` ไปถอดค่าเลขฐานคอมพิวเตอร์จริงตัวต่อตัว (`ASCII unicode`) แล้วจับมาบวกกันทั้งหมดเพื่อหาค่ามวลหนาแน่นของข้อความ
        * **สูตรประมวลผลคำนวณ:** ใช้รูปแบบสมการตัวเลขคณิตศาสตร์จริงด้านล่างนี้ โดยไม่มีการล็อกผลลัพธ์
        """)
        st.latex(rf"Hz = (TotalASCII \pmod{{700}}) + 120.0 = ({char_sum} \pmod{{700}}) + 120.0 = {calculated_hz:.2f} \, Hz")

        # หน้าจอแสดงเส้นกราฟิกเรืองแสงตามจังหวะความถี่จริงที่คำนวณได้
        canvas_html = f"""
        <canvas id="live-wave" style="width:100%; height:100px; background:#04070a; border:1px solid #1a2936; border-radius:8px;"></canvas>
        <script>
            const canvas = document.getElementById('live-wave');
            const ctx = canvas.getContext('2d');
            let frame = 0;
            function drawWave() {{
                ctx.clearRect(0,0,canvas.width,canvas.height);
                ctx.strokeStyle = "{theme_color}";
                ctx.lineWidth = 2;
                ctx.beginPath();
                for(let x=0; x<canvas.width; x++) {{
                    // ความเร็วและการกะพริบแปรผันตรงตามความเร็วของค่า Hz จริงที่ได้มาด้านบน
                    let y = canvas.height/2 + Math.sin(x*0.04 + frame) * 22 * Math.cos(x*0.01);
                    if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                }}
                ctx.stroke();
                frame += {calculated_hz / 800};
                requestAnimationFrame(drawWave);
            }}
            drawWave();
        </script>
        """
        components.html(canvas_html, height=120)

# =========================================================
# 8. GLOBAL SYSTEM FOOTER
# =========================================================
st.markdown("<div style='text-align:center; color:#3b566e; font-size:11px; margin-top:30px; font-family:Orbitron;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.4.0</div>", unsafe_allow_html=True)
