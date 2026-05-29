import streamlit as st
import numpy as np
import time
from datetime import datetime

# 1. UI SETTING (เข้มสุด ลกสุด)
st.set_page_config(page_title="SYNAPSE X - COMMAND CENTER", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    .metric-box { border: 1px solid #333; padding: 10px; background: #050505; border-radius: 5px; }
    .status-text { color: #FFD700; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & SLOGAN ---
st.markdown("<h1 style='text-align: center; color: #FF0000;'>🔴 SYNAPSE X : MASTER CONTROL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FFD700;'>\"อยู่นิ่งๆ ไม่เจ็บตัว\" | มองโลกในแง่ดีเสมอ แม้ข้างในจะเจ็บปวด</p>", unsafe_allow_html=True)

# 2. MASTER CLOCK (นาฬิกา 8 ช่วงเวลา)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
hour = now.hour

# 3. LOGIC DETERMINATION (กำหนดโหมดจากเวลาจริง)
if 6 <= hour < 9:
    mode, freq, mood_color = "AWAKENING", 528, "#FFD700"
elif 21 <= hour or hour < 3:
    mode, freq, mood_color = "DEEP HEALING", 432, "#00008B"
else:
    mode, freq, mood_color = "EQUILIBRIUM", 440, "#FFFFFF"

# 4. DASHBOARD (Metrics ลกๆ 4 คอลัมน์)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-box'>❤️ PULSE (Real-time)<br><h2 style='color:red;'>72 BPM</h2><span class='status-text'>STABLE</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'>📍 GPS COORDS<br><h2 style='color:#00f2fe;'>13.75, 100.52</h2><span class='status-text'>LOCATED: THAILAND</span></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-box'>☁️ BARO / LIGHT<br><h2 style='color:#00FF00;'>1012 hPa</h2><span class='status-text'>LIGHT: 450 LUX</span></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-box'>🕒 SYSTEM TIME<br><h2 style='color:white;'>{current_time}</h2><span class='status-text'>MODE: {mode}</span></div>", unsafe_allow_html=True)

# 5. ASSASSIN 144 MATH ENGINE (สูตรคณิตศาสตร์แท้)
st.markdown("---")
st.subheader("📐 Assassin 144 : Matrix Calculation")
st.latex(r"Sound(t) = \int_{144} Matrix(V,A) \cdot \Phi(f,T) dt")
st.code(f"# Current Matrix State\nFrequency_Target: {freq}Hz\nAmplitude_Mod: 0.85\nPhase_Shift: 0.002", language='python')

# 6. YOUTUBE PLAYLIST & 7. EMOTION LED (แสดงผลข้างกัน)
st.markdown("---")
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📺 S.S.S STATION (24/7 LIVE)")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    st.markdown(f'<iframe width="100%" height="400" src="https://www.youtube.com/embed/videoseries?list={playlist_id}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)

with right_col:
    st.subheader("💡 Emotion LED")
    st.markdown(f"<div style='width:100%; height:150px; background-color:{mood_color}; border-radius:20px; border: 5px solid #333;'></div>", unsafe_allow_html=True)
    st.write(f"Current Hue: {mood_color}")
    
    # 8. MATRIX V1.0/V2.0 Sliders
    st.slider("Valence (Joy/Sad)", 0.0, 1.0, 0.7)
    st.slider("Arousal (Energy)", 0.0, 1.0, 0.5)

# 9. CONSOLE LOGS (ตัวหนังสือวิ่งรกๆ)
st.markdown("---")
st.subheader("📋 System Console Logs")
st.text_area("Live Data Stream", value="[INFO] Synchronizing GPS...\n[SUCCESS] Matrix 144 Loaded.\n[ACTIVE] Frequency adjusted to " + str(freq) + "Hz\n[READY] Awaiting User Interaction...", height=100)

# 10. TURBO CONTROL BUTTONS
st.markdown("---")
cb1, cb2, cb3, cb4 = st.columns(4)
with cb1: st.button("🚀 TURBO BOOST", use_container_width=True)
with cb2: st.button("💾 SAVE STATE", use_container_width=True)
with cb3: st.button("📡 SHARE MATRIX", use_container_width=True)
with cb4: st.button("🛑 EMERGENCY RESET", use_container_width=True)
