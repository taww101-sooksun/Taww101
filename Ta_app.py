import json
import math
import os

import folium
import streamlit as st
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Ta App - วัดพื้นที่นา",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PLOW_RATE = 250.0
MILL_RATE = 350.0
RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0
DEFAULT_CENTER = [13.7563, 100.5018]
DATA_FILE = "ta_saved_plots.json"
LOGO_PATH = "logo1.png"


def thai_area(m2):
    m2 = max(0.0, float(m2))
    rai = int(m2 // RAI_M2)
    remain = m2 - rai * RAI_M2
    ngan = int(remain // NGAN_M2)
    remain -= ngan * NGAN_M2
    wa = int(remain // WA_M2)
    remain -= wa * WA_M2
    return rai, ngan, wa, remain


def polygon_area_m2(points):
    if len(points) < 3:
        return 0.0

    average_lat = sum(p[0] for p in points) / len(points)
    lat_radians = math.radians(average_lat)
    earth_radius = 6378137.0
    xy = []

    for lat, lon in points:
        x = math.radians(lon) * earth_radius * math.cos(lat_radians)
        y = math.radians(lat) * earth_radius
        xy.append((x, y))

    area = 0.0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2.0


def money(value):
    return f"{value:,.2f}"


def load_saved_plots():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_saved_plots(records):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


if "points" not in st.session_state:
    st.session_state.points = []

if "saved_plots" not in st.session_state:
    st.session_state.saved_plots = load_saved_plots()

if "map_key" not in st.session_state:
    st.session_state.map_key = 0


st.markdown(
    """
    <style>
    html, body, [class*="css"], .stApp,
    button, input, textarea, select {
        font-family: Tahoma, Arial, sans-serif !important;
    }
    .total-box {
        padding: 22px;
        border-radius: 18px;
        background: rgba(46, 125, 50, 0.12);
        border: 2px solid rgba(46, 125, 50, 0.35);
        text-align: center;
        margin-top: 10px;
    }
    .total-title { font-size: 20px; }
    .total-money { font-size: 42px; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)

header_left, header_right = st.columns([1, 5], vertical_alignment="center")

with header_left:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=115)
    else:
        st.markdown("## 🌾")

with header_right:
    st.title("🌾 Ta App")
    st.caption("วัดพื้นที่นา • ลากขอบเขตอิสระ • ปรับจุดได้ • คำนวณค่าไถและค่าปั่น")

st.divider()

c1, c2 = st.columns(2)

with c1:
    owner = st.text_input(
        "👤 ชื่อเจ้าของนา",
        placeholder="เช่น นายสมชาย ใจดี",
        key="owner",
    )

with c2:
    note = st.text_input(
        "📝 บันทึก / หมายเหตุ",
        placeholder="เช่น นาหลังบ้าน นัดทำงานวันจันทร์",
        key="note",
    )

st.subheader("🗺️ วัดพื้นที่แปลงนา")

st.info(
    "เมื่อเปิดแอป ระบบจะขอตำแหน่ง GPS และพยายามซูมเข้าใกล้ตำแหน่งปัจจุบัน "
    "ที่สุดที่แผนที่รองรับ • ใช้เครื่องมือรูปหลายเหลี่ยมเพื่อวาดขอบเขต "
    "• หลังวาดแล้วใช้เครื่องมือแก้ไขเพื่อเลื่อนจุดให้ตรงแนวแปลง"
)

m = folium.Map(
    location=DEFAULT_CENTER,
    zoom_start=18,
    max_zoom=19,
    control_scale=True,
    tiles="OpenStreetMap",
    prefer_canvas=True,
)

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="ภาพดาวเทียม",
    overlay=False,
    control=True,
    max_zoom=19,
).add_to(m)

LocateControl(
    auto_start=True,
    flyTo=True,
    keepCurrentZoomLevel=False,
    initialZoomLevel=19,
    showCompass=True,
    position="topleft",
    strings={
        "title": "ไปตำแหน่งปัจจุบัน",
        "popup": "ตำแหน่งปัจจุบัน",
    },
).add_to(m)

Draw(
    export=False,
    position="topleft",
    show_geometry_on_click=False,
    draw_options={
        "polyline": False,
        "polygon": {
            "allowIntersection": False,
            "showArea": False,
            "shapeOptions": {
                "color": "#16a34a",
                "weight": 4,
                "fillOpacity": 0.20,
            },
        },
        "rectangle": False,
        "circle": False,
        "circlemarker": False,
        "marker": False,
    },
    edit_options={
        "edit": True,
        "remove": True,
    },
).add_to(m)

map_data = st_folium(
    m,
    width=None,
    height=600,
    returned_objects=[
        "all_drawings",
        "last_active_drawing",
        "last_clicked",
        "center",
        "zoom",
    ],
    key=f"farm_map_{st.session_state.map_key}",
)

drawings = map_data.get("all_drawings")

if drawings:
    polygon = None

    for feature in drawings:
        geometry = feature.get("geometry", {})
        if geometry.get("type") == "Polygon":
            polygon = geometry
            break

    if polygon:
        coordinates = polygon.get("coordinates", [])

        if coordinates and coordinates[0]:
            ring = coordinates[0]
            new_points = [
                (float(coord[1]), float(coord[0]))
                for coord in ring[:-1]
            ]

            if len(new_points) >= 3:
                st.session_state.points = new_points

st.markdown("### 🛠️ จัดการพื้นที่")

b1, b2, b3 = st.columns(3)

with b1:
    if st.button("🗑️ ล้างพื้นที่", use_container_width=True):
        st.session_state.points = []
        st.session_state.map_key += 1
        st.rerun()

with b2:
    if st.button("📍 ตัวอย่างพื้นที่", use_container_width=True):
        st.session_state.points = [
            (13.75630, 100.50180),
            (13.75630, 100.50300),
            (13.75530, 100.50300),
            (13.75530, 100.50180),
        ]
        st.session_state.map_key += 1
        st.rerun()

with b3:
    if st.button("🔄 รีเฟรชแผนที่", use_container_width=True):
        st.session_state.map_key += 1
        st.rerun()

area_m2 = polygon_area_m2(st.session_state.points)
rai, ngan, wa, remain_m2 = thai_area(area_m2)

plow_cost = (area_m2 / RAI_M2) * PLOW_RATE
mill_cost = (area_m2 / RAI_M2) * MILL_RATE
total_cost = plow_cost + mill_cost

st.divider()
st.subheader("📐 ผลการวัดพื้นที่")

if len(st.session_state.points) < 3:
    st.warning(
        "ยังไม่มีพื้นที่ที่วัดได้ กรุณาใช้เครื่องมือรูปหลายเหลี่ยมบนแผนที่ "
        "แตะจุดรอบแปลงนาให้ครบ แล้วแตะจุดแรกเพื่อปิดพื้นที่"
    )
else:
    a1, a2, a3, a4 = st.columns(4)

    with a1:
        st.metric("พื้นที่รวม", f"{area_m2:,.2f} ตร.ม.")
    with a2:
        st.metric("ไร่", f"{rai:,}")
    with a3:
        st.metric("งาน", f"{ngan:,}")
    with a4:
        st.metric("ตารางวา", f"{wa:,}")

    st.success(
        f"รวม {rai} ไร่ {ngan} งาน {wa} ตารางวา "
        f"เหลือ {remain_m2:.2f} ตร.ม."
    )

    st.divider()
    st.subheader("💰 ยอดค่าใช้จ่าย")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric("1. ค่าไถนา", f"{money(plow_cost)} บาท")
        st.caption("อัตรา 250 บาท / ไร่")

    with s2:
        st.metric("2. ค่าปั่นดิน", f"{money(mill_cost)} บาท")
        st.caption("อัตรา 350 บาท / ไร่")

    with s3:
        st.metric("3. รวมไถนา + ปั่นดิน", f"{money(total_cost)} บาท")

    st.markdown(
        f"""
        <div class="total-box">
            <div class="total-title">💰 ยอดที่ต้องจ่ายทั้งหมด</div>
            <div class="total-money">{money(total_cost)} บาท</div>
            <div>ไถนา {money(plow_cost)} + ปั่นดิน {money(mill_cost)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("💾 บันทึกแปลงนี้", type="primary", use_container_width=True):
        record = {
            "เจ้าของนา": owner or "-",
            "หมายเหตุ": note or "-",
            "พื้นที่_ตรม": round(area_m2, 2),
            "ไร่": rai,
            "งาน": ngan,
            "ตารางวา": wa,
            "เหลือ_ตรม": round(remain_m2, 2),
            "ค่าไถนา": round(plow_cost, 2),
            "ค่าปั่นดิน": round(mill_cost, 2),
            "รวม": round(total_cost, 2),
            "หมุด": [
                [round(float(lat), 7), round(float(lon), 7)]
                for lat, lon in st.session_state.points
            ],
        }

        st.session_state.saved_plots.append(record)

        if save_saved_plots(st.session_state.saved_plots):
            st.success("บันทึกแปลงนาเรียบร้อยแล้วครับ 🌾")
        else:
            st.warning("บันทึกไว้ในหน่วยความจำของแอปแล้ว แต่เขียนไฟล์ไม่ได้")

if st.session_state.saved_plots:
    st.divider()
    st.subheader("📋 ข้อมูลแปลงที่บันทึกไว้")

    for index, item in enumerate(reversed(st.session_state.saved_plots), 1):
        number = len(st.session_state.saved_plots) - index + 1

        with st.expander(
            f"แปลงที่ {number} • {item.get('เจ้าของนา', '-')} • "
            f"{money(item.get('รวม', 0))} บาท"
        ):
            st.write(f"**เจ้าของนา:** {item.get('เจ้าของนา', '-')}")
            st.write(f"**หมายเหตุ:** {item.get('หมายเหตุ', '-')}")
            st.write(
                f"**พื้นที่:** {item.get('ไร่', 0)} ไร่ "
                f"{item.get('งาน', 0)} งาน "
                f"{item.get('ตารางวา', 0)} ตารางวา "
                f"เหลือ {item.get('เหลือ_ตรม', 0):,.2f} ตร.ม."
            )
            st.write(f"**ค่าไถนา:** {money(item.get('ค่าไถนา', 0))} บาท")
            st.write(f"**ค่าปั่นดิน:** {money(item.get('ค่าปั่นดิน', 0))} บาท")
            st.write(f"**รวม:** {money(item.get('รวม', 0))} บาท")

st.divider()
st.caption(
    "Ta App • พื้นที่คำนวณจากพิกัด GPS โดยประมาณ "
    "ควรตรวจสอบแนวเขตจริงก่อนใช้เป็นข้อมูลทางกฎหมาย"
)
