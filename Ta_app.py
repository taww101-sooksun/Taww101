def math
import os

import folium
import streamlit as st
from folium.plugins import LocateControl
from streamlit_folium import st_folium

st.set_page_config(
page_title="Ta App - วัดพื้นที่นา",
page_icon="🌾",
layout="wide",
initial_sidebar_state="collapsed",
)

st.markdown(
""" <style>
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

PLOW_RATE = 250.0
MILL_RATE = 350.0

RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0

LOGO_PATH = "logo1.png"

def thai_area(m2):
if m2 < 0:
m2 = 0

```
rai = int(m2 // RAI_M2)
remain = m2 - rai * RAI_M2

ngan = int(remain // NGAN_M2)
remain = remain - ngan * NGAN_M2

wa = int(remain // WA_M2)
remain = remain - wa * WA_M2

return rai, ngan, wa, remain
```

def polygon_area_m2(points):
if len(points) < 3:
return 0.0

```
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
    x2, y2 = xy[(i + 1) % len(xy)]

    area += (
        x1 * y2
        - x2 * y1
    )

return abs(area) / 2.0
```

def money(value):
return f"{value:,.2f}"

if "points" not in st.session_state:
st.session_state.points = []

if "saved_plots" not in st.session_state:
st.session_state.saved_plots = []

if "lat" not in st.session_state:
st.session_state.lat = 13.7563

if "lon" not in st.session_state:
st.session_state.lon = 100.5018
