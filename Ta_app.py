import numpy as np
import streamlit as st
from scipy.io import wavfile
import librosa
import time
import io  # เพิ่มเข้ามาเพื่อใช้จัดการก้อนข้อมูลดาวน์โหลดในหน่วยความจำจริง

# -----------------------------------------------------------
# 1. INPUT MODULE (จัดการข้อมูล Symbolic)
# -----------------------------------------------------------
class InputModule:
    """จัดการการแปลงข้อมูลดนตรีเชิงสัญลักษณ์ (Symbolic Data) และอารมณ์ให้เป็น Symbolic Sequence."""
    ROOT_VOCAB = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11} 
    
    def แปลง_คอร์ด_เป็น_ตัวเลข(self, chord_string):
        if not chord_string:
             return 0
        try:
            root = chord_string.split()[0].upper()
            return self.ROOT_VOCAB.get(root, 0)
        except:
             return 0

    def จัด_โครงสร้าง_คำสั่ง(self, คำสั่งคอร์ด, valence, arousal):
        num_chords = len(คำสั่งคอร์ด.split(','))
        total_length = num_chords * 50 if num_chords > 0 else 500
        
        symbolic_sequence = np.zeros((total_length, 3)) 
        chord_indices = [self.แปลง_คอร์ด_เป็น_ตัวเลข(c.strip()) for c in คำสั่งคอร์ด.split(',') if c.strip()]
        
        if chord_indices:
            for i, index in enumerate(chord_indices):
                start = i * 50
                end = (i + 1) * 50
                symbolic_sequence[start:end, 0] = index
        
        symbolic_sequence[:, 1] = valence
        symbolic_sequence[:, 2] = arousal
        
        st.sidebar.markdown(f"**Symbolic Sequence (Array A) Generated:** {symbolic_sequence.shape} (Time Steps, Features)")
        return symbolic_sequence

# -----------------------------------------------------------
# 2. AI SYNTHESIS ENGINE (จัดการ RNN และรายละเอียดดนตรี)
# -----------------------------------------------------------
class AISynthesisEngine:
    """จัดการการประมวลผล RNN และการสังเคราะห์รายละเอียดดนตรี (Rhythm-Based Features)."""
    def __init__(self, samplerate=44100):
        self.sampling_rate = samplerate

    def สร้าง_Vibrato_Wave(self, amplitude, frequency, duration_sec):
        time_axis = np.linspace(0, duration_sec, int(self.sampling_rate * duration_sec), endpoint=False)
        return amplitude * np.sin(2 * np.pi * frequency * time_axis)

    def สังเคราะห์_ด้วย_รายละเอียด_RBF(self, symbolic_sequence):
        st.sidebar.markdown("---")
        st.sidebar.markdown("**AI Synthesis Engine Processing...**")
        st.sidebar.markdown("1. Preparing Data for RNN...")
        st.sidebar.markdown("2. **RNN/Transformer Inference** (Mock: Generating MFCC features)...")
        
        mfcc_features = np.random.rand(symbolic_sequence.shape[0], 40) 
        st.sidebar.markdown("3. Applying Rhythm Humanization & Vibrato Correction...")
        return mfcc_features

# -----------------------------------------------------------
# 3. MASTERING MODULE (จัดการคุณภาพเสียง)
# -----------------------------------------------------------
class MasteringModule:
    """จัดการการแปลงคุณสมบัติเสียงให้เป็น Raw Audio และการมาสเตอร์เสียง."""
    def ใช้_Limiter(self, ข้อมูลเสียง, ceiling_value=0.99):
        return np.clip(ข้อมูลเสียง, -ceiling_value, ceiling_value)

    def เขียน_ไฟล์เพลง_สุดท้าย(self, mfcc_features, samplerate=44100):
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Mastering Module Processing...**")
        st.sidebar.markdown("1. **Vocoder** (Mock: Convert MFCC features back to Raw Audio)...")
        
        duration_sec = 5.0  # ล็อกเวลาจำลองไว้ที่ 5 วินาทีคงที่เพื่อความเสถียรของหน่วยความจำมือถือ
        
        # ปรับปรุงสัญญาณเสียงจำลองให้มีความนุ่มละมุนโอบล้อม (คลื่นความถี่บำบัด 432Hz) แทนเสียงซ่าสุ่ม
        t = np.linspace(0, duration_sec, int(samplerate * duration_sec), endpoint=False)
        ข้อมูลเสียง_สังเคราะห์ = 0.4 * np.sin(2 * np.pi * 432.0 * t)
        
        ข้อมูลเสียง_จำกัด = self.ใช้_Limiter(ข้อมูลเสียง_สังเคราะห์)
        st.sidebar.markdown("2. Applying Limiter (Peak Value Clipping)...")
        
        scaling_factor = 0.6
        ข้อมูลเสียง_Mastered = (ข้อมูลเสียง_จำกัด * scaling_factor * 32767).astype(np.int16)
        st.sidebar.markdown("3. LUFS Normalization (Mock) & Final Bit Depth Conversion (16-bit)...")
        
        return ข้อมูลเสียง_Mastered, samplerate

