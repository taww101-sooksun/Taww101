import streamlit as st
import os
# ใช้การ Import แบบใหม่ที่รองรับ MoviePy 2.0+
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    # 1. เช็กไฟล์ต้นฉบับ
    video_path = "ta101.mp4"
    if not os.path.exists(video_path):
        st.error(f"ไม่พบไฟล์ {video_path} ในโฟลเดอร์ครับเพื่อน!")
        return None

    try:
        # 2. โหลดวิดีโอ
        base_video = VideoFileClip(video_path)
        
        # 3. สร้างข้อความ (ตรงนี้แหละที่ต้องใช้ ImageMagick)
        txt = TextClip(
            text="วันหนึ่งถ้าเธอมองย้อนกลับมา",
            font_size=70,
            color='yellow',
            duration=5
        ).with_position(('center', 'center')).with_start(1)
        
        # 4. รวมร่างและประมวลผล
        final = CompositeVideoClip([base_video, txt])
        output_file = "result.mp4"
        
        # ใช้ logger=None เพื่อให้หน้าจอ streamlit ไม่ค้าง
        final.write_videofile(output_file, fps=24, codec="libx264")
        return output_file

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        st.info("💡 คำแนะนำ: ตรวจสอบว่าสร้างไฟล์ 'packages.txt' และใส่คำว่า 'imagemagick' หรือยังครับ?")
        return None

# --- ส่วนแสดงผลหน้าเว็บ ---
st.title("🎬 SYNAPSE Video Maker")
st.markdown("---")

if st.button("🚀 เสกตัวหนังสือวิ้ง"):
    with st.spinner("กำลังประมวลผลวิดีโอ... อาจใช้เวลาสักครู่นะครับ"):
        res = make_video()
        if res:
            st.video(res)
            st.success("ทำสำเร็จแล้วครับเพื่อน!")

st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE PROJECT 2026")
