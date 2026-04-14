import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    # ระบุชื่อไฟล์ให้ตรงตามที่เพื่อนบอก
    target_file = "ta101.mp4" 
    
    if not os.path.exists(target_file):
        st.error(f"หาไฟล์ {target_file} ไม่เจอในโฟลเดอร์ครับ! ลองเช็กชื่อไฟล์บน GitHub ดูนะ")
        return None

    try:
        # 1. โหลดวิดีโอ ta101.mp4
        base_video = VideoFileClip(target_file)
        
        # 2. ตั้งค่าเนื้อเพลง (ใส่ท่อนที่เพื่อนอยากให้วิ้ง)
        txt = TextClip(
            text="วันหนึ่งถ้าเธอมองย้อนกลับมา",
            font_size=60,
            color='yellow',
            duration=5
        ).with_position(('center', 'center')).with_start(1)
        
        # 3. รวมร่าง
        final = CompositeVideoClip([base_video, txt])
        
        # 4. เขียนไฟล์ใหม่
        output_name = "synapse_final.mp4"
        final.write_videofile(output_name, fps=24, codec="libx264")
        
        # คืนหน่วยความจำ
        base_video.close()
        final.close()
        
        return output_name

    except Exception as e:
        st.error(f"ติดปัญหาตอนประมวลผล: {e}")
        return None

st.title("🎬 SYNAPSE Video Maker (ta101)")
if st.button("🚀 เริ่มเสกตัวหนังสือวิ้ง"):
    with st.spinner("กำลังทำวิดีโอจากไฟล์ ta101.mp4..."):
        res = make_video()
        if res:
            st.video(res)
            st.success("เสร็จแล้วครับเพื่อน!")
