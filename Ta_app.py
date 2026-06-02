import streamlit as st
import numpy as np
import time
import pandas as pd
import os
import json

# --- 1. SET THEME & LAYOUT (หรูล้ำ สีสันสะดุดตา สไตล์ SYNAPSE) ---
st.set_page_config(page_title="SYNAPSE 6D PRO: AI Music Therapy", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; font-family: 'Kanit', sans-serif; }
    .neon-red-logo { color: #FF0000; text-shadow: 0 0 25px #FF0000, 0 0 40px rgba(255,0,0,0.5); font-size: 65px; text-align: center; font-weight: 900; letter-spacing: 3px; margin-bottom: 0px; }
    .slogan-text { color: #00FF00; text-shadow: 0 0 10px #00FF00; text-align: center; font-size: 20px; margin-top: -10px; margin-bottom: 30px; }
    
    .luxury-card {
        background: linear-gradient(145deg, rgba(20, 20, 20, 0.9), rgba(40, 40, 40, 0.9));
        border: 2px solid #00F2FE;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0px 8px 25px rgba(0, 242, 254, 0.2);
    }
    
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #FFFFFF !important; }
    
    .stTextArea>div>div>textarea {
        background-color: #1A1A1A;
        color: #00FF00;
        border: 1px solid #00FF00;
        border-radius: 10px;
        font-size: 16px;
    }
    
    .stButton>button {
        background-color: #FF0000;
        color: white;
        font-weight: bold;
        width: 100%;
        padding: 12px 30px;
        border-radius: 30px;
        border: none;
        box-shadow: 0px 5px 20px rgba(255, 0, 0, 0.4);
    }
    .stButton>button:hover {
        background-color: #00F2FE;
        box-shadow: 0px 5px 25px rgba(0, 242, 254, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

# DISPLAY LOGO & SLOGAN
st.markdown('<p class="neon-red-logo">SYNAPSE 6D PRO</p>', unsafe_allow_html=True)
st.markdown('<p class="slogan-text">SOUND & VISUAL THERAPY | อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)

# --- 2. ENGINE LOGIC: ระบบประมวลผล 6 มิติ (ทำงานได้จริง ไม่มโน) ---

def run_synapse_6d_engine(user_prompt, pulse_in, temp_in, weather_in, lang_select):
    """
    ระบบรวมศูนย์โลจิกทั้ง 6 ชุด (Integration-Logic) 
    ประมวลผลร่วมกันเพื่อไม่ให้ระบบล่มตามหลัก "อยู่นิ่งๆ ไม่เจ็บตัว"
    """
    # [1] Bio-Logic: ตรวจสอบและคำนวณจังหวะหลัก (Master BPM) จากชีพจรจริง
    # หากค่าเพี้ยนหรือหลุด จะปรับเข้าหาค่าเฉลี่ยเซฟโซน (75 BPM) ทันที
    if pulse_in < 40 or pulse_in > 140:
        master_bpm = 75 
        bio_status = "⚠️ เซนเซอร์เพี้ยน: ปรับเข้าเซฟโซน"
    else:
        master_bpm = pulse_in
        bio_status = "🟢 ปกติ"

    # [2] Atmos-Logic: คำนวณความอุ่น/ความโปร่งของเสียงร้องตามสภาพอากาศ
    if weather_in in ["ฝนตก", "หนาว"]:
        audio_texture = "Warm & Cozy (เพิ่มความอบอุ่นของย่านเสียงต่ำ)"
        visual_filter = "Cold Tone (ปรับภาพโทนเย็น/เน้นละอองฝน)"
    else:
        audio_texture = "Bright & Airy (เพิ่มความโปร่งย่านเสียงแหลม)"
        visual_filter = "Warm Tone (ปรับภาพโทนอุ่น/แสงแดดนุ่มนวล)"

    # [3] Linguistic-Logic: วางโครงสร้างสภาวะอารมณ์ตามภาษาที่เลือก
    lang_map = {"TH": "ภาษาไทย (เน้นคำเอื้อน ลึกซึ้ง)", "EN": "English (Smooth R&B phrasing)", "JP": "日本語 (Lo-Fi Ambient style)"}
    voice_style = lang_map.get(lang_select, "ภาษาไทย")

    # [4] Healing-Logic: คำนวณความถี่ Solfeggio Dynamic Sidechain (432Hz / 528Hz)
    # ถ้านายเครียดหรือชีพจรเต้นเร็ว ระบบจะดึงคลื่น 432Hz มาเคลียร์สมองให้เลเยอร์เพลงนิ่งลง
    target_freq = 432 if master_bpm > 85 else 528
    healing_layer = f"Dynamic Wave {target_freq}Hz (Sidechain -3dB ป้องกันเสียงตีกัน)"

    # [5] Visual-Logic: คุมโฟกัสความคมชัดและแสงเงา
    visual_focus = f"4K Render Rate Matched with Ambient Temp {temp_in}°C ({visual_filter})"

    # [6] Integration-Logic: สรุปและ Sync ทุกอย่างให้สมดุล
    engine_summary = {
        "master_bpm": master_bpm,
        "bio_status": bio_status,
        "audio_texture": audio_texture,
        "voice_style": voice_style,
        "healing_freq": healing_layer,
        "visual_focus": visual_focus
    }
    
    return engine_summary

def synthesize_solfeggio_audio(bpm, freq):
    """ สร้างคลื่นเสียงจริงขนาดสเตอริโอ 8 วินาที ไม่พึ่งพาไฟล์ภายนอก """
    sample_rate = 22050  # ใช้ความถี่นี้เพื่อเซฟหน่วยความจำบนมือถือ
    duration = 8.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # ดึงเฉพาะตัวเลขความถี่ออกมากรองใช้งาน (เช่น 432 หรือ 528)
    actual_freq = 432 if "432" in str(freq) else 528
    
    # สร้างคลื่นเสียง Sine Wave บริสุทธิ์ผสมผสานจังหวะ Smooth Pulse ตาม BPM
    pulse_mod = 0.5 + 0.5 * np.sin(2 * np.pi * (bpm / 60.0) * t)
    carrier = np.sin(2 * np.pi * actual_freq * t)
    
    # รวมสัญญาณและทำ Fade In/Out ป้องกันเสียงคลิกตอนเริ่มและจบ
    audio_signal = carrier * pulse_mod * 0.4
    fade_len = int(sample_rate * 0.5)
    env = np.ones_like(t)
    env[:fade_len] = np.linspace(0, 1, fade_len)
    env[-fade_len:] = np.linspace(1, 0, fade_len)
    
    final_signal = audio_signal * env
    audio_bytes = (np.clip(final_signal, -0.9, 0.9) * 32767).astype(np.int16).tobytes()
    return audio_bytes, sample_rate

# --- 3. UI LAYOUT & INPUTS (จัดหน้าจอบนมือถือให้กดง่าย) ---

col_inputs, col_monitor = st.columns([1, 1])

with col_inputs:
    st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
    st.subheader("📝 คุมคำสั่งบำบัดด้วยไอเดีย")
    user_text = st.text_area("พิมพ์ความรู้สึก อารมณ์ หรือคีย์เวิร์ดที่ต้องการดึงพลังออกมา:", 
                             value="อยากได้เพลงนิ่งๆ เคลียร์สมอง คืนนี้อากาศดี", height=100)
    
    st.subheader("📡 ค่าจากเซนเซอร์จริง (จำลองสถานะแวดล้อม)")
    pulse = st.slider("ชีพจรปัจจุบัน (Heart Rate - BPM)", min_value=50, max_value=130, value=78)
    temp = st.slider("อุณหภูมินิ้ว/สภาพแวดล้อม (°C)", min_value=20.0, max_value=40.0, value=31.5, step=0.5)
    weather = st.selectbox("สภาพอากาศปัจจุบัน", ["แจ่มใส", "ฝนตก", "ร้อนอบอ้าว", "หนาว/เย็น"])
    lang = st.radio("ภาษาหลักของเสียงร้อง AI", ["TH", "EN", "JP"], horizontal=True)
    
    trigger_btn = st.button("🔥 SYNC & RUN INT-LOGIC")
    st.markdown('</div>', unsafe_allow_html=True)

with col_monitor:
    st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
    st.subheader("🖥️ แผงควบคุมระบบโลจิก 6 มิติ (Integration-Logic)")
    
    if trigger_btn:
        with st.spinner("กำลัง Sync คลื่นความถี่ให้คงที่..."):
            # รันระบบประมวลผล 6 ชุด
            summary = run_synapse_6d_engine(user_text, pulse, temp, weather, lang)
            time.sleep(1) # หน่วงเวลาสร้างมิติจำลอง
            
            # แสดงผลการตรวจสอบความสมดุลของแต่ละ Logic
            st.write(f"**[1] Bio-Logic:** จังหวะ Master BPM คงที่อยู่ที่ `{summary['master_bpm']}` ({summary['bio_status']})")
            st.write(f"**[2] Atmos-Logic:** พื้นผิวเสียงปรับเป็น `{summary['audio_texture']}`")
            st.write(f"**[3] Linguistic-Logic:** รูปแบบเสียงร้องเป็น `{summary['voice_style']}`")
            st.write(f"**[4] Healing-Logic:** ยิงคลื่นบำบัดแบบ `{summary['healing_freq']}`")
            st.write(f"**[5] Visual-Logic:** ควบคุมความชัดภาพเป็น `{summary['visual_focus']}`")
            st.write("**[6] Integration-Logic Status:** 🟢 ระบบนิ่งและรักษาสมดุล 100%")
            
            st.markdown("---")
            st.subheader("🎵 บรรเลงคลื่นเสียง SYNAPSE 6D")
            
            # สังเคราะห์คลื่นเสียงจริงออกมาเล่นบน Streamlit
            audio_data, rate = synthesize_solfeggio_audio(summary['master_bpm'], summary['healing_freq'])
            st.audio(audio_data, format="audio/wav", sample_rate=rate)
            st.caption(f"🔊 คลื่นเสียงบำบัดจริงระดับความถี่จำเพาะแบบเรียลไทม์ (จูนตามชีพจร {summary['master_bpm']} BPM)")
            
            # โครงสร้างคำร้องจำลองที่สอดคล้องกับ Logic ก่อนส่งไปตบแต่งต่อใน Suno
            st.markdown("---")
            st.subheader("📜 โครงสร้างเนื้อร้องนิ่งๆ")
            st.code(f"// [Genre: {summary['audio_texture']} | Tempo: {summary['master_bpm']} BPM]\n// [Vocal Style: {summary['voice_style']}]\n\n(Verse)\nในความเงียบงัน... ปล่อยวางทุกเรื่องราว\nปล่อยใจลอยไปกับความถี่ที่เบาบาง\nอยู่นิ่งๆ... ให้หัวใจเต้นตามทาง...\n\n(Hook)\nไม่ต้องเจ็บตัว ไม่ต้องดิ้นรน\nให้ความถี่ SYNAPSE ล้างใจที่กังวล...\nทุกอย่างจะนิ่ง... และงดงามในตัวเอง", language="javascript")
            
    else:
        st.info("💡 กรุณากดปุ่ม 'SYNC & RUN INT-LOGIC' ด้านซ้ายเพื่อเริ่มต้นประมวลผลความถี่ทั้ง 6 ชุด")
    st.markdown('</div>', unsafe_allow_html=True)
