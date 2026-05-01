import streamlit as st
import os 
import time
import base64
import math
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, timedelta
from streamlit_js_eval import get_geolocation 

# ==========================================
# 1. SETUP & THEME (ดีดความเป็น Streamlit ออก)
# ==========================================
st.set_page_config(page_title="SYNAPSE OS V5", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_ui():
    p = st.session_state.get('theme_color', "#39FF14")
    bg = st.session_state.get('bg_color', "#000000")
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        #MainMenu, footer, header {{visibility: hidden;}}
        .stApp {{ background: {bg}; color: white; font-family: 'Orbitron', sans-serif; }}
        
        .neon-title {{
            color: {p}; font-size: 50px; font-weight: bold;
            text-shadow: 0 0 10px {p}, 0 0 20px {p};
            margin-bottom: 0px; text-align: center;
        }}
        .slogan {{ text-align: center; letter-spacing: 3px; margin-bottom: 30px; color: #888; }}
        
        /* สไตล์ปุ่มเมนูหน้าหลัก */
        .stButton>button {{
            width: 100%; border: 1px solid {p} !important;
            background: rgba(0,0,0,0.6) !important; color: {p} !important;
            border-radius: 12px; height: 80px; font-size: 20px !important;
            transition: 0.4s; margin-bottom: 15px;
        }}
        .stButton>button:hover {{
            box-shadow: 0 0 20px {p}; background: {p} !important; color: black !important;
            transform: scale(1.02);
        }}
        
        .room-card {{
            border: 1px solid {p}33; padding: 25px; border-radius: 20px;
            background: rgba(255,255,255,0.03); text-align: center;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CORE LOGIC (ไส้ในคำนวณ)
# ==========================================
def get_logic(dt):
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar = (diff - 0.5) % 29.530589
    day_val = dt.weekday() + 1
    is_waxing = lunar <= 14.765
    m_num = int(lunar) + 1 if is_waxing else int(lunar - 14.765) + 1
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        f, t = f"√({day_val}² + {m_num}²)", "Vector Force"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        f, t = f"({day_val} × 1.618) / {m_num}", "Phi Balance"
    return {"res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ", "formula": f, "tech": t}

# ==========================================
# 3. ROOMS (ฟีเจอร์ข้างใน)
# ==========================================

def room_music():
    st.markdown("<h2 class='neon-title'>🎧 MUSIC ROOM</h2>", unsafe_allow_html=True)
    st.info("💡 ปรับจูนคลื่นสมองด้วยระบบ Visualizer ตามรหัสเสียงจริง")
    songs = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if songs:
        s = st.selectbox("เลือกสัญญาณ", songs)
        with open(s, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        components.html(f"""
            <canvas id="v" style="width:100%; height:150px; border:1px solid {st.session_state.theme_color}; border-radius:10px;"></canvas>
            <audio id="a" src="data:audio/mp3;base64,{b64}"></audio>
            <button id="p" style="width:100%; margin-top:10px; padding:15px; background:none; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; cursor:pointer;">[ ACTIVATE ]</button>
            <script>
                const a=document.getElementById('a'), v=document.getElementById('v'), ctx=v.getContext('2d'), btn=document.getElementById('p');
                let ac, an, sr, dt;
                btn.onclick=()=>{{
                    if(!ac){{ ac=new AudioContext(); an=ac.createAnalyser(); sr=ac.createMediaElementSource(a); sr.connect(an); an.connect(ac.destination); dt=new Uint8Array(an.frequencyBinCount); run(); }}
                    a.paused ? a.play() : a.pause();
                }};
                function run(){{ requestAnimationFrame(run); an.getByteFrequencyData(dt); ctx.clearRect(0,0,v.width,v.height); dt.forEach((val,i)=>{{ ctx.fillStyle='{st.session_state.theme_color}'; ctx.fillRect(i*3, v.height-val/2, 2, val/2); }}); }}
            </script>
        """, height=300)
    if st.button("🔙 กลับหน้าหลัก"): st.session_state.page = "home"; st.rerun()

def room_logic():
    st.markdown("<h2 class='neon-title'>🧬 LOGIC CENTER</h2>", unsafe_allow_html=True)
    st.info("💡 คำนวณพิกัดบรรจบ (เพชร/ธร/กงจักร) ล่วงหน้าและย้อนหลัง 365 วัน")
    d_in = st.date_input("วันที่ตรวจสอบ", value=date.today())
    l = get_logic(d_in)
    st.markdown(f"<div class='room-card'><h1>{l['res']}</h1><p>{l['phase']} ({l['tech']})</p></div>", unsafe_allow_html=True)
    
    if st.button("🔍 สแกนหาจุดบรรจบ 365 วัน"):
        results = []
        for i in range(-182, 183):
            target = d_in + timedelta(days=i)
            res = get_logic(target)
            gap = abs(l['res'] - res['res'])
            if gap < 0.5: results.append({"วันที่": target, "พิกัด": res['res'], "GAP": round(gap,4), "สถานะ": "💎 เพชร"})
        st.table(pd.DataFrame(results))
    
    if st.button("🔙 กลับหน้าหลัก"): st.session_state.page = "home"; st.rerun()

def room_sensor():
    st.markdown("<h2 class='neon-title'>📟 SENSOR ARRAY</h2>", unsafe_allow_html=True)
    st.info("💡 ตรวจวัดความนิ่งผ่าน G-Force และระดับเสียงแวดล้อมจริง")
    components.html(f"""
        <div style="background:#000; border:2px solid {st.session_state.theme_color}; border-radius:15px; padding:30px; text-align:center; color:white;">
            <div style="display:grid; grid-template-columns:1fr 1fr;">
                <div><small>SONIC</small><h2 id="v">{random.randint(20,50)}</h2></div>
                <div><small>MOTION</small><h2 id="a">1.00</h2></div>
            </div>
            <button id="s" style="width:100%; padding:15px; background:none; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; cursor:pointer; margin-top:20px;">[ START SCAN ]</button>
        </div>
        <script>
            const btn=document.getElementById('s');
            btn.onclick=async()=>{{
                btn.style.display='none';
                const str=await navigator.mediaDevices.getUserMedia({{audio:true}});
                const ac=new AudioContext(); const ana=ac.createAnalyser();
                ac.createMediaStreamSource(str).connect(ana);
                const d=new Uint8Array(ana.frequencyBinCount);
                if(window.DeviceMotionEvent && typeof DeviceMotionEvent.requestPermission==='function') await DeviceMotionEvent.requestPermission();
                function run() {{ requestAnimationFrame(run); ana.getByteFrequencyData(d); document.getElementById('v').innerText=Math.round(d.reduce((a,b)=>a+b)/d.length); }}
                window.addEventListener('devicemotion',e=>{{ let g=e.accelerationIncludingGravity; let v=Math.sqrt(g.x**2+g.y**2+g.z**2)/9.8; document.getElementById('a').innerText=v.toFixed(2); }});
                run();
            }}
        </script>
    """, height=300)
    if st.button("🔙 กลับหน้าหลัก"): st.session_state.page = "home"; st.rerun()

# ==========================================
# 4. MAIN NAVIGATION
# ==========================================
def main():
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    
    apply_custom_ui()

    if st.session_state.page == "home":
        st.markdown("<h1 class='neon-title'>SYNAPSE</h1>", unsafe_allow_html=True)
        st.markdown("<p class='slogan'>'อยู่นิ่งๆ ไม่เจ็บตัว'</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎧 เครื่องเล่นเพลง"): st.session_state.page = "music"; st.rerun()
            if st.button("🧬 สูตรคำนวณ"): st.session_state.page = "logic"; st.rerun()
        with col2:
            if st.button("📟 วัดเซนเซอร์"): st.session_state.page = "sensor"; st.rerun()
            if st.button("⚙️ ตั้งค่าแอป"): st.session_state.page = "settings"; st.rerun()
            
        st.markdown("---")
        st.markdown("<div class='room-card'><h3>SYSTEM: ONLINE</h3><p>พิกัดพร้อมประมวลผล</p></div>", unsafe_allow_html=True)

    elif st.session_state.page == "music": room_music()
    elif st.session_state.page == "logic": room_logic()
    elif st.session_state.page == "sensor": room_sensor()
    elif st.session_state.page == "settings":
        st.markdown("<h2 class='neon-title'>SETTINGS</h2>")
        st.session_state.theme_color = st.color_picker("สีนีออนหลัก", st.session_state.theme_color)
        if st.button("🔙 กลับหน้าหลัก"): st.session_state.page = "home"; st.rerun()

if __name__ == "__main__":
    main()
