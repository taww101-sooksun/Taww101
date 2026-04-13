import streamlit as st
import base64

# --- 1. Setup ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def setup_ui():
    # ใช้ f-string แยกตัวเลขออกมาเพื่อเลี่ยง Error จากตัวแปลภาษา
    px30 = "30px"
    st.markdown(f"""
        <style>
        header, footer, #MainMenu {{visibility: hidden;}}
        .stApp {{ background: #000; color: #00f2fe; }}
        .neon-text {{ 
            text-align: center; 
            color: #fff; 
            font-size: {px30}; 
            font-weight: bold;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 40px #00f2fe;
            animation: flicker 1.5s infinite alternate;
        }}
        @keyframes flicker {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}
        .stButton>button {{ border-radius: 10px; border: 1px solid #ff1744; background: rgba(0,0,0,0.5); color: white; }}
        </style>
    """, unsafe_allow_html=True)

def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{{data}}" style="width: 140px; filter: drop-shadow(0 0 10px #ff1744);"></div>', unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

# --- 2. Execution ---
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

setup_ui()
display_logo("logo1.png")

if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

# --- 3. Logic ---
if st.session_state.nav_level == "HOME":
    st.markdown("<div class='neon-text'>MAIN CENTER</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 CORE", key="b1", use_container_width=True):
            st.session_state.nav_level = "1"
            st.rerun()
    with c2:
        if st.button("📺 MEDIA", key="b2", use_container_width=True):
            st.session_state.nav_level = "2"
            st.rerun()

elif st.session_state.nav_level == "1":
    st.markdown("<div class='neon-text'>🎵 AUDIO & LYRICS</div>", unsafe_allow_html=True)
    try:
        st.audio("วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp3")
    except:
        st.warning("วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4")
    st.markdown("<div class='neon-text'>✨ อยู่นิ่งๆ ไม่เจ็บตัว ✨</div>", unsafe_allow_html=True)

else:
    st.write(f"LOCATION: {st.session_state.nav_level}")
