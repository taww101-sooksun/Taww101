import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# --- บังคับปลุกระบบวาดภาพ (IMAGEMAGICK) ---
if os.path.exists("/usr/bin/convert"):
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def make_synapse_vdo():
    v_file = "ta101.mp4"
    f_file = "THSarabunNew.ttf"

    try:
        base = VideoFileClip(v_file)
        
        # 1. ข้อมูลเวลา (Timeline) ที่คุณให้มา
        lyrics = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
            (26.0, 60.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร\nคืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง"),
            (64.0, 74.0, "ปล่อยวางความโกรธที่เผาใจ..."),
            (77.0, 85.0, "ทิ้งความโลภที่ไม่มีวันพอ"),
            (101.0, 111.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (114.0, 124.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
            (127.0, 163.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร\nคืนที่ร้องไห้จนไม่รู้จะไปทางไหน\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง"),
            (168.0, 178.0, "ปล่อยวางความโกรธที่เผาใจ... ทิ้งความโลภที่ไม่มีวันพอ")
        ]

        txt_clips = []
        for start, end, text in lyrics:
            # สร้างตัวหนังสือวิ้งๆ สีเหลือง
            t_clip = (TextClip(
                text=text, 
                font_size=55, 
                color='yellow', 
                font=f_file, 
                duration=(end - start),
                method='caption',
                size=(base.w * 0.8, None)
            ).with_start(start).with_position(('center', 0.75 * base.h)))
            
            txt_clips.append(t_clip)

        # 2. รวมร่างวิดีโอกับตัวหนังสือ
        final = CompositeVideoClip([base] + txt_clips)
        out_name = "synapse_final.mp4"
        
        # 3. สั่งเขียนไฟล์ (เน้นความเสถียรสำหรับมือถือ)
        final.write_videofile(out_name, fps=12, codec="libx264", audio_codec="aac", threads=1)
        
        base.close()
        return out_name

    except Exception as e:
        st.error(f"❌ ระบบยังติดขัด: {e}")
        return None

# --- หน้าจอหลัก ---
st.title("🎬 SYNAPSE Lyric Video")
if st.button("🚀 เริ่มทำวิดีโอให้วิ้งตามเวลา"):
    with st.spinner("กำลังประมวลผล... กรุณาอยู่นิ่งๆ รอนะครับเพื่อน"):
        res = make_synapse_vdo()
        if res:
            st.video(res)
            st.success("เรียบร้อย! วิ้งตามเวลาที่คุณต้องการแล้วครับ")
