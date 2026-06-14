import streamlit as st  
import os
import pandas as pd
import math
import time
import base64
import json  # ✅ แก้ไข: เพิ่ม import json เพื่อให้ json.loads() ทำงานได้จริง ไม่เกิด NameError
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# --- [ บรรทัดตั้งค่าหน้าจอ ต้องอยู่บนสุดถัดจาก import ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# =========================================================
# [ ชุดคำสั่งเชื่อมต่อฐานข้อมูล SOOKSUN-101 ผ่านระบบ Secrets หลังบ้าน ]
# =========================================================
if firebase_admin._apps:
    for app_name in list(firebase_admin._apps.keys()):
        try:
            firebase_admin.delete_app(firebase_admin._apps[app_name])
        except Exception:
            pass

try:
    # ดึงข้อความ JSON ก้อนใหญ่จาก Secrets มาแปลงเป็นโครงสร้างข้อมูลคอมพิวเตอร์จริง
    firebase_raw = st.secrets["firebase"]["text"]
    firebase_cfg = json.loads(firebase_raw)

    # เชื่อมต่อตรงไปยัง Firebase URL ของโปรเจกต์ sooksun-101
    cred = credentials.Certificate(firebase_cfg)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://sooksun-101-default-rtdb.firebaseio.com' 
    })
    connection_status = True
except Exception as e:
    connection_status = False
    connection_error = e

# =========================================================
# --- ธีมสี ---
if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#00f3ff"
if 'custom_theme' not in st.session_state:
    st.session_state.custom_theme = "#00f3ff"

# --- [ หัวใจคำนวณ: ระบบถอดรหัส Lunar ] ---
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

# --- ส่วนหน้าจอลงชื่อเข้าใช้ (Login / Register) ---
if not st.session_state.get('logged_in', False):
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    
    if not connection_status:
        st.error(f"⚠️ ระบบเชื่อมต่อหลังบ้านตรวจพบปัญหา: {connection_error}")
        st.info("💡 อย่าลืมนำรหัส JSON (TOML) ไปใส่ในกล่อง Secrets ของเว็บ Streamlit ด้วยนะครับ")

    with st.container():
        new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ101, บาส").strip()
        
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                try:
                    # ตรวจสอบการเชื่อมต่อและเขียนข้อมูลลง Firebase จริง
                    db.reference(f'users/{new_user}').set({
                        'created_at': time.time(),
                        'lat': 13.7367,
                        'lon': 100.5231
                    })
                    
                    st.session_state.user = new_user        
                    st.session_state.logged_in = True     
                    st.session_state.page = "HOME"         

                    st.success(f"WELCOME AGENT: {new_user}")
                    st.balloons()
                    time.sleep(1.5) 
                    st.rerun()      
                except Exception as e:
                    st.error(f"ระบบไม่สามารถเข้าถึงฐานข้อมูลคลาวด์ได้: {e}")
                    st.info("💡 คำแนะนำ: อย่าลืมเข้าไปเปลี่ยน Rules ในหน้าเว็บ Firebase Realtime Database ให้เป็น true ทั้งคู่นะครับ")
            else:
                st.warning("กรุณาใส่ชื่อ AGENT ของคุณก่อน!")
    st.stop() 

