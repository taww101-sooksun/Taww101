import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- แก้ปัญหา MoviePy v2.0+ ---
# ไม่ต้องใช้ change_settings แล้วครับ เวอร์ชั่นใหม่จะฉลาดขึ้น 
# แต่เพื่อนต้องมั่นใจว่ามีไฟล์ 'packages.txt' ที่เขียนว่า 'imagemagick' ใน GitHub นะ

def make_vdo_final():
    v_file = "ta101.mp4"
    f_file = "THSarabunNew.ttf"

    try:
        # 1. โหลดวิดีโอต้นฉบับ
        base = VideoFileClip(v_file)
        
        # 2. ข้อมูล Timeline ที่เพื่อนให้มาล่าสุด (แปลงนาทีเป็นวินาที)
        lyrics = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
            (26.0, 60.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร\nคืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง"),
            (64.0, 74.0, "ปล่อยวางความโกรธที่เผาใจ..."),
            (77.0, 85.0, "ทิ้งความโลภที่ไม่มีวันพอ"),
            # เพิ่มท่อนหลังตามที่ส่งมา...
            (101.0, 111.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (114.0, 124.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้")
        ]

        txt_clips = []
        for start, end, text in lyrics:
            # สร้างตัวหนังสือสีเหลืองวิ้งๆ
            t_clip = (TextClip(
                text=text, 
                font_size=50, 
                color='yellow', 
                font=f_file, 
                duration=(end - start),
                method='caption',
                size=(base.w * 0.8, None)
            ).with_start(start).with_position(('center', 0.75 * base.h)))
            
            txt_clips.append(t_clip)

        # 3. รวมร่าง
        final = CompositeVideoClip([base] + txt_clips)
        out_name = "synapse_final.mp4"
        
        # สั่งเขียนไฟล์ (FPS ต่ำเพื่อถนอมเครื่อง)
        final.write_videofile(out_name, fps=12, codec="libx264")
        
        base.close()
        return out_name

    except Exception as e:
        st.error(f"❌ ระบบแจ้งว่า: {e}")
        return None

# --- ส่วนแสดงผล ---
st.title("🎬 SYNAPSE Video Master")
if st.button("🚀 เริ่มสร้างวิดีโอวิ้งๆ"):
    with st.spinner("กำลังประมวลผลตาม Timeline..."):
        res = make_vdo_final()
        if res:
            st.video(res)
