import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_lyric_video():
    # 1. ชื่อไฟล์ต้องเป๊ะตามที่เห็นใน GitHub
    video_file = "ta101.mp4"
    font_file = "THSarabunNew.ttf" 

    try:
        # โหลดวิดีโอหลัก
        clip = VideoFileClip(video_file)
        
        # 2. ใส่เนื้อเพลง (อ้างอิงจากคลิป YouTube ของเพื่อน)
        lyrics = [
            (10.0, 20.0, "ขอบคุณถ้อยคำที่เคยทำฉันเจ็บ\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร"),
            (21.0, 30.0, "คืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง")
        ]
        
        clips = [clip]
        for start, end, text in lyrics:
            txt_clip = (TextClip(
                text=text, 
                font_size=60, 
                color='yellow',     # สีเหลืองเหมือนในคลิป
                font=font_file, 
                duration=(end - start),
                method='caption',
                size=(clip.w * 0.8, None)
            ).with_start(start).with_position(('center', 0.8 * clip.h)))
            clips.append(txt_clip)
        
        # 3. รวมร่างและส่งออก
        final = CompositeVideoClip(clips)
        output = "synapse_master.mp4"
        
        # ใช้ค่าประหยัดพลังงานเพื่อไม่ให้เครื่องค้าง
        final.write_videofile(output, fps=12, codec="libx264", audio_codec="aac", threads=1)
        
        clip.close()
        return output

    except Exception as e:
        st.error(f"❌ ติดปัญหา: {e}")
        return None

# --- หน้าจอแอป ---
st.title("🎬 SYNAPSE Video Creator")
st.write("สร้างวิดีโอเนื้อเพลงแบบเดียวกับใน YouTube")

if st.button("🚀 เริ่มสร้างวิดีโอ"):
    if os.path.exists("ta101.mp4") and os.path.exists("THSarabunNew.ttf"):
        with st.spinner("กำลังประมวลผล... อาจใช้เวลา 1-2 นาทีนะครับ"):
            res = make_lyric_video()
            if res:
                st.video(res)
                st.success("สร้างเสร็จแล้วครับเพื่อน! วิ้งแน่นอน")
    else:
        st.error("เช็กไฟล์ใน GitHub อีกรอบนะเพื่อน เหมือนจะหาไฟล์ไม่เจอ")