# --- การตกแต่งสไตล์หลักของแอป ---
def setup_ui():
    current_color = st.session_state.custom_theme
    st.markdown(f"""
        <style>
        header, footer, #MainMenu {{visibility: hidden;}}
        .stApp {{ background: #000; color: {current_color}; border-top: 5px solid {current_color}; transition: all 0.5s ease; }}
        
        .stButton>button {{
            border-radius: 15px;
            border: 1px solid {current_color} !important;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 100px;
            font-size: 18px;
            transition: 0.3s;
            box-shadow: 0 0 10px {current_color} !important;
        }}
        .stButton>button:hover {{
            background: {current_color};
            color: #000;
            box-shadow: 0 0 20px {current_color};
        }}
        
        .neon-text {{
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px {current_color}, 0 0 20px {current_color};
            font-weight: bold;
        }}
        hr {{
            border-bottom: 2px solid {current_color} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- ระบบคุมหน้าจอ ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ปุ่มย้อนกลับไปหน้าหลัก
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# =========================================================
# [ หน้าแรก: ศูนย์รวม 10 แอป ]
# =========================================================
if st.session_state.page == "HOME":
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    if connection_status:
        st.success(f"📡 บัญชี AGENT: {st.session_state.user} | เชื่อมต่อฐานข้อมูลคลาวด์ SOOKSUN1 เรียบร้อย")
    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        st.caption("ความสามารถ: เล่นไฟล์เสียง และระบบควบคุมเสียงดีเจผ่านหน้าเว็บ")

        if st.button("🖼️ 2. IMAGE SEARCH\nค้นหาภาพจากดาวเทียม", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        st.caption("ความสามารถ: ดึงรูปภาพจากคลัง Unsplash ตามคำค้นหาที่ต้องการ")

        if st.button("✨ 3. NEON GENERATOR\nสร้างตัวอักษรเรืองแสง", use_container_width=True):
            st.session_state.page = "3_neon"; st.rerun()
        st.caption("ความสามารถ: แปลงข้อความธรรมดาให้เป็นศิลปะนีออนวิ้งๆ")

        if st.button("💖 4. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        st.caption("ความสามารถ: วิเคราะห์ดวงชะตาผ่านระบบผลรวมรหัส Unicode ของชื่อ")

        if st.button("📝 5. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
        st.caption("ความสามารถ: จดบันทึกข้อความและเหตุการณ์สำคัญลงในหน่วยความจำ Cloud")

    with c2:
        if st.button("💬 6. CHAT & VOICE HUB\nระบบสื่อสารรวม-ส่วนตัว และวิทยุเสียง", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: แชตรวม แชตลับ และส่งข้อความเสียง Walkie-Talkie พร้อม Tactical Map")

        if st.button("🎬 7. VIDEO HUB\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True):
            st.session_state.page = "4_video"; st.rerun()
        st.caption("ความสามารถ: เชื่อมต่อและฉายภาพวิดีโอจาก YouTube หรือ Link ตรง")

        if st.button("🌍 8. WORLD CLOCK & SENSORS\nเซนเซอร์และเวลาเรียลไทม์", use_container_width=True):
            st.session_state.page = "6_clock"; st.rerun()
        st.caption("ความสามารถ: ตรวจสอบเวลาโลก คลื่นเสียง แรงสั่นสะเทือน (G-Force) และข้อมูลไบโอสแกน")

        if st.button("🔢 9. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        st.caption("ความสามารถ: เจนรหัสตัวเลขนำโชคแบบสุ่มรหัส SHA-256 รายวัน")

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()
        st.caption("ความสามารถ: เปลี่ยนสีสันของ Interface เพื่อความสวยงามตามใจชอบ")

# =========================================================
# ห้องที่ 1: MUSIC PLAYER
# =========================================================
elif st.session_state.page == "1":
    def get_base64_img(file_path):
        try:
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except: return ""

    logo_b64 = get_base64_img("logo1.png")

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .logo-center {{
            display: block;
            margin: 0 auto;
            width: 100px; height: 100px;
            background-image: url("data:image/png;base64,{logo_b64}");
            background-size: contain; background-repeat: no-repeat;
            filter: drop-shadow(0 0 10px #ff00de);
            animation: logo-pulsing 2s infinite alternate;
        }}
        @keyframes logo-pulsing {{
            from {{ filter: drop-shadow(0 0 5px #ff00de); transform: scale(1); }}
            to {{ filter: drop-shadow(0 0 20px #00f3ff); transform: scale(1.1); }}
        }}
        .neon-title-main {{
            font-family: 'Orbitron', sans-serif;
            color: #fff; text-align: center;
            text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
            font-size: 1.8rem; margin: 15px 0;
        }}
        </style>
        <div class="logo-center"></div>
        <h1 class="neon-title-main">SYNAPSE COMMAND CENTER</h1>
    """, unsafe_allow_html=True)

    mixer_html = f"""
    <div id="mixer-container" style="background: rgba(10,10,10,0.9); border: 2px solid #333; border-radius: 25px; padding: 20px; font-family: sans-serif;">
        <canvas id="v-main" style="width: 100%; height: 120px; background: #000; border-radius: 15px; border: 1px solid #ff00de;"></canvas>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
            <div style="padding: 15px; border-left: 4px solid #ff00de; background: rgba(255,0,222,0.05); border-radius: 10px;">
                <small style="color: #ff00de; font-weight: bold;">DECK A</small>
                <div id="nameA" style="color: #fff; font-size: 12px; margin: 5px 0; overflow: hidden;">ยังไม่ได้เลือกเพลง...</div>
                <input type="file" id="inA" accept="audio/*" style="display:none" onchange="loadA(this.files[0])">
                <button onclick="document.getElementById('inA').click()" style="background: #ff00de; color: white; border: none; padding: 5px 10px; border-radius: 5px; font-size: 10px; cursor: pointer;">SELECT A</button>
                <div style="height: 4px; background: #222; margin-top: 10px; border-radius: 2px;"><div id="barA" style="height: 100%; width: 0%; background: #ff00de;"></div></div>
            </div>
            <div style="padding: 15px; border-left: 4px solid #00f3ff; background: rgba(0,243,255,0.05); border-radius: 10px;">
                <small style="color: #00f3ff; font-weight: bold;">DECK B</small>
                <div id="nameB" style="color: #fff; font-size: 12px; margin: 5px 0; overflow: hidden;">ยังไม่ได้เลือกเพลง...</div>
                <input type="file" id="inB" accept="audio/*" style="display:none" onchange="loadB(this.files[0])">
                <button onclick="document.getElementById('inB').click()" style="background: #00f3ff; color: black; border: none; padding: 5px 10px; border-radius: 5px; font-size: 10px; cursor: pointer;">SELECT B</button>
                <div style="height: 4px; background: #222; margin-top: 10px; border-radius: 2px;"><div id="barB" style="height: 100%; width: 0%; background: #00f3ff;"></div></div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr; gap: 10px; margin-top: 20px;">
            <button onclick="playAll()" style="width: 100%; padding: 12px; background: none; border: 2px solid #ff0055; color: #ff0055; font-weight: bold; border-radius: 15px; cursor: pointer;">⚡ START MIX</button>
            <button onclick="fade()" style="width: 100%; padding: 12px; background: none; border: 2px solid #00ffcc; color: #00ffcc; font-weight: bold; border-radius: 15px; cursor: pointer; margin-top: 10px;">🔄 CROSSFADE (5s)</button>
        </div>
    </div>
    <script>
        let ctx, ana, sA, sB, gA, gB, isP = false, cur = 'A', data;
        function init() {{ if(!ctx) {{ ctx = new (window.AudioContext || window.webkitAudioContext)(); ana = ctx.createAnalyser(); ana.fftSize = 128; data = new Uint8Array(ana.frequencyBinCount); loop(); }} }}
        function loop() {{
            requestAnimationFrame(loop); if(!ana) return; ana.getByteFrequencyData(data);
            const can = document.getElementById('v-main'); const c = can.getContext('2d');
            c.fillStyle = 'rgba(0,0,0,0.2)'; c.fillRect(0,0,can.width,can.height);
            let x = 0; let w = (can.width/data.length)*2;
            for(let i=0; i<data.length; i++) {{
                let h = (data[i]/255)*can.height;
                c.fillStyle = 'hsl('+(180+i*5)+', 100%, 50%)';
                c.fillRect(x, can.height-h, w-1, h); x += w;
            }}
            updateProgress();
        }}
        async function loadA(f) {{ init(); document.getElementById('nameA').innerText = f.name; sA = await ctx.decodeAudioData(await f.arrayBuffer()); }}
        async function loadB(f) {{ init(); document.getElementById('nameB').innerText = f.name; sB = await ctx.decodeAudioData(await f.arrayBuffer()); }}
        function playAll() {{
            if(!sA || !sB || isP) return;
            srcA = ctx.createBufferSource(); srcA.buffer = sA; gA = ctx.createGain();
            srcA.connect(gA).connect(ana).connect(ctx.destination);
            srcB = ctx.createBufferSource(); srcB.buffer = sB; gB = ctx.createGain(); gB.gain.value = 0;
            srcB.connect(gB).connect(ana).connect(ctx.destination);
            srcA.start(0); srcB.start(0); isP = true;
        }}
        function fade() {{
            let now = ctx.currentTime;
            if(cur === 'A') {{ gA.gain.linearRampToValueAtTime(0, now+5); gB.gain.linearRampToValueAtTime(1, now+5); cur = 'B'; }}
            else {{ gB.gain.linearRampToValueAtTime(0, now+5); gA.gain.linearRampToValueAtTime(1, now+5); cur = 'A'; }}
        }}
        function updateProgress() {{
             if(isP) {{
                document.getElementById('barA').style.width = cur === 'A' ? '100%' : '0%';
                document.getElementById('barB').style.width = cur === 'B' ? '100%' : '0%';
             }}
        }}
    </script>
    """
    components.html(mixer_html, height=520)

    st.write("---")
    st.markdown("<h4 style='color:#00f3ff; font-family:Orbitron; text-align:center;'>📂 GLOBAL DATABASE</h4>", unsafe_allow_html=True)
    all_songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if all_songs:
        with st.expander("คลิกเพื่อเลือกเล่นเพลงในคลัง (52+ เพลง)"):
            for s in all_songs:
                if st.button(f"🎵 {s}", use_container_width=True):
                    st.audio(s)
    
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Studio v.1")

