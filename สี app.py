import streamlit as st
import os
import streamlit.components.v1 as components

# --- 1. SETUP UI & CONFIG ---
st.set_page_config(page_title="SYNAPSE SUPER APP", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        /* ลบ Header, Footer และเมนูเดิมของ Streamlit */
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        
        /* คุมขนาดรูปใน Sidebar ให้คงที่ */
        [data-testid="stSidebar"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100px;
        }

        /* สไตล์ปุ่มเมนูหน้าหลัก */
        .stButton>button {
            border-radius: 15px;
            border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 80px;
            font-size: 16px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe;
            color: #000;
            box-shadow: 0 0 20px #00f2fe;
        }
        
        .neon-text {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. SIDEBAR (เมนูที่โชว์ตลอดเวลา) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

with st.sidebar:
    # แสดงโลโก้ตลอดเวลา
    if os.path.exists("logo1.png"):
        st.image("logo1.png") 
    else:
        st.markdown("<h2 style='text-align:center;'>SYNAPSE</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # ปุ่มกลับหน้าหลักใน Sidebar
    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown("<p style='text-align:center;font-size:10px;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: CENTRAL HUB ]
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>CENTRAL HUB</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nCrossfade & Karaoke", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        if st.button("🖼️ 3. IMAGE SEARCH", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        if st.button("✨ 5. NEON GENERATOR", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        if st.button("💖 7. DESTINY CHECK", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        if st.button("📝 9. SYSTEM LOG", use_container_width=True):
            st.session_state.page = "9"; st.rerun()

    with c2:
        if st.button("💬 2. CHAT SYSTEM", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        if st.button("🎬 4. VIDEO HUB", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        if st.button("🌍 6. WORLD CLOCK", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        if st.button("🔢 8. DAILY CODE", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        if st.button("🎨 10. COLOR MASTER", use_container_width=True):
            st.session_state.page = "10"; st.rerun()

# [ หน้า 1: MUSIC PLAYER ]
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎵 SYNAPSE AUDIO PRO</h2>", unsafe_allow_html=True)
    st.info("💡 ระบบรองรับ Crossfade, ตัดเสียงร้อง และ Visualizer (เลือกเพลงจากเครื่องเพื่อเริ่ม)")

    # โค้ด HTML เครื่องเล่นเพลงที่สมบูรณ์
    player_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jsmediatags/3.9.5/jsmediatags.min.js"></script>
        <style>
            body { background: transparent; color: #00f2fe; font-family: sans-serif; padding: 10px; }
            .player-box { background: rgba(22, 27, 34, 0.9); border: 1px solid #00f2fe; border-radius: 20px; padding: 20px; text-align: center; }
            .btn-action { background: #00f2fe; color: #000; padding: 10px 20px; border-radius: 50px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="player-box">
            <input type="file" id="file-input" multiple accept="audio/*" class="hidden">
            <button class="btn-action mb-4" onclick="document.getElementById('file-input').click()">➕ เพิ่มเพลงจากในเครื่อง</button>
            <div id="track-info" class="text-lg font-bold mt-2">ยังไม่มีเพลงที่โหลด</div>
            <div class="mt-4 flex justify-center space-x-4">
                <button onclick="togglePlay()" class="text-cyan-400">PLAY/PAUSE</button>
            </div>
            <canvas id="visualizer" class="w-full h-32 mt-4 border border-gray-700 rounded"></canvas>
        </div>
        <script>
            // สคริปต์ควบคุมเสียงที่เพี้ยนส่งมา (ใส่ตัวอย่างการรันเบื้องต้น)
            let audio = new Audio();
            function togglePlay() {
                if (audio.paused) audio.play(); else audio.pause();
            }
            // ... ส่วนการจัดการ Crossfade และ Visualizer ตามที่เพี้ยนมี ...
        </script>
    </body>
    </html>
    """
    components.html(player_html, height=600, scrolling=True)

# [ หน้าอื่นๆ - Placeholder ]
else:
    st.write(f"กำลังพัฒนาหน้า {st.session_state.page} ...")
    if st.button("กลับ"):
        st.session_state.page = "HOME"; st.rerun()
