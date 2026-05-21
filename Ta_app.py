import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date  # นำเข้า date เพิ่มเติมเพื่อใช้คำนวณพิกัดความจริง
import math  # นำเข้าคำสั่งคณิตศาสตร์สำหรับการถอดรหัสรูทรากที่สอง
import base64
import os

# --- 0. CONFIG & CSS HIDE STREAMLIT ---
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")

def hide_st_ui():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; }
            body { background-color: #000; color: #fff; }
            /* ปรับแต่ง Tab ให้เข้ากับธีมไซเบอร์นีออน */
            .stTabs [data-baseweb="tab-list"] { gap: 10px; }
            .stTabs [data-baseweb="tab"] {
                background-color: #111; border: 1px solid #333;
                border-radius: 5px; padding: 10px 20px; color: #888;
                font-family: sans-serif;
            }
            .stTabs [aria-selected="true"] {
                background-color: #39FF1422 !important;
                border-color: #39FF14 !important; color: #39FF14 !important;
            }
        </style>
    """, unsafe_allow_html=True)

hide_st_ui()

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# --- 1. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"🛰️ Firebase Connection Error: {e}")

# --- 2. SESSION STATE & LOGO/SOUND DATA ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" # กำหนดค่าสีเริ่มต้นควบคุมระบบ

logo_base64 = get_base64("logo1.png")
audio_data = get_base64("notification.mp3")
theme_color = st.session_state.theme_color

# --- 3. HEADER: LOGO DANCING & SLOGAN WINKING ---
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
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 15px 0; }}
    .logo-img {{ width: 100px; height: 100px; animation: dance 0.6s infinite; object-fit: contain; }}
    .slogan-txt {{ 
        font-family: sans-serif; font-weight: bold; font-size: 20px; 
        margin-left: 15px; animation: wink 1.5s infinite; 
    }}
</style>
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}" class="logo-img">
    <span class="slogan-txt">SYNAPSE อยู่นิ่งๆไม่เจ็บตัว</span>
</div>
"""
components.html(header_html, height=140)

# --- 4. LOGIN / REGISTER PAGE ---
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color};'>ยืนยันตัวตนเจ้าหน้าที่</h3>", unsafe_allow_html=True)
    tab_l1, tab_l2 = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียน"])
    
    with tab_l1:
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
                    st.error("ข้อมูลไม่ถูกต้อง ความปลอดภัยปฏิเสธการเข้าถึง")
    
    with tab_l2:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาไปที่หน้าเข้าสู่ระบบ")
    st.stop()

# --- 5. MAIN CORE MODULE TABS ---
st.markdown(f"<div style='text-align:right; color:{theme_color}; font-size:12px; padding-right:10px; font-weight:bold;'>AGENT: {st.session_state.user}</div>", unsafe_allow_html=True)

# สร้างเมนูแยกแท็บการใช้งานหลักระหว่างห้องแชตและห้องถอดรหัสคณิตศาสตร์ควอนตัม
main_tabs = st.tabs(["💬 SYNAPSE CHAT LIVE", "🧬 TRUTH DECODER"])

with main_tabs[0]:
    chat_display_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        #chat-screen {{
            background: rgba(0,0,0,0.95); border: 2px solid {theme_color}; border-radius: 12px;
            height: 480px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
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
    components.html(chat_display_html, height=520)

    # --- CONTROLS CHAT INTERFACE ---
    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            m_txt = st.text_input("MESSAGE", placeholder="พิมพ์ข้อความตอบกลับโครงข่าย...", label_visibility="collapsed")
        with c2:
            m_img = st.file_uploader("IMAGE", type=['png','jpg','jpeg'], label_visibility="collapsed")
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

with main_tabs[1]:
    # --- 6. LOGIC ROOM MODULE ---
    def room_logic():
        st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
        
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

        st.subheader("🔍 วิเคราะห์พิกัดความจริง (อดีต-อนาคต)")
        target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
        
        if target_date:
            d = decode_truth(target_date)
            st.markdown(f"""
                <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3); box-shadow: 0 0 15px {st.session_state.theme_color}55;">
                    <small style="color:#aaa; letter-spacing: 2px;">รหัสพิกัดจักรวาล</small>
                    <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0; text-shadow: 0 0 15px {st.session_state.theme_color};">{d['res']}</h1>
                    <p style="color:#888; margin-top:5px; font-weight:bold;">{d['type']}</p>
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
                    <p style="font-size:14px; color:#aaa; margin:0; font-family: monospace;">
                        <b>สูตรการคำนวณรหัสลับ:</b> {d['formula']}<br>
                        คำนวณจากวันที่สะสมตั้งแต่ปี 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if target_date < date.today(): st.warning("⏪ ตรวจสอบรอยเท้าพลังงานใน **'อดีต'**")
            elif target_date > date.today(): st.error("🔮 ตรวจสอบพิกัดเป้าหมายใน **'อนาคต'**")
            else: st.success("🟢 พิกัดพลังงานใน **'ปัจจุบัน'**")

    # เรียกใช้งานฟังก์ชันห้องคำนวณความจริงด้านในแท็บ
    room_logic()

# --- 7. GLOBAL TERMINAL CONTROLS ---
st.markdown("<br>", unsafe_allow_html=True)
st.divider()
col_act1, col_act2 = st.columns(2)
with col_act1:
    if st.button("ล้างการแจ้งเตือน (RESET)", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()
with col_act2:
    if st.button("ออกจากระบบ (LOGOUT)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
