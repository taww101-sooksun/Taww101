import math
import os
import json
from datetime import datetime
from io import BytesIO

import folium
import streamlit as st
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium

try:
    import requests
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# =========================================================
# ตั้งค่าหน้าแอป
# =========================================================

st.set_page_config(
    page_title="Ta App - วัดพื้นที่นา",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CSS
# =========================================================

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

    .saved-box {
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ค่าคงที่
# =========================================================

PLOW_RATE = 250.0
MILL_RATE = 350.0

RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

DEFAULT_LAT = 13.7563
DEFAULT_LON = 100.5018

DATA_FILE = "saved_plots.json"
IMAGE_DIR = "saved_maps"


# =========================================================
# ฟังก์ชันพื้นที่
# =========================================================

def thai_area(m2):
    """
    แปลงตารางเมตรเป็น
    ไร่ / งาน / ตารางวา / ตารางเมตรที่เหลือ
    """

    m2 = max(float(m2), 0.0)

    rai = int(m2 // RAI_M2)
    remain = m2 - (rai * RAI_M2)

    ngan = int(remain // NGAN_M2)
    remain = remain - (ngan * NGAN_M2)

    wa = int(remain // WA_M2)
    remain = remain - (wa * WA_M2)

    return rai, ngan, wa, remain


def polygon_area_m2(points):
    """
    คำนวณพื้นที่จากพิกัดละติจูด/ลองจิจูด
    โดยแปลงเป็นระนาบเมตรบริเวณพื้นที่นั้น
    """

    if len(points) < 3:
        return 0.0

    average_lat = sum(
        point[0] for point in points
    ) / len(points)

    latitude_radians = math.radians(average_lat)

    earth_radius = 6378137.0

    xy = []

    for lat, lon in points:

        x = (
            math.radians(lon)
            * earth_radius
            * math.cos(latitude_radians)
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


def money(value):
    return f"{float(value):,.2f}"


def area_text(m2):
    rai, ngan, wa, remain = thai_area(m2)

    return (
        f"{rai} ไร่ "
        f"{ngan} งาน "
        f"{wa} ตารางวา "
        f"เหลือ {remain:.2f} ตร.ม."
    )


# =========================================================
# ฟังก์ชันบันทึกข้อมูล
# =========================================================

def load_saved_plots():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except Exception:
        pass

    return []


def save_saved_plots():
    try:
        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                st.session_state.saved_plots,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return True

    except Exception:
        return False


# =========================================================
# ฟังก์ชันแผนที่ดาวเทียม
# =========================================================

def latlon_to_tile(lat, lon, zoom):
    """
    แปลงพิกัด GPS เป็นตำแหน่ง tile ของ Web Mercator
    """

    lat = max(
        min(lat, 85.05112878),
        -85.05112878
    )

    n = 2.0 ** zoom

    x = (
        (lon + 180.0)
        / 360.0
        * n
    )

    lat_radians = math.radians(lat)

    y = (
        (
            1.0
            - (
                math.asinh(
                    math.tan(lat_radians)
                )
                / math.pi
            )
        )
        / 2.0
        * n
    )

    return x, y


def create_satellite_image(points, filename):
    """
    สร้างภาพดาวเทียมของแปลงนา
    แล้ววาดเส้นขอบเขตสีเขียวทับลงไป
    """

    if not PIL_AVAILABLE:
        return False

    if len(points) < 3:
        return False

    try:

        min_lat = min(
            p[0] for p in points
        )

        max_lat = max(
            p[0] for p in points
        )

        min_lon = min(
            p[1] for p in points
        )

        max_lon = max(
            p[1] for p in points
        )

        center_lat = (
            min_lat + max_lat
        ) / 2.0

        center_lon = (
            min_lon + max_lon
        ) / 2.0

        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon

        largest_span = max(
            lat_span,
            lon_span
        )

        if largest_span > 0.02:
            zoom = 14

        elif largest_span > 0.01:
            zoom = 15

        elif largest_span > 0.005:
            zoom = 16

        elif largest_span > 0.002:
            zoom = 17

        else:
            zoom = 18

        center_x, center_y = latlon_to_tile(
            center_lat,
            center_lon,
            zoom
        )

        tile_size = 256

        center_tile_x = int(
            math.floor(center_x)
        )

        center_tile_y = int(
            math.floor(center_y)
        )

        canvas = Image.new(
            "RGB",
            (
                tile_size * 3,
                tile_size * 3
            ),
            "white",
        )

        session = requests.Session()

        session.headers.update(
            {
                "User-Agent":
                    "Ta-App/1.0"
            }
        )

        for dx in range(-1, 2):

            for dy in range(-1, 2):

                tile_x = (
                    center_tile_x
                    + dx
                )

                tile_y = (
                    center_tile_y
                    + dy
                )

                url = (
                    "https://server.arcgisonline.com/"
                    "ArcGIS/rest/services/"
                    "World_Imagery/"
                    "MapServer/tile/"
                    f"{zoom}/"
                    f"{tile_y}/"
                    f"{tile_x}"
                )

                response = session.get(
                    url,
                    timeout=10
                )

                response.raise_for_status()

                tile_image = Image.open(
                    BytesIO(
                        response.content
                    )
                ).convert("RGB")

                paste_x = (
                    (dx + 1)
                    * tile_size
                )

                paste_y = (
                    (dy + 1)
                    * tile_size
                )

                canvas.paste(
                    tile_image,
                    (
                        paste_x,
                        paste_y
                    )
                )

        def gps_to_pixel(lat, lon):

            tile_x, tile_y = (
                latlon_to_tile(
                    lat,
                    lon,
                    zoom
                )
            )

            pixel_x = (
                tile_x
                - (center_tile_x - 1)
            ) * tile_size

            pixel_y = (
                tile_y
                - (center_tile_y - 1)
            ) * tile_size

            return (
                int(pixel_x),
                int(pixel_y)
            )

        image_draw = ImageDraw.Draw(
            canvas,
            "RGBA"
        )

        pixel_points = [
            gps_to_pixel(
                lat,
                lon
            )
            for lat, lon in points
        ]

        # พื้นที่สีเขียวโปร่งใส
        image_draw.polygon(
            pixel_points,
            fill=(
                0,
                180,
                70,
                65
            ),
        )

        # เส้นขอบ
        closed_points = (
            pixel_points
            + [pixel_points[0]]
        )

        image_draw.line(
            closed_points,
            fill=(
                0,
                180,
                70,
                255
            ),
            width=6,
            joint="curve",
        )

        # จุดแต่ละจุด
        for x, y in pixel_points:

            radius = 6

            image_draw.ellipse(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                ),
                fill=(
                    255,
                    255,
                    255,
                    255
                ),
                outline=(
                    0,
                    130,
                    60,
                    255
                ),
                width=2,
            )

        os.makedirs(
            IMAGE_DIR,
            exist_ok=True
        )

        canvas.save(
            filename,
            "PNG",
            optimize=True
        )

        return True

    except Exception:
        return False


def create_fallback_image(points, filename):
    """
    ถ้าดาวเทียมโหลดไม่ได้
    จะสร้างภาพแปลงนาแบบสำรอง
    """

    if not PIL_AVAILABLE:
        return False

    if len(points) < 3:
        return False

    try:

        width = 900
        height = 650
        margin = 70

        image = Image.new(
            "RGB",
            (
                width,
                height
            ),
            "white",
        )

        draw = ImageDraw.Draw(
            image,
            "RGBA"
        )

        min_lat = min(
            p[0] for p in points
        )

        max_lat = max(
            p[0] for p in points
        )

        min_lon = min(
            p[1] for p in points
        )

        max_lon = max(
            p[1] for p in points
        )

        lat_span = max(
            max_lat - min_lat,
            0.000001
        )

        lon_span = max(
            max_lon - min_lon,
            0.000001
        )

        def convert(
            lat,
            lon
        ):

            x = (
                margin
                + (
                    (lon - min_lon)
                    / lon_span
                )
                * (
                    width
                    - 2 * margin
                )
            )

            y = (
                height
                - margin
                - (
                    (lat - min_lat)
                    / lat_span
                )
                * (
                    height
                    - 2 * margin
                )
            )

            return (
                int(x),
                int(y)
            )

        polygon_points = [
            convert(lat, lon)
            for lat, lon in points
        ]

        draw.polygon(
            polygon_points,
            fill=(
                46,
                180,
                75,
                70
            ),
        )

        draw.line(
            polygon_points
            + [polygon_points[0]],
            fill=(
                0,
                150,
                70,
                255
            ),
            width=6,
        )

        for x, y in polygon_points:

            radius = 6

            draw.ellipse(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                ),
                fill="white",
                outline=(
                    0,
                    120,
                    60,
                    255
                ),
                width=2,
            )

        os.makedirs(
            IMAGE_DIR,
            exist_ok=True
        )

        image.save(
            filename,
            "PNG"
        )

        return True

    except Exception:
        return False


# =========================================================
# สร้างแผนที่
# =========================================================

def create_map(
    center_lat,
    center_lon,
    points
):

    map_object = folium.Map(
        location=[
            center_lat,
            center_lon
        ],
        zoom_start=19,
        control_scale=True,
        tiles=None,
    )

    # แผนที่ถนน
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="🗺️ แผนที่",
        control=True,
    ).add_to(map_object)

    # ดาวเทียม
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/"
            "ArcGIS/rest/services/"
            "World_Imagery/"
            "MapServer/tile/"
            "{z}/{y}/{x}"
        ),
        attr="Esri World Imagery",
        name="🛰️ ดาวเทียม",
        overlay=False,
        control=True,
    ).add_to(map_object)

    # GPS
    LocateControl(
        auto_start=True,
        flyTo=True,
        keepCurrentZoomLevel=False,
        showCompass=True,
        strings={
            "title":
                "ไปยังตำแหน่งปัจจุบัน",
            "popup":
                "ตำแหน่งปัจจุบัน",
        },
    ).add_to(map_object)

    # เครื่องมือวาด
    Draw(
        export=False,
        position="topleft",
        draw_options={
            "polyline": False,
            "rectangle": False,
            "circle": False,
            "circlemarker": False,
            "marker": False,

            "polygon": {
                "allowIntersection": False,
                "showArea": True,

                "shapeOptions": {
                    "color": "#00a651",
                    "weight": 4,
                    "fillColor": "#00a651",
                    "fillOpacity": 0.20,
                },
            },
        },

        edit_options={
            "edit": True,
            "remove": True,
        },
    ).add_to(map_object)

    # วาดพื้นที่เดิม
    if len(points) >= 3:

        folium.Polygon(
            locations=points,
            color="#00a651",
            weight=4,
            fill=True,
            fill_color="#00a651",
            fill_opacity=0.20,
            tooltip="ขอบเขตแปลงนา",
        ).add_to(map_object)

        # จุด
        for index, point in enumerate(
            points,
            start=1
        ):

            folium.CircleMarker(
                location=[
                    point[0],
                    point[1]
                ],
                radius=5,
                color="white",
                weight=2,
                fill=True,
                fill_color="#00a651",
                fill_opacity=1,
                tooltip=(
                    f"จุดที่ {index}"
                ),
            ).add_to(map_object)

    folium.LayerControl(
        collapsed=False
    ).add_to(map_object)

    return map_object


# =========================================================
# SESSION STATE
# =========================================================

if "points" not in st.session_state:
    st.session_state.points = []

if "saved_plots" not in st.session_state:
    st.session_state.saved_plots = (
        load_saved_plots()
    )

if "lat" not in st.session_state:
    st.session_state.lat = DEFAULT_LAT

if "lon" not in st.session_state:
    st.session_state.lon = DEFAULT_LON

if "map_version" not in st.session_state:
    st.session_state.map_version = 0


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns(
    [1, 5]
)

with header_left:

    if os.path.exists(
        "logo1.png"
    ):
        st.image(
            "logo1.png",
            width=110
        )
    else:
        st.markdown(
            "## 🌾"
        )

with header_right:

    st.title(
        "🌾 Ta App - วัดพื้นที่นา"
    )

    st.caption(
        "GPS • ดาวเทียม • วาดขอบเขตแปลงนา "
        "• แก้ไขจุด • คำนวณพื้นที่ "
        "• คำนวณค่าบริการ • บันทึกภาพแปลง"
    )


st.divider()


# =========================================================
# ข้อมูลเจ้าของนา
# =========================================================

info1, info2 = st.columns(2)

with info1:

    owner = st.text_input(
        "👤 ชื่อเจ้าของนา",
        placeholder="เช่น แม่ใหญ่...",
        key="owner",
    )

with info2:

    note = st.text_input(
        "📝 หมายเหตุ",
        placeholder="เช่น ไถนา + ปั่นดิน",
        key="note",
    )


# =========================================================
# แผนที่
# =========================================================

st.subheader(
    "🗺️ กำหนดขอบเขตแปลงนา"
)

st.info(
    "📍 เมื่อเปิดแอป ระบบจะพยายามหาตำแหน่งปัจจุบัน "
    "และซูมเข้าใกล้ให้ • "
    "เลือก 🛰️ ดาวเทียม • "
    "ใช้เครื่องมือรูปหลายเหลี่ยมเพื่อวาดพื้นที่ "
    "• สามารถแก้ไข/ขยับจุดให้ตรงแนวแปลงได้"
)

farm_map = create_map(
    st.session_state.lat,
    st.session_state.lon,
    st.session_state.points,
)

map_data = st_folium(
    farm_map,
    width=None,
    height=620,

    returned_objects=[
        "last_clicked",
        "center",
        "all_drawings",
    ],

    key=(
        f"farm_map_"
        f"{st.session_state.map_version}"
    ),
)


# =========================================================
# อ่านข้อมูลจากแผนที่
# =========================================================

if map_data:

    center = map_data.get(
        "center"
    )

    if center:

        try:

            st.session_state.lat = (
                float(center["lat"])
            )

            st.session_state.lon = (
                float(center["lng"])
            )

        except Exception:
            pass

    drawings = (
        map_data.get(
            "all_drawings"
        )
        or []
    )

    if drawings:

        latest_polygon = None

        for drawing in drawings:

            geometry = drawing.get(
                "geometry",
                {}
            )

            if (
                geometry.get("type")
                == "Polygon"
            ):
                latest_polygon = drawing

        if latest_polygon:

            coordinates = (
                latest_polygon[
                    "geometry"
                ][
                    "coordinates"
                ][0]
            )

            new_points = []

            for coordinate in coordinates:

                if len(coordinate) >= 2:

                    longitude = float(
                        coordinate[0]
                    )

                    latitude = float(
                        coordinate[1]
                    )

                    new_points.append(
                        (
                            latitude,
                            longitude
                        )
                    )

            # จุดสุดท้ายของ GeoJSON
            # จะซ้ำกับจุดแรก
            if len(new_points) >= 2:

                first = new_points[0]
                last = new_points[-1]

                if (
                    abs(first[0] - las
