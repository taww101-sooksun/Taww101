import streamlit as st
import folium
from folium.plugins import Draw, Fullscreen, LocateControl
from streamlit_folium import st_folium

import math
import json
import os
import io
from datetime import datetime

# =========================================================
# ตั้งค่าหน้าเว็บ
# =========================================================
st.set_page_config(
    page_title="อยู่นิ่งๆไม่เจ็บตัว",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# ค่าบริการ
# =========================================================
PLOW_RATE = 250.0       # ไถนา / ไร่
TILL_RATE = 350.0       # ปั่นดิน / ไร่

# =========================================================
# ไฟล์บันทึก
# =========================================================
DATA_FILE = "rice_fields.json"

# =========================================================
# CSS
# =========================================================
st.markdown(
    """
    <style>

    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .app-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
    }

    .app-logo {
        width: 75px;
        height: 75px;
        object-fit: contain;
        border-radius: 15px;
    }

    .app-title {
        font-size: 30px;
        font-weight: 900;
        line-height: 1.1;
    }

    .app-subtitle {
        font-size: 15px;
        opacity: 0.7;
        margin-top: 5px;
    }

    .big-card {
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        border: 2px solid rgba(0,0,0,0.08);
    }

    .area-label {
        font-size: 17px;
        font-weight: 700;
    }

    .area-value {
        font-size: 30px;
        font-weight: 950;
        margin-top: 5px;
    }

    .money-label {
        font-size: 17px;
        font-weight: 700;
    }

    .money-value {
        font-size: 34px;
        font-weight: 950;
        margin-top: 5px;
    }

    .rate-box {
        padding: 12px;
        border-radius: 14px;
        border: 1px solid rgba(0,0,0,0.10);
        margin-bottom: 8px;
    }

    .warning-box {
        padding: 12px;
        border-radius: 12px;
        background: #fff3cd;
        border: 1px solid #ffecb5;
        color: #664d03;
    }

    @media(max-width:700px) {
        .app-title {
            font-size: 24px;
        }

        .area-value {
            font-size: 23px;
        }

        .money-value {
            font-size: 28px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Session State
# =========================================================
if "saved_fields" not in st.session_state:
    st.session_state.saved_fields = []

if "last_points" not in st.session_state:
    st.session_state.last_points = []

if "last_gps" not in st.session_state:
    st.session_state.last_gps = None

if "field_name" not in st.session_state:
    st.session_state.field_name = ""

if "owner" not in st.session_state:
    st.session_state.owner = ""

if "note" not in st.session_state:
    st.session_state.note = ""

if "plow_enabled" not in st.session_state:
    st.session_state.plow_enabled = True

if "till_enabled" not in st.session_state:
    st.session_state.till_enabled = True


# =========================================================
# ฟังก์ชันพื้นที่
# =========================================================
def polygon_area_m2(points):
    """
    คำนวณพื้นที่ polygon บนโลก
    points = [(lat, lon), ...]
    """

    if len(points) < 3:
        return 0.0

    # ใช้ Local Equirectangular Projection
    earth_radius = 6378137.0

    avg_lat = sum(p[0] for p in points) / len(points)
    avg_lat_rad = math.radians(avg_lat)

    xy = []

    for lat, lon in points:
        x = (
            earth_radius
            * math.radians(lon)
            * math.cos(avg_lat_rad)
        )

        y = earth_radius * math.radians(lat)

        xy.append((x, y))

    area = 0.0

    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]

        area += (x1 * y2) - (x2 * y1)

    return abs(area) / 2.0


def convert_thai_area(area_m2):
    """
    1 ไร่ = 1600 ตร.ม.
    1 งาน = 400 ตร.ม.
    1 ตารางวา = 4 ตร.ม.
    """

    rai = int(area_m2 // 1600)

    remain = area_m2 - (rai * 1600)

    ngan = int(remain // 400)

    remain = remain - (ngan * 400)

    square_wah = remain / 4

    return rai, ngan, square_wah


def area_to_rai(area_m2):
    return area_m2 / 1600.0


def calculate_money(area_m2, plow, till):

    rai = area_to_rai(area_m2)

    plow_money = 0.0
    till_money = 0.0

    if plow:
        plow_money = rai * PLOW_RATE

    if till:
        till_money = rai * TILL_RATE

    total = plow_money + till_money

    return rai, plow_money, till_money, total


def format_area(area_m2):

    rai, ngan, wah = convert_thai_area(area_m2)

    return (
        f"{rai:,} ไร่ "
        f"{ngan:,} งาน "
        f"{wah:,.2f} ตร.วา"
    )


# =========================================================
# JSON บันทึกข้อมูล
# =========================================================
def load_fields():

    if not os.path.exists(DATA_FILE):
        return []

    try:

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:

        return []


def save_fields(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# โหลดข้อมูลเก่า
if not st.session_state.saved_fields:

    st.session_state.saved_fields = load_fields()


# =========================================================
# HEADER + LOGO
# =========================================================
logo_path = "logo1.png"

if os.path.exists(logo_path):

    st.markdown(
        """
        <div class="app-header">
            <img class="app-logo"
                 src="logo1.png">
            <div>
                <div class="app-title">
                    🌾 อยู่นิ่งๆไม่เจ็บตัว
                </div>
                <div class="app-subtitle">
                    ระบบวัดพื้นที่นา • GPS • คำนวณค่าจ้าง
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <div class="app-title">
            🌾 อยู่นิ่งๆไม่เจ็บตัว
        </div>

        <div class="app-subtitle">
            ระบบวัดพื้นที่นา • GPS • คำนวณค่าจ้าง
        </div>
        """,
        unsafe_allow_html=True
    )

    st.warning(
        "ไม่พบ logo1.png — กรุณาวาง logo1.png "
        "ไว้ในโฟลเดอร์เดียวกับ app.py"
    )


# =========================================================
# ข้อมูลเจ้าของนา
# =========================================================
st.subheader("👤 ข้อมูลแปลงนา")

c1, c2 = st.columns(2)

with c1:

    owner = st.text_input(
        "ชื่อเจ้าของนา / ผู้ว่าจ้าง",
        value=st.session_state.owner,
        placeholder="เช่น นายสมชาย",
    )

    field_name = st.text_input(
        "ชื่อแปลงนา / สถานที่",
        value=st.session_state.field_name,
        placeholder="เช่น แปลงนาบ้านเหนือ",
    )

with c2:

    note = st.text_area(
        "📝 หมายเหตุ",
        value=st.session_state.note,
        placeholder="เช่น ไถ 1 รอบ ปั่น 1 รอบ",
        height=105,
    )


st.session_state.owner = owner
st.session_state.field_name = field_name
st.session_state.note = note


# =========================================================
# เลือกบริการ
# =========================================================
st.subheader("💰 รายการคิดค่าจ้าง")

r1, r2 = st.columns(2)

with r1:

    plow_enabled = st.checkbox(
        f"🚜 ไถนา — {PLOW_RATE:,.0f} บาท/ไร่",
        value=st.session_state.plow_enabled,
    )

with r2:

    till_enabled = st.checkbox(
        f"⚙️ ปั่นดิน — {TILL_RATE:,.0f} บาท/ไร่",
        value=st.session_state.till_enabled,
    )

st.session_state.plow_enabled = plow_enabled
st.session_state.till_enabled = till_enabled


# =========================================================
# ตำแหน่งเริ่มต้นแผนที่
# =========================================================
DEFAULT_LAT = 15.8700
DEFAULT_LON = 100.9925

if st.session_state.last_gps:

    map_lat = st.session_state.last_gps[0]
    map_lon = st.session_state.last_gps[1]

elif st.session_state.last_points:

    map_lat = sum(p[0] for p in st.session_state.last_points) / len(
        st.session_state.last_points
    )

    map_lon = sum(p[1] for p in st.session_state.last_points) / len(
        st.session_state.last_points
    )

else:

    map_lat = DEFAULT_LAT
    map_lon = DEFAULT_LON


# =========================================================
# สร้างแผนที่
# =========================================================
m = folium.Map(
    location=[map_lat, map_lon],
    zoom_start=17,
    control_scale=True,
    tiles="OpenStreetMap",
)

# ปุ่มเต็มจอ
Fullscreen(
    position="topright"
).add_to(m)

# ปุ่ม GPS
try:

    LocateControl(
        auto_start=False,
        flyTo=True,
        keepCurrentZoomLevel=True,
        showPopup=True,
        strings={
            "title": "หาตำแหน่ง GPS ของฉัน"
        },
    ).add_to(m)

except Exception:

    pass


# =========================================================
# วาด polygon
# =========================================================
Draw(
    export=False,
    position="topleft",
    draw_options={
        "polyline": False,
        "polygon": {
            "allowIntersection": False,
            "showArea": True,
            "shapeOptions": {
                "color": "#e91e63",
                "weight": 4,
                "fillColor": "#ffeb3b",
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


# =========================================================
# ถ้ามี polygon เดิม แสดงบนแผนที่
# =========================================================
if len(st.session_state.last_points) >= 3:

    folium.Polygon(
        locations=st.session_state.last_points,
        color="#e91e63",
        weight=4,
        fill=True,
        fill_color="#ffeb3b",
        fill_opacity=0.20,
        tooltip="ลากจุดเพื่อปรับแนวคันนา",
    ).add_to(m)


# =========================================================
# แสดง GPS ล่าสุด
# =========================================================
if st.session_state.last_gps:

    folium.Marker(
        location=st.session_state.last_gps,
        popup="📍 ตำแหน่ง GPS ล่าสุด",
        tooltip="GPS ปัจจุบัน",
        icon=folium.Icon(
            color="blue",
            icon="location-arrow",
            prefix="fa",
        ),
    ).add_to(m)


# =========================================================
# แผนที่
# =========================================================
st.subheader("🗺️ แผนที่วัดพื้นที่นา")

st.info(
    "📌 กดเครื่องมือรูปหลายเหลี่ยม แล้วแตะจุดรอบแปลงนา "
    "ให้ครบ จากนั้นกดปิดรูปแปลง • สามารถเข้าโหมดแก้ไขแล้ว "
    "ลากจุดไปตรงคันนาได้ • ใช้ปุ่ม + / − หรือสองนิ้วเพื่อซูม"
)

map_data = st_folium(
    m,
    width=None,
    height=600,
    returned_objects=[
        "all_drawings",
        "last_active_drawing",
        "last_clicked",
    ],
    key="rice_map",
)


# =========================================================
# อ่าน polygon จากแผนที่
# =========================================================
drawings = map_data.get("all_drawings", [])

new_points = None

if drawings:

    # เอารูปล่าสุดที่เป็น Polygon
    for drawing in reversed(drawings):

        if drawing.get("geometry", {}).get("type") == "Polygon":

            coords = drawing["geometry"]["coordinates"][0]

            converted = []

            for point in coords:

                lon = point[0]
                lat = point[1]

                converted.append(
                    [lat, lon]
                )

            # จุดสุดท้ายมักซ้ำกับจุดแรก
            if len(converted) > 1:

                if converted[0] == converted[-1]:

                    converted = converted[:-1]

            new_points = converted

            break


# =========================================================
# ถ้าได้ polygon ใหม่
# =========================================================
if new_points and len(new_points) >= 3:

    if new_points != st.session_state.last_points:

        st.session_state.last_points = new_points

        st.rerun()


# =========================================================
# ปุ่มล้างแปลง
# =========================================================
if st.button(
    "🗑️ ล้างแปลงนี้ เริ่มวัดใหม่",
    use_container_width=True
):

    st.session_state.last_points = []

    st.rerun()


# =========================================================
# พื้นที่
# =========================================================
points = st.session_state.last_points

area_m2 = polygon_area_m2(points)

rai_exact, plow_money, till_money, total_money = calculate_money(
    area_m2,
    plow_enabled,
    till_enabled,
)


# =========================================================
# ผลการวัด
# =========================================================
st.divider()

st.subheader("📐 ผลการวัดพื้นที่")


if len(points) < 3:

    st.markdown(
        """
        <div class="warning-box">
        📌 ตอนนี้ยังไม่มีพื้นที่ที่วัดได้<br>
        ให้กดเครื่องมือรูปหลายเหลี่ยมบนแผนที่
        แล้วแตะรอบคันนาอย่างน้อย 3 จุด
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    thai_area = format_area(area_m2)

    a, b = st.columns(2)

    with a:

        st.markdown(
            f"""
            <div class="big-card">

                <div class="area-label">
                    🌾 พื้นที่นา
                </div>

                <div class="area-value">
                    {thai_area}
                </div>

                <div>
                    {area_m2:,.2f} ตารางเมตร
                </div>

                <div style="opacity:.65;font-size:13px;margin-top:5px;">
                    {rai_exact:,.6f} ไร่
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with b:

        st.markdown(
            f"""
            <div class="big-card">

                <div class="money-label">
                    💰 ยอดรวมค่าจ้าง
                </div>

                <div class="money-value">
                    {total_money:,.2f} บาท
                </div>

                <div style="opacity:.65;font-size:13px;margin-top:5px;">
                    คำนวณจากพื้นที่จริง
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # -----------------------------------------------------
    # รายละเอียดเงิน
    # -----------------------------------------------------
    st.subheader("💵 รายละเอียดเงิน")

    m1, m2, m3 = st.columns(3)

    with m1:

        st.metric(
            "🚜 ค่าไถนา",
            f"{plow_money:,.2f} บาท"
        )

    with m2:

        st.metric(
            "⚙️ ค่าปั่นดิน",
            f"{till_money:,.2f} บาท"
        )

    with m3:

        st.metric(
            "💰 รวม",
            f"{total_money:,.2f} บาท"
        )


    # -----------------------------------------------------
    # สรุปเจ้าของ
    # -----------------------------------------------------
    st.markdown("---")

    s1, s2 = st.columns(2)

    with s1:

        st.write(
            f"👤 **เจ้าของนา:** "
            f"{owner if owner else 'ไม่ได้ระบุ'}"
        )

        st.write(
            f"🌾 **แปลง:** "
            f"{field_name if field_name else 'ไม่ได้ระบุ'}"
        )

    with s2:

        st.write(
            f"📝 **หมายเหตุ:** "
            f"{note if note else '-'}"
        )

        st.write(
            f"📍 **จำนวนหมุด:** "
            f"{len(points)} จุด"
        )


# =========================================================
# บันทึกแปลง
# =========================================================
st.divider()

st.subheader("💾 บันทึกข้อมูลแปลง")


if st.button(
    "💾 บันทึกแปลงนี้",
    type="primary",
    use_container_width=True
):

    if len(points) < 3:

        st.error(
            "กรุณาวัดพื้นที่ให้ครบอย่างน้อย 3 จุดก่อนครับ"
        )

    else:

        record = {

            "id": datetime.now().strftime(
                "%Y%m%d%H%M%S"
            ),

            "saved_at": datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            ),

            "owner": owner,

            "field_name": field_name,

            "note": note,

            "points": points,

            "area_m2": area_m2,

            "rai_exact": rai_exact,

            "thai_area": thai_area,

            "plow_enabled": plow_enabled,

            "till_enabled": till_enabled,

            "plow_money": plow_money,

            "till_money": till_money,

            "total_money": total_money,
        }

        st.session_state.saved_fields.append(
            record
        )

        save_fields(
            st.session_state.saved_fields
        )

        st.success(
            "✅ บันทึกข้อมูลแปลงเรียบร้อยแล้วครับ"
        )


# =========================================================
# สร้างไฟล์ JSON สำหรับแปลงปัจจุบัน
# =========================================================
if len(points) >= 3:

    current_data = {

        "เจ้าของนา": owner,

        "ชื่อแปลง": field_name,

        "หมายเหตุ": note,

        "พื้นที่ตารางเมตร": round(
            area_m2,
            2
        ),

        "พื้นที่ไทย": thai_area,

        "พื้นที่ไร่จริง": round(
            rai_exact,
            6
        ),

        "ค่าไถ": round(
            plow_money,
            2
        ),

        "ค่าปั่นดิน": round(
            till_money,
            2
        ),

        "ยอดรวม": round(
            total_money,
            2
        ),

        "พิกัด": points,
    }

    json_bytes = json.dumps(
        current_data,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    st.download_button(
        "📥 ดาวน์โหลดข้อมูลแปลงนี้ (JSON)",
        data=json_bytes,
        file_name=(
            f"แปลงนา_"
            f"{field_name if field_name else 'ไม่ระบุ'}"
            f".json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# รายการแปลงที่บันทึก
# =========================================================
st.divider()

st.subheader("📋 แปลงนาที่บันทึกไว้")


if not st.session_state.saved_fields:

    st.caption(
        "ยังไม่มีข้อมูลที่บันทึก"
    )

else:

    for index, record in enumerate(
        reversed(
            st.session_state.saved_fields
        )
    ):

        owner_text = (
            record.get("owner")
            or "ไม่ระบุเจ้าของ"
        )

        field_text = (
            record.get("field_name")
            or "ไม่ระบุชื่อแปลง"
        )

        total_text = (
            record.get("total_money", 0)
        )

        title = (
            f"🌾 {field_text} | "
            f"👤 {owner_text} | "
            f"💰 {total_text:,.2f} บาท"
        )

        with st.expander(title):

            st.write(
                "📐 พื้นที่:",
                record.get(
                    "thai_area",
                    "-"
                )
            )

            st.write(
                "📏 ตารางเมตร:",
                f"{record.get('area_m2', 0):,.2f}"
            )

            st.write(
                "🚜 ค่าไถ:",
               
