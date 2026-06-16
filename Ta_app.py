import streamlit as st
import os
import pandas as pd
import math
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# --- [ บรรทัดแรกสุดของไฟล์ ห้ามย้ายเด็ดขาด! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# =========================================================
# 🔐 ระบบเชื่อมต่อ FIREBASE (DEEP CLEAN KEY: ล้างช่องว่างหลุดจากจอมือถือ)
# =========================================================
firebase_ready = False

if not firebase_admin._apps:
    try:
        # ก้อนกุญแจลับดิบๆ ที่ติดเว้นวรรคจากการก๊อปปี้บนหน้าจอมือถือ
        raw_key_block = """MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCjG40Z0gib0k65
yE4jV8q6uwKQhznwV3ybK8F8Z8pF6tdIilR8EiSGQpPTvgTcNIu2gUtC3VNZV7qf
+68alnNpgF5ZnrrLot/QqtxnjzzxZrHQIUz6D1BUjLi3zj1DpG9KPWKb5GgOjFnD
1MEbivAJqpQSA5h/PG/yC6vVruNLw/RCwfnOyZiCkrbTvDppdRQxYtQGcMM1uslk
lJrV5qnpAjBAg90FF1F2Yzl6yGj0d/xfrReq1dkwJVBiQ1nN73SXvu7Rt/cxY42U
d+n9WWKP4K12iH4Pq55lyEik01TQ/IiLrivxo/wDLIjF8HSTI4fkUxJajgak9cmm
P2Bzhi2lAgMBAAECggeAGjR+uLeFMQ26nsAXB7ge5t3NVW2YaiwQJbkDsspVFeMb
V/j7hlx+2EBBklsc2kkp6jY/Iny/G6NL5VCxKw8hd0GLxw/IuJdQKK0O0KeTdcBX
UJZNEP7dW9wpAETnFGNKiw2uNlgdvLqhYGRh6xwpIRByDivcOBL8dFGaN7BLrdwJ
yFrVl9vFcl9Bb9wCItJTlcKT3CRpMZud3M/KcWW36pxLVN3JWLssZtCBdw4BZqBY
VHD/QYHO1su28xL10gpaEXYJNA7zYzSc23BiCE2Lkx2vWKt2GhfmYhiBW+dHLSpa
V72xTiGcUpkbr8L3S3i5cgjwyz7riibUqz9TL5I4kQKBgQDRNx8kRVqkQ8yf0OdN
QJshB1P4ZCSDkTPv75TZOD1aKPbzrbK6Hf+tdcaN8ktv/fcAxkaZORgq6CJr9Q0w
Xnio4g74VHJ5vy9ER7lUK85qs5jqXcubilP3MF5ilpMfFo9V09ERDjrllWGo5Jqn
a5PJmq0FuKlF1+kcrkoH8VF+VQKBgQDHlOr3dhVYquCrO9wXxDzzEi2yRAj0Hoj9
XpD9wZFtpb54EfQ4odkJdKe5zCcQFOIgmmIYMeevhMyToHKjMi2qPbSEgCYYzcYf
IJLbzLPfQfU+cn0ayuDPic69JRJPhqOAYnA2CEDOzAtbwl5aKRxqYe2beWBfcvdS
I3kec3+iEQKBgQCAjt2M/S0AiUTg445uMwfgGM+pb2fcjMocYtzVSbCxiUCOZirQ
IQTuQtPaf4uJasZv7GaPWr0WCIS2T+Nl2HdOV3KZd9LMKwXRcD1aknyJpoiNY0ts
7WhBGbC15g7LaKJ1O+5ZC6R3VP6ouKirvfgXRvuQ63Lgnxb4b8S/8rJ/7QKBgQCT
pMTV4BMWjwK5agT9x/xWzSHk+JOvFE+/MBAOyP2uoahv5shGhOSsLBJQToivSuOl
vs/GmlSM8a7tnwpvVBWYFSHPy4VjYAaqzEwYMiz2gjLMyaFnCqKYpZe9MQmEr1OR
DEF6l0xqL2RPs1BdXoBY6qz+ESKMOd5gc0GMl2DaIQKBgAgLzHmGQj+gVmr4Nz4d
/eH7xPVWB5Y0yGpIFxAUTfnIv+wjTLfF0DnT6xCgOBag2cEFy3YmLa85n/hwd4vb
cNoWeThofCTEVdwnJ8nwreRAepqOQ5Qp1oWFyCUojH6uetFzwoyMCdQdDXVwlBdi
YmaeksHQ6/3MQ6w4Q/IJ9a4L"""

        # ทำความสะอาดระดับลึก: เอาเว้นวรรคและขึ้นบรรทัดใหม่ทั้งหมดออกก่อน แล้วมาจัดระเบียบใหม่ให้ถูกต้องร้อยเปอร์เซ็นต์
        clean_lines = []
        for line in raw_key_block.split('\n'):
            stripped = line.replace(" ", "").replace("\r", "").strip()
            if stripped:
                clean_lines.append(stripped)
        
        # ประกอบร่างกลับคืนตามมาตรฐาน JWT ของ Google
        formatted_private_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(clean_lines) + "\n-----END PRIVATE KEY-----\n"

        firebase_cfg = {
            "type": "service_account",
            "project_id": "sooksun-104",
            "private_key_id": "e13ddd5244c07d6f5c7d9c46c4e604ca2c7b8e3e",
            "private_key": formatted_private_key,
            "client_email": "firebase-adminsdk-fbsvc@sooksun-104.iam.gserviceaccount.com",
            "client_id": "101794686310728865878",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40sooksun-104.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        cred = credentials.Certificate(firebase_cfg)
        db_url = "https://sooksun-104-default-rtdb.firebaseio.com"
        firebase_admin.initialize_app(cred, {'databaseURL': db_url})
        firebase_ready = True
    except Exception as e:
        st.error(f"ระบบตรวจพบบั๊กโครงสร้างคีย์: {e}")
        firebase_ready = False
else:
    firebase_ready = True

# --- ตั้งค่าเริ่มต้นของระบบธีม ---
if 'custom_theme' not in st.session_state:
    st.session_state.custom_theme = "#00f3ff"

# --- ฟังก์ชันคำนวณดาราศาสตร์/ควอนตัมประจำวัน ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"

    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}

