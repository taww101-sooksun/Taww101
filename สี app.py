import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# ฟังก์ชันสำหรับสร้างวิดีโอพร้อมเนื้อเพลง
def generate_lyrics_video():
    video_path = "ta101.mp4"
    font_path = "THSarabunNew.ttf"
    output_path = "synapse_output.mp4"

    # เช็กความพร้อมของไฟล์
    if not os.path.exists(video_path) or not os.path.exists(font_path):
        st.error("❌ หาไฟล์ ta101.mp4 หรือ THSarabunNew.ttf ไม่เจอใน GitHub ครับ!")
        return None

    try:
        # 1. โหลดวิดีโอต้นฉบับ
        clip = VideoFileClip(video_path)
        
        # 2. ข้อมูลเนื้อเพลงและเวลาที่เพื่อนถอดไว้
        lyrics = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต"),
            (26.0, 40.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร"),
            (41.0, 55.0, "คืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง")
        ]

        # 3. สร้างเลเยอร์ตัวหนังสือ
        txt_clips = [clip]
        for start, end, text in lyrics:
            txt = (TextClip(text=text, font_size=70, color='yellow', font=font_path)
                   .with_start(start)
                   .with_duration(end - start)
                   .with_position(('center', 0.8 * clip.h)))
            txt_clips.append(txt)

        # 4. รวมร่างและเซฟ
        final_video = CompositeVideoClip(txt_clips)
        final_video.write_videofile(output_path, fps=24, codec="libx264")
        
        clip.close()
        return output_path

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

# --- ส่วนหน้าจอ Streamlit ---
st.set_page_config(page_title="SYNAPSE Lyrics Maker", page_icon="🎬")
st.title("🎬 SYNAPSE Lyrics Video")
st.write("สร้างวิดีโอเนื้อเพลงวิ่งจากไฟล์ ta101.mp4")

if st.button("🚀 เริ่มประมวลผลวิดีโอ"):
    with st.spinner("กำลังเสกตัวหนังสือวิ้ง... กรุณารอสักครู่นะครับเพื่อน"):
        result = generate_lyrics_video()
        if result:
            st.video(result)
            st.success("ทำสำเร็จแล้ว! อยู่นิ่งๆ ไม่เจ็บตัวนะครับเพื่อน")

st.markdown("---")
st.caption("Developed for SYNAPSE PROJECT 2026")
