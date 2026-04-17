import streamlit as st
import os
import base64
import random

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="SYNAPSEอยู่นิ้งๆไม่เจ็บตัว COMMAND CENTER V.7", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

# ตรวจสอบตัวแปรระบบ
if 'global_song_idx' not in st.session_state:
    st.session_state.global_song_idx = 0

logo_b64 = get_base64("logo1.png")

# --- 2. ข้อมูลห้องและสีสัน ---
room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
]

# สแกนเพลงทั้งหมด
all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. ฟังก์ชันเครื่องเล่น (พร้อมเนื้อเพลงวิ่ง) ---
def synapse_player(room_idx):
    info = room_info[room_idx]
    c1, c2 = info["color1"], info["color2"]
    
    if not all_music:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในคลัง")
        return

    st.session_state.global_song_idx %= len(all_music)
    current_song = all_music[st.session_state.global_song_idx]
    song_data = get_base64(current_song)

    if song_data:
        # ส่วนแสดงผล: กราฟเสียง + เนื้อเพลงวิ่ง + ปุ่มควบคุม
        html_code = f"""
        <div style="margin-top:10px; font-family: 'Orbitron', sans-serif;">
            <canvas id="canvas-{room_idx}" style="width:100%; height:110px; background:#000; border:1px solid {c1}44; border-radius:15px;"></canvas>
            
            <div style="background:rgba(0,0,0,0.8); border:1px solid {c1}; border-radius:8px; margin-top:12px; overflow:hidden; box-shadow: 0 0 10px {c1}44;">
                <marquee scrollamount="6" style="color:{c1}; font-size:18px; padding:8px; font-weight:bold; text-shadow: 0 0 8px {c1};">
                    NOW PLAYING 🎵 {current_song} | {info['name']} | SYNAPSE SYSTEM ONLINE | สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว ⚡
                </marquee>
            </div>

            <button id="btn-{room_idx}" style="width:100%; padding:18px; margin-top:12px; background:transparent; color:{c1}; border:2px solid {c1}; cursor:pointer; border-radius:12px; font-weight:bold; box-shadow: 0 0 15px {c1}33; text-transform:uppercase; letter-spacing: 2px;">
                ACTIVATE {info["name"]} ⚡
            </button>
            
            <audio id="audio-{room_idx}" src="data:audio/mp3;base64,{song_data}"></audio>
        </div>

        <script>
            const audio = document.getElementById('audio-{room_idx}');
            const btn = document.getElementById('btn-{room_idx}');
            const canvas = document.getElementById('canvas-{room_idx}');
            const ctx = canvas.getContext('2d');
            let audioCtx, analyser, source, dataArray;

            btn.onclick = function() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    source = audioCtx.createMediaElementSource(audio);
                    source.connect(analyser);
                    analyser.connect(audioCtx.destination);
                    analyser.fftSize = 256; 
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    render();
                }}
                if (audio.paused) {{ 
                    audio.play(); 
                    btn.innerText = "SYSTEM ONLINE 🟢"; 
                    sessionStorage.setItem('synapse_autoplay', 'true');
                }} else {{ 
                    audio.pause(); 
                    btn.innerText = "SYSTEM PAUSED 🔴"; 
                    sessionStorage.setItem('synapse_autoplay', 'false');
                }}
            }};

            window.onload = function() {{
                if (sessionStorage.getItem('synapse_autoplay') === 'true') {{
                    setTimeout(() => {{
                        audio.play().then(() => {{
                            btn.innerText = "SYSTEM ONLINE 🟢";
                        }}).catch(e => console.log("Waiting for user click..."));
                    }}, 1000);
                }}
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const bWidth = (canvas.width / dataArray.length) * 2.2;
                let x = 0;
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height;
                    let grad = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - h);
                    grad.addColorStop(0, "{c1}"); grad.addColorStop(1, "{c2}");
                    ctx.fillStyle = grad;
                    ctx.shadowBlur = 10; ctx.shadowColor = "{c1}";
                    ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                    x += bWidth;
                }}
            }}

            audio.onended = () => {{
                // สั่งเปลี่ยนเพลงอัตโนมัติผ่านปุ่มลับ
                window.parent.document.querySelector('button[title="AUTO_NEXT_TRIGGER"]').click();
            }};
        </script>
        """
        st.components.v1.html(html_code, height=320)

# --- 4. การแสดงผลหน้าจอหลัก (จุดที่ต้องแก้ไข) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000000 !important; }}
    .logo-img {{
        width: 80px; height: 80px; margin: 0 auto;
        background-image: url("data:image/png;base64,{logo_b64}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 15px #39FF14);
        animation: pulse 2s infinite alternate;
    }}
    @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}
    </style>
    <div class="main-logo"></div>
""", unsafe_allow_html=True)

# สร้าง 5 ห้อง
tabs = st.tabs([r["name"] for r in room_info])

for i, tab in enumerate(tabs):
    with tab:
        # เช็คว่าเราอยู่ที่ Tab ไหน (นี่คือไม้เด็ด!)
        # ถ้าอาจารย์กดเลือก Tab ไหน ให้รัน Player เฉพาะใน Tab นั้น
        st.markdown(f"<h1 style='text-align:center; color:#fff; font-family:Orbitron; font-size:1.5rem;'>{room_info[i]['name']}</h1>", unsafe_allow_html=True)
        
        # ใส่ตัวเช็คสถานะ: ถ้าเลือกห้องนี้ ถึงจะโหลด Player
        synapse_player(i)


# --- 5. ระบบควบคุมและคลังเพลง ---
if st.button("AUTO_NEXT", key="AUTO_NEXT", help="AUTO_NEXT_TRIGGER"):
    st.session_state.global_song_idx += 1
    st.rerun()

st.write("---")
st.markdown("<h3 style='font-family:Orbitron; color:#39FF14; text-align:center;'>🎵 GLOBAL PLAYLIST (52 TRACKS)</h3>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("⏭️ SKIP TRACK"):
        st.session_state.global_song_idx += 1
        st.rerun()
with c2:
    if st.button("🎲 SHUFFLE ALL"):
        st.session_state.global_song_idx = random.randint(0, len(all_music)-1)
        st.rerun()

with st.expander("📂 เลือกเพลงจากคลังทั้งหมด", expanded=True):
    for idx, song in enumerate(all_music):
        is_current = (idx == st.session_state.global_song_idx % len(all_music))
        label = f"▶️ {idx+1}. {song}" if is_current else f"▪️ {idx+1}. {song}"
        if st.button(label, key=f"track_{idx}", use_container_width=True):
            st.session_state.global_song_idx = idx
            st.rerun()

st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE COMMAND CENTER V.7")
