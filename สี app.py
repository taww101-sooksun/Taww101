import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    video_file = "ta101.mp4"
    
    if not os.path.exists(video_file):
        st.error(f"❌ หาไฟล์ {video_file} ไม่เจอใน GitHub ครับ")
        return None

    try:
        # 1. โหลดวิดีโอ (ลดคุณภาพลงนิดเพื่อไม่ให้ RAM เต็ม)
        clip = VideoFileClip(video_file).with_effects([])
        
        # 2. ใส่เนื้อเพลงภาษาอังกฤษ (ใช้ฟอนต์มาตรฐานของระบบ)
        lyrics_data = [
            (1.0, 5.0, "One day if you look back..."),
            (6.0, 10.0, "You might see what was broken.")
        ]
        
        txt_clips = [clip]
        for start, end, text in lyrics_data:
            txt = (TextClip(
                text=text, 
                font_size=50, 
                color='yellow', 
                font='Arial', # ใช้ฟอนต์มาตรฐานภาษาอังกฤษ
                duration=(end - start)
            ).with_start(start).with_position(('center', 0.8 * clip.h)))
            txt_clips.append(txt)
        
        # 3. รวมร่าง
        final = CompositeVideoClip(txt_clips)
        output = "synapse_en_version.mp4"
        
        # 4. เขียนไฟล์แบบ "ประหยัดพลังงาน"
        final.write_videofile(
            output, 
            fps=12,             # ลด FPS ลงเพื่อให้เครื่องไม่ค้าง
            codec="libx264", 
            audio_codec="aac",
            threads=1,          # ใช้แค่ 1 thread เพื่อความนิ่ง
            logger=None
        )
        
        clip.close()
        return output

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

# --- ส่วนหน้าจอแอป ---
st.title("🎬 SYNAPSE Video Test")
st.write("โหมดทดสอบ: ภาษาอังกฤษ (English Mode)")

if st.button("🚀 เริ่มสร้างวิดีโอ (ภาษาอังกฤษ)"):
    with st.spinner("กำลังประมวลผล... กรุณารอสักครู่ (ประมาณ 1-2 นาที)"):
        res = make_video()
        if res:
            st.video(res)
            st.success("ภาษาอังกฤษรันผ่านแล้วครับเพื่อน!")