# =========================================================
# ห้องที่ 2: CHAT SYSTEM, PRIVATE CHAT & WALKIE-TALKIE + RADAR MAP
# =========================================================
elif st.session_state.page == "2":
    st_autorefresh(interval=6000, key="synapse_update")
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🛰️ TACTICAL RADAR & CHAT HUB</h2>", unsafe_allow_html=True)

    # แผนที่เรดาร์พิกัดดาวเทียม
    import folium
    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr='Google Satellite')
    
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)

    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], 
                                 icon=folium.Icon(color='blue'), 
                                 tooltip=f"AGENT: {uid}").add_to(m)
    except: pass

    st_folium(m, width="100%", height=280)

    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        try:
            db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
            st.toast("พิกัดถูกส่งแล้ว!")
        except:
            st.error("ไม่สามารถส่งพิกัดได้ ตรวจสอบการเชื่อมต่อ Firebase")

    st.write("---")

    tab_global, tab_private, tab_voice = st.tabs(["👥 GLOBAL CHAT (แชตรวม)", "🔐 PRIVATE CHAT (แชตส่วนตัว)", "📻 WALKIE-TALKIE (ข้อความเสียง)"])

    # 1. แชตรวม
    with tab_global:
        with st.form("global_chat_form", clear_on_submit=True):
            g_msg = st.text_input("ส่งสัญญาณเข้าช่องแชตรวม:", placeholder="Agent ทุกคนจะเห็นข้อความนี้...")
            if st.form_submit_button("SEND TO ALL"):
                if g_msg:
                    try:
                        db.reference('global_messages').push({
                            'sender': st.session_state.user,
                            'text': g_msg,
                            'ts': time.time()
                        })
                        st.rerun()
                    except: st.error("ฐานข้อมูลขัดข้อง")

        try:
            g_messages = db.reference('global_messages').order_by_child('ts').limit_to_last(10).get()
            if g_messages:
                for mid in reversed(list(g_messages.keys())):
                    m_data = g_messages[mid]
                    is_me = m_data['sender'] == st.session_state.user
                    align = "right" if is_me else "left"
                    color = "#00f3ff" if is_me else "#50C878"
                    bg = "rgba(0, 243, 255, 0.1)" if is_me else "rgba(80, 200, 120, 0.1)"
                    st.markdown(f'<div style="text-align:{align}; margin-bottom:10px;"><div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:15px; border:1px solid {color};"><b>{m_data["sender"]}</b><br>{m_data["text"]}</div></div>', unsafe_allow_html=True)
        except: pass

    # 2. แชตส่วนตัว
    with tab_private:
        try:
            all_users = db.reference('users').get()
            if all_users:
                friends = [u for u in all_users.keys() if u != st.session_state.user]
                target_agent = st.selectbox("🎯 เลือก AGENT ลับเป้าหมาย:", friends)

                if target_agent:
                    room_id = "_".join(sorted([st.session_state.user, target_agent]))
                    chat_ref = db.reference(f'private_messages/{room_id}')

                    with st.form("private_chat_form", clear_on_submit=True):
                        msg = st.text_input(f"TO: {target_agent}", placeholder="พิมพ์ข้อความลับที่นี่...")
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
                            st.markdown(f'<div style="text-align:{align}; margin-bottom:10px;"><div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:15px; border:1px solid {color};"><b>{m_data["sender"]}</b><br>{m_data["text"]}</div></div>', unsafe_allow_html=True)
            else: st.caption("ยังไม่มีข้อมูล Agent คนอื่นในระบบ")
        except: pass

    # 3. ข้อความเสียง Walkie-Talkie
    with tab_voice:
        st.markdown("### 📻 บันทึกสัญญาณคลิปเสียงจริงผ่านมือถือ")
        audio_recorder_html = """
        <div style="background:#111; padding:15px; border-radius:15px; border:1px solid #ff00de; text-align:center;">
            <button id="recordBtn" style="background:#ff00de; color:white; border:none; padding:10px 20px; border-radius:10px; font-weight:bold; cursor:pointer;">🎤 กดเพื่อพูด (RECORD)</button>
            <button id="stopBtn" style="background:#333; color:#ccc; border:none; padding:10px 20px; border-radius:10px; font-weight:bold; cursor:pointer; margin-left:10px;" disabled>🛑 หยุด (STOP)</button>
            <p id="audioStatus" style="color:#aaa; font-size:12px; margin-top:10px;">สถานะ: สแตนด์บายไมโครโฟน</p>
            <audio id="audioPlayback" controls style="display:none; margin:10px auto; width:100%;"></audio>
        </div>
        <script>
            let mediaRecorder; let audioChunks = [];
            const recordBtn = document.getElementById('recordBtn'); const stopBtn = document.getElementById('stopBtn');
            const status = document.getElementById('audioStatus'); const playback = document.getElementById('audioPlayback');

            recordBtn.onclick = async () => {
                audioChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                    playback.src = URL.createObjectURL(audioBlob); playback.style.display = 'block';
                    let reader = new FileReader(); reader.readAsDataURL(audioBlob);
                    reader.onloadend = function() {
                        let base64String = reader.result.split(',')[1];
                        status.innerHTML = "✨ สำเร็จ! คัดลอกรหัสคอมพิวเตอร์ด้านล่างนี้ไปวางในกล่องส่งสัญญาณ:";
                        let t = document.createElement("textarea"); t.value = base64String;
                        t.style.width = "100%"; t.style.height="60px"; t.style.background="#222"; t.style.color="#00f3ff";
                        status.appendChild(t);
                    }
                };
                mediaRecorder.start(); recordBtn.disabled = true; stopBtn.disabled = false;
                status.innerText = "🔴 ระบบกำลังจำรอยคลื่นเสียงของคุณ... พูดได้เลย";
            };
            stopBtn.onclick = () => { mediaRecorder.stop(); recordBtn.disabled = false; stopBtn.disabled = true; };
        </script>
        """
        components.html(audio_recorder_html, height=220)
        
        v_target = st.selectbox("🎯 เลือกผู้รับคลื่นเสียง:", ["ทุกคน (GLOBAL)"] + (friends if 'friends' in locals() else []))
        voice_b64 = st.text_area("📦 วางโค้ดรหัสคลื่นเสียงที่คัดลอกมาด้านบน:")
        
        if st.button("📡 อัดสัญญาณเสียงขึ้นคลาณด์", use_container_width=True):
            if voice_b64:
                try:
                    db.reference('voice_transmission').push({
                        'sender': st.session_state.user, 'target': v_target, 'audio_data': voice_b64, 'ts': time.time()
                    })
                    st.success("ปล่อยคลื่นเสียงออกอากาศแล้ว!")
                    time.sleep(1)
                    st.rerun()
                except: st.error("อัปโหลดล้มเหลว")

        st.write("---")
        st.markdown("#### 📻 รายการคลื่นเสียงที่รับสัญญาณได้")
        try:
            v_logs = db.reference('voice_transmission').order_by_child('ts').limit_to_last(5).get()
            if v_logs:
                for k, v in reversed(list(v_logs.items())):
                    if v['target'] == "ทุกคน (GLOBAL)" or v['target'] == st.session_state.user or v['sender'] == st.session_state.user:
                        st.markdown(f"📻 **ส่งโดย:** {v['sender']} ➡️ **ถึง:** {v['target']}")
                        try:
                            audio_bytes = base64.b64decode(v['audio_data'])
                            st.audio(audio_bytes, format="audio/mp3")
                        except: pass
                        st.divider()
        except: pass

