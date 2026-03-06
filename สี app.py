import streamlit as st
import time

# --- 🎭 1. CSS ฉบับจิ๋ว (Compact Design) ---
st.markdown("""
    <style>
    .mini-clock { font-size: 40px; font-weight: bold; color: #00ff00; text-align: left; }
    .step-box { width: 20px; height: 20px; border-radius: 3px; display: inline-block; margin: 1px; }
    .on-v1 { background-color: #FF7F50; }
    .on-v2 { background-color: #00ffff; }
    .off { background-color: #333; }
    .current { border: 2px solid #fff; box-shadow: 0 0 5px #fff; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว (แบบประหยัดพื้นที่) ---
c1, c2 = st.columns([1, 5])
with c1: 
    # ดัก Error รูปแบบจิ๋ว
    try: st.image("Logo3.jpg", width=40)
    except: st.write("🎯")
with c2: st.caption("SYNAPSE MINI ENGINE | อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 🎛️ 3. แผงควบคุม 4 สไลด์ (แถวเดียวจบ) ---
cols = st.columns(4)
v1_range = cols[0].text_input("V1 Range", "1-4, 16-20")
v2_range = cols[1].text_input("V2 Range", "1-16")
bpm = cols[2].number_input("BPM", 60, 300, 120)
stop_val = cols[3].number_input("Stop", 1, 100, 20)

# --- 📊 4. ตาราง 20 ช่อง (บรรทัดเดียวจิ๋วๆ) ---
def draw_mini_grid(curr=0):
    # ฟังก์ชันแปลง Range ข้อความ (เช่น 1-4) เป็น List ตัวเลขจริง
    def parse_range(r_str, limit=20):
        res = set()
        for part in r_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                res.update(range(start, end + 1))
            else: res.add(int(part))
        return res

    v1_set = parse_range(v1_range)
    v2_set = parse_range(v2_range)
    
    # วาด Grid จิ๋ว
    grid_html = "<div style='line-height: 1;'>"
    for row_set, color_class in [(v1_set, 'on-v1'), (v2_set, 'on-v2')]:
        for i in range(1, stop_val + 1):
            cl = color_class if i in row_set else 'off'
            active = 'current' if i == curr else ''
            grid_html += f"<div class='step-box {cl} {active}' title='{i}'></div>"
        grid_html += "<br>"
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

grid_place = st.empty()
with grid_place: draw_mini_grid()

# --- 🚀 5. ปุ่ม Play และนาฬิกาจิ๋ว ---
c_play, c_time = st.columns([1, 2])
if c_play.button("🔴 PLAY", use_container_width=True):
    step_t = 60 / bpm
    for x in range(1, stop_val + 1):
        with c_time: st.markdown(f"<div class='mini-clock'>CH: {x}</div>", unsafe_allow_html=True)
        with grid_place: draw_mini_grid(x)
        time.sleep(step_t)
    st.toast("🏁 Finished")