# -----------------------------------------------------------
# 4. MAIN APPLICATION LOGIC (ลำดับ 1 -> 2 -> 3)
# -----------------------------------------------------------
class RBAISystem:
    def __init__(self):
        self.input_module = InputModule()
        self.ai_engine = AISynthesisEngine()
        self.mastering_module = MasteringModule()

    def สังเคราะห์_เพลง_RBF(self, chord_sequence, emotion_dict):
        symbolic_seq = self.input_module.จัด_โครงสร้าง_คำสั่ง(chord_sequence, emotion_dict['valence'], emotion_dict['arousal'])
        mfcc_features = self.ai_engine.สังเคราะห์_ด้วย_รายละเอียด_RBF(symbolic_seq)
        ข้อมูลเสียง, samplerate = self.mastering_module.เขียน_ไฟล์เพลง_สุดท้าย(mfcc_features)
        return ข้อมูลเสียง, samplerate

# -----------------------------------------------------------
# 5. STREAMLIT UI 
# -----------------------------------------------------------
st.set_page_config(layout="wide", page_title="RBF AI Music Synthesizer (จำลอง)")
st.title("ระบบสังเคราะห์เพลง RBF AI (Rhythm-Based Feature)")
st.subheader("การจำลอง Flow การทำงานของ AI Music Generation Engine")

system = RBAISystem()

with st.expander("คำแนะนำและสถาปัตยกรรม", expanded=False):
    st.markdown("""
        แอปพลิเคชันนี้จำลองโครงสร้าง 3-Stage: **Input** (Symbolic Data) $\\rightarrow$ **AI Synthesis** (RNN/RBF) $\\rightarrow$ **Mastering** (Vocoder/LUFS)
    """)

st.header("1. Symbolic & Emotional Input")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### 🎹 Chord Sequence")
    chord_input = st.text_input("ป้อนลำดับคอร์ด (คั่นด้วยเครื่องหมายจุลภาค เช่น Cmaj7, Fm, G7)", "Cmaj7, Am, F, G", key="chord_input")

with col2:
    st.markdown("##### 😌 Valence (ความสุข/อารมณ์บวก)")
    valence_input = st.slider("ระดับ Valence (0 = ลบ, 1 = บวก)", min_value=0.0, max_value=1.0, value=0.7, step=0.01)

with col3:
    st.markdown("##### ⚡ Arousal (ความตื่นเต้น/พลังงาน)")
    arousal_input = st.slider("ระดับ Arousal (0 = สงบ, 1 = ตื่นเต้น)", min_value=0.0, max_value=1.0, value=0.6, step=0.01)

emotion_data = {'valence': valence_input, 'arousal': arousal_input}
st.markdown("---")

if st.button("🚀 สังเคราะห์เพลงด้วย RBF AI", type="primary"):
    with st.spinner("กำลังประมวลผลระบบสังเคราะห์ 3 ขั้นตอน..."):
        try:
            audio_data_int16, samplerate = system.สังเคราะห์_เพลง_RBF(chord_input, emotion_data)
            st.success("✅ การสังเคราะห์และการมาสเตอร์เสร็จสมบูรณ์!")
            
            st.header("3. Final Audio Output")
            st.write(f"ไฟล์เสียงที่สังเคราะห์ (Sampling Rate: {samplerate} Hz)")
            
            audio_data_float = audio_data_int16.astype(np.float32) / 32767.0
            st.audio(audio_data_float, format='audio/wav', sample_rate=samplerate)
            
            # --- 💡 จุดแก้ไขวิกฤต: ใช้ BytesIO ทำสตรีมข้อมูลในแรมเพื่อให้ปุ่มดาวน์โหลดทำงานได้จริง ---
            buffer = io.BytesIO()
            wavfile.write(buffer, samplerate, audio_data_int16)
            buffer.seek(0)  # เลื่อนตำแหน่งชี้ข้อมูลกลับไปจุดเริ่มต้นเพื่อเตรียมให้อ่านค่าลงไฟล์ดาวน์โหลด
            
            st.download_button(
                label="⬇️ ดาวน์โหลดไฟล์ WAV (ระบบแปลงข้อมูลจริง)",
                data=buffer.getvalue(),
                file_name="final_track_rbf_ai.wav",
                mime="audio/wav"
            )

            st.markdown("---")
            st.markdown("### รายงานผลการประมวลผลโดยละเอียด (ดูใน Sidebar)")
            st.info("โปรดดูรายละเอียดขั้นตอนการทำงานของ Input, AI Engine, และ Mastering Module ใน Sidebar ทางซ้าย")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดระหว่างการสังเคราะห์: {e}")
else:
    st.info("กดปุ่ม **สังเคราะห์เพลงด้วย RBF AI** เพื่อเริ่มต้นกระบวนการ")
    
st.sidebar.title("🛠️ RBF Engine Log")
st.sidebar.markdown("แสดงขั้นตอนการทำงานของแต่ละ Module")

if st.button("🔄 รีเซ็ต Log"):
    st.rerun()  # เปลี่ยนจากคำสั่งเก่าเป็นตัวใหม่ที่เสถียรกว่าเรียบร้อย
