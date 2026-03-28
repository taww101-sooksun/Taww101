import streamlit as st
import os
import random
import streamlit.components.v1 as components

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบจำสถานะการเข้าใช้งาน (เพื่อแก้ปัญหา Autoplay)
if 'system_active' not in st.session_state:
    st.session_state.system_active = False
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#121212" 

# หน้าจอสำหรับกด "เข้าสู่ระบบ" ครั้งแรก (จำเป็นสำหรับเสียง)
if not st.session_state.system_active:
    st.markdown(f"<style>body {{ background-color: {st.session_state.bg_color}; }}</style>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; margin-top:20%; font-family:Orbitron;'>SYNAPSE ROOMS</h1>", unsafe_allow_html=True)
    if st.button("🚀 CLICK TO ACTIVATE SYSTEM", use_container_width=True):
        st.session_state.system_active = True
        st.rerun()
    st.stop()

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border-radius: 12px; margin-bottom: 15px; border: 4px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-family: 'Orbitron', sans-serif; font-size: 22px; color: {st.session_state.theme_color};
        text-shadow: 0px 0px 10px {st.session_state.theme_color}; margin: 0;
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    .stButton>button {{
        width: 100%; background-color: transparent !important; color: {st.session_state.theme_color} !important;
        border-radius: 10px !important; border: 4px solid {st.session_state.theme_color} !important;
    }}
    .stTextArea textarea {{ background-color: rgba(0,0,0,0.5) !important; color: {st.session_state.theme_color} !important; border: 4px solid {st.session_state.theme_color} !important; }}
    h1, h2, h3, p, span {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    
    /* Fallback Visual Box */
    .visual-box {{
        width: 100%; height: 300px; border: 4px dashed {st.session_state.theme_color};
        display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบจัดการเพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]
    base_name = os.path.splitext(current_song)[0]

    col_l, col_r = st.columns([1, 5])
    with col_l:
        if os.path.exists("logo2.jpg"): st.image("logo2.jpg", width=400)
    with col_r:
        st.title("🎸 SYNAPSE ROOMS 🎼 MUSIC")

    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    # --- ส่วนการแสดงวิดีโอ/ภาพ (Logic ใหม่ที่ทำได้จริง) ---
    found_visual = False
    
    # เช็คไฟล์วิดีโอ
    if os.path.exists(f"{base_name}.mp4"):
        st.video(f"{base_name}.mp4", loop=True, autoplay=True, muted=True)
        found_visual = True
    # เช็คไฟล์ภาพ (.jpg หรือ .png)
    else:
        for ext in [".jpg", ".png", ".jpeg"]:
            if os.path.exists(base_name + ext):
                st.image(base_name + ext, use_container_width=True)
                found_visual = True
                break
    
    # ถ้าไม่เจอเลย ให้ใช้ Visualizer จำลอง
    if not found_visual:
        st.markdown(f"<div class='visual-box'>NO VISUAL DATA FOR: {base_name}</div>", unsafe_allow_html=True)
    
    # เล่นเพลง (เปิด Autoplay)
    st.audio(current_song, autoplay=True)

    # --- 4. ระบบแชต & Playlist ---
    st.markdown("---")
    col_chat, col_list = st.columns([2, 1])

    with col_chat:
        st.subheader("🌐 PUBLIC LOBBY")
        CHAT_FILE = "public_chat.txt"
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                chat_data = "".join(f.readlines()[-10:])
        else:
            chat_data = "ยังไม่มีข้อความ..."
        st.text_area("Live Chat", value=chat_data, height=200, disabled=True, label_visibility="collapsed")
        
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...", key="chat_msg_input")
            if st.form_submit_button("SEND"):
                if msg:
                    with open(CHAT_FILE, "a", encoding="utf-8") as f:
                        f.write(f"> {msg}\n")
                    st.rerun()

    with col_list:
        st.subheader("🎧 PLAYLIST")
        with st.container(border=True, height=250):
            for i, song in enumerate(music_files):
                label = f"▶️ {song}" if i == st.session_state.song_index else f"{song}"
                if st.button(label, key=f"list_{i}"):
                    st.session_state.song_index = i
                    st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # JS สำหรับ Handle ระบบเสียง
    js_code = """
    <script>
    function handleAudio() {
        var audio = window.parent.document.querySelector('audio');
        var buttons = window.parent.document.querySelectorAll('button');
        if (audio) {
            audio.onended = function() {
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('เพลงถัดไป')) {
                        buttons[i].click(); break;
                    }
                }
            };
            if (audio.paused && audio.currentTime == 0) {
                audio.play().catch(e => console.log("Waiting for user..."));
            }
        }
    }
    setInterval(handleAudio, 1000);
    </script>
    """
    components.html(js_code, height=0)

else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์")
