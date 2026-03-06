import streamlit as st
import numpy as np
import scipy.io.wavfile as wavfile
import io
import time

# ==========================================
# 🧮 1. เครื่องยนต์คณิตศาสตร์เสียง (THE AUDIO ENGINE)
# ==========================================
def create_signature_hit(sr=44100):
    # สร้างเสียง 1 จังหวะ (ตึ่บ + แชะ + จิ้ว) ความยาว 0.2 วินาที
    t = np.linspace(0, 0.2, int(sr * 0.2))
    
    # 1. ตึ่บ (Kick) - ความถี่ตกฮวบจาก 150Hz ลงมา 40Hz
    freq_kick = np.geomspace(150, 40, len(t))
    kick = np.sin(2 * np.pi * freq_kick * t) * np.exp(-15 * t)
    
    # 2. แชะ (Hi-hat) - White Noise สั้นๆ
    noise = np.random.uniform(-1, 1, len(t))
    hat = np.diff(noise, prepend=0) * np.exp(-40 * t) * 0.5
    
    # 3. จิ้ว (Acid Bass) - คลื่นหยัก (Sawtooth) กวาดความถี่
    bass_freq = 65.41 # โน้ต C2
    saw = 2 * (t * bass_freq - np.floor(0.5 + t * bass_freq))
    f_env = np.geomspace(2000, 100, len(t)) # กวาดจากแหลมลงทุ้ม (จิ้ว)
    vcf_f = 2 * np.sin(np.pi * f_env / sr)
    vcf_q = 0.2 # Resonance แหลมๆ
    out = np.zeros_like(saw)
    low = 0; band = 0
    for i in range(len(saw)):
        low = low + vcf_f[i] * band
        high = saw[i] - low - vcf_q * band
        band = vcf_f[i] * high + band
        out[i] = low
    bass = out * np.exp(-10 * t)
    
    # ผสมเสียงทั้งหมด
    mixed = kick + hat + (bass * 0.8)
    return mixed

def generate_32step_sequence(pattern, bpm=128, sr=44100):
    # คำนวณเวลา 1 ช่องจังหวะ (16th note)
    step_duration = 60.0 / bpm / 4.0
    step_samples = int(step_duration * sr)
    
    # สร้างกระดาษเปล่าสำหรับเพลงทั้งท่อน (32 ช่อง)
    total_samples = step_samples * 32
    master_track = np.zeros(total_samples)
    
    # ดึงเสียงที่พี่คิดไว้มาใช้
    hit_sound = create_signature_hit(sr)
    
    # กวาดดูว่าพี่ติ๊กช่องไหนไว้บ้าง
    for i in range(32):
        if pattern[i]: # ถ้าช่องที่ i ถูกติ๊ก
            start_idx = i * step_samples
            end_idx = start_idx + len(hit_sound)
            # ป้องกันเสียงล้นความยาวเพลง
            if end_idx > total_samples:
                end_idx = total_samples
                hit_sound = hit_sound[:end_idx-start_idx]
            
            # วางเสียงลงไปใน Master Track
            master_track[start_idx:end_idx] += hit_sound
            
    # ปรับระดับความดังไม่ให้แตก (Normalize)
    if np.max(np.abs(master_track)) > 0:
        master_track = master_track / np.max(np.abs(master_track))
        
    return (master_track * 32767).astype(np.int16)

# ==========================================
# 🎨 2. หน้าจอ UI รกๆ จัดเต็มสูตรพี่
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 5s ease infinite;
    }
    @keyframes RainbowFlow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    h1, h2, p, label { color: #FFFFFF !important; text-shadow: 2px 2px 5px #000; font-family: 'Courier New', monospace; }
    .stCheckbox { background: rgba(0,0,0,0.8); border: 1px solid #444; border-radius: 5px; padding: 10px; }
    .stCheckbox:has(input:checked) { border: 2px solid #00ff00; box-shadow: 0 0 15px #00ff00; }
    div[data-testid="stButton"]:nth-child(1) button { background: linear-gradient(180deg, #ff0000, #660000) !important; color: white !important; border-radius: 10px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ส่วนหัว
c1, c2 = st.columns([2, 1])
c1.markdown("<h1>SYNAPSE: REAL AUDIO ENGINE</h1>", unsafe_allow_html=True)
c2.markdown(f"<h1 style='color:#00ff00; text-align:right;'>🕒 {time.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

# ==========================================
# 🎼 3. กระดาน 32 ช่อง
# ==========================================
st.divider()
st.write("🎹 MULTI-ARRAY SEQUENCER (32-STEP)")

# สร้างตัวแปรเก็บสถานะ 32 ช่อง
if 'steps' not in st.session_state:
    st.session_state.steps = [False] * 32

# สร้างตาราง 4 แถว แถวละ 8 ช่อง
for r in range(4):
    cols = st.columns(8)
    for c in range(8):
        idx = r * 8 + c
        with cols[c]:
            st.session_state.steps[idx] = st.checkbox(f"T{idx+1}", value=st.session_state.steps[idx], key=f"step_{idx}")

# ==========================================
# 🚀 4. ปุ่มลั่นเสียงมหาประลัย
# ==========================================
st.divider()
b_cols = st.columns(4)

with b_cols[0]:
    if st.button("🔴 PLAY (แดงเงา)", use_container_width=True):
        # 1. เช็คความเร็วจากเข็มวัด (สมมติ 128 BPM)
        bpm = 128 
        # 2. ส่ง Array 32 ช่องไปให้ Audio Engine คำนวณ
        audio_data = generate_32step_sequence(st.session_state.steps, bpm)
        
        # 3. แปลงตัวเลขเป็นไฟล์ .wav ชั่วคราวในพริบตา
        buf = io.BytesIO()
        wavfile.write(buf, 44100, audio_data)
        
        # 4. สั่งลำโพงให้ส่งเสียง!
        st.success(f"CALCULATION COMPLETE! บรรเลง ณ วินาทีที่ {time.strftime('%S')}")
        st.audio(buf, autoplay=True)

with b_cols[1]: 
    if st.button("🔵 COPY 1-8", use_container_width=True):
        st.session_state.steps = (st.session_state.steps[:8] * 4)[:32]
        st.rerun()
with b_cols[2]: 
    if st.button("🟣 CLEAR", use_container_width=True):
        st.session_state.steps = [False] * 32
        st.rerun()

st.sidebar.markdown(f"**DATE:** 6 มีนาคม 2026\n\n**STATUS:** 3000 HOURS OF TRUTH\n\n**สโลแกน:** อยู่นิ่งๆ ไม่เจ็บตัว")
