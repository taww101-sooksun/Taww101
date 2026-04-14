import streamlit as st
import os
from moviepy import VideoFileClip

def test_system():
    video_file = "ta101.mp4"
    
    if not os.path.exists(video_file):
        st.error(f"❌ หาไฟล์ {video_file} ไม่เจอใน GitHub!")
        return None

    try:
        # ลองโหลดวิดีโอมาดื้อๆ เลย ไม่ต้องใส่ตัวหนังสือ
        clip = VideoFileClip(video_file)
        
        # ตัดมาแค่ 5 วินาทีเพื่อความเร็ว
        short_clip = clip.subclipped(0, 5) 
        
        output = "system_test.mp4"
        short_clip.write_videofile(output, fps=12, codec="libx264")
        
        clip.close()
        return output
    except Exception as e:
        st.error(f"❌ ระบบวิดีโอมีปัญหา: {e}")
        return None

st.title("🎬 SYNAPSE Video Engine Test")

if st.button("🚀 ทดสอบพลังระบบ (ไม่ใช้ตัวหนังสือ)"):
    with st.spinner("กำลังลองรันวิดีโอ..."):
        res = test_system()
        if res:
            st.video(res)
            st.success("ระบบวิดีโอทำงานปกติ! ปัญหาน่าจะอยู่ที่ตัวหนังสืออย่างเดียวครับ")
