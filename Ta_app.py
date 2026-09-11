# -*- การเข้ารหัส: utf-8 -*-
# Ta_app.py
# \u0e41\u0e2d\u0e1b\u0e27\u0e31\u0e14\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48\u0e19\u0e32 + \u0e1b\u0e31\u0e01\u0e2b\u0e21\u0e38\u0e14 + \u0e04\u0e33\u0e19\u0e27\u0e13\u0e04\u0e48\u0e32\u0e1a\u0e23\u0e34\u0e01\u0e32\u0e23
# \u0e15\u0e49\u0e2d\u0e07\u0e21\u0e35\u0e44\u0e1f\u0e25\u0e4c logo1.png \u0e2d\u0e22\u0e39\u0e48\u0e42\u0e1f\u0e25\u0e40\u0e14\u0e2d\u0e23\u0e4c\u0e40\u0e14\u0e35\u0e22\u0e27\u0e01\u0e31\u0e1a\u0e44\u0e1f\u0e25\u0e4c\u0e19\u0e35\u0e49
#
# \u0e15\u0e34\u0e14\u0e15\u0e31\u0e49\u0e07:
# pip install streamlit streamlit-folium folium shapely
# \u0e23\u0e31\u0e19:
# streamlit run Ta_app.py

นำเข้าคณิตศาสตร์
จาก pathlib นำเข้า Path

นำเข้าโฟเลียม
import streamlit as st
จาก folium.plugins นำเข้า LocateControl
จาก shapely.geometry นำเข้า Polygon
จาก streamlit_folium นำเข้า st_folium



