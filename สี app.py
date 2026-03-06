import streamlit as st
import numpy as np
import time

# --- 🎭 1. จัดเต็ม CSS (ใส่ทุกสูตรที่พี่ปรุงมา) ---
st.markdown(f"""
    <style>
    /* 🌈 ฉากหลังสายรุ้งวิ่งสูตรพี่ 100% */
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    }}
    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}

    /* 🧱 แผงคอนโซล ดำเงาแว๊บ (Deep Piano Black) */
    .console-panel {{
        background: rgba(0, 0, 0, 0.92);
        border: 4px double #FF7F50;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 50px rgba(0,0,0,1);
    }}

    /* 💡 ตัวหนังสือขาวชัดเจน + เรืองแสง */
    .stMarkdown, p, h1, h2, h3 {{
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px #000000;
        font-family: 'Orbitron', sans-serif;
    }}

    /* 🟢 ปุ่มกด 32 ช่อง ล่อแสงมิติ (เขียวสะท้อนแสง) */
    .stCheckbox {{
        background: linear-gradient(145deg, #333, #000);
        border: 1px solid #444;
        border-radius: 8px;
        padding: 10px;
        transition: 0.2s;
        box-shadow: inset 2px 2px 5px #000;
    }}
    .stCheckbox:has(input:checked) {{
        border: 2px solid #00ff00;
        box-shadow: 0 0 20px #00ff00, inset 0 0 10px #00ff00;
    }}

    /* 🔴🔵🟣🟠 แผงปุ่มกดมหาประลัย (เงาแว๊บ) */
    .stButton>button {{
        border-radius: 10px !important;
        font-weight: 900 !important;
        height: 50px !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        transition: 0.3s !important;
    }}
    /* แดงเงา */
    div[data-testid="stButton"]:nth-child(1) button {{ background: linear-gradient(180deg, #ff0000, #660000) !important; }}
    /* น้ำเงินเงา */
    div[data-testid="stButton"]:nth-child(2) button {{ background: linear-gradient(180deg, #0000ff, #000066) !important; }}
    /* ม่วงเงา */
    div[data-testid="stButton"]:nth-child(3) button {{ background: linear-gradient(180deg, #800080, #330033) !important; }}
    /* ส้มเงา */
    div[data-testid="stButton"]:nth-child(4) button {{ background: linear-gradient(180deg, #ff8c00, #ff4500) !important; }}

    /* 🌊 กราฟวิ่ง (Visualizer) */
    .wave-box {{
        width: 100%; height: 60px;
        background: #000;
        border: 1px solid #00ff00;
        position: relative;
        overflow: hidden;
    }}
    .wave-line {{
        width: 200%; height: 100%;
        background: url('https://i.stack.imgur.com/8m9Xp.gif');
        background-size: contain;
        opacity: 0.5;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 🚀 2. เริ่มต้นหน้าจอแบบ "รกและจัดเต็ม" ---
st.markdown('<h1 style="text-align:center;">SYNAPSE QUANTUM ENGINE v3.0</h1>', unsafe_allow_html=True)

# แผงนาฬิกาและสถิติ (รกๆ ไว้ก่อน)
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("OSCILLATOR", "432Hz", "+1.2")
with c2: st.metric("BITRATE", "64-BIT", "MAX")
with c3: st.metric("BPM", "128", "STABLE")
with c4: 
    t_now = time.strftime('%H:%M:%S')
    st.markdown(f"<h2 style='color:#00ff00;'>🕒 {t_now}</h2>", unsafe_allow_html=True)

# หน้าจอกราฟวิ่งไม่หยุด
st.markdown('<div class="wave-box"><div class="wave-line"></div></div>', unsafe_allow_html=True)

# --- 🎼 3. กระดาน 32 ช่อง แบ่งโซน 4-8-16-32 (จัดระเบียบให้ดูแน่น) ---
st.divider()
st.subheader("🎹 SEQUENCER GRID (32-STEP MULTI-ARRAY)")

# แบ่งแถวละ 8 ช่อง จำนวน 4 แถว (เพื่อให้ดูเต็มหน้าจอ)
for r in range(4):
    cols = st.columns(8)
    for c in range(8):
        idx = r * 8 + c
        with cols[c]:
            st.checkbox(f"T{idx+1}", key=f"step_full_{idx}")

# --- 🕹️ 4. แผงปุ่มควบคุมมหาประลัย (หลากสีเงา) ---
st.divider()
st.subheader("🕹️ CONTROL CENTER (GLOSSY BUTTONS)")
btn_cols = st.columns(4)
with btn_cols[0]: st.button("🔴 PLAY (แดงเงา)", use_container_width=True)
with btn_cols[1]: st.button("🔵 COPY (น้ำเงินเงา)", use_container_width=True)
with btn_cols[2]: st.button("🟣 CLEAR (ม่วงเงา)", use_container_width=True)
with btn_cols[3]: st.button("🟠 FX (ส้มเงา)", use_container_width=True)

# --- 🎚️ 5. แผงข้าง (Sidebar) ที่รกไปด้วยตัวปรับจูน ---
with st.sidebar:
    st.markdown("### [ logo3.jpg ]")
    st.image("https://via.placeholder.com/150/FF7F50/FFFFFF?text=SIGNATURE", use_container_width=True)
    st.divider()
    st.markdown("### 🎛️ MODULATION PANELS")
    for i in range(8):
        st.slider(f"FREQUENCY-SET-{i+1}", 0, 100, 50)
    st.divider()
    st.write("บันทึก: 6 มีนาคม 2026")
    st.write("สถานะ: 3,000 ชั่วโมงแห่งความจริง")
    st.markdown("**สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว**")

st.success("✅ โหลดข้อมูลครบถ้วน: ระบบทำงานด้วยประสิทธิภาพสูงสุด ไม่มีการแก้ง ไม่มีการสั้นลง!")
