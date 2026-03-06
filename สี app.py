import streamlit as st
import streamlit.components.v1 as components

# --- 🎭 1. มิติดีไซน์สไตล์ Logo3.jpg (Dark & Glow Orange) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FF7F50; }
    .fx-panel { 
        border: 1px solid #FF7F50; 
        border-radius: 15px; 
        padding: 15px; 
        background: #0a0a0a;
        box-shadow: 0 0 15px rgba(255, 127, 80, 0.2);
    }
    .neon-label { font-size: 12px; color: #FF7F50; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

st.image("Logo3.jpg", width=60)
st.markdown("<h3 style='margin:0;'>SYNAPSE FX CORE 1.1.1</h3>", unsafe_allow_html=True)

# --- 🎛️ 2. แผงควบคุม (Inputs & Effects) ---
with st.container():
    st.markdown("<div class='fx-panel'>", unsafe_allow_html=True)
    
    # ส่วนที่ 1: ตั้งค่าจังหวะและช่วงเวลา
    c1, c2, c3, c4 = st.columns(4)
    v1_range = c1.text_input("V1 (เริ่ม-จบ)", "1-4, 16-20")
    v2_range = c2.text_input("V2 (เริ่ม-จบ)", "1-16")
    bpm = c3.number_input("BPM", 60, 240, 120)
    stop_at = c4.number_input("STOP", 1, 100, 20)
    
    # ส่วนที่ 2: ปุ่มปรับเอฟเฟกต์ (3 ปุ่มสไลด์)
    st.markdown("<p class='neon-label'>🎚️ Effect Processor</p>", unsafe_allow_html=True)
    fx_col = st.columns(3)
    echo_val = fx_col[0].slider("ECHO (Delay)", 0.0, 0.8, 0.3)
    space_val = fx_col[1].slider("SPACE (Reverb)", 0.0, 0.9, 0.4)
    tone_val = fx_col[2].slider("TONE (Filter)", 200, 5000, 2000)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---