# =========================================================
# ห้องที่ 3: IMAGE SEARCH
# =========================================================
elif st.session_state.page == "3":
    st.markdown("<h2 style='color:#00ff41; font-family:Orbitron;'>🖼️ SATELLITE & IMAGE SEARCH</h2>", unsafe_allow_html=True)
    search_query = st.text_input("ป้อนคำค้นหารูปภาพที่ต้องการ (ภาษาอังกฤษ):", "Satellite")
    if search_query:
        st.write(f"ดึงรูปภาพจำลองสถานการณ์สำหรับ: **{search_query}**")
        st.image(f"https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=800", caption="คลังภาพ Unsplash")

# =========================================================
# ห้องเสริม 3_neon: NEON GENERATOR
# =========================================================
elif st.session_state.page == "3_neon":
    st.markdown("<h2 style='color:#00ff41; font-family:Orbitron;'>✨ NEON GENERATOR</h2>", unsafe_allow_html=True)
    text_input = st.text_input("กรอกข้อความที่ต้องการทำแสงนีออน:", "SYNAPSE COMMAND")
    if text_input:
        st.markdown(f"""
            <h1 style='text-align:center; color:#fff; text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;'>
                {text_input}
            </h1>
        """, unsafe_allow_html=True)

# =========================================================
# ห้องที่ 4: VIDEO HUB
# =========================================================
elif st.session_state.page == "4_video":
    st.markdown("<h2 style='color:#00ff41; font-family:Orbitron;'>🎬 VIDEO HUB & CCTV</h2>", unsafe_allow_html=True)
    v_url = st.text_input("วางลิงก์วิดีโอ YouTube หรือไฟล์ตรง:", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    if v_url:
        st.video(v_url)

# =========================================================
# ห้องที่ 6: WORLD CLOCK & SENSORS
# =========================================================
elif st.session_state.page == "6_clock":
    st.markdown("<h2 style='text-align:center; color:#FFD700; font-family:Orbitron;'>⚡ SYNAPSE SENSOR & CLOCK UNIT</h2>", unsafe_allow_html=True)
    
    tab_sonic, tab_motion, tab_bio, tab_power = st.tabs(["🎙️ SONIC SCAN", "📳 MOTION SCAN", "🩸 BIO-SCAN", "🔋 POWER INFO"])

    with tab_sonic:
        st.subheader("🎙️ REAL-TIME SONIC ANALYZER")
        audio_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <div style="display: flex; justify-content: space-around;">
                <div><small>ความดัง</small><h1 id="db_val" style="font-size: 40px; color:#0f0;">0</h1><small>เดซิเบล (dB)</small></div>
                <div><small>ความถี่</small><h1 id="hz_val" style="font-size: 40px; color:#00ffff;">0</h1><small>เฮิรตซ์ (Hz)</small></div>
            </div>
            <p id="audio_status" style="margin-top:10px; color:#888;">🔴 รอสัญญาณเสียง...</p>
        </div>
        <script>
            async function startAudio() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const analyser = audioCtx.createAnalyser();
                    const source = audioCtx.createMediaStreamSource(stream);
                    source.connect(analyser); analyser.fftSize = 2048;
                    const dataArray = new Uint8Array(analyser.frequencyBinCount);
                    function update() {
                        analyser.getByteFrequencyData(dataArray);
                        let sum = 0, maxVal = 0, maxIdx = 0;
                        for (let i = 0; i < dataArray.length; i++) {
                            sum += dataArray[i];
                            if (dataArray[i] > maxVal) { maxVal = dataArray[i]; maxIdx = i; }
                        }
                        let db = Math.round(sum / dataArray.length * 2);
                        let hz = Math.round(maxIdx * audioCtx.sampleRate / analyser.fftSize);
                        document.getElementById('db_val').innerText = db;
                        document.getElementById('hz_val').innerText = hz;
                        document.getElementById('audio_status').innerText = "🟢 ตรวจจับคลื่นเสียงจริง";
                        requestAnimationFrame(update);
                    }
                    update();
                } catch (e) { document.getElementById('audio_status').innerText = "❌ เข้าถึงไมค์ไม่ได้"; }
            }
            startAudio();
        </script>
        """
        components.html(audio_js, height=250)
        st.info("**ที่มาของตัวเลข (The Truth):** ค่าความถี่ (Hz) วัดจากรอบการสั่นของอากาศที่กระทบไมค์จริง ไม่มีการจำลอง")

    with tab_motion:
        st.subheader("📳 MOTION & VIBRATION SENSOR")
        motion_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <small>แรงสั่นสะเทือนรวม (Magnitude)</small>
            <h1 id="mag_val" style="font-size: 50px; color: #0f0;">1.000</h1>
            <p>G-Force</p>
            <p id="motion_info" style="color: #888;">สถานะ: รอนิ่ง...</p>
        </div>
        <script>
            window.addEventListener('devicemotion', (e) => {
                const acc = e.accelerationIncludingGravity;
                if (!acc) return;
                let magnitude = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.80665;
                document.getElementById('mag_val').innerText = magnitude.toFixed(3);
                document.getElementById('mag_val').style.color = (magnitude > 1.05 || magnitude < 0.95) ? "#f00" : "#0f0";
            });
        </script>
        """
        components.html(motion_js, height=250)
        st.info("**ที่มาของตัวเลข (The Truth):** วัดจากเซนเซอร์ Accelerometer ภายในเครื่อง ยึดตามแรงโน้มถ่วงโลก (1G) เป็นเกณฑ์")

    with tab_bio:
        st.markdown("### 🩸 REAL-TIME BIO-DATA SCANNER")
        bio_js = """
        <div style="background-color: #111; color: #FFD700; padding: 15px; border: 2px solid #FFD700; border-radius: 15px; font-family: monospace;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                <div style="border: 1px solid #333; padding: 10px;">
                    <small>BPM</small><h2 id="bpm" style="color:#0f0;">72</h2><small>ครั้ง/นาที</small>
                </div>
                <div style="border: 1px solid #333; padding: 10px;">
                    <small>SpO2</small><h2 id="spo2" style="color:#00ffff;">98</h2><small>%</small>
                </div>
            </div>
            <div id="status" style="margin-top: 10px; text-align: center; color: #0f0;">🟢 ระบบโมดูลสแกนเนอร์สแตนด์บาย</div>
        </div>
        """
        components.html(bio_js, height=180)

    with tab_power:
        st.write("⏱️ เวลาปัจจุบันรอบโลก:")
        st.write(f"เวลาเครื่องเซิร์ฟเวอร์: {datetime.now().strftime('%H:%M:%S')}")

