import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
import time
import folium
from streamlit_folium import st_folium
from datetime import datetime, date

# --- [ 1. INITIAL SETUP ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state:
    st.session_state.user_name = "AGENT_X"
if 'current_page' not in st.session_state:
    st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS Style
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}}
    .stApp {{ background-color: #000; color: #ffffff; font-family: 'Orbitron', sans-serif; }}
    .neon-title {{ color: {st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color}; text-align: center; margin-bottom: 25px; }}
    div.stButton > button {{ background-color: #111; border: 2px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; border-radius: 15px; padding: 15px; font-weight: bold; }}
    div.stButton > button:hover {{ background-color: {st.session_state.theme_color}; color: black; box-shadow: 0 0 20px {st.session_state.theme_color}; }}
    </style>
    """, unsafe_allow_html=True)

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 2. INTERFACE LOGIC ] ---

if st.session_state.current_page == "MAIN MENU":
    st.markdown("<h1 class='neon-title'>SYNAPSE X</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 SETTINGS", use_container_width=True): go_to("SETTINGS")
        if st.button("🛰️ GPS & CHAT", use_container_width=True): go_to("GPS")
    with col2:
        if st.button("🎧 MUSIC", use_container_width=True): go_to("MUSIC")
        if st.button("🧬 DECODER", use_container_width=True): go_to("DECODER")
    if st.button("🎙️ SENSOR LAB", use_container_width=True): go_to("SENSOR")
    st.divider()
    st.caption(f"AGENT: {st.session_state.user_name} | 'อยู่นิ่งๆ ไม่เจ็บตัว'")

else:
    if st.button("⬅️ BACK TO MENU"):
        go_to("MAIN MENU")
    st.write("---")

    # --- PAGE: SETTINGS ---
    if st.session_state.current_page == "SETTINGS":
        st.markdown(f"<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
        if st.button("SAVE"): st.rerun()

    # --- PAGE: MUSIC (กราฟบน รายการล่าง) ---
    elif st.session_state.current_page == "MUSIC":
        st.markdown(f"<h2 class='neon-title'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        if not all_songs: st.error("No .mp3 files found.")
        else:
            s_a = st.session_state.get('sa', "-- Select --")
            s_b = st.session_state.get('sb', "-- Select --")
            def get_b64(f): return base64.b64encode(open(f, "rb").read()).decode() if f != "-- Select --" else ""
            d_a, d_b = get_b64(s_a), get_b64(s_b)
            
            mixer_html = f"""
            <div style="background:#000; border:2px solid {st.session_state.theme_color}; border-radius:20px; padding:15px;">
                <canvas id="v" style="width:100%; height:150px; background:#050505; border-radius:10px;"></canvas>
                <button onclick="play()" style="width:100%; margin-top:10px; padding:15px; background:linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border:none; border-radius:10px; color:white; font-weight:bold;">START MIX</button>
                <audio id="audA" src="data:audio/mp3;base64,{d_a}"></audio>
                <audio id="audB" src="data:audio/mp3;base64,{d_b}"></audio>
                <script>
                    const a=document.getElementById('audA'), b=document.getElementById('audB');
                    let ctx, ans, active='A';
                    function play() {{
                        if(!ctx) {{
                            ctx=new(window.AudioContext||window.webkitAudioContext)(); ans=ctx.createAnalyser();
                            const sA=ctx.createMediaElementSource(a), sB=ctx.createMediaElementSource(b);
                            const gA=ctx.createGain(), gB=ctx.createGain();
                            sA.connect(gA).connect(ans); sB.connect(gB).connect(ans); ans.connect(ctx.destination);
                            window.gs={{A:gA, B:gB}};
                        }}
                        a.play(); window.gs.A.gain.value=1; window.gs.B.gain.value=0; loop();
                    }}
                    function loop() {{
                        requestAnimationFrame(loop); const d=new Uint8Array(ans.frequencyBinCount); ans.getByteFrequencyData(d);
                        const c=document.getElementById('v').getContext('2d'); c.clearRect(0,0,300,150);
                        for(let i=0;i<d.length;i++) {{ c.fillStyle=`hsl(${{i*5}},100%,50%)`; c.fillRect(i*2, 150-(d[i]/2), 1, d[i]/2); }}
                        if(a.duration-a.currentTime<7 && b.paused) {{ b.play(); window.gs.A.gain.linearRampToValueAtTime(0, ctx.currentTime+6); window.gs.B.gain.linearRampToValueAtTime(1, ctx.currentTime+6); }}
                    }}
                </script>
            </div>"""
            components.html(mixer_html, height=250)
            c1, c2 = st.columns(2)
            with c1: st.selectbox("DECK A", ["-- Select --"] + all_songs, key="sa")
            with c2: st.selectbox("DECK B", ["-- Select --"] + all_songs, key="sb")
            if st.button("🔄 UPDATE"): st.rerun()

        # --- PAGE: GPS & CHAT (เวอร์ชันใช้ได้จริง) ---
    elif st.session_state.current_page == "GPS":
        st.markdown(f"<h2 class='neon-title'>🛰️ COMMAND CENTER</h2>", unsafe_allow_html=True)
        
        # 1. ส่วนดึงพิกัดจริงจาก Browser (JavaScript)
        # เราจะใช้ Component ตัวนี้เพื่อขออนุญาตเข้าถึง GPS ของมือถือคุณ
        from streamlit_js_eval import get_geolocation
        
        st.write("📡 **GPS STATUS:**")
        loc = get_geolocation() # ดึงค่าพิกัดจริงจากมือถือ
        
        if loc:
            my_lat = loc['coords']['latitude']
            my_lon = loc['coords']['longitude']
            st.success(f"พิกัดปัจจุบัน: {my_lat:.4f}, {my_lon:.4f}")
        else:
            my_lat, my_lon = 13.7367, 100.5231 # พิกัดสำรองถ้ายังไม่ได้กดอนุญาต
            st.warning("กรุณากด 'Allow' หรือ 'อนุญาต' ให้เข้าถึงพิกัดบนหน้าจอ")

        t1, t2, t3 = st.tabs(["📡 RADAR", "🌐 PUBLIC", "🔐 SECURE"])
        
        with t1: # RADAR VIEW
            # ใช้พิกัดที่ดึงมาได้จริงใส่ในแผนที่
            m = folium.Map(
                location=[my_lat, my_lon], 
                zoom_start=18, 
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                attr='Google Maps Hybrid'
            )
            
            # ปักหมุดตัวเรา (สีแดง)
            folium.Marker(
                [my_lat, my_lon], 
                popup="ตำแหน่งของคุณ",
                icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
            ).add_to(m)

            # วาดแผนที่
            st_folium(m, width="100%", height=400, key="radar_map")
            
            if st.button("📡 BROADCAST POSITION", use_container_width=True):
                # ตรงนี้ใส่โค้ด db.reference('users/...').update(...) เพื่อส่งค่าเข้า Firebase
                st.toast("ส่งพิกัดเข้าฐานข้อมูลแล้ว!")

        with t2: # แชตรวม (โค้ดเดิมของคุณ)
            st.subheader("Global Communication")
            # ... ส่วนแชตที่คุณมีอยู่แล้ว ...

        with t3: # แชตลับ (โค้ดเดิมของคุณ)
            st.subheader("Agent-to-Agent Encryption")
            # ... ส่วนแชตลับที่คุณมีอยู่แล้ว ...


        

    # --- PAGE: DECODER ---
    elif st.session_state.current_page == "DECODER":
        st.markdown(f"<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        st.write("รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        st.write("รหัสจันทรคติ: 29.53")

    # --- PAGE: SENSOR ---
    elif st.session_state.current_page == "SENSOR":
        st.markdown(f"<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        st.info("System scanning for G-Force vibrations...")
