import math
import io
import json
from pathlib import Path
from datetime import datetime

import folium
import streamlit as st
from folium.plugins import LocateControl, Draw
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import requests
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Ta App - วัดพื้นที่นา",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
html, body, [class*="css"], .stApp, button, input, textarea, select {
    font-family: Tahoma, Arial, sans-serif !important;
}
.total-box {
    padding: 24px;
    border-radius: 18px;
    background: rgba(46,125,50,.12);
    border: 2px solid rgba(46,125,50,.35);
    text-align: center;
    margin-top: 10px;
}
.total-money { font-size: 42px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

PLOW_RATE = 250.0
MILL_RATE = 350.0
RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "ta_data.json"

def load_saved():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_saved(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def thai_area(m2):
    m2 = max(float(m2), 0.0)
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
    lat0 = math.radians(sum(p[0] for p in points) / len(points))
    radius = 6378137.0
    xy = []
    for lat, lon in points:
        x = math.radians(lon) * radius * math.cos(lat0)
        y = math.radians(lat) * radius
        xy.append((x, y))
    area = 0.0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0

def money(value):
    return f"{value:,.2f}"

def get_polygon(drawings):
    if not drawings:
        return []
    for feature in reversed(drawings):
        geometry = feature.get("geometry", {})
        if geometry.get("type") != "Polygon":
            continue
        rings = geometry.get("coordinates", [])
        if not rings:
            continue
        ring = rings[0]
        points = [(float(p[1]), float(p[0])) for p in ring if len(p) >= 2]
        if len(points) > 1 and points[0] == points[-1]:
            points.pop()
        if len(points) >= 3:
            return points
    return []

def make_snapshot(points):
    if len(points) < 3:
        return None
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    lat_pad = max((max(lats) - min(lats)) * 0.20, 0.0003)
    lon_pad = max((max(lons) - min(lons)) * 0.20, 0.0003)
    south = min(lats) - lat_pad
    north = max(lats) + lat_pad
    west = min(lons) - lon_pad
    east = max(lons) + lon_pad

    url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/export"
    )
    params = {
        "bbox": f"{west},{south},{east},{north}",
        "bboxSR": "4326",
        "imageSR": "4326",
        "size": "1000,700",
        "format": "png",
        "f": "image",
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        draw = ImageDraw.Draw(image)
        width, height = image.size
        pixel_points = []
        for lat, lon in points:
            x = (lon - west) / (east - west) * (width - 1)
            y = (north - lat) / (north - south) * (height - 1)
            pixel_points.append((int(x), int(y)))
        draw.line(
            pixel_points + [pixel_points[0]],
            fill=(0, 190, 80),
            width=7,
        )
        return image
    except Exception:
        return None

def image_to_base64(image):
    if image is None:
        return None
    import base64
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")

def base64_to_image(value):
    if not value:
        return None
    import base64
    try:
        return Image.open(io.BytesIO(base64.b64decode(value)))
    except Exception:
        return None

if "points" not in st.session_state:
    st.session_state.points = []
if "saved_plots" not in st.session_state:
    st.session_state.saved_plots = load_saved()
if "lat" not in st.session_state:
    st.session_state.lat = None
if "lon" not in st.session_state:
    st.session_state.lon = None

st.title("🌾 ถาวร Ta App")
st.caption("วัดพื้นที่นา • ปรับแนวเขต • คำนวณค่าไถ/ปั่นดิน • บันทึกพร้อมภาพ")

# ขอ GPS ของเครื่องที่เปิดแอป
location = streamlit_geolocation()

if isinstance(location, dict):
    gps_lat = location.get("latitude")
    gps_lon = location.get("longitude")
    if gps_lat is not None and gps_lon is not None:
        new_lat = float(gps_lat)
        new_lon = float(gps_lon)
        if (
            st.session_state.lat != new_lat
            or st.session_state.lon != new_lon
        ):
            st.session_state.lat = new_lat
            st.session_state.lon = new_lon
            st.rerun()

c1, c2 = st.columns(2)
with c1:
    owner = st.text_input(
        "👤 ชื่อเจ้าของนา",
        placeholder="เช่น นาแม่ใหญ่นาง",
    )
with c2:
    note = st.text_input(
        "📝 บันทึก / หมายเหตุ",
        placeholder="เช่น นัดไถวันจันทร์",
    )

st.subheader("🗺️ แผนที่วัดพื้นที่นา")

if st.session_state.lat is None:
    st.info("กดปุ่มตำแหน่งบนแผนที่ เพื่อให้เบราว์เซอร์อนุญาต GPS ของเครื่อง")

center = [
    st.session_state.lat if st.session_state.lat is not None else 13.7563,
    st.session_state.lon if st.session_state.lon is not None else 100.5018,
]

m = folium.Map(
    location=center,
    zoom_start=19,
    control_scale=True,
    tiles="OpenStreetMap",
)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
          "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri",
    name="ภาพดาวเทียม",
    overlay=False,
    control=True,
).add_to(m)

LocateControl(
    auto_start=False,
    flyTo=True,
    keepCurrentZoomLevel=False,
    showCompass=True,
).add_to(m)

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
                "color": "#00b950",
                "weight": 4,
                "fillColor": "#00b950",
                "fillOpacity": 0.18,
            },
        },
    },
    edit_options={"edit": True, "remove": True},
).add_to(m)

