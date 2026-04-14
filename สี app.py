import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

def create_lyrics_video():
    # 1. โหลดวิดีโอจากไฟล์ ta101.mp4
    if not os.path.exists("ta101.mp4"):
        st.error("ไม่พบไฟล์ ta101.mp4 ในโฟลเดอร์ครับเพื่อน!")
        return

    video = VideoFileClip("ta101.mp4")

    # 2. ข้อมูลเนื้อเพลงและเวลาที่คุณให้มา
    lyrics_data = [
        (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
        (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
        (26.0, 35.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร")
    ]

    clips = [video]

    # 3. สร้างตัวหนังสือวิ้งๆ
    for start, end, text in lyrics_data:
        txt_clip = (TextClip(text, fontsize=40, color='yellow', font='Arial', 
                             method='caption', size=(video.w*0.8, None))
                    .set_start(start)
                    .set_duration(end - start)
                    .crossfadein(0.5) # เอฟเฟกต์ค่อยๆ สว่าง (วิ้ง)
                    .set_position(('center', video.h*0.7)))
        clips.append(txt_clip)

    # 4. ประมวลผล
    final = CompositeVideoClip(clips)
    output_file = "ta101_lyrics_final.mp4"
    final.write_videofile(output_file, fps=24, codec="libx264")
    return output_file

st.title("🎬 SYNAPSE LYRICS MAKER")
if st.button("🚀 เริ่มทำวิดีโอวิ้ง"):
    with st.spinner("กำลังเสกเนื้อเพลงลงวิดีโอ..."):
        res = create_lyrics_video()
        if res:
            st.video(res)
            st.success("เสร็จแล้วครับเพื่อน!")
