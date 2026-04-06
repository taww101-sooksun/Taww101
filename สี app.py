import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. CONFIGURATION & FIREBASE CONNECTION ---
# ใช้ค่าจริงจาก Firebase ของคุณต๊ะ
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "sooksun1",
        "private_key": st.secrets["firebase_key"], 
        "client_email": "firebase-adminsdk-fbsvc@sooksun1.iam.gserviceaccount.com",
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://sooksun1-default-rtdb.firebaseio.com/'
    })

# --- 2. DYNAMIC TIME-BASED LOGIC (ตาราง 8 ช่วงเวลา) ---
def get_current_phase():
    h = time.localtime().tm_hour
    if 0 <= h < 3: return {"name": "Deep Healing", "hz": 432, "bpm": 60, "theme": "#0044ff"}
    elif 3 <= h < 6: return {"name": "Pre-Dawn", "hz": 432, "bpm": 63, "theme": "#4400ff"}
    elif 6 <= h < 9: return {"name": "Awakening", "hz": 528, "bpm": 85, "theme": "#ffaa00"}
    elif 9 <= h < 12: return {"name": "Focus", "hz": 440, "bpm": 90, "theme": "#00ffcc"}
    # ... (เพิ่มให้ครบ 8 ช่วงตามตารางของคุณต๊ะ) ...
    return {"name": "Equilibrium", "hz": 440, "bpm": 75, "theme": "#00ff88"}

phase = get_current_phase()

# --- 3. UI NEON INTERFACE ---
st.set_page_config(layout="wide", page_title="SYNAPSE CORE")
st.markdown(f"""
    <style>
    .stApp {{ background-color: #050505; color: {phase['theme']}; font-family: 'Courier New', monospace; }}
    .metric-card {{ background: #111; border: 1px solid {phase['theme']}; padding: 15px; border-radius: 10px; text-align: center; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA SYNCHRONIZATION (Auto-Refresh 1s) ---
st_autorefresh(interval=1000, key="sync_engine")

# ดึงข้อมูล "ความจริง" จาก Firebase
live_hz = db.reference('live/hz').get() or 0.0
live_bpm = db.reference('live/bpm').get() or 0.0

# --- 5. THE COMMAND DASHBOARD ---
st.title(f"🛰️ SYNAPSE CORE: {phase['name']}")
st.write(f"SYSTEM STATUS: **OPERATIONAL** | TUNING: **{phase['hz']}Hz**")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # MATRIX 144 VISUALIZER
    st.subheader("📺 MATRIX SYNC (144-GRID)")
    accuracy = max(0, 100 - (abs(phase['hz'] - live_hz) / phase['hz'] * 100)) if live_hz > 0 else 0
    
    grid_cells = "".join([
        f'<div style="width:100%; height:15px; background:{"#0f0" if i < (accuracy * 1.44) else "#1a1a1a"}; border-radius:2px;"></div>' 
        for i in range(144)
    ])
    st.markdown(f"""
        <div style="display:grid; grid-template-columns: repeat(12, 1fr); gap:3px; background:#000; padding:10px; border:1px solid #333;">
            {grid_cells}
        </div>
        <p style="text-align:right; font-size:0.8em;">ACCURACY: {accuracy:.2f}%</p>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("❤️ HEART RATE")
    st.markdown(f"""<div class="metric-card">
        <h1 style="color:#ff0044; font-size:3em; margin:0;">{int(live_bpm)}</h1>
        <p>BPM (REAL-TIME)</p>
    </div>""", unsafe_allow_html=True)
    st.caption(f"TARGET BPM: {phase['bpm']}")

with col3:
    st.subheader("🎙️ MIC ANALYSIS")
    st.markdown(f"""<div class="metric-card">
        <h1 style="color:{phase['theme']}; font-size:3em; margin:0;">{live_hz:.1f}</h1>
        <p>CURRENT Hz</p>
    </div>""", unsafe_allow_html=True)

# --- 6. HEALER ENGINE (CROSSFADE + MATH-ELASTIC) ---
st.divider()
st.subheader("🎵 HEALER ENGINE (BIO-FEEDBACK CONTROL)")

# ส่งค่า Phase และ Firebase Config ไปที่ JavaScript
healer_logic_js = f"""
<div id="healer-interface" style="background:#111; padding:20px; border:1px solid #333; border-radius:10px; color:white;">
    <div style="display:flex; gap:10px; margin-bottom:15px;">
        <button onclick="initHealer()" style="flex:1; padding:15px; background:{phase['theme']}; color:#000; border:none; font-weight:bold; cursor:pointer;">1. LOAD ENGINE</button>
        <button onclick="startHeal()" style="flex:1; padding:15px; background:#0f0; color:#000; border:none; font-weight:bold; cursor:pointer;">2. START HEALING</button>
    </div>
    <div id="lyrics-display" style="height:100px; border-left:4px solid {phase['theme']}; padding-left:15px; font-style:italic; color:#888;">
        "อยู่นิ่งๆ ไม่เจ็บตัว..." (ระบบพร้อมทำงาน)
    </div>
</div>

<script type="module">
    import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js";
    import {{ getDatabase, ref, onValue }} from "https://www.gstatic.com/firebasejs/9.17.1/firebase-database.js";

    const app = initializeApp({{ databaseURL: "https://sooksun1-default-rtdb.firebaseio.com/" }});
    const database = getDatabase(app);
    let audioCtx, source, gainNode;

    window.initHealer = () => {{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        // เชื่อมต่อระบบ Bio-feedback: ฟังค่า BPM จาก Firebase เพื่อคุมความเร็วเพลง
        onValue(ref(database, 'live/bpm'), (snapshot) => {{
            const bpm = snapshot.val();
            if(source && bpm > 40) {{
                // สูตร: ถ้าหัวใจเต้นเร็ว (BPM สูง) เพลงจะช้าลง (PlaybackRate ต่ำลง) เพื่อปลอบประโลม
                const speed = {phase['bpm']} / bpm;
                source.playbackRate.setValueAtTime(speed, audioCtx.currentTime);
            }}
        }});
    }};

    // ฟังก์ชัน Math-Elastic: ยืดหดเสียงตามความถี่เป้าหมาย {phase['hz']}Hz
    window.startHeal = async () => {{
        // Logic การเล่นเพลงพร้อม Crossfade และจูน 432Hz/528Hz ตรงนี้
        console.log("Healing Started at {phase['hz']}Hz");
    }};
</script>
"""
components.html(healer_logic_js, height=300)
