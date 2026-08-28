# -*- coding: utf-8 -*-

# Ta_app.py

# แอปวัดพื้นที่นา + ปักหมุด + คำนวณค่าบริการ

import math
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import LocateControl
from streamlit_folium import st_folium

# --------------------------------------------------

# ตั้งค่าหน้าเว็บ

# --------------------------------------------------

st.set_page_config(
page_title="Ta App - วัดพื้นที่นา",
page_icon="🌾",
layout="wide",
initial_sidebar_state="collapsed",
)

st.markdown(
""" <style>
html, body, [class*="css"], .stApp, button, input, textarea, select {
font-family: "Noto Sans Thai", "Tahoma", "Arial", sans-serif !important;
} </style>
""",
unsafe_allow_html=True,
)

# --------------------------------------------------

# ตั้งค่าพื้นฐาน

# --------------------------------------------------

PLOW_RATE = 250.0
MILL_RATE = 350.0

RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

BASE_DIR = Path(**file**).resolve().parent
LOGO_PATH = BASE_DIR / "logo1.png"

# --------------------------------------------------

# ฟังก์ชันแปลงพื้นที่

# --------------------------------------------------

def thai_area(m2: float):
"""แปลงตารางเมตรเป็น ไร่ งาน ตารางวา และตารางเมตรที่เหลือ"""

```
if m2 < 0:
    m2 = 0

rai = int(m2 // RAI_M2)
remain = m2 - (rai * RAI_M2)

ngan = int(remain // NGAN_M2)
remain -= ngan * NGAN_M2

wa = int(remain // WA_M2)
remain -= wa * WA_M2

return rai, ngan, wa, remain
```

# --------------------------------------------------

# คำนวณพื้นที่จากพิกัด GPS

# ไม่ใช้ shapely

# --------------------------------------------------

def polygon_area_m2(points):
"""
คำนวณพื้นที่รูปหลายเหลี่ยมจากพิกัด latitude / longitude
โดยประมาณด้วย local projection
"""

```
if len(points) < 3:
    return 0.0

lat0 = math.radians(
    sum(point[0] for point in points) / len(points)
)

earth_radius = 6378137.0

xy = []

for lat, lon in points:
    x = (
        math.radians(lon)
        * earth_radius
        * math.cos(lat0)
    )

    y = math.radians(lat) * earth_radius

    xy.append((x, y))

# Shoelace formula
area = 0.0

for i in range(len(xy)):
    x1, y1 = xy[i]
    x2, y2 = xy[(i + 1) % len(xy)]

    area += (x1 * y2) - (x2 * y1)

return abs(area) / 2.0
```

def money(value):
return f"{value:,.2f}"

# --------------------------------------------------

# Session State

# --------------------------------------------------

if "points" not in st.session_state:
st.session_state.points = []

if "saved_plots" not in st.session_state:
st.session_state.saved_plots = []

if "lat" not in st.session_state:
st.session_state.lat = 13.7563

if "lon" not in st.session_state:
st.session_state.lon = 100.5018

# --------------------------------------------------

# ส่วนหัว

# --------------------------------------------------

header_left, header_right = st.columns(
[1, 5],
vertical_alignment="center",
)

with header_left:
if LOGO_PATH.exists():
st.image(str(LOGO_PATH), width=115)
else:
st.markdown("## 🌾")

with header_right:
st.title("🌾 Ta App")
st.caption(
"วัดพื้นที่นา • ปักหมุด • คำนวณค่าบริการไถ / ปั่น"
)

st.divider()

# --------------------------------------------------

# ข้อมูลแปลงนา

# --------------------------------------------------

c1, c2 = st.columns(2)

with c1:
owner = st.text_input(
"👤 ชื่อเจ้าของนา",
placeholder="เช่น นายสมชาย ใจดี",
key="owner",
)

with c2:
note = st.text_input(
"📝 หมายเหตุ",
placeholder="เช่น นาแปลงหลังบ้าน / นัดไถวันจันทร์",
key="note",
)

# --------------------------------------------------

# แผนที่

# --------------------------------------------------

st.subheader("🗺️ กำหนดขอบเขตแปลงนา")

st.info(
"แตะบนแผนที่เพื่อเพิ่มหมุดทีละจุด "
"• ใช้ปุ่ม GPS เพื่อดูตำแหน่งปัจจุบัน "
"• สามารถลากหมุดเพื่อปรับตำแหน่งได้"
)