# =========================================================
# ห้องที่ 7: DESTINY CHECK (ดวงมิติควอนตัม)
# =========================================================
elif st.session_state.page == "7":
    st.markdown("<h2 style='text-align:center; color:#ff00de; font-family:Orbitron;'>💖 DESTINY CHECK (DIMENSION 4)</h2>", unsafe_allow_html=True)
    st.write("วิเคราะห์ความสัมพันธ์ผ่านระบบผลรวมรหัสตัวอักษร (Unicode Hash)")

    col1, col2 = st.columns(2)
    with col1: name1 = st.text_input("ชื่อ AGENT 1:", placeholder="ระบุชื่อคนที่ 1")
    with col2: name2 = st.text_input("ชื่อ AGENT 2:", placeholder="ระบุชื่อคนที่ 2")

    if st.button("⚡ เดินเครื่องสแกนความถี่", use_container_width=True):
        if name1 and name2:
            score1 = sum(ord(char) for char in name1)
            score2 = sum(ord(char) for char in name2)
            gap = abs(score1 - score2)
            match_percent = 100 - (gap % 100)
            
            st.divider()
            st.metric("ระดับความสอดคล้องของคลื่นความถี่ (Synchronization)", f"{match_percent} %")
        else:
            st.warning("กรุณาระบุชื่อเป้าหมายทั้งสองให้ครบถ้วน")

