importreamlit as st
import cv2
import numpy as np
import tempfile
import os

st.set_page_config(
    page_title="ภาพถ่าย → วิดีโอ",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 ภาพถ่าย → วิดีโอ")
st.write("อัปโหลดภาพ แล้วสร้างวิดีโอแบบมีการเคลื่อนไหว")

uploaded_file = st.file_uploader(
    "เลือกรูปภาพ",
    type=["jpg", "jpeg", "png", "webp"]
)

duration = st.slider(
    "ความยาววิดีโอ (วินาที)",
    min_value=2,
    max_value=20,
    value=5
)

fps = 30

motion = st.selectbox(
    "รูปแบบการเคลื่อนไหว",
    [
        "ซูมเข้า",
        "ซูมออก",
        "เลื่อนซ้าย → ขวา",
        "เลื่อนขวา → ซ้าย",
        "เลื่อนขึ้น → ลง",
        "เลื่อนลง → ขึ้น"
    ]
)

if uploaded_file is not None:

    # อ่านรูป
    file_bytes = np.asarray(
        bytearray(uploaded_file.read()),
        dtype=np.uint8
    )

    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        st.error("ไม่สามารถอ่านรูปภาพได้")
        st.stop()

    height, width = image.shape[:2]

    st.image(
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
        caption="ภาพต้นฉบับ",
        use_container_width=True
    )

    if st.button("🎬 สร้างวิดีโอ", type="primary"):

        total_frames = int(duration * fps)

        # ไฟล์ชั่วคราว
        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        )

        output_path = output_file.name
        output_file.close()

        # ขนาดวิดีโอ
        video_width = 720
        video_height = 1280

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (video_width, video_height)
        )

        progress = st.progress(0)

        for frame_number in range(total_frames):

            progress.progress(
                min((frame_number + 1) / total_frames, 1.0)
            )

            t = frame_number / max(total_frames - 1, 1)

            # --------------------------------
            # สร้างภาพสำหรับแต่ละเฟรม
            # --------------------------------

            if motion == "ซูมเข้า":

                scale = 1.0 + (0.15 * t)

                new_w = int(width * scale)
                new_h = int(height * scale)

                frame = cv2.resize(
                    image,
                    (new_w, new_h),
                    interpolation=cv2.INTER_LINEAR
                )

                x = (new_w - width) // 2
                y = (new_h - height) // 2

                frame = frame[y:y + height, x:x + width]

            elif motion == "ซูมออก":

                scale = 1.15 - (0.15 * t)

                new_w = int(width * scale)
                new_h = int(height * scale)

                resized = cv2.resize(
                    image,
                    (new_w, new_h),
                    interpolation=cv2.INTER_LINEAR
                )

                canvas = np.zeros_like(image)

                x = max((width - new_w) // 2, 0)
                y = max((height - new_h) // 2, 0)

                crop_w = min(new_w, width)
                crop_h = min(new_h, height)

                canvas[
                    y:y + crop_h,
                    x:x + crop_w
                ] = resized[:crop_h, :crop_w]

                frame = canvas

            else:

                # ซูมเล็กน้อยเพื่อให้การเลื่อนดูนุ่มขึ้น
                scale = 1.12

                new_w = int(width * scale)
                new_h = int(height * scale)

                large = cv2.resize(
                    image,
                    (new_w, new_h),
                    interpolation=cv2.INTER_LINEAR
                )

                max_x = new_w - width
                max_y = new_h - height

                if motion == "เลื่อนซ้าย → ขวา":
                    x = int(max_x * t)
                    y = max_y // 2

                elif motion == "เลื่อนขวา → ซ้าย":
                    x = int(max_x * (1 - t))
                    y = max_y // 2

                elif motion == "เลื่อนขึ้น → ลง":
                    x = max_x // 2
                    y = int(max_y * t)

                else:
                    x = max_x // 2
                    y = int(max_y * (1 - t))

                frame = large[
                    y:y + height,
                    x:x + width
                ]

            # --------------------------------
            # ปรับเป็นแนวตั้ง 9:16
            # --------------------------------

            frame_ratio = frame.shape[1] / frame.shape[0]
            target_ratio = video_width / video_height

            if frame_ratio > target_ratio:

                new_h = video_height
                new_w = int(new_h * frame_ratio)

            else:

                new_w = video_width
                new_h = int(new_w / frame_ratio)

            frame = cv2.resize(
                frame,
                (new_w, new_h),
                interpolation=cv2.INTER_AREA
            )

            # ครอปตรงกลาง
            x = max((new_w - video_width) // 2, 0)
            y = max((new_h - video_height) // 2, 0)

            frame = frame[
                y:y + video_height,
                x:x + video_width
            ]

            # ป้องกันขนาดผิด
            if frame.shape[0] != video_height or frame.shape[1] != video_width:
                frame = cv2.resize(
                    frame,
                    (video_width, video_height)
                )

            writer.write(frame)

        writer.release()

        progress.empty()

        st.success("สร้างวิดีโอเสร็จแล้ว 🎉")

        # แสดงวิดีโอ
        with open(output_path, "rb") as f:
            video_bytes = f.read()

        st.video(video_bytes)

        st.download_button(
            label="⬇️ ดาวน์โหลดวิดีโอ",
            data=video_bytes,
            file_name="photo_to_video.mp4",
            mime="video/mp4"
        )

        # ลบไฟล์ชั่วคราว
        try:
            os.remove(output_path)
        except:
            pass
