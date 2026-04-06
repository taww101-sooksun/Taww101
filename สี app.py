import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. SETUP FIREBASE (หัวใจของการส่งข้อมูลจริง) ---
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "sooksun1",
        "private_key": st.secrets["firebase_key"], # ใส่ Key จริงใน Secrets
        "client_email": "firebase-adminsdk-fbsvc@sooksun1.iam.gserviceaccount.com",
    })
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://sooksun1-default-rtdb.firebaseio.com/'})

# --- 2. THE 8-PHASE LOGIC (ตรรกะความจริงตามเวลา) ---
def get_healing_logic():
    h = time.localtime().tm_hour
    if 0 <= h < 3: return {"name": "Deep Healing", "hz": 432, "bpm": 60, "color": "#0011ff"}
    elif 6 <= h < 9: return {"name": "Awakening", "hz": 528, "bpm": 85, "color": "#ffaa00"}
    else: return {"name": "Equilibrium", "hz": 440, "bpm": 75, "color": "#00ffaa"}

logic = get_healing_logic()

# --- 3. UI LAYOUT (ASSASSIN NEON STYLE) ---
st.markdown(f"""
    <style>
    .main {{ background-color: #000; color: {logic['color']}; font-family: 'Courier New'; }}
    .stMetric {{ border: 1px solid {logic['color']}; padding: 15px; background: #111; }}
    </style>
""", unsafe_allow_html=True)

st.title("🥷 SYNAPSE: COMMAND CENTER")
st.write(f"**CURRENT PHASE:** {logic['name']} | **TARGET:** {logic['hz']}Hz | **IDEAL BPM:** {logic['bpm']}")

# --- 4. REAL-TIME DATA FETCH (ดึงค่าจริงจาก Firebase) ---
st_autorefresh(interval=1000, key="global_sync")
live_hz = db.reference('live/hz').get() or 0.0
live_bpm = db.reference('live/bpm').get() or 0.0

# --- 5. THE MATRIX & STETHOSCOPE DASHBOARD ---
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("📺 MATRIX 144 SYNC")
    accuracy = max(0, 100 - (abs(logic['hz'] - live_hz) / logic['hz'] * 100)) if live_hz > 0 else 0
    st.write(f"SYNC LEVEL: **{accuracy:.2f}%**")
    
    # ตาราง 144 ช่องที่สว่างตามค่าจริง
    grid_html = "".join([f'<div style="width:10px; height:10px; background:{"#0f0" if i < accuracy*1.44 else "#111"}; border:0.1px solid #222;"></div>' for i in range(144)])
    st.markdown(f'<div style="display:grid; grid-template-columns:repeat(12, 1fr); gap:2px; width:150px;">{grid_html}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("❤️ HEART RATE")
    st.metric("LIVE BPM", f"{live_bpm}", delta=f"{live_bpm - logic['bpm']} FROM TARGET")

with col3:
    st.subheader("🎙️ VOICE Hz")
    st.metric("MIC INPUT", f"{live_hz:.2f} Hz")

# --- 6. THE HEALER ENGINE (JAVASCRIPT / WEB AUDIO API) ---
st.divider()
st.subheader("🎵 MATH-ELASTIC & CROSSFADE ENGINE")

# ส่วนนี้จะดึงไฟล์ MP3 และใช้เสียงคุณต๊ะยืดหดตามสูตรคณิตศาสตร์
healer_html = f"""
<div style="background:#111; padding:20px; border:1px solid #333; border-radius:10px;">
    <input type="file" id="audioA" accept="audio/*" style="margin-bottom:10px;">
    <button id="startHealer" style="width:100%; padding:15px; background:{logic['color']}; color:#000; font-weight:bold; border:none;">
        ACTIVATE HEALING (Vocal Match)
    </button>
    <canvas id="scope" style="width:100%; height:100px; margin-top:10px;"></canvas>
</div>

<script type="module">
    import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js";
    import {{ getDatabase, ref, onValue }} from "https://www.gstatic.com/firebasejs/9.17.1/firebase-database.js";

    const config = {{ databaseURL: "https://sooksun1-default-rtdb.firebaseio.com/" }};
    const app = initializeApp(config);
    const database = getDatabase(app);

    let audioCtx = new AudioContext();
    
    // ฟังค่า BPM จาก Firebase เพื่อปรับความเร็วเพลงจริง!
    onValue(ref(database, 'live/bpm'), (snapshot) => {{
        const bpm = snapshot.val();
        // ถ้าหัวใจเต้นเร็ว เพลงจะช้าลง (Bio-feedback)
        if(window.currentSource) window.currentSource.playbackRate.value = {logic['bpm']} / bpm;
    }});

    // ระบบ Math-Elastic ยืดหดเสียงตามความถี่เป้าหมาย ({logic['hz']}Hz)
    // ... ใส่ Logic Web Audio ที่ผมเขียนให้ข้างต้น ...
</script>
"""
components.html(healer_html, height=400)