# =========================================================
# ห้องที่ 8: DAILY CODE
# =========================================================
elif st.session_state.page == "8":
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🔢 DAILY SECURITY CODE</h2>", unsafe_allow_html=True)
    today_str = date.today().strftime("%Y-%m-%d")
    current_agent = st.session_state.get('user', 'Guest_Agent')
    raw_data = f"{today_str}_{current_agent}_SYNAPSE"
    
    try:
        hash_object = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        daily_4_digit = str(int(hash_object[:4], 16))[-4:].zfill(4)
        daily_6_digit = str(int(hash_object[4:10], 16))[-6:].zfill(6)
        
        col1, col2 = st.columns(2)
        with col1: st.markdown(f'<div style="text-align:center; border:2px solid #00f3ff; padding:20px; border-radius:15px;">PIN: <h1>{daily_4_digit}</h1></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div style="text-align:center; border:2px solid #ff00de; padding:20px; border-radius:15px;">KEY: <h1>{daily_6_digit}</h1></div>', unsafe_allow_html=True)
    except: pass

# =========================================================
# ห้องที่ 9: SYSTEM LOG
# =========================================================
elif st.session_state.page == "9":
    st.markdown("<h2 style='text-align:center; color:#50C878; font-family:Orbitron;'>📝 SYNAPSE MEMORY LOG</h2>", unsafe_allow_html=True)
    with st.form("log_form", clear_on_submit=True):
        log_entry = st.text_area("✍️ ข้อความบันทึก:")
        if st.form_submit_button("💾 SAVE TO CLOUD") and log_entry:
            try:
                db.reference(f'system_logs/{st.session_state.user}').push({
                    'text': log_entry, 'timestamp': time.time(), 'datetime': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                })
                st.success("บันทึกเรียบร้อย!")
            except: pass

# =========================================================
# ห้องที่ 10: COLOR MASTER
# =========================================================
elif st.session_state.page == "10":
    st.markdown("<h2 style='text-align:center; color:#FFD700; font-family:Orbitron;'>🎨 COLOR MASTER UI</h2>", unsafe_allow_html=True)
    new_color = st.color_picker("เลือกโค้ดสีระบบ:", st.session_state.custom_theme)
    if st.button("🔥 อัปเดตสีระบบ", use_container_width=True):
        st.session_state.custom_theme = new_color
        st.rerun()
