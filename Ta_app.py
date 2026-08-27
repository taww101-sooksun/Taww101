# Ta_app.py โ€” เนเธเธฅเนเน€เธ”เธตเธขเธงเธชเธณเธซเธฃเธฑเธ GitHub + Streamlit
# เธซเธกเธฒเธขเน€เธซเธ•เธธ: logo1.png เธ•เนเธญเธเธญเธขเธนเนเนเธ repository เน€เธ”เธตเธขเธงเธเธฑเธเน€เธเธทเนเธญเนเธชเธ”เธเนเธฅเนเธเนเธเธฃเธดเธ
# เนเธญเธเธงเธฑเธ”เธเธทเนเธเธ—เธตเนเธเธฒ + เธเธฑเธเธซเธกเธธเธ” + เธเธณเธเธงเธ“เธเนเธฒเธเธฃเธดเธเธฒเธฃ
# เธ•เนเธญเธเธกเธตเนเธเธฅเน logo1.png เธญเธขเธนเนเนเธเธฅเน€เธ”เธญเธฃเนเน€เธ”เธตเธขเธงเธเธฑเธเนเธเธฅเนเธเธตเน
#
# เธ•เธดเธ”เธ•เธฑเนเธ:
#   pip install streamlit streamlit-folium folium shapely
# เธฃเธฑเธ:
#   streamlit run Ta_app.py

import math
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import LocateControl
from shapely.geometry import Polygon
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Ta App - เธงเธฑเธ”เธเธทเนเธเธ—เธตเนเธเธฒ",
    page_icon="๐พ",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# เธ•เธฑเนเธเธเนเธฒเธเธทเนเธเธเธฒเธ
# ----------------------------
PLOW_RATE = 250.0
MILL_RATE = 350.0
RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

LOGO_PATH = Path(__file__).parent / "logo1.png"


