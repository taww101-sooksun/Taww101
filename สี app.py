import streamlit as st
import streamlit.components.v1 as components
import os

# --- 🎭 1. มิติดีไซน์ Logo3 (Dark & Orange) ---
st.set_page_config(page_title="SYNAPSE SCALE", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FF7F50; }
    .main-panel { border: 2px solid #FF7F50; border-radius: 12px; padding: 15px; background: #080808; }
    .neon-clock { font-family: monospace; font-size: 60px; color: #00ff00; text-align: center; }
    .note-label { color: #FF7F50; font-weight: bold; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว ---
c1, c2 = st.columns([1, 5])
with c1:
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", width=60)
    else: st.markdown("<h2 style='margin:0;'>🎹</h2>", unsafe_allow_html=True)
with c2:
    st.markdown("<h3 style='margin:0; color:#FF7F50;'>SYNAPSE SCALE v1.2.1</h3>", unsafe_allow_html=True)
    st.caption("มิติเสียง โด-เร-มี | ลากยาวพิเศษ | อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 🎛️ 3. แผงควบคุมโน้ต 8 เสียง (โด-โด) ---
st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
st.markdown("<p class='note-label'>🎼 วางตำแหน่งโน้ต (1-20)</p>", unsafe_allow_html=True)
n1, n2, n3, n4 = st.columns(4)
c_do = n1.text_input("โด (C4)", "1, 9, 17")
c_re = n2.text_input("เร (D4)", "2, 10")
c_mi = n3.text_input("มี (E4)", "3, 11")
c_fa = n4.text_input("ฟา (F4)", "4, 12")
n5, n6, n7, n8 = st.columns(4)
c_so = n5.text_input("ซอล (G4)", "5, 13")
c_la = n6.text_input("ลา (A4)", "6, 14")
c_ti = n7.text_input("ที (B4)", "7, 15")
c_do2 = n8.text_input("โด+ (C5)", "8, 16, 20")

st.markdown("<hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)

# 🎯 3 ปุ่มสไลด์ 0-10 (ที่พี่สั่ง)
s1, s2, s3 = st.columns(3)
val_sus = s1.slider("1. ลากยาว (SUSTAIN)", 0.0, 10.0, 8.0)
val_tone = s2.slider("2. มิติทุ้ม-แหลม (TONE)", 0.0, 10.0, 3.0)
val_gain = s3.slider("3. ระดับเสียง (GAIN)", 0.0, 10.0, 7.0)
bpm = st.slider("ความเร็ว (BPM)", 40, 180, 80)
st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 4. JavaScript Engine: เสียงสังเคราะห์ลากยาว ---
audio_engine_js = f"""
<div style="background:#000; padding:15px; border:1px solid #444; border-radius:10px; text-align:center; margin-top:10px;">
    <button id="run" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; font-size:20px; cursor:pointer;
