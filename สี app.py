import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    video_input = "ta101.mp4"
    video_output = "result.mp4"

    if not os.path.exists(video_input):
        st.error(f"❌ หาไฟล์ {video_input} ไม่เจอใน GitHub!")
        return None

    try:
        # 1. โหลดคลิปต้นฉบับ
        base_video = VideoFileClip(video_input)
        
        # 2. รายการซับไทเติล (ตามที่คุณส่งมา)
        # รูปแบบ: (เวลาเริ่ม, เวลาจบ, ข้อความ)
        subtitles_data = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
            (26.0, 84.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว...\n(และข้อความส่วนที่เหลือของคุณ)"),
            (101.0, 111.0, "ปล่อยวางความโกรธที่เผาใจ...\nทิ้งความโลภที่ไม่มีวันพอ")
        ]

        clips_to_overlay = [base_video]

        # 3. วนลูปสร้าง TextClip ตามช่วงเวลา
        for start_t, end_t, txt_content in subtitles_data:
            txt_clip = (TextClip(
                            text=txt_content,
                            font_size=50,
                            color='yellow',
                            method='caption',
                            size=(base_video.w*0.8, None) # บีบข้อความไม่ให้ล้นจอ
                        )
                        .with_start(start_t)
                        .with_duration(end_t - start_t)
                        .with_position(('center', 'bottom')) # วางไว้ด้านล่างเหมือนซับปกติ
                       )
            clips_to_overlay.append(txt_clip)

        # 4. รวมร่าง
        final = CompositeVideoClip(clips_to_overlay)
        
        # 5. Export (ใส่เบรกเกอร์เผื่อไฟล์ยาวเกินไป)
        final.write_videofile(video_output, fps=24, codec="libx264", audio_codec="aac")
        
        base_video.close()
        final.close()
        return video_output

    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
        return None

# --- UI ---
st.title("🎬 SYNAPSE Video Maker (Subtitled)")
st.info("กำลังจะเสกซับไทเติลลงใน ta101.mp4 ตามเวลาที่กำหนด")

if st.button("🚀 เริ่มเสกวิดีโอ"):
    with st.spinner('กำลังประมวลผล... ขั้นตอนนี้อาจใช้เวลา 1-3 นาทีตามความยาวคลิป'):
        res = make_video()
        if res:
            st.success("เสร็จแล้ว! ดาวน์โหลดหรือดูด้านล่างได้เลย")
            st.video(res)
