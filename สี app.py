import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- ส่วนตั้งค่าชื่อไฟล์ (เช็กให้ตรงกับใน GitHub นะครับ) ---
VIDEO_FILENAME = "ta101.mp4"
FONT_FILENAME = "2.3.2 THSarabunNew.ttf" # แก้ตามที่เห็นในรูป GitHub เป๊ะๆ
OUTPUT_FILENAME = "synapse_output.mp4"

def generate_lyrics_video():
    # หาตำแหน่งโฟลเดอร์ปัจจุบันที่โค้ดรันอยู่
    base_path = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_path, VIDEO_FILENAME)
    font_path = os.path.join(base_path, FONT_FILENAME)
    output_path = os.path.join(base_path, OUTPUT_FILENAME)

    # 1. เช็กความพร้อมของไฟล์และ Debug
    files_in_dir = os.listdir(base_path)
    if VIDEO_FILENAME not in files_in_dir or FONT_FILENAME not in files_in_dir:
        st.error(f"❌ หาไฟล์ไม่เจอใน GitHub!")
        st.write("ไฟล์ที่ระบบมองเห็นตอนนี้คือ:", files_in_dir)
        st.info(f"ต้องการหา: {VIDEO_FILENAME} และ {FONT_FILENAME}")
        return None

    try:
        # 2. โหลดวิดีโอต้นฉบับ
        clip = VideoFileClip(video_path)
        
        # 3. ข้อมูลเนื้อเพลงและเวลา
        lyrics = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต"),
            (26.0, 40.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร"),
            (41.0, 55.0, "คืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง")
        ]

        # 4. สร้างเลเยอร์ตัวหนังสือ
        txt_clips = [clip]
        for start, end, text in lyrics:
            txt = (TextClip(text=text, font_size=70, color='yellow', font=font_path)
                   .with_start(start)
                   .with_duration(end - start)
                   .with_position(('center', 0.8 * clip.h)))
            txt_clips.append(txt)

        # 5. รวมร่างและเซฟ
        final_video = CompositeVideoClip(txt_clips)
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        clip.close()
        return output_path

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดทางเทคนิค: {e}")
        st.info("ใบ้ให้: ส่วนใหญ่เกิดจากยังไม่ได้ลง 'imagemagick' ใน packages.txt ครับ")
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
