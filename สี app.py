import streamlit as st
import os
import base64
import json
import streamlit.components.v1 as components

# --- 1. SETUP UI ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        .stButton>button {
            border-radius: 15px; border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1); color: white;
            height: 100px; font-size: 18px; transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe; color: #000; box-shadow: 0 0 20px #00f2fe;
        }
        .neon-text {
            text-align: center; color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. SIDEBAR PLAYER (เพื่อให้เพลงไม่ดับเวลาเปลี่ยนห้อง) ---
with st.sidebar:
    st.markdown("<h3 class='neon-text'>SYNAPSE PLAYER</h3>", unsafe_allow_html=True)
    
    # สแกนไฟล์เพลง
    song_list = [f for f in os.listdir('.') if f.endswith('.mp3')]
    
    if song_list:
        # ฟังก์ชันแปลงไฟล์เป็น Base64 (เพื่อให้ JS เล่นได้จริง)
        def get_audio_base64(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()

        # สร้างเพลย์ลิสต์ในรูปแบบ JSON
        playlist_data = []
        for s in song_list[:5]: # จำกัดไว้ 5 เพลงก่อนเพื่อความเร็วในการโหลด
            playlist_data.append({
                "name": s,
                "src": f"data:audio/mp3;base64,{get_audio_base64(s)}"
            })
        
        player_js = f"""
        <div style="background:#111; padding:15px; border-radius:15px; border:1px solid #00f2fe; color:white; text-align:center;">
            <div id="t-name" style="font-size:12px; margin-bottom:10px;">เตรียมระบบ...</div>
            <audio id="player" controls style="width:100%; height:30px;"></audio>
            <button onclick="playNext()" style="margin-top:10px; width:100%; background:#00f2fe; border:none; border-radius:5px; cursor:pointer;">NEXT ⏭️</button>
        </div>
        <script>
            const songs = {json.dumps(playlist_data)};
            let cur = 0;
            const p = document.getElementById('player');
            const t = document.getElementById('t-name');

            function loadS(i) {{
                t.innerText = "Playing: " + songs[i].name;
                p.src = songs[i].src;
                p.play();
            }}
            function playNext() {{
                cur = (cur + 1) % songs.length;
                loadS(cur);
            }}
            p.onended = playNext;
            // เริ่มเพลงแรกเมื่อพร้อม
            setTimeout(() => loadS(0), 1000);
        </script>
        """
        components.html(player_js, height=180)
    else:
        st.caption("ไม่มีไฟล์ .mp3 ในโฟลเดอร์")

# --- 3. NAVIGATION & PAGES ---
if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 MUSIC SYSTEM"): st.session_state.page = "1"; st.rerun()
        if st.button("✨ NEON GEN"): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("🏠 BACK HOME"): st.session_state.page = "HOME"; st.rerun()

elif st.session_state.page == "5":
    if st.button("⬅️ BACK"): st.session_state.page = "HOME"; st.rerun()
    st.header("✨ NEON LYRICS")
    user_text = st.text_area("ใส่เนื้อเพลง:", "อยู่นิ่งๆ\nไม่เจ็บตัว", height=100)
    glow_color = st.color_picker("สีไฟนีออน:", "#FF007F")
    
    st.markdown(f"""
        <style>
        @keyframes flicker {{
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{
                text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px {glow_color}, 0 0 40px {glow_color};
            }}
            20%, 22%, 55% {{ text-shadow: none; }}
        }}
        .neon-box {{
            background: #000; padding: 40px; border: 2px solid {glow_color};
            border-radius: 20px; text-align: center;
            animation: flicker 3s infinite;
        }}
        .txt {{ color: #fff; font-size: 30px; white-space: pre-wrap; }}
        </style>
        <div class="neon-box"><div class="txt">{user_text}</div></div>
    """, unsafe_allow_html=True)
