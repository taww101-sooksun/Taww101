import streamlit as st
import os
import datetime

# --- 1. SETUP & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        /* ลบ Header, Footer และเมนูเดิมของ Streamlit */
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        
        /* สไตล์ปุ่มเมนู */
        .stButton>button {
            border-radius: 15px;
            border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 100px;
            font-size: 18px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe;
            color: #000;
            box-shadow: 0 0 20px #00f2fe;
        }
        
        /* ตัวหนังสือวิ้ง */
        .neon-text {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. การจัดการหน้าจอ (Navigation) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ฟังก์ชันย้อนกลับ
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: ศูนย์รวม 10 แอป ]
if st.session_state.page == "HOME":
    # วาง LOGO แทนที่ติ่ง
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    # สร้าง Grid 10 แอป (แบ่งเป็น 2 คอลัมน์)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        st.caption("ความสามารถ: เล่นไฟล์เสียง 1.mp3 และระบบควบคุมเสียงผ่านหน้าเว็บ")

        if st.button("🖼️ 3. IMAGE SEARCH\nค้นหาภาพจากดาวเทียม", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        st.caption("ความสามารถ: ดึงรูปภาพจากคลัง Unsplash ตามคำค้นหาที่ต้องการ")

        if st.button("✨ 5. NEON GENERATOR\nสร้างตัวอักษรเรืองแสง", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        st.caption("ความสามารถ: แปลงข้อความธรรมดาให้เป็นศิลปะนีออนวิ้งๆ")

        if st.button("💖 7. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        st.caption("ความสามารถ: วิเคราะห์ดวงชะตาในมิติที่ 4 ผ่านระบบฐานข้อมูลชื่อ")

        if st.button("📝 9. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
        st.caption("ความสามารถ: จดบันทึกข้อความและเหตุการณ์สำคัญลงในหน่วยความจำ")

    with c2:
        if st.button("💬 2. CHAT SYSTEM\nระบบสื่อสารอัจฉริยะ", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: โต้ตอบผ่านข้อความกับระบบจัดการ AI")

        if st.button("🎬 4. VIDEO HUB\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        st.caption("ความสามารถ: เชื่อมต่อและฉายภาพวิดีโอจาก YouTube หรือ Link ตรง")

        if st.button("🌍 6. WORLD CLOCK\nเวลาโลกแบบเรียลไทม์", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        st.caption("ความสามารถ: ตรวจสอบเวลาปัจจุบันในโซนต่างๆ ทั่วโลก")

        if st.button("🔢 8. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        st.caption("ความสามารถ: เจนรหัสตัวเลขนำโชคและรหัสรักษาความปลอดภัยรายวัน")

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()
        st.caption("ความสามารถ: เปลี่ยนสีสันของ Interface เพื่อความสวยงามตามใจชอบ")

# --- ส่วนนี้คือที่วางโค้ดของแต่ละแอปย่อย (ทำเหมือนเดิม) ---
elif st.session_state.page == "1":
    import os
    import base64
    import json
    import streamlit.components.v1 as components

    st.markdown("<h2 class='neon-text'>🎵 SYNAPSE AUTOMATIC PLAYER</h2>", unsafe_allow_html=True)

    # 1. กวาดไฟล์ .mp3 ทุกไฟล์ที่อยู่ในโฟลเดอร์เดียวกับไฟล์ .py
    music_folder = "." # หรือใส่พาธโฟลเดอร์เพลงของคุณ
    song_list = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]

    if not song_list:
        st.error("❌ ไม่เจอไฟล์เพลงในโฟลเดอร์เลยครับเพื่อน")
    else:
        # 2. เตรียมข้อมูลเพลงส่งให้ JavaScript
        # เราส่งเป็นชื่อไฟล์ไปก่อน แล้วให้ JS เรียกดึงผ่าน URL (วิธีนี้จะเร็วกว่า Base64 มาก)
        st.write(f"พบทั้งหมด {len(song_list)} เพลง พร้อมรันระบบ...")

        # สุ่มลำดับเพลง (Shuffle) ตั้งแต่เริ่มถ้าต้องการ
        # import random; random.shuffle(song_list)

        # 3. HTML/JS เครื่องเล่นเพลง (ดึงความสามารถจากโค้ดที่คุณมี)
        player_html = f"""
        <style>
            .player-container {{
                background: rgba(0,0,0,0.8);
                border: 2px solid #00f2fe;
                border-radius: 20px;
                padding: 20px;
                text-align: center;
                color: #fff;
                box-shadow: 0 0 20px #00f2fe;
            }}
            .neon-txt {{ color: #00f2fe; text-shadow: 0 0 10px #00f2fe; font-weight: bold; }}
            .btn {{ 
                background: #00f2fe; color: #000; border: none; padding: 15px; 
                border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%;
                margin-top: 10px;
            }}
        </style>

        <div class="player-container">
            <div id="status" class="neon-txt">พร้อมเล่น {len(song_list)} เพลง</div>
            <div id="track-name" style="margin: 15px 0; font-size: 1.2rem;">กดปุ่มเพื่อเริ่มฟัง</div>
            <button class="btn" id="playBtn" onclick="initPlayer()">▶️ เริ่มเดินเครื่อง (START ENGINE)</button>
            
            <audio id="mainAudio"></audio>
            </div>

        <script>
            const playlist = {json.dumps(song_list)};
            let currentIdx = 0;
            const audio = document.getElementById('mainAudio');
            const trackDisplay = document.getElementById('track-name');
            const statusDisplay = document.getElementById('status');

            function initPlayer() {{
                playTrack(0);
                document.getElementById('playBtn').style.display = 'none';
            }}

            function playTrack(idx) {{
                if (idx >= playlist.length) idx = 0;
                currentIdx = idx;
                
                const fileName = playlist[idx];
                trackDisplay.innerText = "กำลังเล่น: " + fileName;
                statusDisplay.innerText = "เพลงที่ " + (idx + 1) + " จาก " + playlist.length;
                
                // ใน Streamlit การดึงไฟล์ตรงๆ ต้องใช้เทคนิค static หรือส่งเป็น blob
                // แต่ถ้าคุณรัน local ปกติ วิธีที่ง่ายที่สุดคือส่ง path 
                audio.src = fileName; 
                audio.play();

                audio.onended = () => {{
                    playTrack(currentIdx + 1);
                }};
            }}
        </script>
        """
        components.html(player_html, height=400)

    st.info("💡 ความจริง: เพื่อไม่ให้เพลงดับเวลาสลับห้อง แนะนำให้ย้ายโค้ดชุดนี้ไปไว้ใน st.sidebar ครับ")

elif st.session_state.page == "5":
    st.header("✨ NEON LYRICS")
    
    user_text = st.text_area("วางเนื้อเพลงที่นี่:", "อยู่นิ่งๆ\nไม่เจ็บตัว", height=150)
    glow_color = st.color_picker("เลือกสีนีออน", "#FF007F") 
    
    st.markdown(f"""
        <style>
        /* สร้าง Animation แบบสั่นไหวและเรืองแสง */
        @keyframes neon-flicker {{
            0%, 18%, 22%, 25%, 53%, 57%, 100% {{
                text-shadow: 
                    0 0 4px #fff,
                    0 0 11px #fff,
                    0 0 19px #fff,
                    0 0 40px {glow_color},
                    0 0 80px {glow_color},
                    0 0 90px {glow_color},
                    0 0 100px {glow_color},
                    0 0 150px {glow_color};
            }}
            20%, 24%, 55% {{        
                text-shadow: none; /* จังหวะนี้จะทำให้มันเหมือนไฟกระพริบ */
            }}
        }}

        .neon-wrapper {{
            background-color: #000;
            padding: 50px 20px;
            border-radius: 20px;
            border: 3px solid {glow_color};
            box-shadow: 0 0 15px {glow_color}, inset 0 0 15px {glow_color};
            text-align: center;
            margin-top: 20px;
        }}

        .neon-text-blink {{
            font-size: 35px;
            font-weight: bold;
            color: #fff;
            font-family: 'Kanit', sans-serif;
            white-space: pre-wrap;
            line-height: 1.6;
            /* สั่งให้มันเล่น animation neon-flicker */
            animation: neon-flicker 2s infinite alternate;
        }}
        </style>
        
        <div class="neon-wrapper">
            <div class="neon-text-blink">{user_text}</div>
        </div>
    """, unsafe_allow_html=True)