# --- หน้าแรกบังคับลงชื่อ Agent ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ, บาส").strip()
    
    if st.button("ACTIVATE SYSTEM", use_container_width=True):
        if new_user:
            st.session_state.user = new_user        
            st.session_state.logged_in = True     
            st.session_state.page = "HOME"
            
            if firebase_ready:
                try:
                    db.reference(f'users/{new_user}').set({
                        'created_at': time.time(),
                        'lat': 13.7367, 'lon': 100.5231
                    })
                except: pass
                
            st.success(f"WELCOME AGENT: {new_user}")
            st.rerun()      
        else:
            st.warning("กรุณาใส่ชื่อ AGENT ของคุณก่อน!")
    st.stop()

# --- การปรับแต่งเฉดสีหน้าจอ ---
def setup_ui():
    current_color = st.session_state.custom_theme
    st.markdown(f"""
        <style>
        header, footer, #MainMenu {{visibility: hidden;}}
        .stApp {{ background: #000; color: {current_color}; border-top: 5px solid {current_color}; }}
        .stButton>button {{
            border-radius: 15px; border: 1px solid {current_color} !important;
            background: rgba(0, 242, 254, 0.1); color: white; height: 80px; font-size: 16px;
            box-shadow: 0 0 10px {current_color} !important;
        }}
        .stButton>button:hover {{ background: {current_color}; color: #000; }}
        </style>
    """, unsafe_allow_html=True)

setup_ui()

if 'page' not in st.session_state:
    st.session_state.page = "HOME"

if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"; st.rerun()

