import streamlit as st

# --- 1. คอนฟิกหน้าตาแอป ---
st.set_page_config(page_title="SYNAPSE IMAGE", layout="wide")
theme_color = "#39FF14"  # เขียวนีออนที่คุณชอบ

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000 !important; color: {theme_color} !important; }}
    .img-card {{ border: 2px solid {theme_color}; border-radius: 10px; padding: 10px; margin-bottom: 20px; text-align: center; }}
    </style>
""", unsafe_allow_html=True)

st.title("🔍 SYNAPSE IMAGE ENGINE")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. ระบบค้นหาด้วยคำค้นเดียว (ส่งไป 5 แหล่ง) ---
query = st.text_input("พิมพ์คำค้นหา (ภาษาอังกฤษ)", placeholder="เช่น Cyberpunk, Forest, Space")

if query:
    q = query.replace(" ", "+")
    
    # 5 ลิงก์จากแหล่งข้อมูลที่ต่างกัน เพื่อความหลากหลาย
    sources = [
        {"provider": "Unsplash High-Res", "url": f"https://source.unsplash.com/featured/800x600?{q}&sig=1"},
        {"provider": "Creative Commons", "url": f"https://loremflickr.com/800/600/{q}"},
        {"provider": "Professional Stock", "url": f"https://source.unsplash.com/featured/800x600?{q}&sig=2"},
        {"provider": "Abstract/Random", "url": f"https://picsum.photos/seed/{q}/800/600"},
        {"provider": "Artistic Style", "url": f"https://source.unsplash.com/featured/800x600?{q}&sig=3"}
    ]

    st.write(f"### 🚀 กำลังดึงข้อมูลจาก 5 แหล่งสำหรับ: {query}")
    
    # แสดงผลแบบ Grid 2 คอลัมน์เพื่อให้ดูง่ายบนมือถือ
    cols = st.columns(2)
    for i, item in enumerate(sources):
        with cols[i % 2]:
            st.markdown(f'<div class="img-card">', unsafe_allow_html=True)
            st.write(f"**Source {i+1}: {item['provider']}**")
            st.image(item['url'], use_container_width=True)
            st.markdown(f"[📥 คลิกเพื่อเปิดรูปเต็ม]({item['url']})")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("กรุณาระบุคำค้นหา เพื่อเริ่มการทำงานครับ")

st.write("---")
st.caption("SYNAPSE PROJECT | Ta/Bas 2026")
