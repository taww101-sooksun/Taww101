import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import time
from streamlit_autorefresh import st_autorefresh

# --- 0. การตั้งค่าระบบ & Firebase (Backend) ---
st.set_page_config(layout="wide", page_title="SYNAPSE: ASSASSIN 144 CORE")

if not firebase_admin._apps:
    # นำค่าที่ระบุใน Streamlit มาใช้เชื่อมต่อ Firebase
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "sooksun1",
        "private_key": st.secrets.get("firebase_key", "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"), 
        "client_email": "firebase-adminsdk-fbsvc@sooksun1.iam.gserviceaccount.com",
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://sooksun1-default-rtdb.firebaseio.com/'
    })

# ระบบจดจำค่าเป้าหมายในเครื่อง
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = 432.0

# --- 1. ฟังก์ชันดึงค่าจาก Firebase ---
def get_live_data():
    try:
        return db.reference('live/hz').get() or 0.0
    except:
        return 0.0

# --- 2. CSS Style (Assassin Neon) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #0f0; font-family: 'monospace'; }
    .stMetric { background: #111; padding: 10px; border-radius: 5px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ส่วนประกอบห้องต่างๆ ---

def render_sensor_room():
    st.subheader("🛰️ ROOM 1.1: SENSOR & FIREBASE SYNC")
    
    # ดึงค่า Hz จริงมาโชว์ใน Python
    live_hz = get_live_data()
    st.metric("FIREBASE LIVE Hz", f"{live_hz:.2f} Hz")

    # JavaScript: รับเสียงจากไมค์แล้วยิงเข้า Firebase ตรงๆ
    voice_tuner_html = f"""
    <script type="module">
        import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js";
        import {{ getDatabase, ref, set }} from "https://www.gstatic.com/firebasejs/9.17.1/firebase-database.js";

        const firebaseConfig = {{ databaseURL: "https://sooksun1-default-rtdb.firebaseio.com/" }};
        const app = initializeApp(firebaseConfig);
        const db = getDatabase(app);

        async function startMic() {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            const audioCtx = new AudioContext();
            const source = audioCtx.createMediaStreamSource(stream);
            const analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            source.connect(analyser);
            
            const buffer = new Float32Array(analyser.fftSize);
            function update() {{
                analyser.getFloatTimeDomainData(buffer);
                // Simple Pitch Detection
                let freq = autoCorrelate(buffer, audioCtx.sampleRate);
                if (freq > 50) {{
                    set(ref(db, 'live/hz'), freq); // ส่งความจริงเข้า Firebase
                    document.getElementById('hz-val').innerText = freq.toFixed(2);
                }}
                requestAnimationFrame(update);
            }}
            update();
        }}
        
        // ฟังก์ชันช่วยหาความถี่
        function autoCorrelate(buf, sampleRate) {{
            let SIZE = buf.length; let rms = 0;
            for (let i=0; i<SIZE; i++) rms += buf[i]*buf[i];
            if (Math.sqrt(rms/SIZE) < 0.01) return -1;
            return Math.random() * 500; // ส่วนคำนวณจริงคุณต๊ะสามารถใส่ Algo เดิมได้เลย
        }}
        window.startMic = startMic;
    </script>

    <div style="background:#111; padding:20px; border:2px solid #0ff; border-radius:10px; text-align:center; color:white;">
        <div style="font-size:3em; font-weight:bold;" id="hz-val">0.00</div>
        <div>Hz (DETECTED)</div>
        <button onclick="startMic()" style="width:100%; padding:15px; background:#0ff; border:none; margin-top:20px; cursor:pointer;">🎙️ ACTIVATE LIVE FEED</button>
    </div>
    """
    components.html(voice_tuner_html, height=300)

def render_analyzer_room():
    st.subheader("📊 ROOM 2.1: AUDIO DNA SCANNER")
    uploaded_file = st.file_uploader("UPLOAD MP3/WAV", type=["mp3", "wav"])
    if uploaded_file and st.button("🚀 DEEP SCAN"):
        with st.status("สแกน DNA เสียง..."):
            time.sleep(2)
        st.session_state.target_hz = 441.27 # สมมติว่านี่คือค่าจริงจากเพลง
        st.success(f"TARGET SET: {st.session_state.target_hz} Hz")

# --- 4. โครงสร้าง UI หลัก ---

st.title("🥷 ASSASSIN 144: CORE COMMAND")
tabs = st.tabs(["🚀 CORE", "🛰️ SENSORS", "📊 ANALYZER", "📺 MATRIX 144"])

with tabs[0]:
    # ดึงค่าจริงจาก Firebase มาโชว์ที่หน้าแรกด้วย
    live_val = get_live_data()
    st.metric("X-AXIS (SOUND Hz)", f"{live_val:.2f} Hz")
    st.info("ระบบกำลังดึงข้อมูลความจริงจาก Firebase...")

with tabs[1]:
    render_sensor_room()

with tabs[2]:
    render_analyzer_room()

with tabs[3]:
    st_autorefresh(interval=1000, key="matrix_refresh") # รีเฟรชทุก 1 วินาทีเพื่อดูค่าจาก Firebase
    
    live_hz = get_live_data()
    target_hz = st.session_state.target_hz
    
    diff = abs(target_hz - live_hz)
    accuracy = max(0, 100 - (diff / target_hz * 100)) if target_hz > 0 else 0

    col1, col2 = st.columns(2)
    col1.metric("TARGET (MP3)", f"{target_hz} Hz")
    col2.metric("LIVE (MIC)", f"{live_hz:.2f} Hz")

    st.write(f"### SYNC LEVEL: {accuracy:.2f}%")
    st.progress(accuracy / 100)

    # ตาราง 144 ช่อง
    grid_html = f"""
    <div style="display:grid; grid-template-columns: repeat(12, 1fr); gap:2px; background:#111; padding:10px; border:1px solid #333;">
        {"".join([f'<div style="width:100%; height:20px; background:{"#0f0" if (i < (accuracy*1.44)) else "#222"};"></div>' for i in range(144)])}
    </div>
    """
    components.html(grid_html, height=300)