map_center = [
st.session_state.lat,
st.session_state.lon,
]

m = folium.Map(
location=map_center,
zoom_start=17,
control_scale=True,
tiles="OpenStreetMap",
)

# ปุ่ม GPS

LocateControl(
auto_start=False,
flyTo=True,
keepCurrentZoomLevel=False,
showCompass=True,
).add_to(m)

# --------------------------------------------------

# วาดหมุด

# --------------------------------------------------

for i, (lat, lon) in enumerate(
st.session_state.points
):

```
folium.Marker(
    [lat, lon],
    tooltip=f"หมุด {i + 1}",
    draggable=True,
    icon=folium.Icon(
        color="green",
        icon="map-marker",
    ),
).add_to(m)
```

# --------------------------------------------------

# วาดเส้นรอบแปลง

# --------------------------------------------------

if len(st.session_state.points) >= 2:

```
line_points = list(st.session_state.points)

if len(line_points) >= 3:
    line_points.append(line_points[0])

folium.PolyLine(
    line_points,
    color="green",
    weight=4,
    opacity=0.85,
).add_to(m)
```

# --------------------------------------------------

# วาดพื้นที่

# --------------------------------------------------

if len(st.session_state.points) >= 3:

```
folium.Polygon(
    st.session_state.points,
    color="green",
    weight=2,
    fill=True,
    fill_opacity=0.20,
).add_to(m)
```

# --------------------------------------------------

# แสดงแผนที่

# --------------------------------------------------

map_data = st_folium(
m,
width=None,
height=520,
returned_objects=[
"last_clicked",
"last_object_clicked",
"center",
],
key="farm_map",
)

# --------------------------------------------------

# เพิ่มหมุดเมื่อแตะแผนที่

# --------------------------------------------------

clicked = map_data.get("last_clicked")

if clicked:

```
lat = float(clicked["lat"])
lon = float(clicked["lng"])

if st.session_state.points:

    last = st.session_state.points[-1]

else:

    last = None

# ป้องกันการเพิ่มหมุดเดิมซ้ำตอน Streamlit rerun
if (
    last is None
    or abs(last[0] - lat) > 0.000001
    or abs(last[1] - lon) > 0.000001
):

    st.session_state.points.append(
        (lat, lon)
    )

    st.rerun()
```

# --------------------------------------------------

# ปุ่มจัดการหมุด

# --------------------------------------------------

b1, b2, b3, b4 = st.columns(4)

with b1:

```
if st.button(
    "↩️ ลบหมุดล่าสุด",
    use_container_width=True,
):

    if st.session_state.points:

        st.session_state.points.pop()
        st.rerun()
```

with b2:

```
if st.button(
    "🗑️ ล้างหมุดทั้งหมด",
    use_container_width=True,
):

    st.session_state.points = []
    st.rerun()
```

with b3:

```
if st.button(
    "📍 ใช้ตำแหน่งตัวอย่าง",
    use_container_width=True,
):

    st.session_state.points = [
        (13.75630, 100.50180),
        (13.75630, 100.50300),
        (13.75530, 100.50300),
        (13.75530, 100.50180),
    ]

    st.rerun()
```

with b4:

```
if st.button(
    "🔄 รีเฟรชแผนที่",
    use_container_width=True,
):

    st.rerun()
```

# --------------------------------------------------

# คำนวณพื้นที่

# --------------------------------------------------

area_m2 = polygon_area_m2(
st.session_state.points
)

rai, ngan, wa, remain_m2 = thai_area(
area_m2
)

# --------------------------------------------------

# คำนวณค่าบริการ

# --------------------------------------------------

plow_cost = (
area_m2 / RAI_M2
) * PLOW_RATE

mill_cost = (
area_m2 / RAI_M2
) * MILL_RATE

total_cost = plow_cost + mill_cost

# --------------------------------------------------

# แสดงผลพื้นที่

# --------------------------------------------------

st.divider()

st.subheader("📐 ผลการวัดพื้นที่")

if len(st.session_state.points) < 3:

```
st.warning(
    "กรุณาปักหมุดอย่างน้อย 3 จุด "
    "เพื่อคำนวณพื้นที่"
)
```

else:

```
a1, a2, a3, a4 = st.columns(4)

with a1:
    st.metric(
        "พื้นที่รวม",
        f"{area_m2:,.2f} ตร.ม.",
    )

with a2:
    st.metric(
        "ไร่",
        f"{rai:,}",
    )

with a3:
    st.metric(
        "งาน",
        f"{ngan:,}",
    )

with a4:
    st.metric(
        "ตารางวา",
        f"{wa:,}",
    )

st.success(
    f"พื้นที่โดยประมาณ **{rai} ไร่ "
    f"{ngan} งาน {wa} ตารางวา "
    f"{remain_m2:.2f} ตร.ม.**"
)


# --------------------------------------------------
# ค่าบริการ
# --------------------------------------------------

st.divider()

st.subheader("💰 ค่าบริการ")

s1, s2 = st.columns(2)

with s1:

    st.markdown("### 🚜 ไถ")

    st.markdown(
        f"**{money(PLOW_RATE)} บาท / ไร่**"
    )

    st.metric(
        "ค่าไถ",
        f"{money(plow_cost)} บาท",
    )


with s2:

    st.markdown("### ⚙️ ปั่น")

    st.markdown(
        f"**{money(MILL_RATE)} บาท / ไร่**"
    )

    st.metric(
        "ค่าปั่น",
        f"{money(mill_cost)} บาท",
    )


# --------------------------------------------------
# ยอดรวม
# --------------------------------------------------

st.markdown("---")

st.markdown(
    f"""
    <div style="
        padding:24px;
        border-radius:18px;
        background:rgba(46,125,50,.12);
        border:2px solid rgba(46,125,50,.35);
        text-align:center;
        margin-top:10px;
    ">

        <div style="font-size:20px;">
            💰 ยอดรวมทั้งหมด
        </div>

        <div style="
            font-size:44px;
            font-weight:800;
        ">
            {money(total_cost)} บาท
        </div>

        <div style="font-size:15px;">
            ไถ {money(plow_cost)}
            +
            ปั่น {money(mill_cost)}
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# บันทึกแปลงนา
# --------------------------------------------------

st.divider()

if st.button(
    "💾 บันทึกแปลงนี้",
    type="primary",
    use_container_width=True,
):

    record = {

        "เจ้าของนา": owner or "-",

        "พื้นที่ ตร.ม.": round(
            area_m2,
            2,
        ),

        "พื้นที่": (
            f"{rai} ไร่ "
            f"{ngan} งาน "
            f"{wa} ตารางวา "
            f"{remain_m2:.2f} ตร.ม."
        ),

        "ค่าไถ": round(
            plow_cost,
            2,
        ),

        "ค่าปั่น": round(
            mill_cost,
            2,
        ),

        "ยอดรวม": round(
            total_cost,
            2,
        ),

        "หมายเหตุ": note or "-",

        "หมุด": list(
            st.session_state.points
        ),
    }

    st.session_state.saved_plots.append(
        record
    )

    st.success(
        "บันทึกข้อมูลแปลงนาเรียบร้อยแล้วครับ 🌾"
    )
```

# --------------------------------------------------

# รายการแปลงนาที่บันทึก

# --------------------------------------------------

if st.session_state.saved_plots:

```
st.divider()

st.subheader(
    "📋 แปลงนาที่บันทึกไว้"
)

for idx, item in enumerate(
    reversed(
        st.session_state.saved_plots
    ),
    1,
):

    plot_number = (
        len(st.session_state.saved_plots)
        - idx
        \+ 1
    )

    with st.expander(
        f"แปลงที่ {plot_number} • "
        f"{item['เจ้าของนา']} • "
        f"{money(item['ยอดรวม'])} บาท"
    ):

        st.write(
            f"**เจ้าของนา:** "
            f"{item['เจ้าของนา']}"
        )

        st.write(
            f"**พื้นที่:** "
            f"{item['พื้นที่']}"
        )

        st.write(
            f"**ค่าไถ:** "
            f"{money(item['ค่าไถ'])} บาท"
        )

        st.write(
            f"**ค่าปั่น:** "
            f"{money(item['ค่าปั่น'])} บาท"
        )

        st.write(
            f"**ยอดรวม:** "
            f"{money(item['ยอดรวม'])} บาท"
        )

        st.write(
            f"**หมายเหตุ:** "
            f"{item['หมายเหตุ']}"
        )
```

# --------------------------------------------------

# ส่วนท้าย

# --------------------------------------------------

st.divider()

st.caption(
"Ta App • ระบบคำนวณพื้นที่จากพิกัด GPS โดยประมาณ "
"ควรตรวจสอบแนวเขตจริงก่อนนำไปใช้เป็นข้อมูลทางกฎหมาย"
    )
