import streamlit as st
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

# --- 1. INITIAL SETUP ---
st.set_page_config(layout="wide", page_title="SYNAPSE: ASSASSIN 144")

if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            firebase_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://firebaseio.com"
            })
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# --- 2. CORE FUNCTIONS ---
def analyze_audio_144(y, sr):
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)
    if len(y_trimmed) == 0: y_trimmed = y
    pitches, magnitudes = librosa.piptrack(y=y_trimmed, sr=sr)
    x_val = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 432.0
    y_val = np.mean(librosa.feature.rms(y=y_trimmed)) * 1000
    z_val = np.mean(librosa.feature.spectral_centroid(y=y_trimmed, sr=sr)) / 100
    score = np.sqrt(x_val**2 + y_val**2 + z_val**2) / 10
    return {"X": x_val, "Y": y_val, "Z": z_val, "Score": score, "Wave": y_trimmed}

def auto_calibrate_pitch(target_x, user_y, user_sr):
    """คำนวณหาค่า Pitch ที่ควรปรับให้อัตโนมัติ"""
    u_pitches, _ = librosa.piptrack(y=user_y, sr=user_sr)
    u_pitch_mean = np.mean(u_pitches[u_pitches > 0]) if np.any(u_pitches > 0) else 432.0
    # สูตรคำนวณความต่างของตัวโน้ต (Semitones)
    pitch_diff = 12 * np.log2(target_x / u_pitch_mean)
    return round(float(pitch_diff), 2)

# --- 3. UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #0f0; }
    .stButton>button { height: 3em; background: #004444; color: #0ff; border: 1px solid #0ff; width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🥷 ASSASSIN 144: MATRIX CORE")
tabs = st.tabs(["🚀 THE CORE", "📊 ANALYZER", "📺 LOGS"])

with tabs[0]:
    st.html('<div style="border:2px solid #0ff; padding:30px; text-align:center; background:#050505; border-radius:15px;"><h1 style="font-size:3rem; margin:0; color:#fff;">144.00</h1><p style="color:#0ff;">OPTIMIZED HARMONIC RESONANCE</p></div>')

with tabs[1]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 TARGET")
        ref_file = st.file_uploader("ไฟล์ต้นฉบับ", type=["mp3", "wav"], key="ref_up")
        if ref_file:
            y_ref, sr_ref = librosa.load(ref_file)
            st.session_state['ref_data'] = analyze_audio_144(y_ref, sr_ref)
            st.success("Target Locked")

    with col2:
        st.subheader("🎙️ MIMIC")
        user_file = st.file_uploader("ไฟล์เสียงคุณ", type=["mp3", "wav"], key="user_up")
        
        if user_file:
            y_u, sr_u = librosa.load(user_file)
            
            # --- ระบบ AUTO CALIBRATE ---
            if st.button("✨ AI AUTO CALIBRATE"):
                if 'ref_data' in st.session_state:
                    suggested_p = auto_calibrate_pitch(st.session_state['ref_data']['X'], y_u, sr_u)
                    st.session_state['p_val'] = suggested_p
                    st.toast(f"ปรับ Pitch อัตโนมัติ: {suggested_p}")
                else:
                    st.error("ต้องอัปโหลด Target ก่อนครับ")

            # ดึงค่าจากปุ่ม Auto หรือ Manual Slider
            p_init = st.session_state.get('p_val', 0.0)
            p_adj = st.slider("Pitch Adjust", -12.0, 12.0, p_init, key="p_slider")
            s_adj = st.slider("Speed Adjust", 0.5, 2.0, 1.0)
            
            # ประมวลผล (เช็กย่อหน้าตรงนี้ให้ดี)
            y_p = librosa.effects.pitch_shift(y_u, sr=sr_u, n_steps=p_adj)
            y_p = librosa.effects.time_stretch(y=y_p, rate=s_adj)
            
            # เล่นเสียง
            tmp_buf = io.BytesIO()
            sf.write(tmp_buf, y_p, sr_u, format='WAV')
            st.audio(tmp_buf.getvalue())
            
            if st.button("📡 ANALYZE NOW"):
                u_res = analyze_audio_144(y_p, sr_u)
                if 'ref_data' in st.session_state:
                    ref = st.session_state['ref_data']
                    diff = np.sqrt((u_res['X']-ref['X'])**2 + (u_res['Y']-ref['Y'])**2 + (u_res['Z']-ref['Z'])**2)
                    sim = max(0, 100 - (diff/15))
                    st.metric("Similarity Score", f"{sim:.2f}%")
                    
                    fig, ax = plt.subplots(figsize=(8, 2), facecolor='black')
                    librosa.display.waveshow(ref['Wave'], sr=sr_ref, ax=ax, color='#0ff', alpha=0.5)
                    librosa.display.waveshow(u_res['Wave'], sr=sr_u, ax=ax, color='#0f0', alpha=0.7)
                    ax.set_axis_off()
                    st.pyplot(fig)
                    
                    try:
                        db.reference('assassin_144/logs').push({"sim": round(sim, 2), "time": time.time()})
                    except: pass

with tabs[2]:
    st.subheader("HISTORY")
    try:
        data = db.reference('assassin_144/logs').get()
        if data: st.write(pd.DataFrame.from_dict(data, orient='index'))
    except: st.write("No Connection")
