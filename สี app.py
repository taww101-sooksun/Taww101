import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    # 1. ตั้งชื่อให้ตรงกับที่เห็นใน Logs
    video_file = "ta101.mp4"
    font_file = "THSarabunNew.ttf" 

    # เช็คไฟล์ก่อนเริ่ม (เพื่อความชัวร์)
    if not os.path.exists(video_file):
        st.error(f"❌ ไม่เจอวิดีโอชื่อ: {video_file}")
        return None
    if not os.path.exists(font_file):
        st.error(f"❌ ไม่เจอไฟล์ฟอนต์ชื่อ: {font_file}")
        return None

    try:
        # 2. โหลดวิดีโอ
        clip = VideoFileClip(video_file)
        
        # 3. ใส่เนื้อเพลง (ตัวอย่างท่อนแรก)
        txt = (TextClip(
                text="วันหนึ่งถ้าเธอมองย้อนกลับมา", 
                font_size=70, 
                color='yellow', 
                font=font_file, 
                duration=5
            ).with_start(1).with_position(('center', 0.8 * clip.h)))
        
        # 4. รวมร่าง
        final = CompositeVideoClip([clip, txt])
        output = "synapse_final.mp4"
        
        # เขียนไฟล์
        final.write_videofile(output, fps=24, codec="libx264")
        
        clip.close()
        return output

    except Exception as e:
        st.error(f"❌ ติดปัญหา: {e}")
        return None

# --- หน้าจอแอป ---
st.title("🎬 SYNAPSE Lyrics Maker")
st.write(f"สถานะไฟล์: วิดีโอ({os.path.exists('ta101.mp4')}), ฟอนต์({os.path.exists('THSarabunNew.ttf')})")

if st.button("🚀 เริ่มรันวิดีโอ"):
    with st.spinner("กำลังประมวลผล..."):
        res = make_video()
        if res:
            st.video(res)
            st.success("สำเร็จแล้วครับเพื่อน!")
