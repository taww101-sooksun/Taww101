import streamlit as st
import replicate
import os

# --- 1. SET UP THEME ---
st.set_page_config(page_title="SYNAPSE AI VIDEO", layout="wide")
theme_color = "#39FF14" 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000 !important; color: {theme_color} !important; }}
    h1 {{ text-align: center; text-shadow: 0 0 10px {theme_color}; }}
    </style>
""", unsafe_allow_html=True)

st.title("🎬 SYNAPSE AI VIDEO")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. INPUT ---
REPLICATE_API_TOKEN = st.text_input("ใส่ Replicate API Token ของคุณ", type="password", key="token_input")
prompt = st.text_input("พิมพ์ข้อความที่ต้องการสร้างเป็นวิดีโอ (ภาษาอังกฤษ)", key="prompt_input")

# --- 3. แก้ไขปัญหา Duplicate ID โดยการใส่ key เฉพาะตัว ---
if st.button("🚀 เริ่มสร้างวิดีโอ", key="main_gen_button"):
    if not REPLICATE_API_TOKEN:
        st.error("กรุณาใส่ API Token ก่อนครับ!")
    elif not prompt:
        st.warning("พิมพ์ข้อความก่อนนะ!")
    else:
        with st.spinner("กำลังประมวลผล..."):
            try:
                os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
                # บังคับให้เป็นข้อความที่สะอาดเพื่อเลี่ยง ASCII error
                clean_prompt = str(prompt).strip()
                
                output = replicate.run(
                    "anotherjesse/zeroscope-v2-xl:9f747895e5b2828a90827106604565195444e7975850b864f5ad67a2d2958742",
                    input={"prompt": clean_prompt}
                )
                
                if output:
                    st.success("สำเร็จ!")
                    st.video(output[0])
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

st.write("---")
st.caption("SYNAPSE PROJECT | Ta/Bas 2026")
