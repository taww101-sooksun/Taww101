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
from datetime import datetime, date

# =========================================================
# 1. CONFIG & UI INITIALIZATION
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

def hide_st_ui():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; background-color: #0e1117; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 10px; }
            .stTabs [data-baseweb="tab"] {
                background-color: #111; border: 1px solid #333;
                border-radius: 5px; padding: 10px 20px; color: #888;
            }
            .stTabs [aria-selected="true"] {
                background-color: #39FF1422 !important;
                border-color: #39FF14 !important; color: #39FF14 !important;
            }
            @keyframes neon-glow {
                0% { filter: drop-shadow(0 0 5px #39FF14) drop-shadow(0 0 10px #39FF14); }
                50% { filter: drop-shadow(0 0 15px #39FF14) drop-shadow(0 0 25px #39FF14); }
                100% { filter: drop-shadow(0 0 5px #39FF14) drop-shadow(0 0 10px #39FF14); }
            }
            .neon-logo-main {
                width: 100px;
                display: block;
                margin: 0 auto 10px auto;
                animation: neon-glow 2s infinite ease-in-out;
            }
        </style>
    """, unsafe_allow_html=True)

hide_st_ui()

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64("logo1.png")
audio_data = get_base64("notification.mp3")
theme_color = "#39FF14"

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
        25% {{ transform: translate(2px, -2px) rotate(2deg); }}
        50% {{ transform: translate(-2px, 2px) rotate(-2deg); }}
        75% {{ transform: translate(1px, -1px) rotate(1deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 10px {theme_color}; }}
        50% {{ opacity: 0.2; color: #fff; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 10px 0; }}
    .logo-img {{ width: 80px; height: 80px; animation: dance 0.6s infinite; object-fit: contain; }}
    .slogan-txt {{ 
        font-family: sans-serif; font-weight: bold; font-size: 18px; 
        margin-left: 15px; animation: wink 1.5s infinite; 
    }}
</style>
<div class="logo-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else ''}
    <span class="slogan-txt">SYNAPSE อยู่นิ่งๆไม่เจ็บตัว</span>
</div>
"""
components.html(header_html, height=110)

# =========================================================
# 5. AUTHENTICATION SYSTEM (LOGIN / REGISTER)
# =========================================================
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color};'>🔒 SYSTEM AUTHENTICATION</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียนบัญชีใหม่"])
    
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
                    st.error("ข้อมูลไม่ถูกต้อง")
    
    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี AGENT"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาสลับไปหน้าเข้าสู่ระบบ")
    st.stop()

st.markdown(f"<div style='text-align:right; color:{theme_color}; font-size:12px; padding-right:10px;'>📡 AGENT OUTPOST: {st.session_state.user}</div>", unsafe_allow_html=True)

# =========================================================
# 6. NAVIGATION CONTROLLER (ตั้งค่าปุ่มเลือกห้องให้อยู่หน้าหลัก)
# =========================================================
st.markdown("<h4 style='color:#fff; margin-bottom:0px;'>🎛️ SELECT COMMAND SYSTEM</h4>", unsafe_allow_html=True)
menu_choice = st.radio(
    "เลือกฟังก์ชันระบบ:", 
    ["💬 GLOBAL CHATROOM", "🛰️ GPS TRACER", "🔮 THE TRUTH SCANNER", "🎵 NEON MIXER"],
    horizontal=True,
    key="main_menu_navigator"
)

st.divider()

# แถบปุ่มออกจากระบบไว้ที่ Sidebar เหมือนเดิมเพื่อไม่ให้รกหน้าจอหลัก
if st.sidebar.button("🔴 ออกจากระบบ (LOGOUT)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# =========================================================
# 7. MODULE LOGIC APPLICATIONS
# =========================================================

# --- 7.1 ระบบแชทเรียลไทม์ ---
if menu_choice == "💬 GLOBAL CHATROOM":
    st.markdown(f"<h3 style='color:{theme_color};'>💬 GLOBAL CHATROOM</h3>", unsafe_allow_html=True)
    
    chat_display_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    #chat-screen {{
        background: rgba(0,0,0,0.95); border: 2px solid {theme_color}; border-radius: 12px;
        height: 400px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
        box-shadow: inset 0 0 15px {theme_color}33;
    }}
    .bubble {{ padding: 10px 15px; border-radius: 10px; margin: 8px 0; max-width: 85%; color: #fff; font-family: 'Orbitron', sans-serif; font-size: 14px; line-height: 1.4; }}
    .me {{ background: {theme_color}22; border-right: 4px solid {theme_color}; align-self: flex-end; }}
    .others {{ background: #222; border-left: 4px solid #777; align-self: flex-start; }}
    .notif-box {{ background: #333; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; transition: 0.3s; }}
    .alert-red {{ background: #F00 !important; box-shadow: 0 0 15px #F00; font-weight: bold; }}
</style>

<div id="chat-screen">
    <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #333; padding-bottom: 5px;">
        <span style="color:{theme_color}; font-size:10px; letter-spacing: 2px;">📡 SYSTEM_ACTIVE</span>
        <span id="notif-box" class="notif-box">0 NEW SIGNAL</span>
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
        
        let html = `<div style="font-size:10px; color:#777; margin-bottom:5px;">${{msg.user}}</div>`;
        if(msg.text) html += `<div>${{msg.text}}</div>`;
        if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:8px; margin-top:8px; border: 1px solid #444;">`;
        
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
    components.html(chat_display_html, height=440)

    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            m_txt = st.text_input("MESSAGE", placeholder="พิมพ์ข้อความ...", label_visibility="collapsed", key="msg_input")
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
    if st.button("🧼 ล้างการแจ้งเตือนแชทสะสม (RESET COUNT)", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()

# --- 7.2 ระบบแผนที่ดาวเทียม GPS ---
elif menu_choice == "🛰️ GPS TRACER":
    st.markdown(f"<h3 style='color:#00FF00;'>🛰️ GLOBAL GPS TARGET TRACER</h3>", unsafe_allow_html=True)
    
    loc = get_geolocation() 

    if loc and 'coords' in loc:
        st.session_state.user_lat = loc['coords']['latitude']
        st.session_state.user_lon = loc['coords']['longitude']
        accuracy = loc['coords'].get('accuracy', 0)
        st.success(f"🎯 ล็อกเป้าหมายดาวเทียมสำเร็จ! (ช่วงความแม่นยำระยะ {accuracy:.0f} เมตร)")
        
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

        if st.button("🛰️ บันทึกพิกัดและยิงสัญญาณเข้า Firebase", use_container_width=True):
            try:
                db.reference(f'users/{st.session_state.user}').update({
                    'lat': my_lat, 'lon': my_lon, 'ts': time.time()
                })
                st.toast("ส่งพิกัดเข้าศูนย์ข้อมูลเรียบร้อย!")
            except: 
                st.error("Firebase Connection Error")
    else:
        st.info("🛰️ กำลังจับพิกัดจากเครื่องอุปกรณ์... โปรดเปิด GPS หน้าจอมือถือของคุณ (ระบบจะแสดงแผนที่เมื่อพิกัดมาครบ)")

# --- 7.3 ระบบคำนวณถอดรหัสความจริง ---
elif menu_choice == "🔮 THE TRUTH SCANNER":
    st.markdown(f"<h2 style='color:{theme_color}; text-shadow: 0 0 20px {theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
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

    st.subheader("🔍 วิเคราะห์พิกัดความจริง (เจาะลึกสมดุลพลังงาน)")
    target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
    
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {theme_color}; border-radius:20px; background:rgba(0,0,0,0.3);">
                <small>รหัสพิกัดเลขศาสตร์ควอนตัม</small>
                <h1 style="color:{theme_color}; font-size:50px; margin:0;">{d['res']}</h1>
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
            <div style="background:#111; padding:15px; border-left:5px solid {theme_color}; border-radius:10px; margin-top:10px;">
                <p style="font-size:14px; color:#aaa; margin:0;">
                    <b>สูตรการคำนวณเบื้องหลัง:</b> {d['formula']}<br>
                    คำนวณจากวันที่สะสมตั้งแต่ปี 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                </p>
            </div>
        """, unsafe_allow_html=True)

        if target_date < date.today(): st.warning("⏪ ตรวจสอบรอยเท้าพลังงานใน 'อดีต'")
        elif target_date > date.today(): st.error("🔮 ตรวจสอบพิกัดเป้าหมายใน 'อนาคต'")
        else: st.success("🟢 พิกัดพลังงานในระดับปัจจุบัน")

# --- 7.4 ระบบมิกเซอร์ครอสเฟดเพลง V.2 ---
elif menu_choice == "🎵 NEON MIXER":
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    all_songs = sorted(all_songs)
    mixer_logo_b64 = get_base64("logo1.png")

    st.markdown("""
        <style>
        .neon-mixer-text {
            font-family: sans-serif; color: #fff; text-align: center; font-size: 1.8rem; letter-spacing: 5px;
            text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 40px #00f3ff; margin-bottom: 20px;
        }
        </style>
        <div class="neon-mixer-text">SYNAPSE MIXER ENGINE</div>
        """, unsafe_allow_html=True)

    if all_songs:
        col_mix1, col_mix2 = st.columns(2)
        with col_mix1: sA = st.selectbox("DECK A (เริ่มก่อน)", all_songs, key="mixer_sA")
        with col_mix2: sB = st.selectbox("DECK B (เล่นต่อ)", all_songs, key="mixer_sB")
        
        def get_audio_base64_local(file_path):
            try:
                with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
            except: return None

        audio_a = get_audio_base64_local(sA)
        audio_b = get_audio_base64_local(sB)

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body {{ background: transparent; color: white; font-family: sans-serif; overflow: hidden; }}
                .neon-card {{ border: 2px solid #333; background: rgba(10,10,10,0.95); box-shadow: 0 0 20px rgba(255,0,222,0.3); }}
                .logo-box {{ width: 60px; height: 60px; margin: 0 auto 15px auto; background: url('data:image/png;base64,{mixer_logo_b64}') no-repeat center; background-size: contain; filter: drop-shadow(0 0 8px #00f3ff); }}
                .visualizer {{ height: 80px; background: #000; border-radius: 10px; border: 1px solid #222; }}
                .deck {{ padding: 10px; border-radius: 10px; border: 1px solid #222; margin-top: 10px; transition: 0.3s; opacity: 0.5; }}
                .active-a {{ border-color: #ff00de; box-shadow: 0 0 10px #ff00de; opacity: 1; }}
                .active-b {{ border-color: #00f3ff; box-shadow: 0 0 10px #00f3ff; opacity: 1; }}
                .btn-mix {{ background: linear-gradient(45deg, #ff00de, #00f3ff); width: 100%; padding: 12px; border-radius: 10px; font-weight: bold; margin-top: 15px; cursor: pointer; }}
                .progress {{ height: 4px; background: #222; margin-top: 5px; }}
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
                    <div class="flex justify-between text-[10px]"><span style="color:#00f3ff">DECK B</span><span id="tB">00:00</span></div>
                    <div class="text-[11px] truncate">{sB}</div>
                    <div class="progress"><div id="barB" class="bar" style="background:#00f3ff"></div></div>
                </div>

                <button onclick="start()" class="btn-mix">🚀 START MIXING</button>
                <div id="status" class="text-[9px] mt-3 text-gray-500">SYSTEM READY</div>
            </div>

            <script>
                let ctx, analyser, songA, songB, gA, gB, srcA, srcB;
                let isPlaying = false, active = 'A', data;

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
                        document.getElementById('tA').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                        document.getElementById('barA').style.width = (elapsed/songA.duration*100) + "%";
                        if (rem < 8) {{
                            active = 'B'; gA.gain.linearRampToValueAtTime(0, ctx.currentTime + 5);
                            playDeckB(); document.getElementById('status').innerText = "CROSSFADING...";
                        }}
                    }} else if (active == 'B' && srcB) {{
                        let elapsed = ctx.currentTime - srcB.t0; let rem = songB.duration - elapsed;
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
    else:
        st.error("ไม่พบไฟล์เพลงนามสกุล .mp3 ในโฟลเดอร์หลัก")

# =========================================================
# 8. GLOBAL SYSTEM FOOTER
# =========================================================
st.markdown("<div style='text-align:center; color:#444; font-size:11px; margin-top:30px;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.3</div>", unsafe_allow_html=True)
