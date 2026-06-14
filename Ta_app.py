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

# --- [ บรรทัดแรกสุดของไฟล์ ห้ามย้าย! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# --- ค่าเริ่มต้นของระบบธีมสี ---
if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#00f3ff"
if 'custom_theme' not in st.session_state:
    st.session_state.custom_theme = "#00f3ff"

# --- ส่วนหน้าจอลงชื่อเข้าใช้ (Login / Register) ---
if not st.session_state.get('logged_in', False):
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    
    with st.container():
        new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ101, บาส").strip()
        
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                try:
                    user_check = db.reference(f'users/{new_user}').get()
                    if not user_check:
                        db.reference(f'users/{new_user}').set({
                            'created_at': time.time(),
                            'lat': 13.7367,
                            'lon': 100.5231
                        })
                except Exception as e:
                    st.warning(f"ระบบ Local หรือไม่ได้ต่อ Firebase: {e}")
                
                st.session_state.user = new_user        
                st.session_state.logged_in = True     
                st.session_state.page = "HOME"         

                st.success(f"WELCOME AGENT: {new_user}")
                st.balloons()
                time.sleep(1.5) 
                st.rerun()      
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
            height: 80px;
            font-size: 16px;
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
# [ หน้าแรก: ศูนย์รวมแอป ]
# =========================================================
if st.session_state.page == "HOME":
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("<h1 class='neon-text'>SYNAPSE COMMAND</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💬 6. CHAT & VOICE HUB\nระบบสื่อสารและส่งข้อความเสียง", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: แชตรวม แชตแยก และส่งคลิปเสียง Walkie-Talkie")

        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()

        if st.button("🖼️ 2. IMAGE SEARCH\nค้นหาภาพ", use_container_width=True):
            st.session_state.page = "3"; st.rerun()

    with c2:
        if st.button("🌍 8. WORLD CLOCK & SENSOR\nเซนเซอร์ตรวจจับความเคลื่อนไหว", use_container_width=True):
            st.session_state.page = "6_clock"; st.rerun()

        if st.button("💖 4. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()

# =========================================================
# ห้องที่ 2: อัปเกรดใหม่ CHAT SYSTEM, PRIVATE CHAT & WALKIE-TALKIE
# =========================================================
elif st.session_state.page == "2":
    # สั่งออโต้รีเฟรชทุก 5 วินาทีเพื่อให้ข้อความแชตอัปเดตเรื่อยๆ
    st_autorefresh(interval=5000, key="chat_refresh")
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🛰️ SYNAPSE COMMUNICATIONS</h2>", unsafe_allow_html=True)

    tab_global, tab_private, tab_voice = st.tabs(["👥 GLOBAL CHAT (แชตรวม)", "🔐 PRIVATE CHAT (แชตส่วนตัว)", "📻 WALKIE-TALKIE (ส่งข้อความเสียง)"])

    # --- 1. แชตรวม ---
    with tab_global:
        st.markdown("### 👥 ศูนย์กระจายข่าวสารร่วม")
        
        with st.form("global_chat_form", clear_on_submit=True):
            g_msg = st.text_input("พิมพ์ข้อความส่งเข้าแชตรวม:", placeholder="Agent ทุกคนจะเห็นข้อความนี้...")
            if st.form_submit_button("SEND TO ALL"):
                if g_msg:
                    try:
                        db.reference('global_messages').push({
                            'sender': st.session_state.user,
                            'text': g_msg,
                            'ts': time.time()
                        })
                        st.rerun()
                    except: st.error("เชื่อมต่อฐานข้อมูลไม่ได้")

        # ดึงข้อความแชตรวมมาแสดง
        try:
            g_messages = db.reference('global_messages').order_by_child('ts').limit_to_last(15).get()
            if g_messages:
                for mid in reversed(list(g_messages.keys())):
                    m_data = g_messages[mid]
                    is_me = m_data['sender'] == st.session_state.user
                    align = "right" if is_me else "left"
                    color = "#00f3ff" if is_me else "#50C878"
                    bg = "rgba(0, 243, 255, 0.1)" if is_me else "rgba(80, 200, 120, 0.1)"
                    st.markdown(f"""
                        <div style="text-align:{align}; margin-bottom:8px;">
                            <div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:12px; border:1px solid {color}; text-align:left;">
                                <b style="color:{color}; font-size:0.75rem;">{m_data['sender']}</b><br>
                                <span style="color:white;">{m_data['text']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("ยังไม่มีข้อความในแชตรวม")
        except: st.caption("รันโหมดออฟไลน์ หรือยังไม่ได้เชื่อมโยงฐานข้อมูล")

    # --- 2. แชตส่วนตัว ---
    with tab_private:
        st.markdown("### 🔐 ช่องสัญญาณลับส่วนบุคคล")
        try:
            all_users = db.reference('users').get()
            if all_users:
                friends = [u for u in all_users.keys() if u != st.session_state.user]
                target_agent = st.selectbox("🎯 เลือก AGENT ที่ต้องการคุยด้วย:", friends, key="private_target")

                if target_agent:
                    room_id = "_".join(sorted([st.session_state.user, target_agent]))
                    chat_ref = db.reference(f'private_messages/{room_id}')

                    with st.form("private_chat_form_updated", clear_on_submit=True):
                        p_msg = st.text_input(f"ข้อความลับถึง (AGENT: {target_agent}):", placeholder="พิมพ์ข้อความลับที่นี่...")
                        if st.form_submit_button("SEND PRIVATE SIGNAL"):
                            if p_msg:
                                chat_ref.push({
                                    'sender': st.session_state.user,
                                    'text': p_msg,
                                    'ts': time.time()
                                })
                                st.rerun()

                    p_messages = chat_ref.order_by_child('ts').limit_to_last(10).get()
                    if p_messages:
                        for mid in reversed(list(p_messages.keys())):
                            m_data = p_messages[mid]
                            is_me = m_data['sender'] == st.session_state.user
                            align = "right" if is_me else "left"
                            color = "#00f3ff" if is_me else "#ff00de"
                            bg = "rgba(0, 243, 255, 0.1)" if is_me else "rgba(255, 0, 222, 0.1)"
                            st.markdown(f"""
                                <div style="text-align:{align}; margin-bottom:8px;">
                                    <div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:12px; border:1px solid {color}; text-align:left;">
                                        <b style="color:{color}; font-size:0.75rem;">{m_data['sender']}</b><br>
                                        <span style="color:white;">{m_data['text']}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
            else: st.caption("ยังไม่มีข้อมูล Agent คนอื่นในระบบ")
        except: st.caption("ระบบฐานข้อมูลไม่พร้อมใช้งาน")

    # --- 3. ระบบข้อความเสียง WALKIE-TALKIE (ทำได้จริงบนมือถือ) ---
    with tab_voice:
        st.markdown("### 📻 บันทึกและส่งข้อความเสียง (Walkie-Talkie)")
        st.info("💡 วิธีใช้งานบนมือถือ: กดปุ่มไมโครโฟนเพื่ออัดเสียง พูดเสร็จแล้วกดส่งสัญญาณ เสียงจะถูกบันทึกขึ้นระบบคลาวด์ให้ Agent คนอื่นกดเปิดฟังได้ทันที")
        
        # HTML5 + JS Component สำหรับอัดเสียงผ่านไมโครโฟนโทรศัพท์มือถือโดยตรงแปลงเป็น Base64
        audio_recorder_html = """
        <div style="background:#111; padding:15px; border-radius:15px; border:1px solid #ff00de; text-align:center;">
            <button id="recordBtn" style="background:#ff00de; color:white; border:none; padding:10px 20px; border-radius:10px; font-weight:bold; cursor:pointer;">🎤 กดเพื่อพูด (RECORD)</button>
            <button id="stopBtn" style="background:#333; color:#ccc; border:none; padding:10px 20px; border-radius:10px; font-weight:bold; cursor:pointer; margin-left:10px;" disabled>🛑 หยุด (STOP)</button>
            <p id="audioStatus" style="color:#aaa; font-size:12px; margin-top:10px;">สถานะ: รอคำสั่ง</p>
            <audio id="audioPlayback" controls style="display:none; margin:10px auto; width:100%;"></audio>
            
            <form id="voiceForm" style="display:none;">
                <input type="text" id="base64Data" name="base64Data">
            </form>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            const recordBtn = document.getElementById('recordBtn');
            const stopBtn = document.getElementById('stopBtn');
            const status = document.getElementById('audioStatus');
            const playback = document.getElementById('audioPlayback');

            recordBtn.onclick = async () => {
                audioChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                    playback.src = URL.createObjectURL(audioBlob);
                    playback.style.display = 'block';
                    
                    // แปลงไฟล์เสียงเป็น Base64 String เพื่อเตรียมส่งกลับไปยัง Python/Streamlit ผ่านคลิปบอร์ดหรือ API
                    let reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = function() {
                        let base64String = reader.result.split(',')[1];
                        status.innerHTML = "✨ อัดเสียงเสร็จสิ้น! คัดลอกรหัสเสียงด้านล่างไปวางในช่องข้อความเสียงเพื่อส่ง";
                        // สร้างกล่องข้อความชั่วคราวให้ผู้ใช้คัดลอกได้ง่ายบนมือถือ
                        let t = document.createElement("textarea");
                        t.value = base64String;
                        t.style.width = "100%"; t.style.height="60px"; t.style.background="#222"; t.style.color="#00f3ff";
                        t.id = "strResult";
                        document.getElementById('audioStatus').appendChild(t);
                    }
                };
                mediaRecorder.start();
                recordBtn.disabled = true; stopBtn.disabled = false;
                status.innerText = "🔴 กำลังอัดเสียงสัญญาณ... พูดใส่ไมค์มือถือได้เลย";
            };

            stopBtn.onclick = () => {
                mediaRecorder.stop();
                recordBtn.disabled = false; stopBtn.disabled = true;
                status.innerText = "🔄 กําลังประมวลผลคลื่นเสียง...";
            };
        </script>
        """
        components.html(audio_recorder_html, height=220)
        
        # ช่องสำหรับรับรหัสคลิปเสียงเพื่อบันทึกลง Firebase
        v_target = st.selectbox("🎯 ส่งคลิปเสียงนี้ให้แก่:", ["ทุกคน (GLOBAL)"] + (friends if 'friends' in locals() else []))
        voice_b64 = st.text_area("📦 วางรหัสคลื่นเสียงที่ได้จากกล่องสแกนด้านบน:", placeholder="คัดลอกรหัสตัวอักษรยาวๆ จากกล่องด้านบนมาวางตรงนี้เพื่อส่งเข้าวิทยุสื่อสาร...")
        
        if st.button("📡 ปล่อยสัญญาณเสียงออกอากาศ", use_container_width=True):
            if voice_b64:
                try:
                    db.reference('voice_transmission').push({
                        'sender': st.session_state.user,
                        'target': v_target,
                        'audio_data': voice_b64,
                        'ts': time.time()
                    })
                    st.success("ส่งสัญญาณเสียงเรียบร้อย!")
                    time.sleep(1)
                    st.rerun()
                except: st.error("ไม่สามารถเชื่อมต่อฐานข้อมูลศูนย์ใหญ่ได้")
            else: st.warning("กรุณาอัดเสียงและนำรหัสมาวางก่อนส่ง!")

        # แสดงรายการวิทยุสื่อสารที่ส่งมาถึงเรา หรือแชตรวม
        st.write("---")
        st.markdown("#### 📻 รายการรับสัญญาณวิทยุล่าสุด")
        try:
            v_logs = db.reference('voice_transmission').order_by_child('ts').limit_to_last(10).get()
            if v_logs:
                for k, v in reversed(list(v_logs.items())):
                    # กรองเฉพาะเสียงที่เป็น Global หรือส่งถึงตัวเรา
                    if v['target'] == "ทุกคน (GLOBAL)" or v['target'] == st.session_state.user or v['sender'] == st.session_state.user:
                        is_global = v['target'] == "ทุกคน (GLOBAL)"
                        st.markdown(f"**จาก Agent:** {v['sender']} ➡️ **ถึง:** {v['target']}")
                        try:
                            # แปลงข้อมูล Base64 กลับมาเป็นเสียงและเปิดเครื่องเล่นเสียงจริงทันที
                            audio_bytes = base64.b64decode(v['audio_data'])
                            st.audio(audio_bytes, format="audio/mp3")
                        except: st.caption("❌ ไฟล์คลื่นเสียงเสียหาย")
                        st.divider()
            else: st.caption("ไม่มีการส่งสัญญาณเสียงในขณะนี้")
        except: st.caption("รันในระบบปิดภายนอกคลาวด์")

# =========================================================
# (ส่วนห้องที่เหลือคงเดิมจากโค้ดเดิมของผู้ใช้)
# =========================================================
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>SYNAPSE MUSIC PLAYER</h2>", unsafe_allow_html=True)
    all_songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if all_songs:
        for s in all_songs:
            if st.button(f"🎵 {s}", use_container_width=True): st.audio(s)
    else: st.caption("ไม่มีไฟล์เสียงในคลัง")

elif st.session_state.page == "3":
    st.markdown("## 🖼️ IMAGE SEARCH")
    st.image("https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=800", caption="คลังภาพจำลอง")

elif st.session_state.page == "6_clock":
    st.markdown("## ⚡ SYNAPSE SENSOR CONTROL")
    st.write("เวลาเซิร์ฟเวอร์ปัจจุบัน:", datetime.now().strftime('%H:%M:%S'))
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว")

elif st.session_state.page == "7":
    st.markdown("## 💖 DESTINY CHECK")
    st.write("ระบบคำนวณผ่านรหัส Unicode")

elif st.session_state.page == "10":
    st.markdown("## 🎨 COLOR MASTER")
    new_color = st.color_picker("เลือกสีระบบ:", st.session_state.custom_theme)
    if st.button("🔥 อัปเดตสี"):
        st.session_state.custom_theme = new_color
        st.rerun()
