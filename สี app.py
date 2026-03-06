import streamlit as st
import time

# --- 🎭 1. ดีไซน์ (ดำเงา-ส้มสว่าง) ---
st.markdown("""
    <style>
    .big-clock { font-size: 100px; font-weight: bold; color: #00ff00; text-align: center; }
    .active-v1 { background-color: #FF7F50; border-radius: 5px; height: 25px; }
    .active-v2 { background-color: #00ffff; border-radius: 5px; height: 25px; }
    .idle { background-color: #333; border-radius: 5px; height: 25px; }
    .current-marker { border: 2px solid #fff; box-shadow: 0 0 10px #fff; transform: scale(1.1); }
    </style>
""", unsafe_allow_html=True)

st.image("Logo3.jpg", width=80)
st.title("🎯 SYNAPSE: CUSTOM SEQUENCE")

# --- 🛠️ 2. แผงควบคุม (3 ปุ่มสไลด์ + ความเร็ว) ---
c1, c2, c3, c4 = st.columns(4)
with c1: s_len = st.slider("LEN", 0.1, 2.0, 1.0)
with c2: s_tail = st.slider("TAIL", 1, 20, 10)
with c3: s_gain = st.slider("GAIN", 0.0, 2.0, 1.0)
with c4: bpm = st.slider("SPEED (BPM)", 60, 240, 120)

# --- 📝 3. ส่วน "ตามใจพี่" (กำหนดช่วงห้อง) ---
st.markdown("### ✍️ กำหนดช่วงเวลา (สั่งตามใจ)")
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("🎵 **เสียงที่ 1**")
    v1_start = st.number_input("เริ่มห้องที่ (V1):", value=1, min_value=1)
    v1_end = st.number_input("จบห้องที่ (V1):", value=4, min_value=1)

with col_v2:
    st.markdown("🎵 **เสียงที่ 2**")
    v2_start = st.number_input("เริ่มห้องที่ (V2):", value=1, min_value=1)
    v2_end = st.number_input("จบห้องที่ (V2):", value=16, min_value=1)

# หาจุดจบที่ไกลที่สุดเพื่อกำหนดความยาวนาฬิกา
max_rooms = max(v1_end, v2_end, 20)

# --- 📊 4. ตาราง Visualizer วิ่งตามนาฬิกา ---
grid_placeholder = st.empty()

def draw_custom_grid(current_x=0):
    st.write(f"ตาราง 1-{max_rooms} ห้อง")
    
    # แถวเสียง 1
    v1_cols = st.columns(max_rooms)
    for i in range(max_rooms):
        room_num = i + 1
        is_on = (v1_start <= room_num <= v1_end)
        style = "active-v1" if is_on else "idle"
        marker = "current-marker" if room_num == current_x else ""
        v1_cols[i].markdown(f"<div class='{style} {marker}'></div>", unsafe_allow_html=True)
        v1_cols[i].caption(f"{room_num}")

    # แถวเสียง 2
    v2_cols = st.columns(max_rooms)
    for i in range(max_rooms):
        room_num = i + 1
        is_on = (v2_start <= room_num <= v2_end)
        style = "active-v2" if is_on else "idle"
        marker = "current-marker" if room_num == current_x else ""
        v2_cols[i].markdown(f"<div class='{style} {marker}'></div>", unsafe_allow_html=True)

with grid_placeholder.container():
    draw_custom_grid()

# --- 🚀 5. ปุ่ม PLAY มหาประลัย ---
st.divider()
if st.button("🔴 PLAY: เริ่มเดินตามคำสั่ง", use_container_width=True):
    clock_placeholder = st.empty()
    step_time = 60 / bpm
    
    for x in range(1, max_rooms + 1):
        clock_placeholder.markdown(f"<div class='big-clock'>{x}</div>", unsafe_allow_html=True)
        with grid_placeholder.container():
            draw_custom_grid(current_x=x)
        time.sleep(step_time)
        
    st.success(f"🏁 ระบบหยุดทำงานที่ห้อง {max_rooms} เรียบร้อย!")
