import streamlit as st
import os
import streamlit.components.v1 as components

# --- 1. SETUP UI & CONFIG ---
st.set_page_config(page_title="SYNAPSE SUPER APP", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        [data-testid="stSidebar"] img { display: block; margin: 0 auto; width: 100px; }
        .stButton>button {
            border-radius: 15px; border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1); color: white;
            height: 80px; font-size: 16px; transition: 0.3s;
        }
        .stButton>button:hover { background: #00f2fe; color: #000; box-shadow: 0 0 20px #00f2fe; }
        .neon-text { text-align: center; color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. SIDEBAR (Global Player - เพลงไม่ดับ) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

with st.sidebar:
    if os.path.exists("logo1.png"):
        st.image("logo1.png") 
    else:
        st.markdown("<h2 class='neon-text'>SYNAPSE</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # --- เครื่องเล่นเพลงชุดใหญ่ (ย้ายมานี่เพื่อความต่อเนื่อง) ---
    st.markdown("### 🎧 SYNAPSE GLOBAL PLAYER")
    player_sidebar_html = """
    <div style="background:#111; padding:15px; border-radius:15px; border:1px solid #00f2fe; text-align:center;">
        <canvas id="side-vis" style="width:100%; height:60px; background:#000; border-radius:5px;"></canvas>
        <div id="side-track" style="font-size:11px; color:#fff; margin:10px 0; overflow:hidden; white-space:nowrap;">Ready to scan...</div>
        
        <input type="file" id="up" multiple accept="audio/*" style="display:none" onchange="hLoad(this.files)">
        <button onclick="document.getElementById('up').click()" style="width:100%; background:#00f2fe; color:#000; border:none; padding:8px; border-radius:20px; font-weight:bold; cursor:pointer;">➕ LOAD MUSIC</button>
        
        <div style="margin-top:15px; border-top:1px solid #333; pt-10px;">
            <label style="font-size:10px; color:#00f2fe;">KARAOKE CUT (NOTCH)</label>
            <input type="range" min="0" max="100" value="0" style="width:100%; accent-color:#00f2fe;" oninput="updateK(this.value)">
        </div>
        <div style="font-size:9px; color:#555; margin-top:5px;">CROSSFADE 10S ACTIVE</div>
    </div>

    <script>
        let ctx, anl, src, flt, aud = new Audio(), list = [], idx = 0;
        aud.crossOrigin = "anonymous";

        function init() {
            if(!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                anl = ctx.createAnalyser();
                src = ctx.createMediaElementSource(aud);
                flt = ctx.createBiquadFilter();
                flt.type = "notch"; flt.frequency.value = 1000; flt.Q.value = 0;
                src.connect(flt); flt.connect(anl); anl.connect(ctx.destination);
                draw();
            }
        }

        function hLoad(f) { init(); list = Array.from(f); if(list.length>0) play(0); }
        function play(i) {
            idx = i; const file = list[idx];
            aud.src = URL.createObjectURL(file);
            document.getElementById('side-track').innerText = file.name;
            aud.play();
        }

        function updateK(v) { if(flt) flt.Q.value = v / 5; }

        aud.ontimeupdate = () => {
            let left = aud.duration - aud.currentTime;
            if(left <= 10 && left > 0) aud.volume = left / 10; else aud.volume = 1;
        };
        aud.onended = () => { idx = (idx+1)%list.length; play(idx); };

        function draw() {
            const canv = document.getElementById('side-vis'), c = canv.getContext('2d');
            const data = new Uint8Array(anl.frequencyBinCount);
            function r() {
                requestAnimationFrame(r); anl.getByteFrequencyData(data);
                c.clearRect(0,0,canv.width,canv.height);
                c.fillStyle = '#00f2fe';
                for(let i=0; i<data.length; i++) {
                    let h = data[i]/4; c.fillRect(i*3, canv.height-h, 2, h);
                }
            }
            r();
        }
    </script>
    """
    components.html(player_sidebar_html, height=280)

    st.divider()
    if st.button("🏠 Home / กลับหน้าหลัก", use_container_width=True):
        st.session_state.page = "HOME"; st.rerun()
    st.markdown("<p style='text-align:center;font-size:10px;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)

# --- 3. เนื้อหาแต่ละหน้า (MAIN CONTENT) ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>CENTRAL HUB</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nStatus: Sidebar Active", use_container_width=True):
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

elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎵 AUDIO CONTROL CENTER</h2>", unsafe_allow_html=True)
    st.info("ขณะนี้เครื่องเล่นทำงานอยู่ในเมนูแถบข้าง (Sidebar) เพื่อให้คุณสลับไปใช้แอปอื่นๆ ได้โดยเพลงไม่ดับครับ")
    if st.button("⬅️ ย้อนกลับ"):
        st.session_state.page = "HOME"; st.rerun()

else:
    st.write(f"กำลังพัฒนาหน้า {st.session_state.page} ...")
    if st.button("กลับ"):
        st.session_state.page = "HOME"; st.rerun()
