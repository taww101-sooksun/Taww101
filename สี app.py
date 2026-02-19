import streamlit as st

st.set_page_config(layout="wide")

# 1. เตรียม "ค่าเริ่มต้น" ที่ต่างกันไว้ 8 ชุด (ผนัง, กรอบ, ปุ่ม)
default_colors = [
    ("#F0F0F0", "#333333", "#FF4B4B"), # แบบที่ 1
    ("#E3F2FD", "#1565C0", "#0D47A1"), # แบบที่ 2 (โทนฟ้า)
    ("#F1F8E9", "#33691E", "#558B2F"), # แบบที่ 3 (โทนเขียว)
    ("#FFF3E0", "#E65100", "#EF6C00"), # แบบที่ 4 (โทนส้ม)
    ("#FCE4EC", "#880E4F", "#AD1457"), # แบบที่ 5 (โทนชมพู)
    ("#F3E5F5", "#4A148C", "#6A1B9A"), # แบบที่ 6 (โทนม่วง)
    ("#EFEBE9", "#3E2723", "#4E342E"), # แบบที่ 7 (โทนน้ำตาล)
    ("#FAFAFA", "#212121", "#000000"), # แบบที่ 8 (ขาวดำ)
]

st.title("🎨 ทดลองสี 8 แบบ (เริ่มด้วยสีที่ต่างกัน)")

for row in range(2):
    cols = st.columns(4)
    for col_idx in range(4):
        num = (row * 4) + col_idx # ลำดับ index 0-7
        with cols[col_idx]:
            # ดึงสีจาก List มาเป็นค่าเริ่มต้น
            bg_def, fr_def, bt_def = default_colors[num]
            
            bg = st.color_picker(f"ผนัง {num+1}", bg_def, key=f"bg{num}")
            fr = st.color_picker(f"กรอบ {num+1}", fr_def, key=f"fr{num}")
            bt = st.color_picker(f"ปุ่ม {num+1}", bt_def, key=f"bt{num}")

            st.markdown(f"""
                <div style="background-color:{bg}; height:150px; display:flex; justify-content:center; align-items:center; border:5px solid #222; border-radius:10px;">
                    <div style="width:80px; height:50px; border:5px solid {fr}; background:white; display:flex; justify-content:center; align-items:center;">
                        <div style="background-color:{bt}; color:white; padding:5px; border-radius:3px; font-size:10px;">ปุ่ม</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
