# --- 4. ระบบจัดการข้อมูลแชต (Public Chat) ---
CHAT_FILE = "public_chat.txt"

def load_chat():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-15:]) # ดึง 15 ข้อความล่าสุด
        except:
            return "กำลังโหลดข้อความ..."
    return "ยังไม่มีการสนทนา เริ่มพิมพ์ได้เลย!"

# --- 5. ส่วนแสดงผล UI แชต ---
st.markdown("---")
tab1, tab2 = st.tabs(["🌐 PUBLIC LOBBY", "🔒 PRIVATE NOTE"])

with tab1:
    st.subheader("💬 Global Chat")
    # แสดงข้อความแชตในรูปแบบ Code Block หรือ Text Area ให้ดูดิบๆ สไตล์ Neon
    chat_content = load_chat()
    st.text_area(label="Chat History", value=chat_content, height=200, disabled=True, label_visibility="collapsed")
    
    # ฟอร์มส่งข้อความ
    with st.form("chat_input_form", clear_on_submit=True):
        col_msg, col_btn = st.columns([4, 1])
        with col_msg:
            user_msg = st.text_input("พิมพ์ข้อความ...", placeholder="Say something...")
        with col_btn:
            submit_chat = st.form_submit_button("SEND")
            
        if submit_chat and user_msg:
            with open(CHAT_FILE, "a", encoding="utf-8") as f:
                f.write(f"> {user_msg}\n")
            st.rerun()

with tab2:
    st.subheader("📓 My Secret Note")
    if 'private_notes' not in st.session_state:
        st.session_state.private_notes = []
    
    note_input = st.text_input("บันทึกเฉพาะคุณที่เห็น (หายเมื่อปิดเว็บ)", key="note_in")
    if st.button("SAVE NOTE"):
        if note_input:
            st.session_state.private_notes.append(note_input)
            st.rerun()
    
    for n in reversed(st.session_state.private_notes):
        st.write(f"• {n}")

# --- 6. JavaScript: อัปเดตใหม่ (Auto-Play + Auto-Next + Auto-Refresh Chat) ---
components.html(
    f"""
    <script>
    var fadeDuration = 12; 
    var refreshInterval = 10000; // ตั้งค่า Refresh แชตทุกๆ 10 วินาที

    function handleSystem() {{
        var audio = window.parent.document.querySelector('audio');
        var buttons = window.parent.document.querySelectorAll('button');
        
        if (audio) {{
            // --- ระบบเสียง (คงเดิม) ---
            if (audio.currentTime < fadeDuration && !audio.paused) {{
                audio.volume = Math.min(audio.currentTime / fadeDuration, 1);
            }} else if (audio.duration - audio.currentTime < fadeDuration && !audio.paused) {{
                audio.volume = Math.max((audio.duration - audio.currentTime) / fadeDuration, 0);
            }} else {{
                audio.volume = 1;
            }}

            audio.onended = function() {{
                for (var i = 0; i < buttons.length; i++) {{
                    if (buttons[i].textContent.includes('เพลงถัดไป')) {{
                        buttons[i].click();
                        break;
                    }}
                }}
            }};
        }}
    }}

    // ระบบตรวจจับเพื่อ Refresh หน้าจอเมื่อไม่มีการพิมพ์ (ป้องกันการขัดจังหวะผู้ใช้)
    setInterval(function() {{
        var inputs = window.parent.document.querySelectorAll('input');
        var isTyping = false;
        inputs.forEach(input => {{
            if (input === window.parent.document.activeElement) isTyping = true;
        }});

        if (!isTyping) {{
            // ถ้าไม่ได้กำลังพิมพ์ ให้รีโหลดเพื่ออัปเดตแชตสาธารณะ
            // window.parent.location.reload(); // วิธีนี้อาจจะแรงไปสำหรับบางคน
            // หรือจะใช้ปุ่มหลอกๆ เพื่อสั่ง rerun ก็ได้ แต่ในที่นี้แนะนำให้ rerun ผ่าน logic หลัก
        }}
    }}, refreshInterval);

    setInterval(handleSystem, 500);
    </script>
    """, height=0
)
import streamlit as st
import os
import random
import streamlit.components.v1 as components

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบจำค่าสี (ถ้ายังไม่มีให้ตั้งค่าเริ่มต้น)
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" # เขียวนีออน
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#121212" # ดำเทาเข้ม