if len(st.session_state.points) >= 3:
    folium.Polygon(
        locations=st.session_state.points,
        color="#00b950",
        weight=5,
        fill=True,
        fill_color="#00b950",
        fill_opacity=0.18,
    ).add_to(m)

map_data = st_folium(
    m,
    width=None,
    height=550,
    returned_objects=["all_drawings"],
    key="ta_map",
)

if map_data and map_data.get("all_drawings") is not None:
    new_points = get_polygon(map_data["all_drawings"])
    if new_points != st.session_state.points:
        st.session_state.points = new_points
        st.rerun()

b1, b2 = st.columns(2)
with b1:
    if st.button("🗑️ ล้างแนวเขต", use_container_width=True):
        st.session_state.points = []
        st.rerun()
with b2:
    if st.button("🔄 รีเฟรชแผนที่", use_container_width=True):
        st.rerun()

area_m2 = polygon_area_m2(st.session_state.points)
rai, ngan, wa, remain_m2 = thai_area(area_m2)
plow_cost = area_m2 / RAI_M2 * PLOW_RATE
mill_cost = area_m2 / RAI_M2 * MILL_RATE
total_cost = plow_cost + mill_cost

st.divider()
st.subheader("📐 ผลการวัดพื้นที่")

if len(st.session_state.points) < 3:
    st.warning("กรุณาวาดขอบเขตแปลงนาอย่างน้อย 3 จุด")
