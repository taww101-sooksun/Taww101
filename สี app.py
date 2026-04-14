import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    target_file = "ta101.mp4"
    # ระบุชื่อไฟล์ฟอนต์ที่เพื่อนอัปโหลดขึ้น GitHub (ตัวอย่าง: 'font.ttf')
    font_path = "THSarabunNew.ttf" 

    if not os.path.exists(target_file):
        st.error(f"ไม่พบไฟล์ {target_file}")
        return None
    
    # ตรวจสอบว่ามีไฟล์ฟอนต์ไหม ถ้าไม่มีให้ใช้ฟอนต์ระบบ (ป้องกันแอปค้าง)
    if not os.path.exists(font_path):
        st.warning("⚠️ ไม่พบไฟล์ฟอนต์ใน GitHub ระบบจะลองใช้ฟอนต์มาตรฐานแทน")
        font_to_use = "Courier" # ฟอนต์มาตรฐานที่มักจะมีบน Linux
    else:
        font_to_use = font_path

    try:
        base_video = VideoFileClip(target_file)
        
        lyrics_data = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
            (26.0, 40.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร")
        ]
        
        clips = [base_video]

        for start, end, text in lyrics_data:
            txt_clip = (TextClip(
                text=text, 
                font_size=60, 
                color='yellow', 
                font=font_to_use, # ใช้ฟอนต์ที่เราเตรียมไว้
                duration=(end - start)
            ).with_start(start)
             .with_position(('center', 0.8 * base_video.h)))
            
            clips.append(txt_clip)
        
        final = CompositeVideoClip(clips)
        output_name = "ta101_lyrics_final.mp4"
        
        final.write_videofile(output_name, fps=24, codec="libx264")
        
        base_video.close()
        final.close()
        return output_name

    except Exception as e:
        st.error(f"❌ แก้ไข Error: {e}")
        return None

st.title("🎬 SYNAPSE Lyrics Maker")
if st.button("🚀 เริ่มใส่เนื้อเพลง (ฉบับแก้ฟอนต์)"):
    with st.spinner("กำลังประมวลผล..."):
        res = make_video()
        if res:
            st.video(res)
            st.success("เสร็จแล้วครับเพื่อน!")
