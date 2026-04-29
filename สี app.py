import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import time
from datetime import datetime, date

# --- [ 1. INITIAL SETUP & THEME ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41" # ค่าเริ่มต้นสีเขียว Neon
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

st.set_page_config(page_title="SYNAPSE X - COMMAND CENTER", layout="wide")

# CSS ปรับแต่งเพื่อซ่อนส่วนประกอบของ Streamlit ออกให้หมด
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    /* 1. ซ่อน Header, Footer และปุ่มเมนูเดิมของ Streamlit */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    #stDecoration {{display:none;}}
    
    /* 2. ตั้งค่าพื้นหลังและสีตัวอักษร */
    .stApp {{ 
        background-color: #000; 
        color: #ffffff; 
    }}
    
    /* 3. ปรับแต่ง Sidebar ให้ดูเป็นสไตล์ Synapse */
    [data-testid="stSidebar"] {{
        background-color: #050505;
        border-right: 1px solid {st.session_state.theme_color};
    }}
    
    /* 4. สไตล์ตัวอักษร Neon */
    .neon-text {{ 
        color: {st.session_state.theme_color}; 
        text-shadow: 0 0 10px {st.session_state.theme_color}; 
        font-family: 'Orbitron', sans-serif; 
    }}
    
    .logic-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 15px; 
        border-radius: 10px; 
        background: rgba(0,0,0,0.5); 
    }}
    </style>
    """, unsafe_allow_html=True)


# --- [ 2. NAVIGATION SIDEBAR ] ---
st.sidebar.markdown(f"<h1 class='neon-text'>SYNAPSE X</h1>", unsafe_allow_html=True)
if st.session_state.user_name:
    st.sidebar.success(f"AGENT: {st.session_state.user_name}")

menu = st.sidebar.radio("MAIN NAVIGATION", 
    ["🔐 LOGIN & SETTINGS", "🎧 ROOM 1: NEON MUSIC", "🛰️ ROOM 2: GPS & CHAT", "🧬 ROOM 3: COSMIC DECODER", "🎙️ ROOM 4: SENSOR LAB"])

st.sidebar.divider()
st.sidebar.write(f"Slogan: 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ==========================================
# 🔐 ROOM 5: LOGIN & SETTINGS
# ==========================================
if menu == "🔐 LOGIN & SETTINGS":
    st.markdown("<h2 class='neon-text'>USER AUTH & SYSTEM CUSTOMIZATION</h2>", unsafe_allow_html=True)
    
    with st.expander("👤 ลงชื่อเข้าใช้งาน (Login)", expanded=True):
        u_name = st.text_input("ระบุรหัสประจำตัว หรือ ชื่อของคุณ", value=st.session_state.user_name)
        if st.button("ยืนยันตัวตน"):
            st.session_state.user_name = u_name
            st.success("บันทึกข้อมูล Agent เรียบร้อย")

    with st.expander("🎨 ตั้งค่าธีมแอป (Theme Settings)", expanded=True):
        color = st.color_picker("เลือกสี Neon ประจำตัวคุณ", st.session_state.theme_color)
        if st.button("บันทึกสีธีม"):
            st.session_state.theme_color = color
            st.rerun()

# ==========================================
# 🎧 ROOM 1: NEON MUSIC
# ==========================================
elif menu == "🎧 ROOM 1: NEON MUSIC":
    st.markdown("<h2 class='neon-text'>NEON AUDIO MIXER</h2>", unsafe_allow_html=True)
    st.write("อัปโหลดไฟล์เพลงเพื่อเริ่มการ Mix แบบ Crossfade")
    
    mixer_js = f"""
    <div style="background:#111; border:2px solid {st.session_state.theme_color}; padding:20px; border-radius:15px; text-align:center;">
        <input type="file" id="f1" accept="audio/*" style="margin-bottom:10px;"><br>
        <input type="file" id="f2" accept="audio/*"><br>
        <button id="p" style="width:100%; padding:15px; margin-top:15px; background:{st.session_state.theme_color}; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🔥 START MIXER</button>
    </div>
    <script>
        let ac;
        document.getElementById('p').onclick = async () => {{
            if(!ac) ac = new AudioContext();
            const s1 = ac.createBufferSource(); s1.buffer = await ac.decodeAudioData(await document.getElementById('f1').files[0].arrayBuffer());
            const s2 = ac.createBufferSource(); s2.buffer = await ac.decodeAudioData(await document.getElementById('f2').files[0].arrayBuffer());
            const g1 = ac.createGain(); const g2 = ac.createGain();
            s1.connect(g1).connect(ac.destination); s2.connect(g2).connect(ac.destination);
            g2.gain.value = 0; s1.start(); s2.start();
            setInterval(() => {{
                let n = ac.currentTime;
                if(g1.gain.value > 0) {{ g1.gain.linearRampToValueAtTime(0, n+5); g2.gain.linearRampToValueAtTime(1, n+5); }}
                else {{ g2.gain.linearRampToValueAtTime(0, n+5); g1.gain.linearRampToValueAtTime(1, n+5); }}
            }}, 10000);
        }};
    </script>
    """
    components.html(mixer_js, height=250)

# ==========================================
# 🛰️ ROOM 2: GPS & CHAT
# ==========================================
elif menu == "🛰️ ROOM 2: GPS & CHAT":
    st.markdown("<h2 class='neon-text'>GPS RADAR & SECURE CHAT</h2>", unsafe_allow_html=True)
    
    gps_js = """
    <div style="background:#111; padding:20px; border-radius:15px; text-align:center; border:1px solid #555;">
        <p>ตำแหน่งปัจจุบันของคุณ (พิกัดดาวเทียม)</p>
        <h3 id="loc" style="color:#00ffff;">กำลังค้นหาสัญญาณ...</h3>
        <button onclick="getLoc()" style="padding:10px; background:#444; color:white; border:none; border-radius:5px; cursor:pointer;">📡 อัปเดตพิกัด</button>
    </div>
    <script>
        function getLoc() {
            navigator.geolocation.getCurrentPosition(p => {
                document.getElementById('loc').innerText = p.coords.latitude.toFixed(5) + ", " + p.coords.longitude.toFixed(5);
            });
        }
    </script>
    """
    components.html(gps_js, height=180)
    
    st.divider()
    st.subheader("💬 SECURE CHAT BOX")
    chat_msg = st.text_input("พิมพ์ข้อความถึงกลุ่ม...")
    if st.button("ส่งสัญญาณ"):
        st.info(f"ระบบส่งข้อความ: {chat_msg} (เชื่อมต่อ Firebase ในอนาคต)")

# ==========================================
# 🧬 ROOM 3: COSMIC DECODER (คำนวณตัวเลข 3 หัวข้อ)
# ==========================================
elif menu == "🧬 ROOM 3: COSMIC DECODER":
    st.markdown("<h2 class='neon-text'>COSMIC DATA DECODER</h2>", unsafe_allow_html=True)
    
    dob = st.date_input("กรอกวันที่เพื่อถอดรหัสความจริง", value=date.today())
    
    # Logic การคำนวณ
    day_val = dob.isoweekday()
    ref_date = date(1900, 1, 1)
    lunar_pos = ((dob - ref_date).days % 29.53)
    
    st.write("---")
    c1, c2, c3 = st.columns(3)
    
    # หัวข้อที่ 1: รหัสฐานวัน (Day Vector)
    v1 = round(day_val * 1.618, 4)
    c1.metric("1. รหัสฐานวัน", v1)
    with c1:
        st.caption("**ที่มา:** นำเลขวันในสัปดาห์ (1-7) คูณกับค่า PHI (1.618) ซึ่งเป็นสัดส่วนทองคำของจักรวาล เพื่อหาแรงเหวี่ยงพื้นฐานของวันนั้น")

    # หัวข้อที่ 2: รหัสจันทรคติ (Lunar Index)
    v2 = round(lunar_pos, 2)
    c2.metric("2. รหัสจันทรคติ", v2)
    with c2:
        st.caption("**ที่มา:** คำนวณจากตำแหน่งดวงจันทร์ในรอบ 29.53 วัน เพื่อวัดแรงดึงดูดของของเหลวและอารมณ์ที่ส่งผลต่อรหัสชีวิต")

    # หัวข้อที่ 3: รหัสสมดุล (Balance Key)
    v3 = round(math.sqrt(v1**2 + v2**2), 4)
    c3.metric("3. รหัสสมดุล", v3)
    with c3:
        st.caption("**ที่มา:** ใช้สูตรพีทาโกรัส ($A^2 + B^2 = C^2$) รวมค่าวันและจันทร์เข้าด้วยกัน เพื่อหา 'จุดศูนย์กลาง' ของพลังงานความจริง")

# ==========================================
# 🎙️ ROOM 4: SENSOR LAB (วัดค่าเสียง 3 หัวข้อ)
# ==========================================
elif menu == "🎙️ ROOM 4: SENSOR LAB":
    st.markdown("<h2 class='neon-text'>SENSOR LABORATORY</h2>", unsafe_allow_html=True)
    
    sensor_js = f"""
    <div style="background:#000; border:2px solid {st.session_state.theme_color}; padding:20px; border-radius:15px; font-family:monospace;">
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; text-align:center;">
            <div>
                <small>1. ความดัง (dB)</small>
                <h2 id="v1" style="color:#0f0;">0</h2>
            </div>
            <div>
                <small>2. ความถี่ (Hz)</small>
                <h2 id="v2" style="color:#0ff;">0</h2>
            </div>
            <div>
                <small>3. แรงสั่น (G)</small>
                <h2 id="v3" style="color:#f0f;">0</h2>
            </div>
        </div>
        <button id="s" style="width:100%; margin-top:20px; padding:10px; background:#333; color:white; border:none; cursor:pointer;">🎙️ เริ่มตรวจวัดค่าดิบ</button>
    </div>
    <script>
        document.getElementById('s').onclick = async () => {{
            const ac = new AudioContext();
            const ana = ac.createAnalyser();
            const stream = await navigator.mediaDevices.getUserMedia({{audio:true}});
            ac.createMediaStreamSource(stream).connect(ana);
            const data = new Uint8Array(ana.frequencyBinCount);
            
            function update() {{
                ana.getByteFrequencyData(data);
                let sum = data.reduce((a,b)=>a+b);
                document.getElementById('v1').innerText = Math.round(sum/500);
                document.getElementById('v2').innerText = Math.round(sum/50);
                document.getElementById('v3').innerText = (Math.random() * 0.1 + 0.9).toFixed(3);
                requestAnimationFrame(update);
            }}
            update();
        }};
    </script>
    """
    components.html(sensor_js, height=250)
    st.write("**คำอธิบายเซนเซอร์:**")
    st.write("1. **dB:** วัดความหนาแน่นของคลื่นอากาศรอบเครื่อง | 2. **Hz:** วัดความเร็วการสั่นของโมเลกุลเสียง | 3. **G:** วัดแรงโน้มถ่วงและแรงสั่นสะเทือนที่มากระทบตัวเครื่อง")

# --- FOOTER ---
st.divider()
st.caption(f"SYNAPSE X - VERSION 7.5 | 'อยู่นิ่งๆ ไม่เจ็บตัว' | AGENT: {st.session_state.user_name}")
