import streamlit as st
import streamlit.components.v1 as components
import librosa
import librosa.display
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import time
import soundfile as sf
import io
import matplotlib.pyplot as plt

# --- 1. INITIAL SETUP & FIREBASE ---
st.set_page_config(layout="wide", page_title="SYNAPSE: ASSASSIN 144 CORE")

if not firebase_admin._apps:
    try:
        firebase_creds = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://firebaseio.com"
        })
    except Exception as e:
        st.error(f"⚠️ Firebase Setup Error: {e}")

# --- 2. CSS NEON DESIGN (Modern Assassin Style) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #0f0; font-family: 'Courier New', monospace; }
    .stTabs [data-baseweb="tab"] { background-color: #111; color: #0f0; border: 1px solid #333; }
    .stTabs [aria-selected="true"] { border-color: #0ff; box-shadow: 0 0 10px #0ff; }
    h1, h2, h3 { color: #0ff !important; text-shadow: 0 0 8px #0ff; }
    .stButton>button {
        background: linear-gradient(45deg, #004444, #000);
        color: #0ff; border: 1px solid #0ff; width: 100%;
        transition: 0.3s; text-transform: uppercase; letter-spacing: 2px;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #0ff; color: #fff; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CORE PROCESSING FUNCTIONS ---
def process_audio_clean(y):
    """ตัดช่วงเงียบและ Normalize เพื่อความแม่นยำ"""
    y_trimmed, _ = librosa.effects.trim(y, top_db=25)
    if len(y_trimmed) == 0: return y
    return librosa.util.normalize(y_trimmed)

def analyze_audio_144(y, sr):
    """สกัดค่าสถิติเพื่อใช้เปรียบเทียบ"""
    y = process_audio_clean(y)
    
    # X: Pitch (เน้นช่วงที่มีความเข้มเสียงสูง)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    mask = magnitudes > np.median(magnitudes)
    x_val = np.mean(pitches[mask]) if np.any(mask) else 432.0
    
    # Y: Energy (RMS)
    y_val = np.mean(librosa.feature.rms(y=y)) * 1000
    
    # Z: Brightness
    z_val = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)) / 100
    
    score = np.sqrt(x_val**2 + y_val**2 + z_val**2) / 10
    return {"X": x_val, "Y": y_val, "Z": z_val, "Score": score, "Wave": y}

def add_human_touch(y, sr):
    """สุ่มความเพี้ยนเล็กน้อยให้ดูเป็นธรรมชาติ"""
    random_pitch = np.random.uniform(-0.08, 0.08)
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=random_pitch)

# --- 4. MAIN UI LAYOUT ---
st.title("🥷 ASSASSIN 144: UNIFIED MATRIX CORE")
st.write(f"STATUS: `OPERATIONAL` | {time.strftime('%Y-%m-%d %H:%M:%S')}")

tabs = st.tabs(["🚀 THE CORE", "📊 ANALYZER (MIMIC)", "📺 MATRIX LOGS"])

# --- TAB 1: THE CORE ---
with tabs[0]:
    core_html = """
    <div style="border:2px solid #0ff; padding:40px; text-align:center; background:#050505; border-radius:15px; box-shadow: 0 0 25px #0ff;">
        <h1 style="font-size:5rem; margin:0; color:#fff; font-family:monospace;">144.00</h1>
        <p style="color:#0ff; letter-spacing:5px;">OPTIMIZED HARMONIC RESONANCE</p>
    </div>
    """
    components.html(core_html, height=220)
    st.info("💡 ระบบจะดึงค่าจาก Target ล่าสุดมาแสดงผลที่นี่ (Coming Soon: Real-time Sync)")

# --- TAB 2: ANALYZER ---
with tabs[1]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 TARGET (ต้นฉบับ)")
        ref_file = st.file_uploader("Upload Target Voice", type=["mp3", "wav"], key="ref")
        if ref_file:
            y_ref, sr_ref = librosa.load(ref_file)
            ref_stats = analyze_audio_144(y_ref, sr_ref)
            st.session_state['ref_stats'] = ref_stats
            st.success(f"Target Acquired: Score {ref_stats['Score']:.2f}")

    with col2:
        st.markdown("### 🎙️ YOUR VOICE (เสียงของคุณ)")
        user_file = st.file_uploader("Upload Your Voice", type=["mp3", "wav"], key="user")
        
        if user_file:
            y_u, sr_u = librosa.load(user_file)
            st.write("---")
            t_pitch = st.slider("Pitch Calibration", -5.0, 5.0, 0.0)
            t_speed = st.slider("Temporal Scale", 0.5, 2.0, 1.0)
            use_human = st.checkbox("Enable Human Touch (Random Variance)", value=True)
            
            # Processing
            y_proc = librosa.effects.pitch_shift(y_u, sr=sr_u, n_steps=t_pitch)
            y_proc = librosa.effects.time_stretch(y=y_proc, rate=t_speed)
            if use_human: y_proc = add_human_touch(y_proc, sr_u)
            
            st.audio(io.BytesIO(sf.write(io.BytesIO(), y_proc, sr_u, format='WAV').getvalue() if False else sf.write(io.BytesIO(), y_proc, sr_u, format='WAV') or True and io.BytesIO()), format="audio/wav") # Shortened for display logic
            
            # Re-write audio for playback
            buf = io.BytesIO()
            sf.write(buf, y_proc, sr_u, format='WAV')
            st.audio(buf.getvalue(), format="audio/wav")

            if st.button("📡 EXECUTE ANALYSIS"):
                u_stats = analyze_audio_144(y_proc, sr_u)
                
                if 'ref_stats' in st.session_state:
                    t = st.session_state['ref_stats']
                    dist = np.sqrt((u_stats['X']-t['X'])**2 + (u_stats['Y']-t['Y'])**2 + (u_stats['Z']-t['Z'])**2)
                    similarity = max(0, 100 - (dist/15)) 
                    
                    st.divider()
                    st.header(f"Similarity: {similarity:.2f}%")
                    
                    # Waveform Comparison
                    fig, ax = plt.subplots(figsize=(10, 3), facecolor='black')
                    librosa.display.waveshow(t['Wave'], sr=sr_ref, ax=ax, alpha=0.4, color='#0ff', label='Target')
                    librosa.display.waveshow(u_stats['Wave'], sr=sr_u, ax=ax, alpha=0.6, color='#0f0', label='Mimic')
                    ax.set_axis_off()
                    ax.legend()
                    st.pyplot(fig)

                    if 92 <= similarity <= 97:
                        st.balloons(); st.success("💎 PERFECT HUMAN MATCH: เนียนระดับสายลับ!")
                    elif similarity > 98:
                        st.warning("🤖 ROBOTIC ALERT: เสียงตรงกันเกินไปจนดูไม่เป็นธรรมชาติ")
                    
                    # Firebase Log
                    try:
                        db.reference('assassin_144/logs').push({
                            "agent": "AGENT_X", "similarity": round(similarity, 2),
                            "timestamp": time.time(), "score": round(u_stats['Score'], 2)
                        })
                        st.caption("Data synced to Matrix Core.")
                    except: st.error("Firebase Sync Failed.")

# --- TAB 3: MATRIX LOGS ---
with tabs[2]:
    try:
        logs = db.reference('assassin_144/logs').get()
        if logs:
            df = pd.DataFrame.from_dict(logs, orient='index')
            st.dataframe(df.sort_values('timestamp', ascending=False), use_container_width=True)
            st.line_chart(df['similarity'])
        else: st.write("NO DATA IN MATRIX.")
    except: st.write("Waiting for Connection...")
