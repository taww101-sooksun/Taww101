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

# เชื่อมต่อ Firebase (ใช้ try-except เพื่อป้องกันแอปค้างถ้าต่อไม่ได้)
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            firebase_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://firebaseio.com" # ใส่ URL ของคุณตรงนี้
            })
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# --- 2. CSS DESIGN (ปรับให้ปุ่มกดง่ายขึ้นบนมือถือ) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #0f0; }
    h1, h2, h3 { color: #0ff !important; }
    /* ปรับปุ่มให้ใหญ่และกดง่าย */
    .stButton>button {
        height: 3em;
        background: #004444;
        color: #0ff;
        border: 1px solid #0ff;
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CORE FUNCTIONS ---
def analyze_audio_144(y, sr):
    # ตัดเสียงเงียบก่อนวิเคราะห์
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)
    if len(y_trimmed) == 0: y_trimmed = y
    
    # คำนวณค่า X, Y, Z
    pitches, magnitudes = librosa.piptrack(y=y_trimmed, sr=sr)
    x_val = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 432.0
    y_val = np.mean(librosa.feature.rms(y=y_trimmed)) * 1000
    z_val = np.mean(librosa.feature.spectral_centroid(y=y_trimmed, sr=sr)) / 100
    
    score = np.sqrt(x_val**2 + y_val**2 + z_val**2) / 10
    return {"X": x_val, "Y": y_val, "Z": z_val, "Score": score, "Wave": y_trimmed}

# --- 4. UI LAYOUT ---
st.title("🥷 ASSASSIN 144: MATRIX CORE")

tabs = st.tabs(["🚀 THE CORE", "📊 ANALYZER", "📺 LOGS"])

with tabs[0]:
    # ใช้ st.html แทน components.html ตามที่ Logs แนะนำ
    st.html("""
    <div style="border:2px solid #0ff; padding:30px; text-align:center; background:#050505; border-radius:15px;">
        <h1 style="font-size:3rem; margin:0; color:#fff;">144.00</h1>
        <p style="color:#0ff;">OPTIMIZED HARMONIC RESONANCE</p>
    </div>
    """)

with tabs[1]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 TARGET")
        ref_file = st.file_uploader("ไฟล์ต้นฉบับ", type=["mp3", "wav"], key="ref_up")
        if ref_file:
            y_ref, sr_ref = librosa.load(ref_file)
            st.session_state['ref_data'] = analyze_audio_144(y_ref, sr_ref)
            st.success("Target Ready")

    with col2:
        st.subheader("🎙️ MIMIC")
        user_file = st.file_uploader("ไฟล์เสียงคุณ", type=["mp3", "wav"], key="user_up")
        
        # --- ในส่วน if user_file: ---
with col2:
    # ... (โค้ดเดิม) ...
    
    if st.button("✨ AI AUTO CALIBRATE (ปรับอัตโนมัติ)"):
        if 'ref_data' in st.session_state:
            # สั่งคำนวณค่าที่ควรจะเป็น
            suggested_pitch = auto_calibrate(st.session_state['ref_data'], y_u, sr_u)
            
            # เก็บค่าลง session_state เพื่อให้ Slider เลื่อนตาม
            st.session_state['p_adj'] = suggested_pitch
            st.success(f"ระบบปรับ Pitch ให้คุณแล้ว: {suggested_pitch} semitones")
            st.rerun() # สั่งให้แอปโหลดใหม่เพื่ออัปเดตค่าใน Slider
        else:
            st.warning("กรุณาอัปโหลด Target ก่อนครับ")

    # ปรับ Slider ให้ดึงค่าจาก session_state (ถ้ามี)
    p_val = st.session_state.get('p_adj', 0.0)
    p_adj = st.slider("Pitch Adjust", -12.0, 12.0, p_val, key="pitch_slider")
    
    # ... (ส่วนประมวลผลเสียง y_p เหมือนเดิม) ...

            # ประมวลผล
            y_p = librosa.effects.pitch_shift(y_u, sr=sr_u, n_steps=p_adj)
            y_p = librosa.effects.time_stretch(y=y_p, rate=s_adj)
            
            # เล่นเสียง (แยกออกออกมาให้ชัดเจน)
            tmp_buf = io.BytesIO()
            sf.write(tmp_buf, y_p, sr_u, format='WAV')
            st.audio(tmp_buf.getvalue())
            
            st.divider()
            
            # ปุ่ม Execute (ใส่ Key ป้องกันบั๊ก)
            if st.button("📡 ANALYZE NOW", key="run_analysis"):
                u_res = analyze_audio_144(y_p, sr_u)
                
                if 'ref_data' in st.session_state:
                    ref = st.session_state['ref_data']
                    # คำนวณความเหมือน
                    diff = np.sqrt((u_res['X']-ref['X'])**2 + (u_res['Y']-ref['Y'])**2 + (u_res['Z']-ref['Z'])**2)
                    sim = max(0, 100 - (diff/15))
                    
                    st.metric("Similarity Score", f"{sim:.2f}%")
                    
                    # วาดกราฟเปรียบเทียบ
                    fig, ax = plt.subplots(figsize=(8, 2), facecolor='black')
                    librosa.display.waveshow(ref['Wave'], sr=sr_ref, ax=ax, color='#0ff', alpha=0.5)
                    librosa.display.waveshow(u_res['Wave'], sr=sr_u, ax=ax, color='#0f0', alpha=0.7)
                    ax.set_axis_off()
                    st.pyplot(fig)
                    
                    # บันทึกลง Firebase
                    try:
                        db.reference('assassin_144/logs').push({
                            "similarity": round(sim, 2),
                            "timestamp": time.time()
                        })
                    except:
def auto_calibrate(target_stats, user_y, user_sr):
    """คำนวณหาค่า Pitch และ Speed ที่ควรจะเป็นโดยอัตโนมัติ"""
    # วิเคราะห์เสียงผู้ใช้ก่อนปรับ
    u_pitches, _ = librosa.piptrack(y=user_y, sr=user_sr)
    u_pitch_mean = np.mean(u_pitches[u_pitches > 0]) if np.any(u_pitches > 0) else 432.0
    
    # 1. คำนวณ Pitch Shift (หาความต่างเป็น Semitones)
    # สูตร: n_steps = 12 * log2(f2 / f1)
    pitch_diff = 12 * np.log2(target_stats['X'] / u_pitch_mean)
    
    # 2. คำนวณ Speed (เทียบความยาวคลื่นเสียง - ถ้าสั้นไปให้ยืด ถ้ายาวไปให้หด)
    # ในที่นี้สมมติว่าเราต้องการให้ Energy (Y) ใกล้เคียงกัน หรือเทียบ Duration ง่ายๆ
    # (เวอร์ชันนี้เน้น Pitch เป็นหลักก่อนเพื่อความเนียน)
    
    return round(pitch_diff, 2)
                        st.warning("Firebase sync skipped.")

with tabs[2]:
    st.subheader("HISTORY")
    try:
        data = db.reference('assassin_144/logs').get()
        if data:
            st.write(pd.DataFrame.from_dict(data, orient='index').sort_values('timestamp', ascending=False))
        else:
            st.write("No data found.")
    except:
        st.write("Connect to Firebase to see logs.")
