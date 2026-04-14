from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# 1. โหลดวิดีโอต้นฉบับ
video = VideoFileClip("ta101.mp4")

# 2. ตั้งค่าเนื้อเพลงและช่วงเวลา (เอามาจากตารางที่เราคุยกัน)
# (เริ่มกี่วินาที, จบกี่วินาที, ข้อความ)
lyrics_data = [
    (1, 10, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
    (13, 23, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
    (26, 35, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร"),
    # ... เพื่อนสามารถเพิ่มท่อนอื่นๆ ต่อได้จนครบ 3 นาที ...
]

# 3. สร้างรายการของข้อความที่จะไปแปะบนวิดีโอ
clips = [video]

for start, end, text in lyrics_data:
    txt_clip = (TextClip(text, fontsize=50, color='white', font='Arial-Bold', 
                         method='caption', size=(video.w*0.8, None))
                .set_start(start)
                .set_duration(end - start)
                .set_position(('center', video.h*0.8))) # วางไว้ด้านล่าง 80% ของจอ
    clips.append(txt_clip)

# 4. รวมร่างวิดีโอและข้อความเข้าด้วยกัน
final_video = CompositeVideoClip(clips)

# 5. เซฟไฟล์ออกมาเป็นวิดีโอใหม่
final_video.write_videofile("ta101_lyrics.mp4", fps=video.fps)