# =========================================================
# [ หน้าแรก: ศูนย์ควบคุมหลัก ]
# =========================================================
if st.session_state.page == "HOME":
    st.markdown("<h1 style='text-align:center; color:#fff; text-shadow: 0 0 10px #00f3ff;'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>AGENT ONLINE: {st.session_state.user} | อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER (ดีเจมิกซ์เสียง)", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. TACTICAL CHAT & MAP (ระบบแชทลับ)", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🖼️ 3. SATELLITE IMAGE (ค้นรูปภาพดาวเทียม)", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("✨ 4. NEON GENERATOR (อักษรเรืองแสง)", use_container_width=True): st.session_state.page = "3_neon"; st.rerun()
        if st.button("🎬 5. VIDEO HUB (ดูสตรีมวิดีโอ/วงจรปิด)", use_container_width=True): st.session_state.page = "4_video"; st.rerun()
    with c2:
        if st.button("🎙️ 6. SENSOR RADAR (วัดคลื่นเสียง/สั่นสะเทือน)", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("💖 7. DESTINY CHECK (ถอดรหัสดวงดาว)", use_container_width=True): st.session_state.page = "7"; st.rerun()
        if st.button("🔢 8. DAILY PINCODE (รหัสรักษาความปลอดภัย)", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("📝 9. MEMORY SYSTEM LOG (จดบันทึกคลาวด์)", use_container_width=True): st.session_state.page = "9"; st.rerun()
        if st.button("🎨 10. INTERFACE COLOR (ปรับแต่งสีระบบ)", use_container_width=True): st.session_state.page = "10"; st.rerun()

# =========================================================
# ห้องที่ 1: MUSIC PLAYER
# =========================================================
elif st.session_state.page == "1":
    st.markdown("<h2 style='text-align:center;'>🎵 MUSIC PLAYER DIRECT MIXER</h2>", unsafe_allow_html=True)
    mixer_html = """
    <div style="background:#111; border:2px solid #00f3ff; border-radius:15px; padding:20px; text-align:center;">
        <p style="color:white;">🎛️ เครื่องผสมสัญญาณเสียงและคุมความถี่ดีเจผ่านเว็บ</p>
        <canvas id="v-main" style="width:100%; height:100px; background:#000; border:1px solid #ff00de;"></canvas>
    </div>
    """
    components.html(mixer_html, height=160)
    st.write("---")
    st.subheader("📂 มิวสิคคลังข้อมูลท้องถิ่น (.mp3)")
    all_songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if all_songs:
        for s in all_songs:
            if st.button(f"▶️ {s}", use_container_width=True): st.audio(s)
    else:
        st.caption("ไม่พบไฟล์ .mp3 ในโฟลเดอร์แอปหลัก")

# =========================================================
# ห้องที่ 2: CHAT SYSTEM & RADAR (เชื่อมต่อตรงสลุด 100%)
# =========================================================
elif st.session_state.page == "2":
    st.markdown("<h2 style='text-align:center; color:#ff00de;'>🛰️ TACTICAL RADAR & PRIVATE CHAT</h2>", unsafe_allow_html=True)
    
    import folium
    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=14, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Satellite')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)

    if firebase_ready:
        try:
            users_ref = db.reference('users').get()
            if users_ref:
                for uid, data in users_ref.items():
                    if uid != st.session_state.user and isinstance(data, dict) and 'lat' in data:
                        folium.Marker([data['lat'], data['lon']], icon=folium.Icon(color='blue'), tooltip=f"AGENT: {uid}").add_to(m)
        except: pass

    st_folium(m, width="100%", height=250)

    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        if firebase_ready:
            try:
                db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
                st.toast("พิกัดอัปเดตเข้าฐานข้อมูลวิจัยแล้ว!")
            except Exception as e: st.error(f"Error: {e}")

    st.write("---")
    st.markdown("<h4>🔐 PRIVATE SECURE CHAT</h4>", unsafe_allow_html=True)
    
    if not firebase_ready:
        st.error("⚠️ ขัดข้อง: ระบบตรวจพบบั๊ก JWT Token ไม่ยอมทำงาน")
    else:
        try:
            all_users = db.reference('users').get()
            if all_users:
                friends = [u for u in all_users.keys() if u != st.session_state.user]
                if friends:
                    target_agent = st.selectbox("🎯 เลือก AGENT ที่ต้องการติดต่อ:", friends)
                    if target_agent:
                        room_id = "_".join(sorted([st.session_state.user, target_agent]))
                        chat_ref = db.reference(f'private_messages/{room_id}')

                        with st.form("private_chat_form", clear_on_submit=True):
                            msg = st.text_input(f"TO: {target_agent}", placeholder="พิมพ์ข้อความข้อความลับตรงนี้...")
                            if st.form_submit_button("SEND SIGNAL"):
                                if msg:
                                    chat_ref.push({'sender': st.session_state.user, 'text': msg, 'ts': time.time()})
                                    st.rerun()

                        messages = chat_ref.order_by_child('ts').limit_to_last(10).get()
                        if messages:
                            for mid in reversed(list(messages.keys())):
                                m_data = messages[mid]
                                is_me = m_data['sender'] == st.session_state.user
                                align = "right" if is_me else "left"
                                color = "#00f3ff" if is_me else "#ff00de"
                                bg = "rgba(0, 243, 255, 0.15)" if is_me else "rgba(255, 0, 222, 0.15)"
                                st.markdown(f"""
                                    <div style="text-align:{align}; margin-bottom:10px;">
                                        <div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:15px; border:1px solid {color};">
                                            <b style="color:{color}; font-size:0.75rem;">{m_data['sender']}</b><br>
                                            <span style="color:white;">{m_data['text']}</span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                else: st.caption("🛰️ ตรวจพบคุณเป็น Agent ออนไลน์คนเดียวในเครือข่าย")
        except Exception as e: st.error(f"Chat Error: {e}")

# =========================================================
# ห้องที่ 3: IMAGE SEARCH
# =========================================================
elif st.session_state.page == "3":
    st.markdown("<h2>🖼️ SATELLITE IMAGE FIELD</h2>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=800")

# =========================================================
# ห้องเสริม 3_neon: NEON GENERATOR
# =========================================================
elif st.session_state.page == "3_neon":
    st.markdown("<h2>✨ NEON TEXT MAKER</h2>", unsafe_allow_html=True)
    txt = st.text_input("พิมพ์ตัวหนังสือที่คุณต้องการแปลงสภาพ:", "STAY STILL NO PAIN")
    st.markdown(f"<h1 style='text-align:center; color:#fff; text-shadow:0 0 15px #ff00de, 0 0 30px #00f3ff;'>{txt}</h1>", unsafe_allow_html=True)

# =========================================================
# ห้องที่ 4: VIDEO HUB
# =========================================================
elif st.session_state.page == "4_video":
    st.markdown("<h2>🎬 VIDEO FEED CONTROL</h2>", unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# =========================================================
# ห้องที่ 6: SENSOR RADAR
# =========================================================
elif st.session_state.page == "6":
    st.markdown("<h2 style='text-align:center;'>⚡ LIVE AUDIO & FREQUENCY SENSOR</h2>", unsafe_allow_html=True)
    audio_html = """
    <div style="background:#111; padding:15px; border:1px solid #FFD700; text-align:center; font-family:monospace; color:#FFD700;">
        🎤 สัญญาณความถี่เสียงปัจจุบัน: <span id="hz">0</span> Hz
    </div>
    <script>
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            const ctx = new AudioContext(); const ana = ctx.createAnalyser();
            ctx.createMediaStreamSource(stream).connect(ana);
            const data = new Uint8Array(ana.frequencyBinCount);
            function run() {
                ana.getByteFrequencyData(data);
                let max = 0, idx = 0;
                for(let i=0;i<data.length;i++) { if(data[i]>max) { max=data[i]; idx=i; } }
                document.getElementById('hz').innerText = Math.round(idx * ctx.sampleRate / ana.fftSize);
                requestAnimationFrame(run);
            }
            run();
        }).catch(()=>{});
    </script>
    """
    components.html(audio_html, height=100)

# =========================================================
# ห้องที่ 7: DESTINY CHECK & LUNAR DECODER
# =========================================================
elif st.session_state.page == "7":
    st.markdown("<h2>🌙 LUNAR & UNICODE DECODER</h2>", unsafe_allow_html=True)
    target_date = st.date_input("เลือกพิกัดวันเวลาเพื่อถอดสัญญาณดวงดาว:", date.today())
    if st.button("🌀 ประมวลผลรหัสควอนตัม", use_container_width=True):
        res_data = get_detailed_logic(target_date)
        if res_data:
            st.write(f"ผลลัพธ์ดวงดาวประจำวัน: **{res_data['phase']}**")
            st.metric("VECTOR ENERGY VALUE", res_data['res'])
            st.code(f"สูตรประมวลผลทางคณิตศาสตร์: {res_data['formula']}")

# =========================================================
# ห้องที่ 8: DAILY ACCESS PINCODE
# =========================================================
elif st.session_state.page == "8":
    st.markdown("<h2>🔢 DAILY SECURITY PINCODE</h2>", unsafe_allow_html=True)
    today_str = date.today().strftime("%Y-%m-%d")
    raw_key = f"{today_str}_{st.session_state.user}_SYNAPSE"
    hash_res = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
    pin = str(int(hash_res[:4], 16))[-4:].zfill(4)
    st.success(f"🔐 รหัสเข้าเซิร์ฟเวอร์สูงสุดของคุณประจำวันนี้คือ: {pin}")

# =========================================================
# ห้องที่ 9: SYSTEM LOG (บันทึกข้อมูลเข้าเซิร์ฟเวอร์)
# =========================================================
elif st.session_state.page == "9":
    st.markdown("<h2>📝 MEMORY SYSTEM LOG</h2>", unsafe_allow_html=True)
    log_txt = st.text_area("กรอกข้อความที่ต้องการบันทึกลงคลังความจำ:")
    if st.button("💾 SAVE LOG", use_container_width=True):
        if log_txt and firebase_ready:
            try:
                db.reference(f'system_logs/{st.session_state.user}').push({
                    'text': log_txt, 'ts': time.time(),
                    'datetime': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                })
                st.success("บันทึกข้อมูลเข้าคลาวด์ Firebase สำเร็จ!")
            except Exception as e: st.error(f"เกิดข้อผิดพลาด: {e}")
            
    st.divider()
    st.markdown("#### 📂 บันทึกล่าสุดของคุณ")
    if firebase_ready:
        try:
            my_logs = db.reference(f'system_logs/{st.session_state.user}').order_by_child('ts').limit_to_last(5).get()
            if my_logs:
                for key, val in reversed(list(my_logs.items())):
                    st.markdown(f"""
                    <div style="background: rgba(80, 200, 120, 0.1); border-left: 3px solid #50C878; padding: 10px; margin-bottom: 10px;">
                        <small style="color:#50C878;">🕒 {val.get('datetime', 'N/A')}</small><br>
                        <span style="color: white;">{val.get('text', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        except: pass

# =========================================================
# ห้องที่ 10: INTERFACE COLOR
# =========================================================
elif st.session_state.page == "10":
    st.markdown("<h2>🎨 COLOR MASTER UI</h2>", unsafe_allow_html=True)
    c_pick = st.color_picker("เลือกเฉดสีนีออนหลักของหน้าจอแอปพลิเคชัน:", st.session_state.custom_theme)
    if st.button("🔥 บังคับอัปเดตสีระบบ", use_container_width=True):
        st.session_state.custom_theme = c_pick
        st.rerun()
