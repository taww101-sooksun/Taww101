import math
import io
import json
from datetime import datetime

import folium
import streamlit as st
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import requests
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Ta App None- วัดพื้นที่นา",
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

if "points" not in st.session_state:
    st.session_state.points = []
if "saved_plots" not in st.session_state:
    st.session_state.saved_plots = []
if "lat" not in st.session_state:
    st.session_state.lat = 13.7563
if "lon" not in st.session_state:
    st.session_state.lon = 100.5018
if "gps_loaded" not in st.session_state:
    st.session_state.gps_loaded = False

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
    r = 6378137.0
    xy = []
    for lat, lon in points:
        x = math.radians(lon) * r * math.cos(lat0)
        y = math.radians(lat) * r
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
    lat_pad = max((max(lats)-min(lats))*0.2, 0.0003)
    lon_pad = max((max(lons)-min(lons))*0.2, 0.0003)
    south, north = min(lats)-lat_pad, max(lats)+lat_pad
    west, east = min(lons)-lon_pad, max(lons)+lon_pad
    url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"
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
        w, h = image.size
        pix = []
        for lat, lon in points:
            x = (lon-west)/(east-west)*(w-1)
            y = (north-lat)/(north-south)*(h-1)
            pix.append((int(x), int(y)))
        draw.line(pix + [pix[0]], fill=(0,190,80), width=7)
        return image
    except Exception:
        return None

def image_bytes(image):
    if image is None:
        return None
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()

st.title("🌾 Ta App")
st.caption("วัดพื้นที่นา • แก้ไขแนวเขต • คำนวณค่าไถ/ปั่นดิน • บันทึกพร้อมภาพพื้นที่")

gps = streamlit_geolocation()
if isinstance(gps, dict) and gps.get("latitude") is not None:
    lat = float(gps["latitude"])
    lon = float(gps["longitude"])
    if not st.session_state.gps_loaded:
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.session_state.gps_loaded = True
        st.rerun()

c1, c2 = st.columns(2)
with c1:
    owner = st.text_input("👤 ชื่อเจ้าของนา", placeholder="เช่น นายสมชาย ใจดี")
with c2:
    note = st.text_input("📝 บันทึก / หมายเหตุ", placeholder="เช่น นัดไถวันจันทร์")

st.subheader("🗺️ วัดพื้นที่นา")
st.info("กดปุ่ม GPS เพื่อหาตำแหน่งปัจจุบัน แล้วเลือกเครื่องมือรูปหลายเหลี่ยมเพื่อวาดรอบแปลงนา สามารถแก้ไขจุดได้")

m = folium.Map(
    location=[st.session_state.lat, st.session_state.lon],
    zoom_start=19,
    control_scale=True,
    tiles=None,
)

folium.TileLayer(
    "OpenStreetMap",
    name="แผนที่ถนน",
    control=True,
).add_to(m)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
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

folium.LayerControl(collapsed=False).add_to(m)

