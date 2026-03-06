import streamlit as st
import time

# --- 🎭 1. ใส่โลโก้ logo3.jpg (ถ้าพี่มีไฟล์ในโฟลเดอร์เดียวกัน) ---
try:
    st.image("logo3.jpg", width=200)
except:
    st.markdown("<h1 style='color:white; text-align:center;'>[ logo3.jpg ]</h1>", unsafe_allow_html=True)

# --- 🌈 2. ใส่ CSS ปรุงแต่งสีและแสง (ตามสูตรพี่) ---
st.markdown(f"""
    <style>
    /* พื้นหลังดำเงาแว๊บ (Deep Black) */
    .stApp {{
        background-color: #000000;
        background-image: radial-gradient(#1a1a1a 1px, transparent 1px);
        background-size: 20px 20px;
    }}

    /* ตัวหนังสือขาวชัดเจน (Stark White) */
    h1, h2, h3, p, label {{
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif;
    }}

    /* ปรับแต่ง Tabs ให้ดูเงา */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #111;
        border-radius: 10px;
        border: 1px solid #333;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #888;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: #ffffff;
        background-color: #222;
        border-radius: 10px;
    }}

    /* 🔴🔵🟣🟢 ปรับแต่งปุ่มกดให้มี "มิติลาแสง" (Glossy/Neon) */
    .stCheckbox {{
        background: linear-gradient(145deg, #222, #000); /* พื้นหลังปุ่มเงา */
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #333;
        transition: 0.3s;
        box-shadow: 3px 3px 5px #000, -1px -1px 2px #333; /* มิตินูน */
    }}

    /* เมื่อติ๊กปุ่ม (Active) ให้แสงสะท้อน */
    .stCheckbox:has(input:checked) {{
        border: 2px solid #00ff00; /* เขียวสะท้อนแสง */
        box-shadow: 0 0 15px #00ff00, inset 0 0 5px #00ff00; /* แสงสะท้อนมิติ */
    }}

    /* ปรับแต่งปุ่มกด Play/Copy (แดง/น้ำเงิน/ม่วง เงา) */
    .stButton>button {{
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s !important;
    }}
    /* ปุ่ม Play (แดงเงา) */
    div[data-testid="stButton"] button:first-child {{
        background: linear-gradient(145deg, #ff4b4b, #8b0000) !important;
        border: 2px solid #ff0000 !important;
        color: white !important;
        box-shadow: 0 0 10px #ff0000 !important;
    }}
    /* ปุ่ม Copy (น้ำเงินเงา) */
    div[data-testid="stButton"] + div[data-testid="stButton"] button {{
        background: linear-gradient(145deg, #4b4bff, #00008b) !important;
        border: 2px solid #0000ff !important;
        color: white !important;
        box-shadow: 0 0 10px #0000ff !important;
    }}
    /* ปุ่ม Clear (ม่วงเงา) */
    div[data-testid="stButton"] + div[data-testid="stButton"] + div[data-testid="stButton"] button {{
        background: linear-gradient(145deg, #8b4bcf, #4b0082) !important;
        border: 2px solid #800080 !important;
        color: white !important;
        box-shadow: 0 0 10px #800080 !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# --- 🕒 ส่วนแสดงวินาที (Real-time Clock) ---
col_logo, col_clock = st.columns([1, 2])
with col_clock:
    t_now = time.strftime('%H:%M:%S')
    st.markdown(f"<h1 style='text-align:right; color:#00ff00;'>🕒 {t_now}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:right; color:white;'>\"อยู่นิ่งๆ ไม่เจ็บตัว\"</p>", unsafe_allow_html=True)

# --- 🎼 กระดานห้องเพลงแบ่งโซน (4-8-16-32) ---
st.divider()
st.subheader("🎹 ห้องจังหวะเพลง (ปุ่มกดล่อแสง)")

tab1, tab2, tab3, tab4 = st.tabs(["ห้อง 4", "ห้อง 8", "ห้อง 16", "ห้อง 32"])

def create_glossy_grid(num):
    cols = st.columns(8)
    for i in range(num):
        with cols[i % 8]:
            # ปุ่ม checkbox ที่ถูกปรุงแต่งด้วย CSS ให้ดูมีมิติ
            st.checkbox(f"P-{i+1}", key=f"gbeat_{num}_{i}")

with tab1: create_glossy_grid(4)
with tab2: create_glossy_grid(8)
with tab3: create_glossy_grid(16)
with tab4: create_glossy_grid(32)

# --- 🚀 ปุ่มสั่งงานหลัก (จัดเต็ม แดง/น้ำเงิน/ม่วง เงา) ---
st.divider()
c1, c2, c3 = st.columns(3)
with c1: st.button("▶️ PLAY LOOP (แดงเงา)", use_container_width=True)
with c2: st.button("📋 COPY 4-STEPS (น้ำเงินเงา)", use_container_width=True)
with c3: st.button("🗑️ CLEAR ALL (ม่วงเงา)", use_container_width=True)

st.info("💡 เครื่องนี้คำนวณเสียงในพริบตา ด้วยคณิตศาสตร์ที่พี่คิดเอง!")
