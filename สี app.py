import streamlit as st
import os
import pandas as pd
import math
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# =================================================================
# 1. INITIAL SYSTEM SETUP (การตั้งค่าระบบหลัก)
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE HUB", layout="wide", initial_sidebar_state="expanded")

def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- SESSION STATE MANAGEMENT ---
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "Unknown"

# =================================================================
# 2. CORE LOGIC FUNCTIONS (หัวใจการคำนวณ)
# =================================================================
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

# =================================================================
# 3. GLOBAL CSS & LOGO (คุมโทนสีทุกห้อง)
# =================================================================
logo_b64 = get_base64_data("logo1.png")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    :root {{ --primary: {st.session_state.main_color}; --secondary: {st.session_state.sub_color}; }}
    .stApp {{ background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }}
    header, footer, #MainMenu {{visibility: hidden;}}
    
    .global-logo {{
        position: fixed; top: 15px; right: 25px; width: 65px; z-index: 10000;
        filter: drop-shadow(0 0 10px var(--primary));
        animation: pulse 2s infinite alternate;
    }}
    @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}
    
    .neon-text {{ color: var(--primary); text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary); text-align: center; }}
    .stButton>button {{
        border-radius: 12px; border: 1px solid var(--primary);
        background: rgba(0,0,0,0.3); color: #fff; transition: 0.3s;
    }}
    .stButton>button:hover {{ background: var(--primary); box-shadow: 0 0 20px var(--primary); color: #000; }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)

# =================================================================
# 4. SIDEBAR CONTROL (เพลงต่อเนื่องและธีม)
# =================================================================
with st.sidebar:
    st.markdown("<h2 class='neon-text'>AGENT CONTROL</h2>", unsafe_allow_html=True)
    all_mp3 = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    st.markdown("### 📻 GLOBAL AUDIO")
    selected_bg = st.selectbox("Background Music (Non-Stop)", ["OFF"] + all_mp3)
    if selected_bg != "OFF":
        bg_data = get_base64_data(selected_bg)
        st.markdown(f"""
            <audio id="bgPlayer" autoplay loop controls style="width: 100%; height: 35px;">
                <source src="data:audio/mp3;base64,{bg_data}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("🎨 THEME COLORS"):
        st.session_state.main_color = st.color_picker("Primary Neon", st.session_state.main_color)
        st.session_state.sub_color = st.color_picker("Secondary Neon", st.session_state.sub_color)
    
    if st.session_state.logged_in:
        st.markdown(f"**Agent:** {st.session_state.user}")
        if st.button("TERMINATE SESSION"):
            st.session_state.logged_in = False
            st.rerun()

# =================================================================
# 5. LOGIN / REGISTER SECTION
# =================================================================
if not st.session_state.logged_in:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("<br><br><h1 class='neon-text'>INITIALIZE AGENT</h1>", unsafe_allow_html=True)
        new_agent = st.text_input("NAME:", placeholder="ENTER CODE NAME").strip()
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_agent:
                st.session_state.user = new_agent
                st.session_state.logged_in = True
                st.session_state.page = "HOME"
                st.rerun()
    st.stop()

# =================================================================
# 6. MAIN NAVIGATION CONTENT
# =================================================================
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"; st.rerun()

# --- [ PAGE: HOME HUB ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. DJ STATION (512Hz)", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🛰️ 2. TACTICAL RADAR", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🧬 3. LUNAR DECODER", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("🛰️ 4. PARALLEL SCANNER", use_container_width=True): st.session_state.page = "4"; st.rerun()
        if st.button("🔮 5. DESTINY TIMELINE", use_container_width=True): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("📳 6. VIBRATION SENSOR", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("💖 7. DESTINY CHECK", use_container_width=True): st.session_state.page = "7"; st.rerun()
        if st.button("🔢 8. DAILY CODE", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("📝 9. MEMORY LOG", use_container_width=True): st.session_state.page = "9"; st.rerun()
        if st.button("🎨 10. COLOR MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ PAGE 1: DJ STATION ] ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 DUAL DECK DJ UNIT</h2>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA: sA = st.selectbox("DECK A", ["--"] + all_mp3, key="sa")
    with colB: sB = st.selectbox("DECK B", ["--"] + all_mp3, key="sb")
    
    bA, bB = get_base64_data(sA), get_base64_data(sB)
    mixer_html = f"""
    <div style="background:#000; border:2px solid #333; padding:20px; border-radius:20px;">
        <marquee style="color:var(--primary);">DJ AGENT: {st.session_state.user} | NOW MIXING: {sA} & {sB}</marquee>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
            <div style="border:1px solid var(--primary); padding:10px; border-radius:15px; text-align:center;">
                <canvas id="cA" style="width:100%; height:80px; background:#111;"></canvas>
                <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--primary);"><span id="cA_t">00:00</span><span id="rA_t">-00:00</span></div>
                <button onclick="pD('A')" style="background:var(--primary); border:none; padding:10px; width:100%; margin-top:10px;">PLAY A</button>
            </div>
            <div style="border:1px solid var(--secondary); padding:10px; border-radius:15px; text-align:center;">
                <canvas id="cB" style="width:100%; height:80px; background:#111;"></canvas>
                <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--secondary);"><span id="cB_t">00:00</span><span id="rB_t">-00:00</span></div>
                <button onclick="pD('B')" style="background:var(--secondary); border:none; padding:10px; width:100%; margin-top:10px; color:white;">PLAY B</button>
            </div>
        </div>
        <audio id="audA" src="data:audio/mp3;base64,{bA}"></audio>
        <audio id="audB" src="data:audio/mp3;base64,{bB}"></audio>
        <script>
            let ctx = null;
            function v(a, cI, color) {{
                if(!ctx) ctx = new AudioContext();
                const src = ctx.createMediaElementSource(a);
                const ana = ctx.createAnalyser();
                ana.fftSize = 512;
                src.connect(ana); ana.connect(ctx.destination);
                const can = document.getElementById(cI);
                const cc = can.getContext("2d");
                const buf = ana.frequencyBinCount;
                const dat = new Uint8Array(buf);
                function draw() {{
                    requestAnimationFrame(draw);
                    ana.getByteFrequencyData(dat);
                    cc.clearRect(0,0,can.width,can.height);
                    let bw = (can.width/buf)*2.5; let x=0;
                    for(let i=0; i<buf; i++) {{
                        let h = dat[i]/2; cc.fillStyle = color;
                        cc.fillRect(x, can.height-h, bw, h); x += bw+1;
                    }}
                }} draw();
            }}
            let sA=false, sB=false;
            function pD(d) {{
                if(ctx && ctx.state==='suspended') ctx.resume();
                if(d==='A') {{ if(!sA){{v(document.getElementById('audA'),'cA','{st.session_state.main_color}');sA=true;}} document.getElementById('audA').play(); }}
                else {{ if(!sB){{v(document.getElementById('audB'),'cB','{st.session_state.sub_color}');sB=true;}} document.getElementById('audB').play(); }}
            }}
        </script>
    </div>
    """
    components.html(mixer_html, height=450)

# --- [ PAGE 2: RADAR & CHAT ] ---
elif st.session_state.page == "2":
    st_autorefresh(interval=10000, key="radar_up")
    st.markdown("<h2 class='neon-text'>🛰️ RADAR & SECURE CHAT</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    lat, lon = 13.7, 100.5
    if loc: lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    import folium
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}", attr="Google")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width="100%", height=300)

    st.markdown("---")
    msg = st.text_input("BROADCAST MESSAGE:")
    if st.button("SEND SIGNAL"): st.success("SIGNAL SENT TO CLOUD")

# --- [ PAGE 3: LUNAR DECODER ] ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🧬 LUNAR CODE DECODER</h2>", unsafe_allow_html=True)
    dob = st.date_input("SELECT DATE", value=date.today())
    if dob:
        d = get_detailed_logic(dob)
        st.metric("YOUR CODE", d['res'])
        st.write(f"พิกัด: {d['day_name']} | {d['phase']}")
        st.code(f"Formula: {d['formula']}")

# --- [ PAGE 5: DESTINY TIMELINE ] ---
elif st.session_state.page == "5":
    st.markdown("<h2 class='neon-text'>🔮 DESTINY SCANNER (180 DAYS)</h2>", unsafe_allow_html=True)
    user_dob = st.date_input("ENTER BIRTHDATE", key="dt5")
    if user_dob:
        my_code = get_detailed_logic(user_dob)['res']
        results = []
        for i in range(180):
            target = date.today() + timedelta(days=i)
            d = get_detailed_logic(target)
            gap = abs(d['res'] - my_code)
            status = "NORMAL"
            if gap < 0.5: status = "💎 DIAMOND"
            elif 3.8 <= gap <= 4.2: status = "🌀 DHARMA"
            elif gap > 10.0: status = "🪞 MIRROR"
            if status != "NORMAL":
                results.append({"Date": target, "Type": status, "Gap": round(gap,4)})
        st.table(pd.DataFrame(results))

# --- [ PAGE 8: DAILY CODE ] ---
elif st.session_state.page == "8":
    st.markdown("<h2 class='neon-text'>🔢 DAILY SECURITY KEY</h2>", unsafe_allow_html=True)
    today = date.today().strftime("%Y%m%d")
    raw = f"{today}_{st.session_state.user}_SYNAPSE"
    h = hashlib.sha256(raw.encode()).hexdigest()
    st.write(f"AGENT: {st.session_state.user}")
    st.code(f"PIN (4): {str(int(h[:4],16))[-4:]}")
    st.code(f"KEY (6): {str(int(h[4:10],16))[-6:]}")

# --- [ PAGE 10: COLOR MASTER ] ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 UI INTERFACE MASTER</h2>", unsafe_allow_html=True)
    st.session_state.main_color = st.color_picker("PRIMARY NEON", st.session_state.main_color)
    st.session_state.sub_color = st.color_picker("SECONDARY NEON", st.session_state.sub_color)
    if st.button("SAVE & RERUN"): st.rerun()

# =================================================================
# 7. FOOTER SYSTEM
# =================================================================
st.markdown("---")
st.caption(f"SYNAPSE ULTIMATE v.5.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
