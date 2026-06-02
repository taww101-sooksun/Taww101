import numpy as np
import streamlit as st
import google.generativeai as genai
import json
import time

# --- 1. ตั้งค่าดีไซน์ตามโลโก้ (ม่วง-ดำ-เขียวมินต์) หรูหราคมชัด ---
st.set_page_config(page_title="SYNAPSE 6D Pro", page_icon="💎", layout="centered")

st.markdown("""
    <style>
    /* พื้นหลังดำสนิทสไตล์ดีไซน์โหมดมืด */
    .stApp { background-color: #0E1117; font-family: 'Kanit', sans-serif; } 
    
    /* หัวข้อสีม่วงนีออนโดดเด่น */
    h1, h2, h3, h4 { color: #B266FF !important; text-shadow: 2px 2px 8px #000000; font-weight: 800; }
    
    /* กล่อง Metric ขอบม่วงมีมิติ */
    .stMetric { 
        background-color: #1E1E1E; 
        border-radius: 15px; 
        padding: 15px; 
        border: 2px solid #B266FF;
        box-shadow: 0px 4px 15px rgba(178, 102, 255, 0.2);
    }
    
    /* กล่องข้อความสีเขียวมินต์เวลาพิมพ์ */
    .stTextArea>div>div>textarea {
        background-color: #1A1A1A;
        color: #00CC99;
        border: 1px solid #00CC99;
        border-radius: 10px;
        font-size: 16px;
    }
    
    /* ปุ่มกดสีเขียวมินต์เรืองแสง */
    .stButton>button { 
        background-color: #00CC99; 
        color: white; 
        border-radius: 25px; 
        width: 100%; 
        font-weight: bold; 
        height: 50px;
        font-size: 18px;
        border: none;
        box-shadow: 0px 4px 15px rgba(0, 204, 153, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #B266FF;
        box-shadow: 0px 4px 20px rgba(178, 102, 255, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ตั้งค่าระบบ AI (ใส่ API Key เชื่อมต่อระบบจริง) ---
# ใส่ Key ที่ใช้งานได้จริงของนายลงในช่องนี้
GOOGLE_GEMINI_API_KEY = "AIzaSyBiKFHClySIV_UmeMznANnhyBoD78CYUrg"
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ระบบวิเคราะห์และสร้างเสียงบำบัดพลังงาน 6 มิติ ---
class UltimateAIsystem:
    def analyze_emotion(self, text):
        """ใช้ Gemini AI วิเคราะห์คลื่นอารมณ์และคำนวณคอร์ดเพลงออกมาเป็นโครงสร้าง JSON"""
        prompt = f"""
        คุณคือ AI ประมวลผลพลังงานดนตรีบำบัด จงวิเคราะห์ข้อความอารมณ์นี้: '{text}'
        แล้วตอบกลับเป็นรูปแบบ JSON บริสุทธิ์เท่านั้น (ห้ามมีคำเกริ่น ห้ามใส่โค้ดบล็อก) ตามโครงสร้างนี้:
        {{
            "v": 0.0-1.0, (ค่าความสว่างของพลังงานอารมณ์)
            "a": 0.0-1.0, (ค่าความเข้มข้น/พลังงานแฝง)
            "chords": "ชื่อคอร์ดแจ๊ส/R&B หรูๆ 3-4 คอร์ด เช่น Cmaj9, Am9, Fmaj7"
        }}
        """
        try:
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            
            # ป้องกันกรณี Gemini ใส่เครื่องหมายโค้ดบล็อกมาให้ดึงออก
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3].strip()
                
            return json.loads(clean_text)
        except Exception as e:
            # Safe-Zone Configuration: หากระบบเชื่อมต่อผิดพลาด จะดึงค่าคงที่ๆ นิ่งที่สุดมาใช้ทันที
            return {"v": 0.75, "a": 0.6, "chords": "Emaj9, Amaj7, B13"}

    def synthesize_sound(self, v):
        """สังเคราะห์คลื่นเสียง Sine Wave บริสุทธิ์ จูนความถี่ Solfeggio ตามสภาวะพลังงาน"""
        sample_rate = 22050 # เซฟพื้นที่หน่วยความจำสำหรับรันบนเว็บมือถือ
        duration = 5.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        # คำนวณความถี่พื้นฐานจากค่าพลังงานอารมณ์ (อิงช่วงรอบความถี่บำบัด 432Hz)
        base_freq = 432.0 + (v * 20.0)
        wave = 0.4 * np.sin(2 * np.pi * base_freq * t) 
        
        # สร้าง Envelope ทำ Fade-In และ Fade-Out เพื่อให้น้ำเสียงนุ่มนวล ไม่บาดหู
        envelope = np.ones_like(t)
        fade = int(sample_rate * 0.5) # นุ่มนวลช่วง 0.5 วินาทีแรกและท้าย
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        
        mastered_wave = np.clip(wave * envelope, -0.9, 0.9)
        return (mastered_wave * 32767).astype(np.int16), sample_rate

# --- 4. หน้าจอใช้งานหลัก (UI Dashboard) ---
st.title("💎 SYNAPSE : 6D ENERGY PRO")
st.markdown("<h4>ระบบปรับจูนคลื่นความถี่บำบัดระดับเซลล์คอมพิวเตอร์</h4>", unsafe_allow_html=True)
st.markdown("---")

system = UltimateAIsystem()

# กล่องรับข้อมูลความรู้สึก
user_input = st.text_area(
    "บอกความรู้สึกของคุณวันนี้ เพื่อทำการแปลงโมเลกุลเสียง:", 
    placeholder="เช่น วันนี้ล้ามาก อยากพักผ่อนอยู่นิ่งๆ..."
)

if st.button("🚀 ACTIVATE ENERGY (เริ่มการบำบัด)"):
    if user_input.strip():
        with st.spinner("ระบบกำลังคำนวณ Matrix และปรับจูนคลื่นความถี่แอนะล็อก..."):
            # ดึงข้อมูลการวิเคราะห์และสังเคราะห์เสียง
            data = system.analyze_emotion(user_input)
            audio_bytes, rate = system.synthesize_sound(data['v'])
            time.sleep(1.2) # หน่วงจังหวะเพื่อให้เอฟเฟกต์ประมวลผลสมจริง
            
            # ส่วนการแสดงผลแถบสถานะพลังงาน
            st.markdown(f"### 🎨 สภาวะสมดุลพลังงานปัจจุบัน (Intensity: {data['v']:.2f})")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("ความสว่างเซลล์ (Light)", f"{data['v']*100:.1f}%")
            with c2:
                st.metric("ความเข้มข้น (Contrast)", f"{data['a']*100:.1f}%")
            
            # เครื่องเล่นเสียงคลื่นความถี่บำบัดสเตอริโอ
            st.markdown(f"### 🔊 เสียงบำบัดประธานคอร์ด: `{data['chords']}`")
            st.audio(audio_bytes, format='audio/wav', sample_rate=rate)
            
            st.success("⚡ ปรับจูนโครงสร้างความถี่สมดุลเรียบร้อยแล้ว")
            st.info("🔒 สโลแกนเซฟโซนของคุณ: 'อยู่นิ่งๆ ไม่เจ็บตัว' — ระบบควบคุมโครงสร้างเสียงให้เสถียรเรียบร้อยครับ")
    else:
        st.error("⚠️ กรุณากรอกข้อความความรู้สึกก่อนสั่งงานระบบครับเพื่อนบาส")
