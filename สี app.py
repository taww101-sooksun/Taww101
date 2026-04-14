import streamlit as st
import os
import base64
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def room_video_sync():
    st.subheader("🎬 ระบบวิดีโอเนื้อเพลง (Sync Master)")

    # 1. ตรวจสอบไฟล์วิดีโอในโฟลเดอร์ (เลียนแบบ music_files)
    video_files = sorted([f for f in os.listdir('.') if f.endswith(".mp4")])
    
    if not video_files:
        st.warning("⚠️ ไม่พบไฟล์วิดีโอ .mp4 ในระบบ")
        return

    # สร้าง index สำหรับวิดีโอใน session_state ถ้ายังไม่มี
    if 'vdo_index' not in st.session_state:
        st.session_state.vdo_index = 0

    # 2. เลือกวิดีโอปัจจุบัน
    current_vdo = video_files[st.session_state.vdo_index]
    st.info(f"🎥 ไฟล์ที่เลือก: {current_vdo} (ลำดับที่ {st.session_state.vdo_index + 1}/{len(video_files)})")

    # 3. ข้อมูล Timeline เนื้อเพลงที่เพื่อนให้มา
    lyrics_data = [
        (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
        (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
        (26.0, 60.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร\nคืนที่ร้องไห้จนไม่รู้จะไปทางไหน"),
        (64.0, 74.0, "ปล่อยวางความโกรธที่เผาใจ..."),
        (77.0, 85.0, "ทิ้งความโลภที่ไม่มีวันพอ")
    ]

    # 4. ส่วนควบคุม (เหมือนปุ่มกดเพลงเป๊ะ)
    col1, col2, col3 = st.columns(3)
    
    if col1.button("⏮️ วิดีโอก่อนหน้า"):
        st.session_state.vdo_index = (st.session_state.vdo_index - 1) % len(video_files)
        st.rerun()

    # ปุ่ม "เริ่มเสกวิ้ง" คือหัวใจของการประกอบร่าง
    if col2.button("🚀 เริ่มสร้างวิดีโอ"):
        f_path = os.path.abspath("THSarabunNew.ttf") # ใช้ Path เต็มแก้ทางตัน
        if os.path.exists(f_path):
            with st.spinner("กำลังเสกตัวหนังสือวิ้งๆ..."):
                try:
                    clip = VideoFileClip(current_vdo)
                    txt_clips = []
                    
                    for start, end, text in lyrics_data:
                        t_clip = (TextClip(
                            text=text, 
                            font_size=55, 
                            color='yellow', 
                            font=f_path, 
                            duration=(end - start),
                            method='caption',
                            size=(clip.w * 0.8, None)
                        ).with_start(start).with_position(('center', 0.8 * clip.h)))
                        txt_clips.append(t_clip)

                    final = CompositeVideoClip([clip] + txt_clips)
                    out_name = f"done_{current_vdo}"
                    final.write_videofile(out_name, fps=12, codec="libx264")
                    
                    st.video(out_name)
                    st.success("✨ วิ้งเรียบร้อยแล้วครับเพื่อน!")
                except Exception as e:
                    st.error(f"❌ ระบบยังดื้อ: {e}")
        else:
            st.error("❌ หาไฟล์ THSarabunNew.ttf ไม่เจอใน GitHub")

    if col3.button("⏭️ วิดีโอถัดไป"):
        st.session_state.vdo_index = (st.session_state.vdo_index + 1) % len(video_files)
        st.rerun()

    # 5. รายชื่อวิดีโอทั้งหมด (คลิกเลือกได้เหมือนระบบเพลง)
    st.write("---")
    with st.expander("📂 คลังวิดีโอในระบบ"):
        for i, f in enumerate(video_files):
            if st.button(f"🎞️ {f}", key=f"vdo_list_{i}", use_container_width=True):
                st.session_state.vdo_index = i
                st.rerun()
