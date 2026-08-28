import math
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

PLOW_RATE = 250.0
MILL_RATE = 350.0
RAI_M2 = 1600.0
NGAN_M2 = 400.0
WA_M2 = 4.0
LOGO_PATH = "logo1.png"


def thai_area(m2):
    m2 = max(0.0, float(m2))
    rai = int(m2 // RAI_M2)
    remain = m2 - rai * RAI_M2
    ngan = int(remain // NGAN_M2)
    remain -= ngan * NGAN_M2
    wa = int(remain //
