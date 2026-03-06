import streamlit as st
import numpy as np
import time

# --- 🎭 1. มิติดีไซน์สไตล์เครื่องจักร (Neon Orange) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    .neon-text { color: #FF7F50; text-shadow: 0 0 10px #FF4500; font-weight: bold; }
    .big-clock { font-family: 'Courier New', monospace; font-size: 60px; color: #FF7F50; text-align: center; }
    /* จุดสถานะเสียง */
    .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin: 1px; }
    .v1-on { background-color: #FF4500; box-shadow: 0 0 5px #FF4500; }
    .v2-on { background-color: #00FFFF; box-shadow: 0 0 5px #00FFFF; }
    .off { background-color: #222; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว (Logo3.jpg) ---
c1, c2 = st.columns([1, 4])
with c1:
    try: st.image("Logo3.jpg", width=60)
    except: st.write("💠")
with c2:
    st.markdown("<h3 class='neon-text'>AUDIO CORE ENGINE</h3>", unsafe_allow_html=True)
    st.caption("ตรวจสอบคลื่นความจริง | อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 🎛️ 3. แผงควบคุมช่วงเวลา (ตามใจพี่) ---
with st.expander("🛠️ ตั้งค่าช่วงเสียง (V1, V2) และความเร็ว", expanded=True):
    col = st.columns(4)
    v1_range = col[0].text_input("V1 (เริ่ม-จบ)", "1-4, 16-20")
    v2_range = col[1].text_input("V2 (เริ่ม-จบ)", "1-16")
    bpm = col[2].number_input("BPM", 60, 240, 120)
    stop_at = col[3].number_input("STOP AT", 1, 100, 20)

# --- 📊 4. ส่วนแสดงผล "กราฟเสียง + นาฬิกา" ---
st.divider()
clock_place = st.empty()
graph_place = st.empty()
grid_place = st.empty()

def get_audio_data(is_active):
    # ถ้าช่วงนั้น "ดัง" ให้สร้างคลื่น Random สวยๆ ถ้า "เงียบ" ให้เป็นเส้นตรง
    if is_active:
        return np.random.uniform(-1, 1, 50)
    return np.zeros(50)

def draw_all(curr=0):
    # 1. วาดตารางจุดสถานะ (จิ๋ว)
    def parse(s):
        res = set()
        for p in s.split(','):
            if '-' in p:
                a, b = map(int, p.split('-')); res.update(range(a, b+1))
            else: res.add(int(p))
        return res
    
    v1_set, v2_set = parse(v1_range), parse(v2_range)
    is_v1_live = curr in v1_set
    is_v2_live = curr in v2_set

    # 2. วาดกราฟเสียง (Wave
