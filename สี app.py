import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    target_file = "ta101.mp4" 
    if not os.path.exists(target_file):
        st.error(f"ไม่พบไฟล์ {target_file}")
        return None

    try:
        # 1. โหลดวิดีโอหลัก
        base_video = VideoFileClip(target_file)
        
        # 2. รายการเนื้อเพลงและเวลา (เพื่อนสามารถเพิ่มท่อนอื่นๆ ต่อได้ที่นี่)
        lyrics_data = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
            (26.0, 40.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร"),
            (41.0, 55.0, "คืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง"),
            (104.0, 114.0, "ปล่อยวางความโกรธที่เผาใจ..."),
            (117.0, 125.0, "ทิ้งความโลภที่ไม่มีวันพอ")
        ]
        
        clips = [base_video]

        # 3. ลูปสร้างตัวหนังสือวิ้งๆ ตามจังหวะ
        for start, end, text in lyrics_data:
            txt_clip = (TextClip(
                text=text, 
                font_size=50, 
                color='yellow', 
                font='Arial',
                duration=(end - start)
            ).with_start(start)
             .with_position(('center', 0.8 * base_video.h))) # วางไว้กึ่งกลางค่อนไปทางล่าง
            
            clips.append(txt_clip)
        
        # 4. รวมร่าง
        final = CompositeVideoClip(clips)
        output_name = "ta101_full_lyrics.mp4"
        
        # เขียนไฟล์ (ใส่ logger=None เพื่อไม่ให้หน้าเว็บค้าง)
        final.write_videofile(output_name, fps=24, codec="libx264")
        
        base_video.close()
        final.close()
        return output_name

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

st.title("🎬 SYNAPSE Lyrics Maker")
if st.button("🚀 เริ่มใส่เนื้อเพลงลง ta101.mp4"):
    with st.spinner("กำลังประมวลผล... ท่อนเพลงกำลังจะวิ้งขึ้นมาแล้วครับ"):
        res = make_video()
        if res:
            st.video(res)
            st.success("ใส่เนื้อเพลงเรียบร้อยแล้วครับเพื่อน!")
