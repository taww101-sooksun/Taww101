import streamlit as st
import streamlit.components.v1 as components
import librosa
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import time
import soundfile as sf
import io

# --- 1. INITIAL SETUP & FIREBASE ---
st.set_page_config(layout="wide", page_title="SYNAPSE: ASSASSIN 144 CORE")

# ตรวจสอบการเชื่อมต่อ Firebase จาก st.secrets
if not firebase_admin._apps:
    try:
        firebase_creds = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://firebaseio.com"
        })
    except Exception as e:
        st.error(f"⚠️ Firebase Setup Error: {e}")

# --- 2. CSS NEON DESIGN (สายลับ) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #0f0; font-family: 'Courier New', monospace; }
    .stTabs [data-baseweb="tab"] { background-color: #111; color: #0f0; border: 1px solid #333; }
    .stTabs [aria-selected="true"] { border-color: #0ff; box-shadow: 0 0 10px #0ff; }
    .metric-card { background: rgba(0,255,255,0.05); border: 1px solid #0ff; padding: 15px; border-radius: 10px; text-align: center; }
    h1, h2, h3 { color: #0ff !important; text-shadow: 0 0 8px #0ff; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CORE PROCESSING FUNCTIONS ---
def analyze_audio_144(y, sr):
    """สกัดค่า X, Y, Z จากคลื่นเสียง"""
    # X: Pitch (ความถี่)
    pitches, _ = librosa.piptrack(y=y, sr=sr)
    x_val = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 432.0
    # Y: Energy (ความดัง)
    y_val = np.mean(librosa.feature.rms(y=y)) * 1000
    # Z: Brightness (ความแหลม/ใส)
    z_val = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)) / 100
    # Formula: SQRT(X^2 + Y^2 + Z^2)
    score = np.sqrt(x_val**2 + y_val**2 + z_val**2) / 10
    return {"X": x_val, "Y": y_val, "Z": z_val, "Score": score}

def add_human_touch(y, sr, variance=0.02):
    """สุ่มความต่างเล็กน้อยเพื่อให้เสียงดูเป็นธรรมชาติ (ไม่เป็นหุ่นยนต์)"""
    # สุ่ม Pitch เล็กน้อย (-0.1 ถึง 0.1 semitones)
    random_pitch = np.random.uniform(-0.1, 0.1)
    y_human = librosa.effects.pitch_shift(y, sr=sr, n_steps=random_pitch)
    return y_human

# --- 4. MAIN UI LAYOUT ---
st.title("🥷 ASSASSIN 144: UNIFIED MATRIX CORE")
st.write("STATUS: `ENCRYPTED` | TARGET DATABASE: `sooksun1`")

tabs = st.tabs(["🚀 THE CORE", "📊 ANALYZER (MIMIC)", "📺 MATRIX LOGS"])

# --- TAB 1: THE CORE (Visualizer) ---
with tabs[0]:
    st.subheader("SYSTEM VISUALIZER")
    # ตัวเลข 6 ทิศทาง (จำลอง)
    core_html = """
    <div style="border:2px solid #0ff; padding:50px; text-align:center; background:#050505; border-radius:15px; box-shadow: 0 0 20px #0ff;">
        <h1 style="font-size:4rem; margin:0; color:#fff;">144.00</h1>
        <p style="color:#0ff;">OPTIMIZED HARMONIC RESONANCE</p>
    </div>
    """
    components.html(core_html, height=250)
    st.info("💡 ระบบจะอัปเดตค่า Unified Score อัตโนมัติเมื่อมีการวิเคราะห์ไฟล์เสียง")

# --- TAB 2: ANALYZER (เรียนแบบเสียง & จูน) ---
with tabs[1]:
    st.header("🎯 VOICE MIMICRY ENGINE")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. TARGET (ต้นฉบับ)")
        ref_file = st.file_uploader("อัปโหลดเสียงที่ต้องการเรียนแบบ", type=["mp3", "wav"], key="ref")
        if ref_file:
            y_ref, sr_ref = librosa.load(ref_file)
            ref_stats = analyze_audio_144(y_ref, sr_ref)
            st.session_state['ref_stats'] = ref_stats
            st.success(f"Target Score: {ref_stats['Score']:.2f}")

    with col2:
        st.markdown("### 2. YOUR VOICE (เสียงของคุณ)")
        user_file = st.file_uploader("อัปโหลดเสียงเลียนแบบของคุณ", type=["mp3", "wav"], key="user")
        
        if user_file:
            y_u, sr_u = librosa.load(user_file)
            
            st.write("---")
            st.write("🛠️ **TUNING TOOLS** (ปรับให้เกือบตรง)")
            t_pitch = st.slider("Pitch Adjust (คีย์)", -5.0, 5.0, 0.0)
            t_speed = st.slider("Speed Adjust (ความเร็ว)", 0.5, 2.0, 1.0)
            use_human = st.checkbox("เปิดโหมด Human Touch (สุ่มความต่างเล็กน้อย)", value=True)
            
            # ประมวลผลเสียง
            y_proc = librosa.effects.pitch_shift(y_u, sr=sr_u, n_steps=t_pitch)
            y_proc = librosa.effects.time_stretch(y=y_proc, rate=t_speed)
            if use_human:
                y_proc = add_human_touch(y_proc, sr_u)
            
            # ลองฟังเสียงที่จูน
            buf = io.BytesIO()
            sf.write(buf, y_proc, sr_u, format='WAV')
            st.audio(buf.getvalue(), format="audio/wav")
            
            if st.button("📡 EXECUTE ANALYSIS (ส่งเข้า MATRIX)"):
                u_stats = analyze_audio_144(y_proc, sr_u)
                
                # คำนวณความเหมือน (Similarity)
                if 'ref_stats' in st.session_state:
                    t = st.session_state['ref_stats']
                    dist = np.sqrt((u_stats['X']-t['X'])**2 + (u_stats['Y']-t['Y'])**2 + (u_stats['Z']-t['Z'])**2)
                    similarity = max(0, 100 - (dist/12)) # หารด้วย 12 เพื่อสเกลคะแนน
                    
                    st.write(f"## ความเหมือน: {similarity:.2f}%")
                    
                    # ตรวจสอบจุดสมดุล (Human vs Robot)
                    if 92 <= similarity <= 97:
                        st.balloons()
                        st.success("💎 **PERFECT HUMAN MATCH**: เสียงเนียนและเป็นธรรมชาติที่สุด!")
                    elif similarity > 98:
                        st.warning("🤖 **ROBOTIC ALERT**: เสียงตรงเกินไปจนฟังดูปลอม (AI)")
                    
                    # ส่งเข้า Firebase
                    db.reference('assassin_144/logs').push({
                        "agent": "AGENT_X",
                        "score": round(u_stats['Score'], 2),
                        "similarity": round(similarity, 2),
                        "x": round(u_stats['X'], 2),
                        "y": round(u_stats['Y'], 2),
                        "z": round(u_stats['Z'], 2),
                        "timestamp": time.time()
                    })
                    st.info("บันทึกข้อมูลเข้าสู่ Cloud Firestore สำเร็จ")

# --- TAB 3: MATRIX LOGS (ประวัติ) ---
with tabs[2]:
    st.header("📺 ANALYTICS HISTORY")
    try:
        logs = db.reference('assassin_144/logs').get()
        if logs:
            df = pd.DataFrame.from_dict(logs, orient='index')
            st.dataframe(df.sort_values('timestamp', ascending=False), use_container_width=True)
            st.line_chart(df['similarity'])
        else:
            st.write("NO DATA FOUND IN MATRIX CORE.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
