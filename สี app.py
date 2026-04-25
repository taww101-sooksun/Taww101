import streamlit as st
import os
import base64

# 1. การตั้งค่าระบบ (System Configuration)
st.set_page_config(page_title="SYNAPSE MASTER", layout="wide")

def load_local_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# เลือกรูปโลโก้ที่สวยที่สุดของพี่
logo_b64 = load_local_image("โลโก้1.png") 

# 2. ส่วนของ CSS (ความพิเศษด้านดีไซน์)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000; color: #ffffff; }}
    
    /* เอฟเฟกต์เรืองแสงให้โลโก้ */
    .logo-container {{
        text-align: center;
        padding: 10px;
        filter: drop-shadow(0 0 15px #ff00ea);
    }}
    
    /* สไตล์การ์ด Deck A/B */
    .deck-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #00ff00;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        margin-bottom: 10px;
    }}
    
    /* ปรับแต่งปุ่ม Selectbox */
    div[data-baseweb="select"] > div {{
        background-color: #111 !important;
        color: white !important;
        border: 1px solid #ff00ea !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 3. ส่วนแสดงผล Header
if logo_b64:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" width="180"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ff00ea; text-shadow: 0 0 10px #ff00ea;'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00ff00;'>สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)

# 4. ส่วนจัดการไฟล์เพลง (Core Logic)
songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if songs:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="deck-card">', unsafe_allow_html=True)
        st.subheader("🎵 DECK A")
        song_a = st.selectbox("เลือกแทร็ก", songs, key="deck_a")
        st.audio(song_a)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="deck-card" style="border-color: #ff00ea; box-shadow: 0 0 10px rgba(255, 0, 234, 0.2);">', unsafe_allow_html=True)
        st.subheader("🎵 DECK B")
        # เลือกเพลงถัดไปให้อัตโนมัติในช่อง B
        default_b = 1 if len(songs) > 1 else 0
        song_b = st.selectbox("เลือกแทร็ก", songs, index=default_b, key="deck_b")
        st.audio(song_b)
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. ฟีเจอร์พิเศษ: Global Playlist Navigator
    with st.expander(f"📂 GLOBAL PLAYLIST ({len(songs)} TRACKS)"):
        for i, s in enumerate(songs, 1):
            st.write(f"{i}. {s}")

else:
    st.error("⚠️ ไม่พบไฟล์เพลงในระบบ กรุณาเช็คโฟลเดอร์บน GitHub")

# 6. แถบสถานะด้านล่าง
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #000; border-top: 1px solid #00ff00; padding: 5px;">
        <marquee style="color: #00ff00;">
            SYSTEM ONLINE | {len(songs)} TRACKS READY | PLAYING: {song_a if songs else 'NONE'} & {song_b if songs else 'NONE'} | MASTERED BY TA101
        </marquee>
    </div>
""", unsafe_allow_html=True)