if len(st.session_state.points) >= 3:
    folium.Polygon(
        locations=st.session_state.points,
        color="#00b950",
        weight=5,
        fill=True,
        fill_color="#00b950",
        fill_opacity=0.18,
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

map_data = st_folium(
    m,
    width=None,
    height=550,
    returned_objects=["all_drawings"],
    key="ta_map",
)

if map_data is not None and map_data.get("all_drawings") is not None:
    new_points = get_polygon(map_data.get("all_drawings"))
    if new_points != st.session_state.points:
        st.session_state.points = new_points
        st.rerun()

b1, b2, b3 = st.columns(3)
with b1:
    if st.button("🗑️ ล้างแปลง", use_container_width=True):
        st.session_state.points = []
        st.rerun()
with b2:
    if st.button("📍 ใช้ตำแหน่งตัวอย่าง", use_container_width=True):
        lat, lon = st.session_state.lat, st.session_state.lon
        d = 0.001
        st.session_state.points = [
            (lat+d, lon-d), (lat+d, lon+d),
            (lat-d, lon+d), (lat-d, lon-d)
        ]
        st.rerun()
with b3:
    if st.button("🔄 รีเฟรช", use_container_width=True):
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
    st.success(f"พื้นที่ประมาณ {rai} ไร่ {ngan} งาน {wa} ตารางวา {remain_m2:.2f} ตร.ม.")

    st.subheader("💰 ยอดค่าใช้จ่าย")
    p1, p2, p3 = st.columns(3)
    p1.metric("1️⃣ ค่าไถนา", f"{money(plow_cost)} บาท")
    p2.metric("2️⃣ ค่าปั่นดิน", f"{money(mill_cost)} บาท")
    p3.metric("3️⃣ รวมไถนา + ปั่นดิน", f"{money(total_cost)} บาท")

    st.caption("อัตรา: ไถนา 250 บาท/ไร่ • ปั่นดิน 350 บาท/ไร่")

    st.markdown(
        f'<div class="total-box"><div>💰 ยอดรวมที่ต้องจ่าย</div>'
        f'<div class="total-money">{money(total_cost)} บาท</div></div>',
        unsafe_allow_html=True,
    )

    st.subheader("💾 บันทึกแปลงนา")
    if st.button("💾 บันทึกข้อมูลพร้อมภาพพื้นที่", type="primary", use_container_width=True):
        snap = make_snapshot(st.session_state.points)
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
            "พิกัด": [[round(a, 7), round(b, 7)] for a, b in st.session_state.points],
            "ภาพพื้นที่": image_bytes(snap),
        }
        st.session_state.saved_plots.append(record)
        st.success("บันทึกข้อมูลเรียบร้อยแล้วครับ 🌾")

st.divider()
st.subheader("📋 แปลงนาที่บันทึกไว้")

if not st.session_state.saved_plots:
    st.info("ยังไม่มีข้อมูลที่บันทึก")
else:
    for item in reversed(st.session_state.saved_plots):
        with st.expander(f"แปลงที่ {item['ลำดับ']} • {item['เจ้าของนา']} • {money(item['รวม'])} บาท"):
            left, right = st.columns([1.2, 1])
            with left:
                if item.get("ภาพพื้นที่"):
                    st.image(item["ภาพพื้นที่"], caption="ภาพดาวเทียมพร้อมขอบเขตแปลง")
                else:
                    st.warning("ไม่มีภาพพื้นที่")
            with right:
                st.write(f"**เจ้าของนา:** {item['เจ้าของนา']}")
                st.write(f"**วันที่:** {item['วันที่บันทึก']}")
                st.write(f"**หมายเหตุ:** {item['หมายเหตุ']}")
                st.write(f"**พื้นที่:** {item['ไร่']} ไร่ {item['งาน']} งาน {item['ตารางวา']} ตารางวา {item['เหลือ_ตรม']:.2f} ตร.ม.")
                st.write(f"**ค่าไถนา:** {money(item['ค่าไถนา'])} บาท")
                st.write(f"**ค่าปั่นดิน:** {money(item['ค่าปั่นดิน'])} บาท")
                st.write(f"**รวม:** {money(item['รวม'])} บาท")
                data = {k: v for k, v in item.items() if k != "ภาพพื้นที่"}
                st.download_button(
                    "⬇️ ดาวน์โหลดข้อมูลแปลงนี้",
                    data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                    file_name=f"ta_plot_{item['ลำดับ']}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"download_{item['ลำดับ']}",
                )

    export_data = [
        {k: v for k, v in item.items() if k != "ภาพพื้นที่"}
        for item in st.session_state.saved_plots
    ]
    st.download_button(
        "⬇️ ดาวน์โหลดข้อมูลทั้งหมด",
        data=json.dumps(export_data, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="ta_plots.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()
st.caption("Ta App • การคำนวณพื้นที่จากพิกัด GPS เป็นค่าประมาณ ควรตรวจสอบแนวเขตจริงก่อนใช้เป็นเอกสารทางกฎหมาย")
