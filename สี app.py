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

# --- [ 1. CONFIG หน้าจอ - ห้ามซ้ำ! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide", initial_sidebar_state="collapsed")

# --- [ 2. ระบบเชื่อมต่อศูนย์บัญชาการ Firebase (จุดที่แก้ Error) ] ---
if not firebase_admin._apps:
    try:
        # ดึงค่าจาก Secrets ที่คุณตั้งไว้
        fb_creds = dict(st.secrets["firebase_credentials"])
        if "private_key" in fb_creds:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        # แก้ไข databaseURL ให้ตรงกับ Region สิงคโปร์ตามรูปที่แจ้ง Error
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app"
        })
    except Exception as e:
        st.error(f"❌ ระบบเชื่อมต่อขัดข้อง: {e}")

# --- [ 3. ฟังก์ชันเล่นเพลง (คงไว้เหมือนเดิม) ] ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    components.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)

# --- [ 4. การจัดการหน้าจอ (Navigation) ] ---
if 'page' not in st.session_state: st.session_state.page = "HOME"

# ปุ่มย้อนกลับ (คงไว้เหมือนเดิม)
if st.session_state.page != "HOME":
    if st.sidebar.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ 5. เนื้อหาแต่ละหน้า ] ---

# [ หน้าแรก: ศูนย์รวม 10 แอป ]
if st.session_state.page == "HOME":
    play_audio()
    # วาง LOGO หรือข้อความนีออน
    st.markdown("<h1 style='text-align: center; color: #00f3ff; text-shadow: 0 0 10px #00f3ff;'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</p>", unsafe_allow_html=True)
    st.divider()

    # สร้าง Grid 10 แอป (คงไว้เหมือนเดิม)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🧬 2. PERSONAL CODE\nค้นหาภาพจากดาวเทียม", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🔮 3. DESTINY TIMELINE\nสร้างตัวอักษรเรืองแสง", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("💖 4. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True): st.session_state.page = "4"; st.rerun()
        if st.button("📝 5. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("💬 6. CHAT SYSTEM\nระบบสื่อสารอัจฉริยะ", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("🛰️ 7. PARALLEL SCANNER\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True): st.session_state.page = "7"; st.rerun()
        if st.button("⚡ 8. VIBRATION UNIT\nเวลาโลกแบบเรียลไทม์", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("🔢 9. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True): st.session_state.page = "9"; st.rerun()
        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ หน้าแอปย่อย 1: Music Deck ] ---
elif st.session_state.page == "1":
    st.markdown("<h2 style='color: #ff00de;'>🎵 SYNAPSE MUSIC DECK</h2>", unsafe_allow_html=True)
    # ใส่ระบบ Mixer ที่คุณออกแบบไว้
    st.info("ระบบกำลังดึงข้อมูลเพลง... อยู่นิ่งๆ ไม่เจ็บตัว")
    
# --- [ หน้าแอปย่อย 6: Chat System (จุดที่เคย Error) ] ---
elif st.session_state.page == "6":
    st.subheader("💬 ระบบสื่อสารผ่านดาวเทียม")
    try:
        # การเรียกฐานข้อมูลตรงนี้จะไม่ Error แล้วเพราะแก้ URL ที่หัวไฟล์แล้ว
        chat_ref = db.reference('/public_chat')
        msg = st.chat_input("ส่งข้อความ...")
        if msg:
            chat_ref.push({'user': 'AGENT_X', 'msg': msg, 'ts': time.time()})
        
        display = chat_ref.get()
        if display:
            for k, v in display.items():
                st.write(f"**{v.get('user')}**: {v.get('msg')}")
    except Exception as e:
        st.warning(f"รอสัญญาณเชื่อมต่อ... ({e})")

# ส่วนท้าย
st.markdown("---")
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Interface Control")
