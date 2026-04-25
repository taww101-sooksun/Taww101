import streamlit as st
import os
import base64
import time
import pandas as pd
import numpy as np

# 1. ตั้งค่าหน้าจอและธีม (โทนสีดำ-นีออน)
st.set_page_config(page_title="SYNAPSE MASTER", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# เรียกใช้โลโก้ของพี่ (อิงจากไฟล์ที่พี่มี)
logo_b64 = get_base64("โลโก้1.png")

# 2. ปรับแต่ง CSS (ตัวหนังสือวิ่งกลางจอ + ธีมสี)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000; color: #00FF00; }}
    
    /* ตัวหนังสือวิ่งกลางจอ */
    .center-marquee {{
        background-color: rgba(255, 0, 234, 0.1);
        border-top: 2px solid #ff00ea;
        border-bottom: 2px solid #ff00ea;
        padding: 10px 0;
        margin: 20px 0;
        font-size: 20px;
        font-weight: bold;
        color: #fff;
        text-shadow: 0 0 10px #ff00ea;
    }}
    
    /* โลโก้เรืองแสง */
    .logo-img {{
        display: block;
        margin: auto;
        width: 150px;
        border-radius: 50%;
        box-shadow: 0 0 20px #00FF00;
    }}

    /* กราฟเสียง */
    .stBarChart {{
        filter: drop-shadow(0 0 5px #00FF00);
    }}
    </style>
""", unsafe_allow_html=True)

# 3. ส่วนหัวและโลโก้
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)

# ตัวหนังสือวิ่งกลางจอตามที่พี่สั่ง
st.markdown("""
    <div class="center-marquee">
        <marquee scrollamount="8">
            🔥 SYNAPSE COMMAND CENTER • อยู่นิ่งๆ ไม่เจ็บตัว • SOUND & VISUAL THERAPY • แปลงยูทูปอ่านเขสนะ 🔥
        </marquee>
    </div>
""", unsafe_allow_html=True)

# 4. ระบบจัดการเพลง
songs = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])

if songs:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎵 DECK A")
        selected_song = st.selectbox("เลือกเพลงที่จะเล่น", songs)
        st.audio(selected_song)
        
    with col2:
        st.markdown("### 📊 REAL-TIME VISUALIZER")
        # จำลองกราฟเสียงแบบ Real-time (ใช้ข้อมูลสุ่มที่ขยับได้)
        chart_data = pd.DataFrame(np.random.randn(20, 1), columns=["Frequency"])
        st.bar_chart(chart_data, color="#00FF00")

    # ส่วนของ Playlist
    with st.expander(f"📂 GLOBAL PLAYLIST ({len(songs)} TRACKS)"):
        for i, s in enumerate(songs, 1):
            st.write(f"{i}. {s}")
else:
    st.error("ไม่พบไฟล์ .mp3 ในระบบ")

# 5. ท้ายแอป
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("SYNAPSE MASTER | @Ta101 | 2026")
