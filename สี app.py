import streamlit as st
import replicate
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. INITIALIZE FIREBASE (อยู่นิ่งๆ ไม่เจ็บตัว) ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Config Error: {e}")

db = firestore.client()

# --- 2. UI SETUP ---
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

# --- 3. INPUTS ---
api_token = st.text_input("ใส่ Replicate API Token", type="password", key="main_token").strip()
prompt = st.text_input("พิมพ์ข้อความสร้างวิดีโอ (English)", key="main_prompt").strip()

if st.button("🚀 เริ่มสร้างวิดีโอ", key="gen_btn"):
    if not api_token or not prompt:
        st.warning("กรุณาใส่ข้อมูลให้ครบก่อนครับเพื่อน")
    else:
        with st.spinner("AI กำลังทำงาน..."):
            try:
                # ป้องกันปัญหา ASCII โดยการทำความสะอาดค่า
                safe_token = api_token.encode("ascii", "ignore").decode("ascii")
                safe_prompt = prompt.encode("ascii", "ignore").decode("ascii")
                
                os.environ["REPLICATE_API_TOKEN"] = safe_token
                
                output = replicate.run(
                    "anotherjesse/zeroscope-v2-xl:9f747895e5b2828a90827106604565195444e7975850b864f5ad67a2d2958742",
                    input={"prompt": safe_prompt}
                )
                
                if output:
                    st.success("สร้างสำเร็จ!")
                    st.video(output[0])
                    # บันทึกลง Firebase
                    db.collection("video_history").add({
                        "prompt": safe_prompt,
                        "url": output[0],
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

st.write("---")
st.caption("SYNAPSE PROJECT | Ta/Bas 2026")
