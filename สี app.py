import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    video_file = "ta101.mp4"
    
    # 1. เช็กว่าเจอวิดีโอไหม
    if not os.path.exists(video_file):
        st.error(f"❌ ไม่พบไฟล์วิดีโอ {video_file} ใน GitHub")
        return None

    try:
        # 2. โหลดวิดีโอ (ลดขนาดการประมวลผลเพื่อ RAM)
        clip = VideoFileClip(video_file)
        
        # 3. ใส่เนื้อเพลงภาษาอังกฤษ (ใช้ฟอนต์มาตรฐานของระบบ)
        txt = (TextClip(
                text="STAY STILL, NO PAIN", 
                font_size=80, 
                color='yellow', 
                font='Arial', 
                duration=5
            ).with_start(1).with_position(('center', 'center')))
        
        # 4. รวมร่าง
        final = CompositeVideoClip([clip, txt])
        output = "test_english.mp4"
        
        # 5. สั่งเขียนไฟล์แบบประหยัดพลังงานที่สุด
        final.write_videofile(
            output, 
            fps=12,             # ลดเฟรมเรตลงเพื่อให้มือถือ/Cloud รับไหว
            codec="libx264", 
            audio_codec="aac",
            threads=1,
            logger=None
        )
        
        clip.close()
        final.close()
        return output

    except Exception as e:
        st.error(f"❌ ติดปัญหาตอนรัน: {e}")
        return None

# --- หน้าจอหลัก ---
st.title("🎬 SYNAPSE System Test")
st.write("กำลังทดสอบระบบด้วยภาษาอังกฤษ (English Test Mode)")

if st.button("🚀 เริ่มทดสอบรันวิดีโอ"):
    with st.spinner("ระบบกำลังประมวลผล... กรุณารอสักครู่"):
        res = make_video()
        if res:
            st.video(res)
            st.success("ภาษาอังกฤษผ่านแล้ว! ระบบ MoviePy ทำงานได้ปกติครับ")