def thai_area(m2: float):
    """เนเธเธฅเธ mยฒ -> เนเธฃเน เธเธฒเธ เธ•เธฒเธฃเธฒเธเธงเธฒ เนเธฅเธฐ mยฒ เธ—เธตเนเน€เธซเธฅเธทเธญ"""
    if m2 < 0:
        m2 = 0

    rai = int(m2 // RAI_M2)
    remain = m2 - rai * RAI_M2

    ngan = int(remain // NGAN_M2)
    remain -= ngan * NGAN_M2

    wa = int(remain // WA_M2)
    remain -= wa * WA_M2

    return rai, ngan, wa, remain


def polygon_area_m2(points):
    """เธเธณเธเธงเธ“เธเธทเนเธเธ—เธตเนเธฃเธนเธเธซเธฅเธฒเธขเน€เธซเธฅเธตเนเธขเธกเธเธเนเธฅเธเธเธฒเธ lat/lon เนเธ”เธขเนเธเน local projection"""
    if len(points) < 3:
        return 0.0

    lat0 = math.radians(sum(p[0] for p in points) / len(points))
    R = 6378137.0

    xy = []
    for lat, lon in points:
        x = math.radians(lon) * R * math.cos(lat0)
        y = math.radians(lat) * R
        xy.append((x, y))

    poly = Polygon(xy)
    return abs(poly.area)


def money(value):
    return f"{value:,.2f}"


# ----------------------------
# Session state
# ----------------------------
if "points" not in st.session_state:
    st.session_state.points = []

if "saved_plots" not in st.session_state:
    st.session_state.saved_plots = []

if "lat" not in st.session_state:
    st.session_state.lat = 13.7563

if "lon" not in st.session_state:
    st.session_state.lon = 100.5018


# ----------------------------
# Header
# ----------------------------
header_left, header_right = st.columns([1, 5], vertical_alignment="center")

with header_left:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=115)
    else:
        st.markdown("## ๐พ")

with header_right:
    st.title("๐พ Ta App")
    st.caption("เธงเธฑเธ”เธเธทเนเธเธ—เธตเนเธเธฒ โ€ข เธเธฑเธเธซเธกเธธเธ” โ€ข เธเธณเธเธงเธ“เธเนเธฒเธเธฃเธดเธเธฒเธฃเนเธ–/เธเธฑเนเธ")

st.divider()

# ----------------------------
# เธเนเธญเธกเธนเธฅเนเธเธฅเธ
# ----------------------------
c1, c2 = st.columns(2)

with c1:
    owner = st.text_input(
        "๐‘ค เธเธทเนเธญเน€เธเนเธฒเธเธญเธเธเธฒ",
        placeholder="เน€เธเนเธ เธเธฒเธขเธชเธกเธเธฒเธข เนเธเธ”เธต",
        key="owner",
    )

with c2:
    note = st.text_input(
        "๐“ เธซเธกเธฒเธขเน€เธซเธ•เธธ",
        placeholder="เน€เธเนเธ เธเธฒเนเธเธฅเธเธซเธฅเธฑเธเธเนเธฒเธ / เธเธฑเธ”เนเธ–เธงเธฑเธเธเธฑเธเธ—เธฃเน",
        key="note",
    )

# ----------------------------
# เนเธเธเธ—เธตเน
# ----------------------------
st.subheader("๐—บ๏ธ เธเธณเธซเธเธ”เธเธญเธเน€เธเธ•เนเธเธฅเธเธเธฒ")

st.info(
    "เนเธ•เธฐเธเธเนเธเธเธ—เธตเนเน€เธเธทเนเธญเน€เธเธดเนเธกเธซเธกเธธเธ”เธ—เธตเธฅเธฐเธเธธเธ” โ€ข เนเธเนเธเธธเนเธก GPS เน€เธเธทเนเธญเธซเธฒเธ•เธณเนเธซเธเนเธเธเธฑเธเธเธธเธเธฑเธ "
    "โ€ข เธชเธฒเธกเธฒเธฃเธ–เธฅเธฒเธเธซเธกเธธเธ”เธ—เธตเนเธชเธฃเนเธฒเธเนเธงเนเน€เธเธทเนเธญเธเธฃเธฑเธเนเธเธงเธเธฑเธเธเธฒเนเธ”เน"
)

map_center = [st.session_state.lat, st.session_state.lon]

m = folium.Map(
    location=map_center,
    zoom_start=17,
    control_scale=True,
    tiles="OpenStreetMap",
)

LocateControl(
    auto_start=False,
    flyTo=True,
    keepCurrentZoomLevel=False,
    showCompass=True,
).add_to(m)

# เธงเธฒเธ”เธเธธเธ”เนเธฅเธฐเน€เธชเนเธ
for i, (lat, lon) in enumerate(st.session_state.points):
    folium.Marker(
        [lat, lon],
        tooltip=f"เธซเธกเธธเธ” {i + 1} (เธฅเธฒเธเน€เธเธทเนเธญเธเธฃเธฑเธเธ•เธณเนเธซเธเนเธ)",
        draggable=True,
        icon=folium.Icon(color="green", icon="map-marker"),
    ).add_to(m)

if len(st.session_state.points) >= 2:
    folium.PolyLine(
        st.session_state.points + (
            [st.session_state.points[0]]
            if len(st.session_state.points) >= 3
            else []
        ),
        color="green",
        weight=4,
        opacity=0.85,
    ).add_to(m)

if len(st.session_state.points) >= 3:
    folium.Polygon(
        st.session_state.points,
        color="green",
        weight=2,
        fill=True,
        fill_opacity=0.20,
    ).add_to(m)

map_data = st_folium(
    m,
    width=None,
    height=520,
    returned_objects=["last_clicked", "last_object_clicked", "center"],
    key="farm_map",
)

# เนเธ•เธฐเนเธเธเธ—เธตเนเน€เธเธทเนเธญเน€เธเธดเนเธกเธซเธกเธธเธ”
clicked = map_data.get("last_clicked")
if clicked:
    lat = float(clicked["lat"])
    lon = float(clicked["lng"])

    # เธเนเธญเธเธเธฑเธเธเธฒเธฃเน€เธเธดเนเธกเธเธธเธ”เน€เธ”เธดเธกเธเนเธณเธเธฒเธ rerun
    last = st.session_state.points[-1] if st.session_state.points else None
    if last is None or abs(last[0] - lat) > 0.000001 or abs(last[1] - lon) > 0.000001:
        st.session_state.points.append((lat, lon))
        st.rerun()

# ----------------------------
# เธเธธเนเธกเธเธฑเธ”เธเธฒเธฃเธซเธกเธธเธ”
# ----------------------------
b1, b2, b3, b4 = st.columns(4)

with b1:
    if st.button("โฉ๏ธ เธฅเธเธซเธกเธธเธ”เธฅเนเธฒเธชเธธเธ”", use_container_width=True):
        if st.session_state.points:
            st.session_state.points.pop()
            st.rerun()

with b2:
    if st.button("๐—‘๏ธ เธฅเนเธฒเธเธซเธกเธธเธ”เธ—เธฑเนเธเธซเธกเธ”", use_container_width=True):
        st.session_state.points = []
        st.rerun()

with b3:
    if st.button("๐“ เนเธเนเธ•เธณเนเธซเธเนเธเธ•เธฑเธงเธญเธขเนเธฒเธ", use_container_width=True):
        st.session_state.points = [
            (13.75630, 100.50180),
            (13.75630, 100.50300),
            (13.75530, 100.50300),
            (13.75530, 100.50180),
        ]
        st.rerun()

with b4:
    if st.button("๐” เธฃเธตเน€เธเธฃเธเนเธเธเธ—เธตเน", use_container_width=True):
        st.rerun()

# ----------------------------
# เธเธณเธเธงเธ“เธเธทเนเธเธ—เธตเน
# ----------------------------
area_m2 = polygon_area_m2(st.session_state.points)

rai, ngan, wa, remain_m2 = thai_area(area_m2)

# เธฃเธฒเธเธฒเธเนเธฒเธเธฃเธดเธเธฒเธฃ
plow_cost = rai * PLOW_RATE + (ngan / 4) * PLOW_RATE + (wa / 400) * PLOW_RATE + (remain_m2 / RAI_M2) * PLOW_RATE
mill_cost = rai * MILL_RATE + (ngan / 4) * MILL_RATE + (wa / 400) * MILL_RATE + (remain_m2 / RAI_M2) * MILL_RATE
total_cost = plow_cost + mill_cost

st.divider()
st.subheader("๐“ เธเธฅเธเธฒเธฃเธงเธฑเธ”เธเธทเนเธเธ—เธตเน")

if len(st.session_state.points) < 3:
    st.warning("เธเธฃเธธเธ“เธฒเธเธฑเธเธซเธกเธธเธ”เธญเธขเนเธฒเธเธเนเธญเธข 3 เธเธธเธ”เน€เธเธทเนเธญเธเธณเธเธงเธ“เธเธทเนเธเธ—เธตเน")
else:
    a1, a2, a3, a4 = st.columns(4)

    a1.metric("เธเธทเนเธเธ—เธตเนเธฃเธงเธก", f"{area_m2:,.2f} เธ•เธฃ.เธก.")
    a2.metric("เนเธฃเน", f"{rai:,}")
    a3.metric("เธเธฒเธ", f"{ngan:,}")
    a4.metric("เธ•เธฒเธฃเธฒเธเธงเธฒ", f"{wa:,}")

    st.success(
        f"เธเธทเนเธเธ—เธตเนเนเธ”เธขเธเธฃเธฐเธกเธฒเธ“ **{rai} เนเธฃเน {ngan} เธเธฒเธ {wa} เธ•เธฒเธฃเธฒเธเธงเธฒ "
        f"{remain_m2:.2f} เธ•เธฃ.เธก.**"
    )

    st.divider()
    st.subheader("๐’ฐ เธเนเธฒเธเธฃเธดเธเธฒเธฃ")

    s1, s2 = st.columns(2)

    with s1:
        st.markdown("### ๐ เนเธ–")
        st.markdown(f"**{money(PLOW_RATE)} เธเธฒเธ— / เนเธฃเน**")
        st.metric("เธเนเธฒเนเธ–", f"{money(plow_cost)} เธเธฒเธ—")

    with s2:
        st.markdown("### โ๏ธ เธเธฑเนเธ")
        st.markdown(f"**{money(MILL_RATE)} เธเธฒเธ— / เนเธฃเน**")
        st.metric("เธเนเธฒเธเธฑเนเธ", f"{money(mill_cost)} เธเธฒเธ—")

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
            <div style="font-size:20px;">๐’ฐ เธขเธญเธ”เธฃเธงเธกเธ—เธฑเนเธเธซเธกเธ”</div>
            <div style="font-size:44px;font-weight:800;">
                {money(total_cost)} เธเธฒเธ—
            </div>
            <div style="font-size:15px;">
                เนเธ– {money(plow_cost)} + เธเธฑเนเธ {money(mill_cost)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("๐’พ เธเธฑเธเธ—เธถเธเนเธเธฅเธเธเธตเน", type="primary", use_container_width=True):
        record = {
            "เน€เธเนเธฒเธเธญเธเธเธฒ": owner or "-",
            "เธเธทเนเธเธ—เธตเน เธ•เธฃ.เธก.": round(area_m2, 2),
            "เธเธทเนเธเธ—เธตเน": f"{rai} เนเธฃเน {ngan} เธเธฒเธ {wa} เธ•เธฒเธฃเธฒเธเธงเธฒ {remain_m2:.2f} เธ•เธฃ.เธก.",
            "เธเนเธฒเนเธ–": round(plow_cost, 2),
            "เธเนเธฒเธเธฑเนเธ": round(mill_cost, 2),
            "เธขเธญเธ”เธฃเธงเธก": round(total_cost, 2),
            "เธซเธกเธฒเธขเน€เธซเธ•เธธ": note or "-",
            "เธซเธกเธธเธ”": list(st.session_state.points),
        }
        st.session_state.saved_plots.append(record)
        st.success("เธเธฑเธเธ—เธถเธเธเนเธญเธกเธนเธฅเนเธเธฅเธเธเธฒเน€เธฃเธตเธขเธเธฃเนเธญเธขเนเธฅเนเธงเธเธฃเธฑเธ ๐พ")

# ----------------------------
# เธฃเธฒเธขเธเธฒเธฃเธ—เธตเนเธเธฑเธเธ—เธถเธ
# ----------------------------
if st.session_state.saved_plots:
    st.divider()
    st.subheader("๐“ เนเธเธฅเธเธเธฒเธ—เธตเนเธเธฑเธเธ—เธถเธเนเธงเน")

    for idx, item in enumerate(reversed(st.session_state.saved_plots), 1):
        with st.expander(
            f"เนเธเธฅเธเธ—เธตเน {len(st.session_state.saved_plots) - idx + 1} โ€ข "
            f"{item['เน€เธเนเธฒเธเธญเธเธเธฒ']} โ€ข {money(item['เธขเธญเธ”เธฃเธงเธก'])} เธเธฒเธ—"
        ):
            st.write(f"**เน€เธเนเธฒเธเธญเธเธเธฒ:** {item['เน€เธเนเธฒเธเธญเธเธเธฒ']}")
            st.write(f"**เธเธทเนเธเธ—เธตเน:** {item['เธเธทเนเธเธ—เธตเน']}")
            st.write(f"**เธเนเธฒเนเธ–:** {money(item['เธเนเธฒเนเธ–'])} เธเธฒเธ—")
            st.write(f"**เธเนเธฒเธเธฑเนเธ:** {money(item['เธเนเธฒเธเธฑเนเธ'])} เธเธฒเธ—")
            st.write(f"**เธขเธญเธ”เธฃเธงเธก:** {money(item['เธขเธญเธ”เธฃเธงเธก'])} เธเธฒเธ—")
            st.write(f"**เธซเธกเธฒเธขเน€เธซเธ•เธธ:** {item['เธซเธกเธฒเธขเน€เธซเธ•เธธ']}")

# ----------------------------
# Footer
# ----------------------------
st.divider()
st.caption(
    "Ta App โ€ข เธฃเธฐเธเธเธเธณเธเธงเธ“เธเธทเนเธเธ—เธตเนเธเธฒเธเธเธดเธเธฑเธ” GPS เนเธ”เธขเธเธฃเธฐเธกเธฒเธ“ "
    "เธเธงเธฃเธ•เธฃเธงเธเธชเธญเธเนเธเธงเน€เธเธ•เธเธฃเธดเธเธเนเธญเธเนเธเนเน€เธเนเธเธเนเธญเธกเธนเธฅเธ—เธฒเธเธเธเธซเธกเธฒเธข"
    )
