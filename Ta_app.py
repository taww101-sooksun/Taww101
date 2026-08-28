import math
import io
import json
from datetime import datetime

import folium
import requests
import streamlit as st
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from PIL import Image, ImageDraw


st.set_page_config(
    page_title="Ta App - วัดพื้นที่นา",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
    html, body, [class*="css"], .stApp,
    button, input, textarea, select {
        font-family: Tahoma, Arial, sans-serif !important;
    }

    .total-box {
        padding: 24px;
        border-radius: 18px;
        background: rgba(46, 125, 50, 0.12);
        border: 2px solid rgba(46, 125, 50, 0.35);
        text-align: center;
        margin-top: 10px;
    }

    .total-title {
        font-size: 20px;
    }

    .total-money {
        font-size: 42px;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ตั้งค่าราคา
# =========================================================

PLOW_RATE = 250.0
MILL_RATE = 350.0

RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

DEFAULT_LAT = 13.7563
DEFAULT_LON = 100.5018


# =========================================================
# ฟังก์ชันแปลงพื้นที่
# =========================================================

def thai_area(m2):
    m2 = max(float(m2), 0.0)

    rai = int(m2 // RAI_M2)

    remain = m2 - rai * RAI_M2

    ngan = int(remain // NGAN_M2)

    remain -= ngan * NGAN_M2

    wa = int(remain // WA_M2)

    remain -= wa * WA_M2

    return rai, ngan, wa, remain


# =========================================================
# คำนวณพื้นที่จากพิกัด GPS
# =========================================================

def polygon_area_m2(points):

    if len(points) < 3:
        return 0.0

    average_lat = sum(
        p[0] for p in points
    ) / len(points)

    lat_radians = math.radians(
        average_lat
    )

    earth_radius = 6378137.0

    xy = []

    for lat, lon in points:

        x = (
            math.radians(lon)
            * earth_radius
            * math.cos(lat_radians)
        )

        y = (
            math.radians(lat)
            * earth_radius
        )

        xy.append((x, y))

    area = 0.0

    for i in range(len(xy)):

        x1, y1 = xy[i]

        x2, y2 = xy[
            (i + 1) % len(xy)
        ]

        area += (
            x1 * y2
            - x2 * y1
        )

    return abs(area) / 2.0


# =========================================================
# เงิน
# =========================================================

def money(value):
    return f"{value:,.2f}"


# =========================================================
# อ่านรูปหลายเหลี่ยมจาก Draw
# =========================================================

def normalize_points_from_drawings(drawings):

    if not drawings:
        return []

    for feature in reversed(drawings):

        geometry = feature.get(
            "geometry",
            {}
        )

        if geometry.get(
            "type"
        ) != "Polygon":
            continue

        coords = geometry.get(
            "coordinates",
            []
        )

        if not coords:
            continue

        ring = coords[0]

        points = []

        for pair in ring:

            if len(pair) >= 2:

                lon = pair[0]
                lat = pair[1]

                points.append(
                    (
                        float(lat),
                        float(lon)
                    )
                )

        if (
            len(points) >= 2
            and points[0] == points[-1]
        ):
            points.pop()

        if len(points) >= 3:
            return points

    return []


# =========================================================
# สร้างภาพดาวเทียมพร้อมเส้นแปลงนา
# =========================================================

def make_satellite_snapshot(
    points,
    width=900,
    height=600
):

    if len(points) < 3:
        return None

    lats = [
        p[0]
        for p in points
    ]

    lons = [
        p[1]
        for p in points
    ]

    lat_pad = max(
        (max(lats) - min(lats))
        * 0.18,
        0.00025
    )

    lon_pad = max(
        (max(lons) - min(lons))
        * 0.18,
        0.00025
    )

    south = min(lats) - lat_pad
    north = max(lats) + lat_pad

    west = min(lons) - lon_pad
    east = max(lons) + lon_pad

    url = (
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/"
        "World_Imagery/MapServer/export"
    )

    params = {
        "bbox": (
            f"{west},{south},"
            f"{east},{north}"
        ),
        "bboxSR": "4326",
        "imageSR": "4326",
        "size": f"{width},{height}",
        "format": "png",
        "f": "image",
        "transparent": "false",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        image = Image.open(
            io.BytesIO(
                response.content
            )
        ).convert("RGB")

        draw = ImageDraw.Draw(
            image
        )

        pixel_points = []

        for lat, lon in points:

            x = (
                (lon - west)
                / (east - west)
                * (width - 1)
            )

            y = (
                (north - lat)
                / (north - south)
                * (height - 1)
            )

            pixel_points.append(
                (
                    int(x),
                    int(y)
                )
            )

        if len(pixel_points) >= 3:

            draw.line(
                pixel_points
                + [pixel_points[0]],
                fill=(0, 190, 80),
                width=7
            )

            draw.polygon(
                pixel_points,
                outline=(0, 190, 80),
                width=7
            )

        return image

    except Exception:

        return None


# =========================================================
# แปลงภาพเป็น bytes
# =========================================================

def image_to_bytes(image):

    if image is None:
        return None

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


# =========================================================
# Session State
# =========================================================

if "points" not in st.session_state:
    st.session_state.points = []


if "saved_plots" not in st.session_state:
    st.session_state.saved_plots = []


if "lat" not in st.session_state:
    st.session_state.lat = DEFAULT_LAT


if "lon" not in st.session_state:
    st.session_state.lon = DEFAULT_LON


if "location_loaded" not in st.session_state:
    st.session_state.location_loaded = False


# =========================================================
# หัวแอป
# =========================================================

st.title("🌾 Ta App")

st.caption(
    "วัดพื้นที่นา • "
    "ลาก/แก้ไขแนวเขต • "
    "คำนวณค่าไถนาและปั่นดิน • "
    "บันทึกข้อมูลพร้อมภาพแปลง"
)


# =========================================================
# GPS มือถือ
# =========================================================

gps = streamlit_geolocation()


if (
    gps
    and isinstance(gps, dict)
    and gps.get("latitude") is not None
):

    new_lat = float(
        gps["latitude"]
    )

    new_lon = float(
        gps["longitude"]
    )

    if (
        not st.session_state.location_loaded
        or abs(
            st.session_state.lat
            - new_lat
        ) > 0.000001
        or abs(
            st.session_state.lon
            - new_lon
        ) > 0.000001
    ):

        st.session_state.lat = new_lat

        st.session_state.lon = new_lon

        st.session_state.location_loaded = True

        st.rerun()


if (
    gps
    and isinstance(gps, dict)
    and gps.get("error")
):

    st.warning(
        "เบราว์เซอร์ไม่อนุญาตให้ใช้ GPS "
        "หรือหาตำแหน่งไม่ได้ "
        "กรุณาอนุญาตตำแหน่งให้เว็บไซต์"
    )


# =========================================================
# ข้อมูลเจ้าของ
# =========================================================

c1, c2 = st.columns(2)


with c1:

    owner = st.text_input(
        "👤 ชื่อเจ้าของนา",
        placeholder="เช่น แม่ใหญ่บุญมี",
        key="owner",
    )


with c2:

    note = st.text_input(
        "📝 บันทึก / หมายเหตุ",
        placeholder="เช่น ไถนา + ปั่นดิน",
        key="note",
    )


# =========================================================
# แผนที่
# =========================================================

st.subheader(
    "🗺️ วัดพื้นที่นา"
)


st.info(
    "📍 กดปุ่ม GPS เพื่อใช้ตำแหน่งปัจจุบัน • "
    "เลือกเครื่องมือรูปหลายเหลี่ยมบนแผนที่ "
    "แล้วลากจุดรอบแปลงนา • "
    "สามารถลากจุดเพื่อแก้แนวเขตได้"
)


m = folium.Map(
    location=[
        st.session_state.lat,
        st.session_state.lon
    ],
    zoom_start=19,
    control_scale=True,
    tiles=None,
)


# =========================================================
# แผนที่ถนน
# =========================================================

folium.TileLayer(
    tiles="OpenStreetMap",
    name="แผนที่ถนน",
    control=True,
).add_to(m)


# =========================================================
# ภาพดาวเทียม
# =========================================================

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/"
        "World_Imagery/MapServer/"
        "tile/{z}/{y}/{x}"
    ),
    attr="Tiles © Esri",
    name="ภาพดาวเทียม",
    overlay=False,
    control=True,
).add_to(m)


folium.LayerControl(
    collapsed=False
).add_to(m)


# =========================================================
# ปุ่มตำแหน่งปัจจุบันบนแผนที่
# =========================================================

LocateControl(
    auto_start=False,
    flyTo=True,
    keepCurrentZoomLevel=False,
    showCompass=True,
    strings={
        "title": "ตำแหน่งปัจจุบัน"
    },
).add_to(m)


# =========================================================
# แสดงแปลงเดิม
# =========================================================

if len(
    st.session_state.points
) >= 3:

    folium.Polygon(
        locations=st.session_state.points,
        color="#00b950",
        weight=5,
        fill=True,
        fill_color="#00b950",
        fill_opacity=0.18,
        tooltip="แปลงนาที่วัด",
    ).add_to(m)


# =========================================================
# เครื่องมือวาด
# =========================================================

draw_options = {

    "polyline": False,

    "rectangle": False,

    "circle": False,

    "circlemarker": False,

    "marker": False,

    "polygon": {
        "allowIntersection": False,
        "showArea": True,
        "shapeOptions": {
            "color": "#00b950",
            "weight": 4,
            "fillColor": "#00b950",
            "fillOpacity": 0.18,
        },
    },
}


edit_options = {
    "edit": True,
    "remove": True,
}


Draw(
    export=False,
    position="topleft",
    draw_options=draw_options,
    edit_options=edit_options,
).add_to(m)


# =========================================================
# แสดงแผนที่
# =========================================================

map_data = st_folium(
    m,
    width=None,
    height=650,
    returned_objects=[
        "all_drawings",
        "last_active_drawing",
    ],
    key="ta_map",
)


# =========================================================
# รับพื้นที่จากการวาด
# =========================================================

drawings = None

if map_data:

    drawings = map_data.get(
        "all_drawings"
    )


new_points = (
    normalize_points_from_drawings(
        drawings
    )
)


if drawings is not None:

    old_points = (
        st.session_state.points
    )

    if new_points != old_points:

        st.session_state.points = (
            new_points
        )

        st.rerun()


# =========================================================
# ปุ่มจัดการ
# =========================================================

b1, b2, b3 = st.columns(3)


with b1:

    if st.button(
        "🗑️ ล้างแปลงที่กำลังวัด",
        use_container_width=True
    ):

        st.session_state.points = []

        st.rerun()


with b2:

    if st.button(
        "📍 ใช้จุดตัวอย่าง",
        use_container_width=True
    ):

        lat = st.session_state.lat
        lon = st.session_state.lon

        step = 0.001

        st.session_state.points = [

            (
                lat + step,
                lon - step
            ),

            (
                lat + step,
                lon + step
            ),

            (
                lat - step,
                lon + step
            ),

            (
                lat - step,
                lon - step
            ),

        ]

        st.rerun()


with b3:

    if st.button(
        "🔄 รีเฟรชแผนที่",
        use_container_width=True
    ):

        st.rerun()


# =========================================================
# คำนวณ
# =========================================================

area_m2 = polygon_area_m2(
    st.session_state.points
)


rai, ngan, wa, remain_m2 = (
    thai_area(area_m2)
)


# =========================================================
# คำนวณราคา
# =========================================================

plow_cost = (
    area_m2 / RAI_M2
) * PLOW_RATE


mill_cost = (
    area_m2 / RAI_M2
) * MILL_RATE


total_cost = (
    plow_cost
    + mill_cost
)


# =========================================================
# ผลการวัด
# =========================================================

st.divider()

st.subheader(
    "📐 ผลการวัด"
)


if len(
    st.session_state.points
) < 3:

    st.warning(
        "กรุณาวาดขอบเขตแปลงนา "
        "อย่างน้อย 3 จุด"
    )


else:

    r1, r2, r3, r4 = (
        st.columns(4)
    )


    r1.metric(
        "พื้นที่รวม",
        f"{area_m2:,.2f} ตร.ม."
    )


    r2.metric(
        "ไร่",
        f"{rai:,}"
    )


    r3.metric(
        "งาน",
        f"{ngan:,}"
    )


    r4.metric(
        "ตารางวา",
        f"{wa:,}"
    )


    st.success(
        f"พื้นที่ประมาณ "
        f"**{rai} ไร่ "
        f"{ngan} งาน "
        f"{wa} ตารางวา "
        f"{remain_m2:.2f} ตร.ม.**"
    )


    # =====================================================
    # ราคา
    # =====================================================

    st.subheader(
        "💰 ยอดค่าใช้จ่าย"
    )


    p1, p2, p3 = (
        st.columns(3)
    )


    p1.metric(
        "1️⃣ ค่าไถนา",
        f"{money(plow_cost)} บาท"
    )


    p2.metric(
        "2️⃣ ค่าปั่นดิน",
        f"{money(mill_cost)} บาท"
    )


    p3.metric(
        "3️⃣ รวมไถนา + ปั่นดิน",
        f"{money(total_cost)} บาท"
    )


    st.caption(
        f"อัตราที่กำหนด: "
        f"ไถนา {money(PLOW_RATE)} บาท/ไร่ • "
        f"ปั่นดิน {money(MILL_RATE)} บาท/ไร่"
    )


    st.markdown(
        f"""
        <div class="total-box">

            <div class="total-title">
                💰 ยอดรวมที่ต้องจ่าย
            </div>

            <div class="total-money">
                {money(total_cost)} บาท
            </div>

            <div>
                ไถนา {money(plow_cost)}
                +
                ปั่นดิน {money(mill_cost)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # =====================================================
    # บันทึก
    # =====================================================

    st.subheader(
        "💾 บันทึกแปลงนา"
    )


    if st.button(
        "💾 บันทึกแปลงนี้ พร้อมภาพพื้นที่",
        type="primary",
        use_container_width=True,
    ):

        snapshot = (
            make_satellite_snapshot(
                st.session_state.points
            )
        )


        snapshot_bytes = (
            image_to_bytes(snapshot)
        )


        record = {

            "ลำดับ":
                len(
                    st.session_state.saved_plots
                ) + 1,

            "วันที่บันทึก":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "เจ้าของนา":
                owner.strip()
                or "-",

            "หมายเหตุ":
                note.strip()
                or "-",

            "พื้นที่_ตรม":
                round(
                    area_m2,
                    2
                ),

            "ไร่":
                rai,

            "งาน":
                ngan,

            "ตารางวา":
                wa,

            "เหลือ_ตรม":
                round(
                    remain_m2,
                    2
                ),

            "ค่าไถนา":
                round(
                    plow_cost,
                    2
                ),

            "ค่าปั่นดิน":
                round(
                    mill_cost,
                    2
                ),

            "รวม":
                round(
                    total_cost,
                    2
                ),

            "พิกัด":
                [
                    [
                        round(
                            lat,
                            7
                        ),
                        round(
                            lon,
                            7
                        )
                    ]
                    for lat, lon
                    in st.session_state.points
                ],

            "ภาพพื้นที่":
                snapshot_bytes,
        }


        st.session_state.saved_plots.append(
            record
        )


        st.success(
            "บันทึกข้อมูลแปลงนา "
            "เรียบร้อยแล้วครับ 🌾"
        )


# =========================================================
# รายการบันทึก
# =========================================================

st.divider()

st.subheader(
    "📋 ข้อมูลแปลงที่บันทึกไว้"
)


if not st.session_state.saved_plots:

    st.info(
        "ยังไม่มีข้อมูลที่บันทึก"
    )


else:

    for idx, item in enumerate(
        reversed(
            st.session_state.saved_plots
        ),
        1
    ):

        title = (
            f"แปลงที่ {item['ลำดับ']} • "
            f"{item['เจ้าของนา']} • "
            f"{money(item['รวม'])} บาท"
        )


        with st.expander(
            title
        ):

            left, right = (
                st.columns(
                    [1.15, 1]
                )
            )


            with left:

                image_bytes = (
                    item.get(
                        "ภาพพื้นที่"
                    )
                )


                if image_bytes:

                    st.image(
                        image_bytes,
                        caption=(
                            "ภาพดาวเทียม "
                            "พร้อมขอบเขตแปลง"
                        )
                    )

                else:

                    st.info(
                        "ไม่สามารถสร้าง "
                        "ภาพดาวเทียมของ "
                        "รายการนี้ได้"
                    )


            with right:

                st.write(
                    f"**เจ้าของนา:** "
                    f"{item['เจ้าของนา']}"
                )


                st.write(
                    f"**วันที่บันทึก:** "
                    f"{item['วันที่บันทึก']}"
                )


                st.write(
                    f"**หมายเหตุ:** "
                    f"{item['หมายเหตุ']}"
                )


                st.write(
                    f"**พื้นที่:** "
                    f"{item['ไร่']} ไร่ "
                    f"{item['งาน']} งาน "
                    f"{item['ตารางวา']} ตารางวา "
                    f"{item['เหลือ_ตรม']:.2f} ตร.ม."
   
