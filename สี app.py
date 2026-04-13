import streamlit as st
import replicate
import os

# --- 1. SET UP THEME ---
st.set_page_config(page_title="SYNAPSE AI VIDEO", layout="wide")

# ใช้ CSS แบบปลอดภัย ไม่ให้มีภาษาไทยหลุดไปในจุดเสี่ยง
st.markdown("""
    <style>
    .stApp { background-color: #000 !important; color: #39FF14 !important; }
    h1 { text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 SYNAPSE AI VIDEO")
# แสดงภาษาไทยแค่ใน UI เท่านั้น ไม่ส่งเข้าฟังก์ชัน
st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- 2. INPUT ---
api_token = st.text_input("Replicate API Token", type="password", key="tk_in")
user_prompt = st.text_input("Prompt (English Only)", key="pr_in")

# --- 3. ฟังก์ชันประมวลผลแบบคลีน ---
if st.button("🚀 เริ่มสร้างวิดีโอ", key="gen_btn"):
    if not api_token:
        st.error("ใส่ Token ก่อนครับ")
    elif not user_prompt:
        st.warning("พิมพ์ข้อความก่อนนะ")
    else:
        with st.spinner("Processing..."):
            try:
                os.environ["REPLICATE_API_TOKEN"] = api_token
                
                # *** จุดสำคัญ: ล้างค่าให้เหลือแค่ตัวอักษรที่ระบบรองรับ (ASCII) ***
                clean_prompt = user_prompt.encode("ascii", "ignore").decode("ascii")
                
                output = replicate.run(
                    "anotherjesse/zeroscope-v2-xl:9f747895e5b2828a90827106604565195444e7975850b864f5ad67a2d2958742",
                    input={"prompt": clean_prompt}
                )
                
                if output:
                    st.success("Success!")
                    st.video(output[0])
            except Exception as e:
                # ถ้า Error ให้โชว์ออกมาดูชัดๆ
                st.error(f"Error detail: {str(e)}")

st.write("---")
st.caption("SYNAPSE PROJECT 2026")
