import streamlit as st
import os
import random
import streamlit.components.v1 as components

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#121212" 

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    else:
        st.write("📌 [ยังไม่มีไฟล์ logo2.jpg]")
        
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp {{
        background-color: {st.session_state.bg_color} !important;
        color: {st.session_state.theme_color} !important;
    }}

    /* ปรับแต่ง Tabs ให้เข้ากับธีม */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 20px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: transparent !important;
        border: 1px solid {st.session_state.theme_color} !important;
        border-radius: 10px 10px 0 0;
        color: {st.session_state.theme_color} !important;
        padding: 10px 20px;
    }}
    
    .stTextArea textarea {{
        background-color: rgba(0,0,0,0.5) !important;
        color: {st.session_state.theme_color} !important;
        border: 1px solid {st.session_state.theme_color} !important;
        font-family: 'Courier New', Courier, monospace;
    }}

    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap;
        background: rgba(0,0,0,0.6); padding: 15px 0;
        border-radius: 12px; margin-bottom: 15px;
        border: 2px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%;
        animation: marquee 20s linear infinite;
        font-family: 'Orbitron', sans-serif; font-size: 22px;
        color: {st.session_state.theme_color};
        text-shadow: 0px 0px 10px {st.session_state.theme_color}; margin: 0;
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    .stButton>button {{
        width: 100%; background-color: transparent !important;
        color: {st.session_state.theme_color} !important;
        border-radius: 10px !important; border: 1px solid {st.session_state.theme_color} !important;
    }}
    
    h1, h2, h3, p, span {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบจัดการเพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    col_l, col_r = st.columns([1, 5])
    with col_l:
        if os.path.exists("logo2.jpg"):
            st.image("logo2.jpg", width=500)
    with col_r:
        st.title("🎸 อยู่นิ่งๆไม่เจ็บตัว 🎼 MUSIC")

    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    st.audio(current_song)

    # --- 4. ระบบแชต (Public & Private) ---
    st.markdown("---")
    tab_music, tab_chat, tab_private = st.tabs(["🎧 Playlist", "🌐 Global Chat", "🔒 My Note"])

    with tab_music:
        st.subheader("🎧 รายชื่อเพลง🎸")
        with st.container(border=True, height=200):
            for i, song in enumerate(music_files):
                label = f"▶️ {i+1}. {song}" if i == st.session_state.song_index else f"{i+1}. {song}"
                if st.button(label, key=f"box_{i}"):
                    st.session_state.song_index = i
                    st.rerun()

    with tab_chat:
        CHAT_FILE = "public_chat.txt"
        st.subheader("💬 Community Lobby")
        
        # Load chat
        display_chat = ""
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                display_chat = "".join(f.readlines()[-15:])
        
        st.text_area("Chat Logs", value=display_chat if display_chat else "No messages yet...", height=200, disabled=True)
        
        with st.form("public_chat_form", clear_on_submit=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                u_msg = st.text_input("พิมพ์ข้อความที่นี่...", key="public_msg")
            with c2:
                if st.form_submit_button("SEND") and u_msg:
                    with open(CHAT_FILE, "a", encoding="utf-8") as f:
                        f.write(f"> {u_msg}\n")
                    st.rerun()

    with tab_private:
        st.subheader("🔒 Personal Space")
        if 'notes' not in st.session_state: st.session_state.notes = []
        
        p_note = st.text_input("จดบันทึกส่วนตัว...", key="p_note_in")
        if st.button("บันทึก"):
            if p_note:
                st.session_state.notes.append(p_note)
                st.rerun()
        for n in reversed(st.session_state.notes):
            st.write(f"• {n}")

    # ปุ่มควบคุมเพลงด้านล่าง
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

        # --- 5. JavaScript (Safe Version: No f-string to avoid SyntaxError) ---
    js_code = """
    <script>
    var fadeDuration = 12; 
    function handleAudio() {
        var audio = window.parent.document.querySelector('audio');
        var buttons = window.parent.document.querySelectorAll('button');
        if (audio) {
            // ระบบ Fade In / Out
            if (audio.currentTime < fadeDuration && !audio.paused) {
                audio.volume = Math.min(audio.currentTime / fadeDuration, 1);
            } else if (audio.duration - audio.currentTime < fadeDuration && !audio.paused) {
                audio.volume = Math.max((audio.duration - audio.currentTime) / fadeDuration, 0);
            } else { 
                audio.volume = 1; 
            }

            // ระบบเล่นเพลงถัดไปอัตโนมัติ
            audio.onended = function() {
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('เพลงถัดไป')) {
                        buttons[i].click(); 
                        break;
                    }
                }
            };
        }
    }
    setInterval(handleAudio, 500);
    </script>
    """
    components.html(js_code, height=0)
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
