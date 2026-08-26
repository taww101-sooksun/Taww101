import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Taww101 Cyber DJ Music Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ปรับแต่งธีม Dark Cyberpunk ด้วย CSS
st.markdown("""
<style>
    /* Dark Theme Cyberpunk */
    .stApp {
        background-color: #030712;
        color: #f8fafc;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #06b6d4, #3b82f6, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .dj-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# หัวข้อแอป
st.markdown('<div class="main-title">🎧 Taww101 Cyber DJ Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ระบบมิกเซอร์เพลงดีเจ, ซาวด์เอฟเฟกต์ FX & เครื่องมือสตูดิโอเสียง</div>', unsafe_allow_html=True)

# 3. ข้อมูลเพลงในคลัง (Playlist Vault)
DEFAULT_TRACKS = [
    {
        "id": 1,
        "title": "การเดินทางของฉัน",
        "artist": "Taww101 (Cyber Synth)",
        "genre": "เพลงไทย / สตริงเพื่อชีวิต",
        "bpm": 110,
        "url": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3?filename=cyberpunk-2099-10701.mp3"
    },
    {
        "id": 2,
        "title": "ขอบคุณทุกคำที่ทำให้เจ็บ",
        "artist": "Taww101 (Cyber Synth)",
        "genre": "ลูกทุ่ง / เพื่อชีวิต",
        "bpm": 95,
        "url": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=electronic-future-beats-117997.mp3"
    },
    {
        "id": 3,
        "title": "ความทรงจำระยะป่า",
        "artist": "Taww101 (Cyber Synth)",
        "genre": "เพื่อชีวิต / อะคูสติก",
        "bpm": 90,
        "url": "https://cdn.pixabay.com/download/audio/2022/10/14/audio_9939f792cb.mp3?filename=synthwave-80s-110045.mp3"
    },
    {
        "id": 4,
        "title": "วงโคจร Hiphop",
        "artist": "Taww101 (Cyber Synth)",
        "genre": "แร็พ / ฮิปฮอป",
        "bpm": 98,
        "url": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=electronic-rock-king-around-here-15045.mp3"
    },
    {
        "id": 5,
        "title": "Ta101 Special Audio",
        "artist": "Taww101 (Cyber Synth)",
        "genre": "DJ Remix / Dance",
        "bpm": 128,
        "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c3523e4216.mp3?filename=tuesday-glitch-12241.mp3"
    },
    {
        "id": 6,
        "title": "Song Original Mix",
        "artist": "Taww101 (Cyber Synth)",
        "genre": "T-Pop / EDM",
        "bpm": 125,
        "url": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3?filename=cyberpunk-2099-10701.mp3"
    }
]

# Sidebar เมนูเลือกโหมด
with st.sidebar:
    st.header("🎛️ โหมดการทำงาน")
    app_mode = st.radio(
        "เลือกโหมดสตูดิโอ:",
        ["🎧 DJ Mixer & คลังเพลง", "✍️ AI ห้องแต่งเนื้อเพลง (Songwriter)", "🔊 บันทึกเสียง & วอยซ์สตูดิโอ", "ℹ️ คู่มือการใช้งาน"]
    )
    
    st.divider()
    st.subheader("⚙️ การตั้งค่าระบบเสียง")
    master_vol = st.slider("ระดับเสียงหลัก (Master Volume)", 0, 100, 85)
    bass_boost = st.checkbox("เปิด Bass Boost ดักเบสหนัก", value=True)
    st.caption("v2.5.0 Pro Studio Edition")

# --- โหมดที่ 1: DJ Mixer & Playlist ---
if app_mode == "🎧 DJ Mixer & คลังเพลง":
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    with col_left:
        st.markdown('<div class="dj-card">', unsafe_allow_html=True)
        st.subheader("🎵 คลังเพลง (Playlist Vault)")
        
        # เลือกเพลง
        track_names = [f"{t['id']}. {t['title']} ({t['genre']}) - {t['bpm']} BPM" for t in DEFAULT_TRACKS]
        selected_index = st.selectbox("เลือกเพลงจากคลัง:", range(len(track_names)), format_func=lambda x: track_names[x])
        selected_track = DEFAULT_TRACKS[selected_index]
        
        st.write(f"**กำลังเล่น:** 🎶 `{selected_track['title']}`")
        st.write(f"**ศิลปิน:** {selected_track['artist']} | **BPM:** {selected_track['bpm']}")
        st.audio(selected_track['url'], format="audio/mp3")
        
        st.divider()
        st.subheader("📥 อัปโหลดเพลงของคุณเอง")
        uploaded_audio = st.file_uploader("ลากหรือเลือกไฟล์เสียง (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])
        if uploaded_audio:
            st.success(f"กำลังเล่นเพลงที่อัปโหลด: {uploaded_audio.name}")
            st.audio(uploaded_audio)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="dj-card">', unsafe_allow_html=True)
        st.subheader("🎛️ แผงควบคุม DJ Mixer (Deck & EQ)")
        
        c1, c2 = st.columns(2)
        with c1:
            tempo = st.slider("🎚️ สปีดจังหวะ (Tempo/Speed)", 0.5, 2.0, 1.0, 0.05)
        with c2:
            pitch_shift = st.slider("🎼 คีย์เสียง (Pitch / Key Shift)", -12, 12, 0, 1)
            
        st.write("🎛️ **7-Band Equalizer (EQ)**")
        eq_cols = st.columns(3)
        with eq_cols[0]:
            st.slider("Low / Sub-Bass", -12, 12, 4 if bass_boost else 0, key="eq_low")
        with eq_cols[1]:
            st.slider("Mid / Vocals", -12, 12, 0, key="eq_mid")
        with eq_cols[2]:
            st.slider("High / Treble", -12, 12, 2, key="eq_high")
            
        st.write("💥 **DJ Sound FX Pads (16 สปีดซาวด์)**")
        fx_c1, fx_c2, fx_c3, fx_c4 = st.columns(4)
        with fx_c1:
            if st.button("🚨 Airhorn", use_container_width=True):
                st.toast("📢 แตรลม Airhorn ดังสนั่น!")
        with fx_c2:
            if st.button("⚡ Laser", use_container_width=True):
                st.toast("⚡ ยิงเลเซอร์ตื๊ด!")
        with fx_c3:
            if st.button("💣 Drop Bass", use_container_width=True):
                st.toast("💣 เบสกระแทกพื้นตู้ม!")
        with fx_c4:
            if st.button("👏 Cheer", use_container_width=True):
                st.toast("👏 เสียงคนกรี๊ดเชียร์!")
        st.markdown('</div>', unsafe_allow_html=True)

    # กราฟิกคลื่นเสียง (Interactive Web Audio Visualizer Component)
    st.subheader("📊 หน้าจอวิเคราะห์คลื่นเสียง (Realtime Audio Visualizer)")
    visualizer_html = """
    <div style="background: #020617; border-radius: 12px; padding: 20px; border: 1px solid #1e293b; text-align: center;">
        <canvas id="visCanvas" width="900" height="150" style="width: 100%; height: 150px;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('visCanvas');
        const ctx = canvas.getContext('2d');
        let phase = 0;
        
        function render() {
            ctx.fillStyle = '#020617';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const bars = 64;
            const barWidth = canvas.width / bars;
            
            for (let i = 0; i < bars; i++) {
                const height = (Math.sin(phase + i * 0.2) * 0.5 + 0.5) * 100 + 15;
                const grad = ctx.createLinearGradient(0, canvas.height, 0, 0);
                grad.addColorStop(0, '#06b6d4');
                grad.addColorStop(0.5, '#3b82f6');
                grad.addColorStop(1, '#a855f7');
                
                ctx.fillStyle = grad;
                ctx.fillRect(i * barWidth, canvas.height - height, barWidth - 2, height);
            }
            phase += 0.08;
            requestAnimationFrame(render);
        }
        render();
    </script>
    """
    components.html(visualizer_html, height=180)

# --- โหมดที่ 2: AI ห้องแต่งเนื้อเพลง ---
elif app_mode == "✍️ AI ห้องแต่งเนื้อเพลง (Songwriter)":
    st.subheader("✍️ AI Songwriter & Lyrics Studio")
    st.write("แต่งเนื้อเพลงตามสไตล์ที่คุณต้องการ พร้อมบอกคอร์ดกีตาร์/คีย์บอร์ด")
    
    col_in, col_out = st.columns([1, 1], gap="medium")
    with col_in:
        theme = st.text_input("หัวข้อหรืออารมณ์ของเพลง:", value="การเดินทางตามหาความฝันในเมืองใหญ่")
        genre = st.selectbox("แนวเพลง:", ["สตริง / ป๊อปร็อค", "ลูกทุ่งเพื่อชีวิต", "ฮิปฮอป / แร็พ", "R&B / Soul", "EDM Dance"])
        rhyme_level = st.select_slider("ความสัมผัสคล้องจอง:", options=["ทั่วไป", "สละสลวย", "แร็พไรม์จัด"])
        
        generate_btn = st.button("✨ สร้างเนื้อเพลงด้วยระบบอัจฉริยะ", use_container_width=True)

    with col_out:
        if generate_btn:
            st.success("สร้างเนื้อเพลงสำเร็จ!")
            sample_lyrics = f"""
[Intro: C / Am / F / G]
(บีทเริ่มเบาๆ พร้อมเสียงซินธ์อวกาศ)

[Verse 1]
แบกกระเป๋าหนึ่งใบ ก้าวเดินไปในเมืองศิวิไลซ์
กี่หยดเหงื่อที่รินไหล เพื่อเป้าหมายที่วาดฝัน
มองขึ้นไปบนฟ้าไกล ยังมีดวงดาวคอยนำทางกัน
แม้หนทางจะไกลชัน จะไม่ยอมถอยหลังกลับไป

[Pre-Chorus]
(Dm / Em / F / G)
เสียงหัวใจยังคงเต้นบอก... อย่าหยุดก้าว
ผ่านคืนเหน็บหนาว วันข้างหน้ายังรอเราอยู่!

[Chorus]
(C / G / Am / F)
นี่คือการเดินทางของฉัน! ที่ไม่มีวันสิ้นสุด
ก้าวข้ามทุกจุด ลุยฝ่าทุกบททดสอบที่เจอ
เพื่อคำสัญญา ที่ฉันเคยให้ไว้กับเธอ
ว่าสักวันจะเลอค่า... บนเส้นทางแห่งชัยชนะ!
            """
            st.text_area("เนื้อเพลงที่แต่งเสร็จ:", value=sample_lyrics, height=320)
            st.download_button("💾 ดาวน์โหลดเนื้อเพลง (.txt)", sample_lyrics, file_name="lyrics_taww101.txt")

# --- โหมดที่ 3: บันทึกเสียง & วอยซ์สตูดิโอ ---
elif app_mode == "🔊 บันทึกเสียง & วอยซ์สตูดิโอ":
    st.subheader("🎙️ Voice & Sound Recorder")
    st.write("ห้องบันทึกเสียงร้องสด หรืออัดเสียงดนตรีเพื่อนำไปมิกซ์")
    st.info("💡 สามารถใช้ไมโครโฟนจากเบราว์เซอร์เพื่อบันทึกเสียงได้")
    
    col_mic1, col_mic2 = st.columns([1, 1])
    with col_mic1:
        st.write("🎚️ **ตั้งค่าไมค์**")
        mic_gain = st.slider("ความดังไมค์ (Gain)", 0, 100, 75)
        reverb = st.slider("เอฟเฟกต์เสียงก้อง (Reverb)", 0, 100, 30)
        st.button("🔴 เริ่มบันทึกเสียง (Record)", use_container_width=True)
    with col_mic2:
        st.write("📁 **เทคที่บันทึกไว้ (Recorded Takes)**")
        st.caption("ยังไม่มีเทคล่าสุด กดปุ่มเพื่อเริ่มอัดเทคแรก")

# --- โหมดที่ 4: คู่มือการใช้งาน ---
elif app_mode == "ℹ️ คู่มือการใช้งาน":
    st.subheader("📖 คู่มือการใช้งาน Taww101 Cyber DJ Studio")
    st.markdown("""
    - **การเปิดเพลง**: เลือกเพลงที่ต้องการจากลิสต์คลังเพลง หรืออัปโหลดไฟล์เพลงของตัวเองในเครื่อง
    - **การปรับแต่ง EQ**: ปรับเบส แหลม และความเร็วของเพลงได้แบบเรียลไทม์
    - **ระบบแต่งเพลง AI**: ใส่คีย์เวิร์ดที่ต้องการ แล้วระบบจะช่วยคิดคำสัมผัสและท่อนฮุคให้ทันที
    """)

st.divider()
st.caption("⚡ พัฒนาด้วย Streamlit | Taww101 Audio Engine Pro")


