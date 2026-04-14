import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    video_file = "ta101.mp4"
    font_file = "THSarabunNew.ttf" 

    if not os.path.exists(video_file) or not os.path.exists(font_file):
        st.error("❌ ไฟล์ไม่ครบ! เช็คชื่อ ta101.mp4 และ THSarabunNew.ttf ใน GitHub อีกทีนะ")
        return None

    try:
        # 1. โหลดวิดีโอแบบลดขนาด (เพื่อให้ RAM ไม่เต็ม)
        clip = VideoFileClip(video_file).with_effects([]) 
        
        # 2. ใส่เนื้อเพลง
        txt = (TextClip(
                text="วันหนึ่งถ้าเธอมองย้อนกลับมา", 
                font_size=60, 
                color='yellow', 
                font=font_file, 
                duration=5
            ).with_start(1).with_position(('center', 0.7 * clip.h)))
        
        # 3. รวมร่าง
        final = CompositeVideoClip([clip, txt])
        output = "synapse_result.mp4"
        
        # 4. เขียนไฟล์แบบประหยัดพลังงาน (หัวใจสำคัญตรงนี้ครับ!)
        final.write_videofile(
            output, 
            fps=15,             # ลด FPS ลงนิดหน่อยเพื่อให้รันผ่าน
            codec="libx264", 
            audio_codec="aac",
            bitrate="1000k",    # จำกัดคุณภาพเพื่อไม่ให้เครื่องค้าง
            threads=1,          # ใช้ 1 thread เพื่อความนิ่ง
            logger=None         # ปิด Log หน้าจอเพื่อลดภาระ
        )
        
        clip.close()
        final.close()
        return output

    except Exception as e:
        st.error(f"❌ เครื่องประมวลผลไม่ไหว: {e}")
        return None

# --- หน้าจอแอป ---
st.title("🎬 SYNAPSE Video Maker")

if st.button("🚀 เริ่มเสกตัวหนังสือ (แบบประหยัด RAM)"):
    with st.spinner("กำลังประมวลผล... ขั้นตอนนี้ใช้เวลา 1-2 นาที ห้ามปิดหน้าจอนะครับ"):
        res = make_video()
        if res:
            st.video(res)
            st.success("สำเร็จแล้ว! อยู่นิ่งๆ ไม่เจ็บตัวนะครับเพื่อน")