เซนต์มาร์คดาวน์("""
<สไตล์>
html, body, [class*="css"], .stApp, button, input, textarea, select {
    ตระกูลฟอนต์: "Noto Sans Thai", "Tahoma", "Arial", sans-serif !สำคัญ;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="แอป Ta - 271114117115181917115181912",
    page_icon="\U0001f33e",
    layout="wide",
    สถานะแถบด้านข้างเริ่มต้น="ยุบ"
)

# ----------------------------
# \u0e15\u0e31\u0e49\u0e07\u0e04\u0e48\u0e32\u0e1e\u0e37\u0e49\u0e19\u0e10\u0e32\u0e19
# ----------------------------
อัตราการไถพรวน = 250.0
อัตราการผลิต = 350.0
RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "logo1.png"


def thai_area(m2: float):
    """\u0e41\u0e1b\u0e25\u0e07 m\u00b2 -> \u0e44\u0e23\u0e48 \u0e07\u0e32\u0e19 \u0e15\u0e32\u0e23\u0e32\u0e07\u0e27\u0e32 \u0e41\u0e25\u0e30 m\u00b2 \u0e17\u0e35\u0e48\u0e40\u0e2b\u0e25\u0e37\u0e2d"""
    ถ้า m2 < 0:
        ม2 = 0

    rai = int(m2 // RAI_M2)
    คงเหลือ = m2 - rai * RAI_M2

    ngan = int(ส่วนที่เหลือ // NGAN_M2)
    คงเหลือ -= ngan * NGAN_M2

    wa = int(remain // WA_M2)
    ยังคงอยู่ -= wa * WA_M2

    return rai, ngan, wa, remain


def polygon_area_m2(points):
    """\u0e04\u0e33\u0e19\u0e27\u0e13\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48\u0e23\u0e39\u0e1b\u0e2b\u0e 25\u0e32\u0e22\u0e40\u0e2b\u0e25\u0e35\u0e48\u0e22\u0e21\u0e1a\u0e19\u0e42\u0e25\u0e01\u0e08\u0e32\u0e01 ละติจูด/ลอน \u0e42\u0e14\u0e22\u0e43\u0e0a\u0e49 การฉายภาพเฉพาะที่"""
    ถ้าจำนวนจุดน้อยกว่า 3:
        ส่งคืนค่า 0.0

    lat0 = math.radians(sum(p[0] for p in points) / len(points))
    R = 6378137.0

    xy = []
    สำหรับค่าละติจูดและลองจิจูดในรูปแบบจุด:
        x = math.radians(lon) * R * math.cos(lat0)
        y = math.radians(lat) * R
        xy.append((x, y))

    poly = Polygon(xy)
    คืนค่า abs(poly.area)


def money(value):
    คืนค่า f"{value:,.2f}"


# ----------------------------
# สถานะเซสชัน
# ----------------------------
ถ้า "points" ไม่อยู่ใน st.session_state:
    st.session_state.points = []

หาก "saved_plots" ไม่อยู่ใน st.session_state:
    st.session_state.saved_plots = []

ถ้า "lat" ไม่อยู่ใน st.session_state:
    st.session_state.lat = 13.7563

ถ้า "lon" ไม่อยู่ใน st.session_state:
    st.session_state.lon = 100.5018


# ----------------------------
# ส่วนหัว
# ----------------------------
header_left, header_right = st.columns([1, 5], vertical_alignment="center")

พร้อมส่วนหัวด้านซ้าย:
    ถ้า LOGO_PATH มีอยู่:
        st.image(str(LOGO_PATH), width=115)
    อื่น:
        st.markdown("## \U0001f33e")

พร้อมส่วนหัวด้านขวา:
    st.title("\U0001f33e Ta App")
    st.caption("\u0e27\u0e31\u0e14\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48\u0e19\u0e32 \u2022 \u0e1b\u0e31\u0e01\u0e2b\u0e21\u0e38\u0e14 \u2022 \u0e04\u0e33\u0e19\u0e27\u0e13\u0e04\u0e48\u0e32\u0e1a\u0e23\ u0e34\u0e01\u0e32\u0e23\u0e44\u0e16/\u0e1b\u0e31\u0e48\u0e19")

st.divider()

# ----------------------------
# \u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e41\u0e1b\u0e25\u0e07
# ----------------------------
c1, c2 = st.columns(2)

ด้วย c1:
    เจ้าของ = st.text_input(
        "\U0001f464 \u0e0a\u0e37\u0e48\u0e2d\u0e40\u0e08\u0e49\u0e32\u0e02\u0e2d\u0e07\u0e19\u0e32",
        placeholder="\u0e40\u0e0a\u0e48\u0e19 \u0e19\u0e32\u0e22\u0e2a\u0e21\u0e0a\u0e32\u0e22 \u0e43\u0e08\u0e14\u0e35",
        คีย์="เจ้าของ"
    )

ด้วย c2:
    หมายเหตุ = st.text_input(
        "\U0001f4dd \u0e2b\u0e21\u0e32\u0e22\u0e40\u0e2b\u0e15\u0e38",
        placeholder="\u0e40\u0e0a\u0e48\u0e19 \u0e19\u0e32\u0e41\u0e1b\u0e25\u0e07\u0e2b\u0e25\u0e31\u0e07\u0e1a\u0e49\u0e32\u0e19 / \u0e19\u0e31\u0e14\u0e44\u0e16\u0e27\u0e31\u0e19\u0e08\u0e31\u0e19\u0e17\u0e23\u0e4c",
        key="note",
    )

# ----------------------------
# \u0e41\u0e1c\u0e19\u0e17\u0e35\u0e48
# ----------------------------
st.subheader("\U0001f5fa\ufe0f \u0e01\u0e33\u0e2b\u0e19\u0e14\u0e02\u0e2d\u0e1a\u0e40\u0e02\u0e15\u0e41\u0e1b\u0e25\u0e07\u0e19\u0e32")

ข้อมูลเบื้องต้น (
    "\u0e41\u0e15\u0e30\u0e1a\u0e19\u0e41\u0e1c\u0e19\u0e17\u0e35\u0e48\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e2b\u0e21\u0e38\u0e14\u0e17\u0e35\u0e25\u0e30\u0e08\u0e38\u0e14 \u2022 \u0e43\u0e0a\u0e49\u0e1b\u0e38\u0e48\u0e21 GPS \u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e2b\u0e32\u0e15\u0e33\u0e41\u0e2b \u0e19\u0e48\u0e07\u0e1b\u0e31\u0e08\u0e08\u0e38\u0e1a\u0e31\u0e19 "
    "\u2022 \u0e2a\u0e32\u0e21\u0e32\u0e23\u0e16\u0e25\u0e32\u0e01\u0e2b\u0e21\u0e38\u0e14\u0e17\u0e35\u0e48\u0e2a\u0e23\u0e49\u0e32\u0e07\u0e44 \u0e27\u0e49\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e1b\u0e23\u0e31\u0e1a \u0e41\u0e19\u0e27\u0e04\u0e31\u0e19\u0e19\u0e32\u0e44\u0e14\u0e49"
)

map_center = [st.session_state.lat, st.session_state.lon]

m = folium.Map(
    ตำแหน่ง = จุดศูนย์กลางแผนที่
    zoom_start=17,
    control_scale=True,
    tiles="OpenStreetMap",
)

โลเคทคอนโทรล(
    auto_start=False,
    flyTo=True,
    keepCurrentZoomLevel=False,
    showCompass=True,
).add_to(m)

# \u0e27\u0e32\u0e14\u0e08\u0e38\u0e14\u0e41\u0e25\u0e30\u0e40\u0e2a\u0e49\u0e19
สำหรับ i, (lat, lon) ใน enumerate(st.session_state.points):
    โฟเลียม.มาร์กเกอร์(
        [ละติจูด, ลองจิจูด]
        tooltip=f"\u0e2b\u0e21\u0e38\u0e14 {i + 1} (\u0e25\u0e32\u0e01\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e1b\u0e23\u0e31\u0e1a\u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07)",
        draggable=True,
        icon=folium.Icon(color="green", icon="map-marker"),
    ).add_to(m)

ถ้า len(st.session_state.points) >= 2:
    โฟเลียม.โพลีไลน์(
        st.session_state.points + (
            [st.session_state.points[0]]
            ถ้า len(st.session_state.points) >= 3
            อื่น []
        ),
        สีเขียว
        น้ำหนัก = 4
        ความทึบแสง = 0.85
    ).add_to(m)

ถ้า len(st.session_state.points) >= 3:
    โฟเลียม.โพลีกอน(
        st.session_state.points,
        สีเขียว
        น้ำหนัก = 2
        fill=True,
        fill_opacity=0.20,
    ).add_to(m)

map_data = st_folium(
    ม,
    ความกว้าง = ไม่มี
    ความสูง = 520
    returned_objects=["last_clicked", "last_object_clicked", "center"],
    คีย์="แผนที่ฟาร์ม",
)

# \u0e41\u0e15\u0e30\u0e41\u0e1c\u0e19\u0e17\u0e35\u0e48\u0e40\u0e1e\u0 e37\u0e48\u0e2d\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e2b\u0e21\u0e38\u0e14
คลิก = map_data.get("คลิกครั้งล่าสุด")
หากคลิก:
    lat = float(clicked["lat"])
    lon = float(clicked["lng"])

    # \u0e1b\u0e49\u0e2d\u0e07\u0e01\u0e31\u0e19\u0e01\u0e32\u0e23\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e08\u0e38\u0e14\u0e40\u0e14\u0e34\u0e21\u0e0b\u0e49\u0e33\u0e08\u0e32\u0e01 rerun
    สุดท้าย = st.session_state.points[-1] ถ้า st.session_state.points มิฉะนั้น None
    ถ้า last เป็น None หรือ abs(last[0] - lat) > 0.000001 หรือ abs(last[1] - lon) > 0.000001:
        st.session_state.points.append((lat, lon))
        st.rerun()

# ----------------------------
# \u0e1b\u0e38\u0e48\u0e21\u0e08\u0e31\u0e14\u0e01\u0e32\u0e23\u0e2b\u0e21\u0e38\u0e14
# ----------------------------
b1, b2, b3, b4 = st.columns(4)

ด้วย b1:
    ถ้า st.button("\u21a9\ufe0f \u0e25\u0e1a\u0e2b\u0e21\u0e38\u0e14\u0e25\u0e48\u0e32\u0e2a\u0e38\u0e14", use_container_width=True):
        ถ้า st.session_state.points:
            st.session_state.points.pop()
            st.rerun()

ด้วย b2:
    ถ้า st.button("\U0001f5d1\ufe0f \u0e25\u0e49\u0e32\u0e07\u0e2b\u0e21\u0e38\u0e14\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14", use_container_width=True):
        st.session_state.points = []
        st.rerun()

ด้วย b3:
    ถ้า st.button("\U0001f4cd \u0e43\u0e0a\u0e49\u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07\u0e15\u0e31\u0e27\u0e2d\u0e22\u0e48\u0e32\u0e07", use_container_width=True):
        st.session_state.points = [
            (13.75630, 100.50180),
            (13.75630, 100.50300),
            (13.75530, 100.50300),
            (13.75530, 100.50180),
        ]
        st.rerun()

ด้วย b4:
    ถ้าปุ่ม st("\U0001f504 \u0e23\u0e35\u0e40\u0e1f\u0e23\u0e0a\u0e41\u0e1c\u0e19\u0e17\u0e35\u0e48", use_container_width=True):
        st.rerun()

# ----------------------------
# \u0e04\u0e33\u0e19\u0e27\u0e13\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48
# ----------------------------
area_m2 = polygon_area_m2(st.session_state.points)

ไร่ งาน วา เหลือ_m2 = thai_area(area_m2)

# \u0e23\u0e32\u0e04\u0e32\u0e04\u0e48\u0e32\u0e1a\u0e23\u0e34\u0e01\u0e32\u0e23
ต้นทุนการไถ = rai * อัตราไถ + (ngan / 4) * อัตราไถ + (wa / 400) * อัตราไถ + (remain_m2 / RAI_M2) * อัตราไถ
ต้นทุนโรงสี = rai * อัตราโรงสี + (ngan / 4) * อัตราโรงสี + (wa / 400) * อัตราโรงสี + (remain_m2 / RAI_M2) * อัตราโรงสี
ต้นทุนรวม = ต้นทุนไถ + ต้นทุนโรงสี

st.divider()
st.subheader("\U0001f4d0 \u0e1c\u0e25\u0e01\u0e32\u0e23\u0e27\u0e31\u0e14\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48")

ถ้า len(st.session_state.points) < 3:
    st.warning("\u0e01\u0e23\u0e38\u0e13\u0e32\u0e1b\u0e31\u0e01\u0e2b\u0e21\u0e38\u0e14\u0e2d\u0e22\u0e48\u0e32\u0e07\u0e19\u0e49\u0e2d\u0e22 3 \u0e08\u0e38\u0e14\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e04\u0e33\ u0e19\u0e27\u0e13\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48")
อื่น:
    a1, a2, a3, a4 = st.columns(4)

    a1.metric("\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48\u0e23\u0e27\u0e21", f"{area_m2:,.2f} \u0e15\u0e23.\u0e21.")
    a2.metric("\u0e44\u0e23\u0e48", f"{rai:,}")
    a3.metric("\u0e07\u0e32\u0e19", f"{ngan:,}")
    a4.metric("\u0e15\u0e32\u0e23\u0e32\u0e07\u0e27\u0e32", f"{wa:,}")

    ความสำเร็จขั้นที่ (
        f"\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48\u0e42\u0e14\u0e22\u0e1b\u0e23\u0e30\u0e21\u0e32\u0e13 **{ไร่} \u0e44\u0e23\u0e48 {ngan} \u0e07\u0e32\u0e19 {wa} \u0e15\u0e32\u0e23\u0e32\u0e07\u0e27\u0e32 "
        f"{remain_m2:.2f} \u0e15\u0e23.\u0e21.**"
    )

    st.divider()
    st.subheader("\U0001f4b0 \u0e04\u0e48\u0e32\u0e1a\u0e23\u0e34\u0e01\u0e32\u0e23")

    s1, s2 = st.columns(2)

    ด้วย s1:
        st.markdown("### \U0001f69c \u0e44\u0e16")
        st.markdown(f"**{money(PLOW_RATE)} \u0e1a\u0e32\u0e17 / \u0e44\u0e23\u0e48**")
        st.metric("\u0e04\u0e48\u0e32\u0e44\u0e16", f"{money(plow_cost)} \u0e1a\u0e32\u0e17")

    ด้วย s2:
        st.markdown("### \u2699\ufe0f \u0e1b\u0e31\u0e48\u0e19")
        st.markdown(f"**{money(MILL_RATE)} \u0e1a\u0e32\u0e17 / \u0e44\u0e23\u0e48**")
        st.metric("\u0e04\u0e48\u0e32\u0e1b\u0e31\u0e48\u0e19", f"{money(mill_cost)} \u0e1a\u0e32\u0e17")

    st.markdown("---")
    เซนต์มาร์คดาวน์(
        ฟ"""
        <div style="
            ระยะห่าง: 24 พิกเซล;
            ขอบโค้งมน: 18 พิกเซล;
            พื้นหลัง: rgba(46,125,50,.12);
            ขอบ: 2px ทึบ rgba(46,125,50,.35);
            จัดตำแหน่งข้อความให้อยู่ตรงกลาง;
            ระยะขอบบน: 10 พิกเซล;
        ">
            <div style="font-size:20px;">\U0001f4b0 \u0e22\u0e2d\u0e14\u0e23\u0e27\u0e21\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14</div>
            <div style="font-size:44px;font-weight:800;">
                {money(total_cost)} \u0e1a\u0e32\u0e17
            </div>
            <div style="font-size:15px;">
                \u0e44\u0e16 {money(plow_cost)} + \u0e1b\u0e31\u0e48\u0e19 {money(mill_cost)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    ถ้า st.button("\U0001f4be \u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e41\u0e1b\u0e25\u0e07\u0e19\u0e35\u0e49", type="primary", use_container_width=True):
        บันทึก = {
            "\u0e40\u0e08\u0e49\u0e32\u0e02\u0e2d\u0e07\u0e19\u0e32": เจ้าของหรือ "-",
            "\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48 \u0e15\u0e23.\u0e21.": round(area_m2, 2),
            "\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48": f"{rai} \u0e44\u0e23\u0e48 {ngan} \u0e07\u0e32\u0e19 {wa} \u0e15\u0e32\u0e23\u0e32\u0e07\u0e27\u0e32 {remain_m2:.2f} \u0e15\u0e23.\u0e21",
            "\u0e04\u0e48\u0e32\u0e44\u0e16": round(plow_cost, 2),
            "\u0e04\u0e48\u0e32\u0e1b\u0e31\u0e48\u0e19": round(mill_cost, 2),
            "\u0e22\u0e2d\u0e14\u0e23\u0e27\u0e21": round(total_cost, 2),
            "\u0e2b\u0e21\u0e32\u0e22\u0e40\u0e2b\u0e15\u0e38": หมายเหตุหรือ "-",
            "\u0e2b\u0e21\u0e38\u0e14": list(st.session_state.points),
        }
        st.session_state.saved_plots.append(record)
        st.success("\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e41\u0e1b\u0e25\u0e07\u0e19\u0e32\u0e40\u0e23\u0e35\u0e22\u0e1a\u0e23\u0e49\u0e2d\u0e22\u0e41\u0e25\u0e49\u0e27\u0e04\u0e23\u0e31\u0e1a \U0001f33e")

# ----------------------------
# \u0e23\u0e32\u0e22\u0e01\u0e32\u0e23\u0e17\u0e35\u0e48\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01
# ----------------------------
ถ้า st.session_state.saved_plots:
    st.divider()
    st.subheader("\U0001f4cb \u0e41\u0e1b\u0e25\u0e07\u0e19\u0e32\u0e17\u0e35\u0e48\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e44\u0e27\u0e49")

    สำหรับ idx, รายการใน enumerate(reversed(st.session_state.saved_plots), 1):
        ด้วย st.expander(
            f"\u0e41\u0e1b\u0e25\u0e07\u0e17\u0e35\u0e48 {len(st.session_state.saved_plots) - idx + 1} \u2022 "
            f"{item['\u0e40\u0e08\u0e49\u0e32\u0e02\u0e2d\u0e07\u0e19\u0e32']} \u2022 {money(item['\u0e22\u0e2d\u0e14\u0e23\u0e27\u0e21'])} \u0e1a\u0e32\u0e17"
        ):
            st.write(f"**\u0e40\u0e08\u0e49\u0e32\u0e02\u0e2d\u0e07\u0e19\u0e32:** {item['\u0e40\u0e08\u0e49\u0e32\u0e02\u0e2d\u0e07\u0e19\u0e32']}")
            st.write(f"**\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48:** {item['\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48']}")
            st.write(f"**\u0e04\u0e48\u0e32\u0e44\u0e16:** {money(item['\u0e04\u0e48\u0e32\u0e44\u0e16'])} \u0e1a\u0e32\u0e17")
            st.write(f"**\u0e04\u0e48\u0e32\u0e1b\u0e31\u0e48\u0e19:** {money(item['\u0e04\u0e48\u0e32\u0e1b\u0e31\u0e48\u0e19'])} \u0e1a\u0e32\u0e17")
            st.write(f"**\u0e22\u0e2d\u0e14\u0e23\u0e27\u0e21:** {money(item['\u0e22\u0e2d\u0e14\u0e23\u0e27\u0e21'])} \u0e1a\u0e32\u0e17")
            st.write(f"**\u0e2b\u0e21\u0e32\u0e22\u0e40\u0e2b\u0e15\u0e38:** {item['\u0e2b\u0e21\u0e32\u0e22\u0e40\u0e2b\u0e15\u0e38']}")

# ----------------------------
# ส่วนท้าย
# ----------------------------
st.divider()
คำบรรยายภาพ(
    "ทาแอป \u2022 \u0e23\u0e30\u0e1a\u0e1a\u0e04\u0e33\u0e19\u0e27\u0e13\u0e1e\u0e37\u0e49 \u0e19\u0e17\u0e35\u0e48\u0e08\u0e32\u0e01\u0e1e\u0e34\u0e01\u0e31\u0e14 จีพีเอส \u0e42\u0e14\u0e22\u0e1b\u0e23\u0e30\u0e21\u0e32\u0e13 "
    "\u0e04\u0e27\u0e23\u0e15\u0e23\u0e27\u0e08\u0e2a\u0e2d\u0e1a\u0e41\u 0e19\u0e27\u0e40\u0e02\u0e15\u0e08\u0e23\u0e34\u0e07\u0e01\u0e48\u0e2d \u0e19\u0e43\u0e0a\u0e49\u0e40\u0e1b\u0e47\u0e19\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e17\u0e32\u0e07\u0e01\u0e0e\u0e2b\u0e21\u0e32\u0e22"
)
