import streamlit as st
import replicate
import os

# --- 1. SET UP THEME ---
st.set_page_config(page_title="SYNAPSE AI VIDEO", layout="wide")
theme_color = "#39FF14" 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000 !important; color: {theme_color} !important; }}
    .stTextInput>div>div>input {{ background-color: #111 !important; color: {theme_color} !important; border: 1px solid {theme_color} !important; }}
    h1 {{ text-align: center; text-shadow: 0 0 10px {theme_color}; }}
    </style>
""", unsafe_allow_html=True)

st.title("🎬 SYNAPSE AI VIDEO")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. CONFIG API (ต้องมี API TOKEN ของ Replicate) ---
# เพื่อนต้องไปสมัครที่ replicate.com แล้วเอา API Token มาใส่ครับ
REPLICATE_API_TOKEN = st.text_input("ใส่ Replicate API Token ของคุณ", type="password")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# --- 3. INPUT PROMPT ---
prompt = st.text_input("พิมพ์ข้อความที่ต้องการสร้างเป็นวิดีโอ (ภาษาอังกฤษ)", placeholder="เช่น: A futuristic neon city, 4k, cinematic")

if st.button("🚀 เริ่มสร้างวิดีโอ"):
    if not REPLICATE_API_TOKEN:
        st.error("กรุณาใส่ API Token ก่อนครับเพื่อน!")
    elif not prompt:
        st.warning("พิมพ์ข้อความก่อนนะ!")
    else:
        with st.spinner("AI กำลังวาดวิดีโอให้คุณ... (อาจใช้เวลา 1-2 นาที)"):
            try:
                # ใช้ Model 'zeroscope-v2-xl' ซึ่งเป็นรุ่นที่ใช้งานได้ดีและเร็ว
                output = replicate.run(
                    "anotherjesse/zeroscope-v2-xl:9f747895e5b2828a90827106604565195444e7975850b864f5ad67a2d2958742",
                    input={"prompt": prompt}
                )
                
                # แสดงผลวิดีโอ
                if output:
                    st.success("สร้างสำเร็จแล้ว!")
                    st.video(output[0])
                    st.markdown(f"[📥 ดาวน์โหลดวิดีโอ]({output[0]})")
            
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

st.write("---")
st.caption("SYNAPSE PROJECT | พัฒนาโดย Ta/Bas 2026")
