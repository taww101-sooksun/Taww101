import streamlit as st
import streamlit.components.v1 as components
import os
import random

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE DJ ROOMS", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#121212" 

# ดึงไฟล์เพลง
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if not music_files:
    st.error("ไม่พบไฟล์เพลง .mp3 ในเครื่องครับเพื่อน")
    st.stop()

if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

current_song = music_files[st.session_state.song_index]
next_song = music_files[(st.session_state.song_index + 1) % len(music_files)]

# --- 2. SIDEBAR & CUSTOM CSS ---
with st.sidebar:
    st.markdown(f"### 🎨 SYNAPSE CONTROL")
    st.session_state.theme_color = st.color_picker("สีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("สีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('*สโลแกน: "อยู่นิ่งๆ ไม่เจ็บตัว"*')

st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.4);
        padding: 10px 0; border: 1px solid {st.session_state.theme_color}; border-radius: 10px; margin-bottom: 20px;
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 15s linear infinite;
        font-size: 18px; color: {st.session_state.theme_color}; margin: 0;
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MAIN PLAYER INTERFACE ---
st.title("🎸 SYNAPSE DJ ROOMS")
st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT: {next_song} </p></div>', unsafe_allow_html=True)

# ส่วนของเครื่องเล่น DJ (HTML/JS)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background: transparent; color: {st.session_state.theme_color}; font-family: sans-serif; text-align: center; margin: 0; }}
        .dj-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 10px; }}
        .deck {{ border: 2px solid #333; border-radius: 20px; padding: 20px; background: rgba(0,0,0,0.6); transition: 0.5s; }}
        .active {{ border-color: {st.session_state.theme_color}; box-shadow: 0 0 20px {st.session_state.theme_color}66; }}
        .timer {{ font-size: 32px; font-family: monospace; margin: 10px 0; color: #ff007f; }}
        .song-info {{ font-size: 12px; opacity: 0.7; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
        #startBtn {{ 
            width: 100%; padding: 20px; background: transparent; border: 2px solid {st.session_state.theme_color}; 
            color: {st.session_state.theme_color}; border-radius: 15px; font-weight: bold; cursor: pointer; font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="dj-grid">
        <div id="deckA" class="deck active">
            <div class="song-info">DECK A (LIVE)</div>
            <div class="song-info">{current_song}</div>
            <div id="timerA" class="timer">00:00</div>
        </div>
        <div id="deckB" class="deck" style="opacity: 0.3;">
            <div class="song-info">DECK B (STANDBY)</div>
            <div class="song-info">{next_song}</div>
            <div id="timerB" class="timer">--:--</div>
        </div>
    </div>
    <button id="startBtn" onclick="initDJ()">TAP TO START SYNAPSE SYSTEM</button>

    <script>
        let ctx, deckA={{}}, deckB={{}}, isFading = false;

        async function decode(filename) {{
            try {{
                const res = await fetch("./" + encodeURIComponent(filename));
                const arrayBuffer = await res.arrayBuffer();
                return await ctx.decodeAudioData(arrayBuffer);
            }} catch(e) {{ return null; }}
        }}

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').innerText = "LOADING PEAK DATA...";
            deckA.buffer = await decode("{current_song}");
            deckB.buffer = await decode("{next_song}");
            document.getElementById('startBtn').style.display = 'none';
            play();
        }}

        function play() {{
            if(!deckA.buffer) return;
            deckA.src = ctx.createBufferSource();
            deckA.src.buffer = deckA.buffer;
            deckA.gain = ctx.createGain();
            deckA.src.connect(deckA.gain).connect(ctx.destination);
            deckA.src.start(0);
            deckA.startTime = ctx.currentTime;

            setInterval(() => {{
                let rem = deckA.buffer.duration - (ctx.currentTime - deckA.startTime);
                if(rem > 0) {{
                    let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                    document.getElementById('timerA').innerText = String(m).padStart(2,'0')+":"+String(s).padStart(2,'0');
                }}
                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    fade();
                }}
            }}, 1000);
        }}

        function fade() {{
            const now = ctx.currentTime;
            if(!deckB.buffer) return;
            deckB.src = ctx.createBufferSource();
            deckB.src.buffer = deckB.buffer;
            deckB.gain = ctx.createGain();
            deckB.src.connect(deckB.gain).connect(ctx.destination);
            deckA.gain.gain.linearRampToValueAtTime(1, now);
            deckA.gain.gain.linearRampToValueAtTime(0, now + 12);
            deckB.gain.gain.setValueAtTime(0, now);
            deckB.gain.gain.linearRampToValueAtTime(1, now + 12);
            deckB.src.start(now);
            document.getElementById('deckB').style.opacity = "1";
            document.getElementById('deckB').classList.add('active');
            setTimeout(() => {{ window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*'); }}, 12000);
        }}
    </script>
</body>
</html>
"""

components.html(html_code, height=350)

# --- 4. CHAT & PLAYLIST ---
st.write("---")
c_chat, c_list = st.columns([2, 1])

with c_chat:
    st.subheader("🌐 PUBLIC LOBBY")
    if not os.path.exists("chat.txt"): open("chat.txt", "w").close()
    with open("chat.txt", "r", encoding="utf-8") as f:
        msgs = f.readlines()[-10:]
    st.text_area("Chat", value="".join(msgs), height=150, disabled=True)
    with st.form("chat", clear_on_submit=True):
        u_msg = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("SEND"):
            with open("chat.txt", "a", encoding="utf-8") as f: f.write(f"> {u_msg}\n")
            st.rerun()

with c_list:
    st.subheader("🎧 PLAYLIST")
    for i, song in enumerate(music_files[:10]): # โชว์แค่ 10 เพลงกันรก
        if st.button(f"{'▶️' if i==st.session_state.song_index else '🎵'} {song}", key=f"s_{i}"):
            st.session_state.song_index = i
            st.rerun()

# รับค่าจาก JS เพื่อเปลี่ยนเพลง
if 'next' in str(st.session_state): # เช็กค่าจากการส่ง Message
    st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