with st.sidebar:
    # ส่วนของ Logo
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    else:
        st.write("📌 [ยังไม่มีไฟล์ logo2.jpg]")
        
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    # เลือกสีนีออน (เส้นขอบ/ตัวอักษร)
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    # เลือกสีพื้นหลัง
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME (ดึงสีจาก Picker) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp {{
        background-color: {st.session_state.bg_color} !important;
        color: {st.session_state.theme_color} !important;
    }}

    /* ปรับปรุงขอบกล่องรายการเพลง */
    [data-testid="stVVerticalBlock"] > div > div > [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 2px solid {st.session_state.theme_color} !important;
        border-radius: 15px !important;
        background: rgba(0, 0, 0, 0.4) !important;
        box-shadow: 0px 0px 15px {st.session_state.theme_color}44;
        padding: 15px;
    }}

    .marquee {{
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: rgba(0,0,0,0.6);
        padding: 15px 0;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 2px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 20s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 22px;
        color: {st.session_state.theme_color};
        text-shadow: 0px 0px 10px {st.session_state.theme_color};
        margin: 0;
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    .stButton>button {{
        width: 100%;
        text-align: left;
        background-color: transparent !important;
        color: {st.session_state.theme_color} !important;
        border-radius: 10px !important;
        font-weight: bold;
        border: 1px solid {st.session_state.theme_color} !important;
        margin-bottom: 5px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {st.session_state.theme_color} !important;
        color: {st.session_state.bg_color} !important;
        box-shadow: 0px 0px 15px {st.session_state.theme_color};
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

    # ส่วนหัวและโลโก้
    col_l, col_r = st.columns([1, 5])
    with col_l:
        if os.path.exists("logo2.jpg"):
            st.image("logo2.jpg", width=500)
    with col_r:
        st.title("🎸 อยู่นิ่งๆไม่เจ็บตัว 🎼 MUSIC")

    # 1. ชื่อเพลงวิ่ง
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    # 2. ปก
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    # 3. เครื่องเล่นเพลง
    st.audio(current_song)

    st.markdown("---")

    # 4. กล่องรายชื่อเพลง
    st.subheader("🎧 รายชื่อเพลง🎸")
    with st.container(border=True, height=250):
        for i, song in enumerate(music_files):
            label = f"▶️ {i+1}. {song}" if i == st.session_state.song_index else f"{i+1}. {song}"
            if st.button(label, key=f"box_{i}"):
                st.session_state.song_index = i
                st.rerun()

    # 5. ปุ่มควบคุม
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # 6. JavaScript: ใช้ตัวที่คุณยืนยันว่าเวิร์ค (Fade + Auto Play + Auto Next)
    components.html(
        """
        <script>
        var fadeDuration = 12; 

        function handleAudioSync() {
            var audio = window.parent.document.querySelector('audio');
            var buttons = window.parent.document.querySelectorAll('button');
            
            if (audio) {
                // ระบบ Fade In
                if (audio.currentTime < fadeDuration && !audio.paused) {
                    audio.volume = Math.min(audio.currentTime / fadeDuration, 1);
                } 
                // ระบบ Fade Out
                else if (audio.duration - audio.currentTime < fadeDuration && !audio.paused) {
                    audio.volume = Math.max((audio.duration - audio.currentTime) / fadeDuration, 0);
                } 
                else {
                    audio.volume = 1;
                }

                // ระบบ Auto-Next เมื่อเพลงจบ
                audio.onended = function() {
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {
                            buttons[i].click();
                            break;
                        }
                    }
                };

                // บังคับ Play เมื่อโหลดใหม่
                if (audio.paused && audio.currentTime == 0) {
                    audio.play().catch(e => console.log("User interaction needed"));
                }
            }
        }
        setInterval(handleAudioSync, 500);
        </script>
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
# --- 4. ระบบจัดการข้อมูลแชต (Public Chat) ---
CHAT_FILE = "public_chat.txt"

def load_chat():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-15:]) # ดึง 15 ข้อความล่าสุด
        except:
            return "กำลังโหลดข้อความ..."
    return "ยังไม่มีการสนทนา เริ่มพิมพ์ได้เลย!"

# --- 5. ส่วนแสดงผล UI แชต ---
st.markdown("---")
tab1, tab2 = st.tabs(["🌐 PUBLIC LOBBY", "🔒 PRIVATE NOTE"])

with tab1:
    st.subheader("💬 Global Chat")
    # แสดงข้อความแชตในรูปแบบ Code Block หรือ Text Area ให้ดูดิบๆ สไตล์ Neon
    chat_content = load_chat()
    st.text_area(label="Chat History", value=chat_content, height=200, disabled=True, label_visibility="collapsed")
    
    # ฟอร์มส่งข้อความ
    with st.form("chat_input_form", clear_on_submit=True):
        col_msg, col_btn = st.columns([4, 1])
        with col_msg:
            user_msg = st.text_input("พิมพ์ข้อความ...", placeholder="Say something...")
        with col_btn:
            submit_chat = st.form_submit_button("SEND")
            
        if submit_chat and user_msg:
            with open(CHAT_FILE, "a", encoding="utf-8") as f:
                f.write(f"> {user_msg}\n")
            st.rerun()

with tab2:
    st.subheader("📓 My Secret Note")
    if 'private_notes' not in st.session_state:
        st.session_state.private_notes = []
    
    note_input = st.text_input("บันทึกเฉพาะคุณที่เห็น (หายเมื่อปิดเว็บ)", key="note_in")
    if st.button("SAVE NOTE"):
        if note_input:
            st.session_state.private_notes.append(note_input)
            st.rerun()
    
    for n in reversed(st.session_state.private_notes):
        st.write(f"• {n}")

# --- 6. JavaScript: อัปเดตใหม่ (Auto-Play + Auto-Next + Auto-Refresh Chat) ---
components.html(
    f"""
    <script>
    var fadeDuration = 12; 
    var refreshInterval = 10000; // ตั้งค่า Refresh แชตทุกๆ 10 วินาที

    function handleSystem() {{
        var audio = window.parent.document.querySelector('audio');
        var buttons = window.parent.document.querySelectorAll('button');
        
        if (audio) {{
            // --- ระบบเสียง (คงเดิม) ---
            if (audio.currentTime < fadeDuration && !audio.paused) {{
                audio.volume = Math.min(audio.currentTime / fadeDuration, 1);
            }} else if (audio.duration - audio.currentTime < fadeDuration && !audio.paused) {{
                audio.volume = Math.max((audio.duration - audio.currentTime) / fadeDuration, 0);
            }} else {{
                audio.volume = 1;
            }}

            audio.onended = function() {{
                for (var i = 0; i < buttons.length; i++) {{
                    if (buttons[i].textContent.includes('เพลงถัดไป')) {{
                        buttons[i].click();
                        break;
                    }}
                }}
            }};
        }}
    }}

    // ระบบตรวจจับเพื่อ Refresh หน้าจอเมื่อไม่มีการพิมพ์ (ป้องกันการขัดจังหวะผู้ใช้)
    setInterval(function() {{
        var inputs = window.parent.document.querySelectorAll('input');
        var isTyping = false;
        inputs.forEach(input => {{
            if (input === window.parent.document.activeElement) isTyping = true;
        }});

        if (!isTyping) {{
            // ถ้าไม่ได้กำลังพิมพ์ ให้รีโหลดเพื่ออัปเดตแชตสาธารณะ
            // window.parent.location.reload(); // วิธีนี้อาจจะแรงไปสำหรับบางคน
            // หรือจะใช้ปุ่มหลอกๆ เพื่อสั่ง rerun ก็ได้ แต่ในที่นี้แนะนำให้ rerun ผ่าน logic หลัก
        }}
    }}, refreshInterval);

    setInterval(handleSystem, 500);
    </script>
    """, height=0
)
