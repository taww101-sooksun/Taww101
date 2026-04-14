import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def room_video_sync():
    st.subheader("🎬 ระบบวิดีโอเนื้อเพลง (Sync Master)")

    # 1. ตรวจสอบไฟล์วิดีโอในโฟลเดอร์ (เหมือนโค้ดเพลงของคุณ)
    video_files = sorted([f for f in os.listdir('.') if f.endswith(".mp4")])
    
    if not video_files:
        st.warning("⚠️ ไม่พบไฟล์วิดีโอ .mp4 ในระบบ")
        return

    # 2. เลือกวิดีโอปัจจุบัน (ใช้ session_state เหมือนระบบเพลง)
    if 'vdo_index' not in st.session_state:
        st.session_state.vdo_index = 0
        
    current_vdo = video_files[st.session_state.vdo_index]
    st.info(f"🎥 ไฟล์ที่เลือก: {current_vdo} ({st.session_state.vdo_index + 1}/{len(video_files)})")

    # 3. ข้อมูลเนื้อเพลงตาม Timeline ที่คุณให้มา
    lyrics_data = [
        (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
        (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต"),
        (26.0, 60.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคืนที่ร้องไห้จนไม่รู้จะไปทางไหน")
    ]

    # 4. ปุ่มควบคุม (ใช้ columns และ rerun เหมือนโค้ดเพลงเป๊ะ)
    col1, col2, col3 = st.columns(3)
    
    if col1.button("⏮️ วิดีโอก่อนหน้า"):
        st.session_state.vdo_index = (st.session_state.vdo_index - 1) % len(video_files)
        st.rerun()

    if col2.button("🚀 เริ่มเสกวิ้ง (Process)"):
        f_file = os.path.abspath("THSarabunNew.ttf")
        if os.path.exists(f_file):
            with st.spinner("กำลังประกอบร่างวิดีโอ..."):
                try:
                    base = VideoFileClip(current_vdo)
                    txt_clips = []
                    for start, end, text in lyrics_data:
                        t_clip = (TextClip(
                            text=text, 
                            font_size=50, 
                            color='yellow', 
                            font=f_file, 
                            duration=(end - start),
                            method='caption',
                            size=(base.w * 0.8, None)
                        ).with_start(start).with_position(('center', 0.8 * base.h)))
                        txt_clips.append(t_clip)

                    final = CompositeVideoClip([base] + txt_clips)
                    out_name = f"sync_{current_vdo}"
                    final.write_videofile(out_name, fps=12, codec="libx264")
                    st.video(out_name)
                    st.success("✅ วิ้งเรียบร้อยตามต้นฉบับ!")
                except Exception as e:
                    st.error(f"❌ ติดปัญหา: {e}")
        else:
            st.error("❌ หาไฟล์ฟอนต์ THSarabunNew.ttf ไม่เจอ")

    if col3.button("⏭️ วิดีโอถัดไป"):
        st.session_state.vdo_index = (st.session_state.vdo_index + 1) % len(video_files)
        st.rerun()

    # 5. รายชื่อวิดีโอ (คลิกเลือกได้เหมือนระบบเพลง)
    st.write("---")
    with st.expander("📂 คลังวิดีโอต้นฉบับ"):
        for i, f in enumerate(video_files):
            if st.button(f"🎞️ {f}", key=f"vdo_{i}", use_container_width=True):
                st.session_state.vdo_index = i
                st.rerun()