else:
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("พื้นที่รวม", f"{area_m2:,.2f} ตร.ม.")
    a2.metric("ไร่", f"{rai:,}")
    a3.metric("งาน", f"{ngan:,}")
    a4.metric("ตารางวา", f"{wa:,}")

    st.success(
        f"พื้นที่ประมาณ {rai} ไร่ {ngan} งาน {wa} ตารางวา "
        f"{remain_m2:.2f} ตร.ม."
    )

    st.subheader("💰 ยอดที่ต้องจ่าย")
    p1, p2, p3 = st.columns(3)
    p1.metric("1️⃣ ค่าไถนา", f"{money(plow_cost)} บาท")
    p2.metric("2️⃣ ค่าปั่นดิน", f"{money(mill_cost)} บาท")
    p3.metric("3️⃣ รวมไถนา + ปั่นดิน", f"{money(total_cost)} บาท")

    st.caption("อัตราค่าบริการ: ไถนา 250 บาท/ไร่ • ปั่นดิน 350 บาท/ไร่")

    st.markdown(
        f"""
        <div class="total-box">
            <div>💰 ยอดรวมทั้งหมด</div>
            <div class="total-money">{money(total_cost)} บาท</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "💾 บันทึกข้อมูล + ภาพพื้นที่",
        type="primary",
        use_container_width=True,
    ):
        snapshot = make_snapshot(st.session_state.points)

        record = {
            "ลำดับ": len(st.session_state.saved_plots) + 1,
            "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "เจ้าของนา": owner.strip() or "-",
            "หมายเหตุ": note.strip() or "-",
            "พื้นที่_ตรม": round(area_m2, 2),
            "ไร่": rai,
            "งาน": ngan,
            "ตารางวา": wa,
            "เหลือ_ตรม": round(remain_m2, 2),
            "ค่าไถนา": round(plow_cost, 2),
            "ค่าปั่นดิน": round(mill_cost, 2),
            "รวม": round(total_cost, 2),
            "พิกัด": [
                [round(lat, 7), round(lon, 7)]
                for lat, lon in st.session_state.points
            ],
            "ภาพพื้นที่_base64": image_to_base64(snapshot),
        }

        st.session_state.saved_plots.append(record)
        save_saved(st.session_state.saved_plots)
        st.success("บันทึกเรียบร้อยแล้วครับ ข้อมูลจะยังอยู่เมื่อปิดและเปิดแอปใหม่ 🌾")

st.divider()
st.subheader("📋 ข้อมูลแปลงนาที่บันทึกไว้")

if not st.session_state.saved_plots:
    st.info("ยังไม่มีข้อมูลที่บันทึก")
else:
    for item in reversed(st.session_state.saved_plots):
        title = (
            f"แปลงที่ {item['ลำดับ']} • "
            f"{item['เจ้าของนา']} • "
            f"{money(item['รวม'])} บาท"
        )
        with st.expander(title):
            left, right = st.columns([1.2, 1])

            with left:
                saved_image = base64_to_image(
                    item.get("ภาพพื้นที่_base64")
                )
                if saved_image is not None:
                    st.image(
                        saved_image,
                        caption="ภาพพื้นที่แปลงนาที่บันทึกไว้",
                        use_container_width=True,
                    )
                else:
                    st.warning("ไม่พบภาพของแปลงนี้")

            with right:
                st.write(f"**เจ้าของนา:** {item['เจ้าของนา']}")
                st.write(f"**วันที่บันทึก:** {item['วันที่บันทึก']}")
                st.write(f"**หมายเหตุ:** {item['หมายเหตุ']}")
                st.write(
                    f"**พื้นที่:** {item['ไร่']} ไร่ "
                    f"{item['งาน']} งาน {item['ตารางวา']} ตารางวา "
                    f"{item['เหลือ_ตรม']:.2f} ตร.ม."
                )
                st.write(f"**ค่าไถนา:** {money(item['ค่าไถนา'])} บาท")
                st.write(f"**ค่าปั่นดิน:** {money(item['ค่าปั่นดิน'])} บาท")
                st.write(f"**รวม:** {money(item['รวม'])} บาท")

                export_item = dict(item)
                export_item.pop("ภาพพื้นที่_base64", None)

                st.download_button(
                    "⬇️ ดาวน์โหลดข้อมูลแปลงนี้",
                    data=json.dumps(
                        export_item,
                        ensure_ascii=False,
                        indent=2,
                    ).encode("utf-8"),
                    file_name=f"ta_plot_{item['ลำดับ']}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"download_{item['ลำดับ']}",
                )

    export_all = []
    for item in st.session_state.saved_plots:
        row = dict(item)
        row.pop("ภาพพื้นที่_base64", None)
        export_all.append(row)

    st.download_button(
        "⬇️ ดาวน์โหลดข้อมูลทั้งหมด",
        data=json.dumps(
            export_all,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8"),
        file_name="ta_plots.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()
st.caption(
    "Ta App • เปิดใช้งานหน้างานด้วย GPS ของเครื่องที่เปิดแอป "
    "• ข้อมูลที่บันทึกเก็บใน ta_data.json บนเครื่อง/เซิร์ฟเวอร์ที่รันแอป "
    "• ค่าพื้นที่เป็นค่าประมาณจากพิกัด GPS"
        )
