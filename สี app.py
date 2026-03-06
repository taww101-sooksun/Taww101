import streamlit as st
import numpy as np

# --- 📈 ฟังก์ชันวาด "กราฟความจริง" ---
def plot_waveform(s1_len, s2_tail, s3_gain):
    # จำลองคลื่นเสียงตามค่าที่พี่ปรับ
    t = np.linspace(0, s1_len, 200) # ตามความยาว Slider 1
    # คลื่นเสียงผสม (Sine + Noise) เพื่อให้กราฟดู "รก" และมีมิติ
    wave = np.sin(2 * np.pi * 5 * t) * np.exp(-(21-s2_tail) * t) * s3_gain
    noise = np.random.normal(0, 0.05, 200) * s3_gain # ใส่ Noise นิดๆ ให้ดูแพง
    return wave + noise

# --- 🎼 ส่วนของกระดาน 8 บรรทัด (8 Layers) ---
for row in range(8):
    with st.container():
        col_info, col_graph, col_grid = st.columns([1, 2, 3])
        
        with col_info:
            st.markdown(f"### 🎛️ L-{row+1}")
            st.image("Logo3.jpg", width=60)
            # 3 ปุ่มสไลด์ที่พี่มี
            s1 = st.slider("LEN", 0.1, 2.0, 0.5, key=f"len_{row}")
            s2 = st.slider("TAIL", 1, 20, 10, key=f"tail_{row}")
            s3 = st.slider("GAIN", 0.0, 2.0, 1.0, key=f"gain_{row}")

        with col_graph:
            # --- หน้าจอกราฟเสียง (Visualizer) ---
            st.markdown("<p style='color:#00ff00; font-size:10px;'>LIVE OSCILLOSCOPE</p>", unsafe_allow_html=True)
            data = plot_waveform(s1, s2, s3)
            # วาดกราฟเส้นสีเขียวสะท้อนแสง
            st.line_chart(data, height=150, use_container_width=True)

        with col_grid:
            # กระดานแบ่งห้อง 4 8 16 32
            st.write("GRID SELECTOR")
            sel_tab = st.radio(f"ROOM-{row+1}", ["4", "8", "16", "32"], horizontal=True, key=f"tab_{row}")
            
            # วาดปุ่มกดตามจำนวนห้องที่เลือก
            num_steps = int(sel_tab)
            grid_cols = st.columns(8) # แบ่งหน้าจอให้รกกำลังดี
            for n in range(num_steps):
                grid_cols[n % 8].checkbox(f"{n+1}", key=f"ch_{row}_{num_steps}_{n}")
        
    st.divider()
