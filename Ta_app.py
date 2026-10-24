"""SYNAPSE MYSTIC NUMBER — rebuilt from scratch.

Uses JPL Horizons API vectors at a requested UTC instant. No mocked ephemeris,
random values, historical lottery results, or silent fallback data are used.
The 00–99 values are transparent encodings of real computed values, not NASA
lottery predictions and not scientifically validated predictors of lottery draws.
"""
from __future__ import annotations

import math
from datetime import date, time
from typing import Any

import pandas as pd
import requests
import streamlit as st

APP_TITLE = "SYNAPSE MYSTIC NUMBER"
HORIZONS_API = "https://ssd.jpl.nasa.gov/api/horizons.api"
TIMEOUT_SECONDS = 25

# JPL Horizons target IDs. 399 is Earth; 500@399 is the geocenter.
BODIES = {
    "Sun": "10",
    "Moon": "301",
    "Mercury": "199",
    "Venus": "299",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899",
}
THAI_NAMES = {
    "Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
    "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสบดี",
    "Saturn": "ดาวเสาร์", "Uranus": "ดาวยูเรนัส", "Neptune": "ดาวเนปจูน",
}

st.set_page_config(page_title=APP_TITLE, page_icon="🌌", layout="wide")
st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at top, #132c51 0%, #071323 48%, #030811 100%); color: #edf4ff; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.block-container { padding-top: 1.6rem; max-width: 1250px; }
.hero { padding: 1.4rem 1.6rem; border: 1px solid #d6b86a; border-radius: 18px; background: linear-gradient(120deg,rgba(16,40,75,.95),rgba(4,12,25,.95)); margin-bottom: 1rem; }
.hero h1 { color: #f2d58a; letter-spacing: .04em; margin: 0; }
.hero p { color: #c4d5ee; margin-bottom: 0; }
.note { border-left: 3px solid #d6b86a; padding: .7rem 1rem; background: rgba(214,184,106,.08); border-radius: 6px; }
[data-testid="stMetric"] { background: rgba(18,39,68,.7); border: 1px solid rgba(214,184,106,.35); padding: 12px; border-radius: 12px; }
</style>
<div class="hero">
<h1>🌌 SYNAPSE MYSTIC NUMBER</h1>
<p>ระบบคำนวณจากเวกเตอร์ดาราศาสตร์จริงของ JPL Horizons • ไม่ใช้ข้อมูลจำลองหรือผลหวยย้อนหลัง</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="note"><b>หลักความโปร่งใส:</b> ค่าตำแหน่งและมุมมาจากข้อมูล JPL Horizons ส่วนเลข 00–99 เป็นเพียงการเข้ารหัสค่าที่คำนวณได้ตามกติกาที่เปิดเผย ไม่ใช่เลขที่ NASA รับรองหรือการทำนายผลหวย</div>""", unsafe_allow_html=True)


def _parse_horizons_vector(payload: dict[str, Any]) -> tuple[float, float, float, str]:
    """Parse first Cartesian vector row from a JPL Horizons JSON response."""
    if payload.get("error"):
        raise ValueError(str(payload["error"]))
    result = payload.get("result")
    if not isinstance(result, str):
        raise ValueError("คำตอบจาก JPL ไม่มีช่อง result ที่คาดไว้")
    if "$$SOE" not in result or "$$EOE" not in result:
        raise ValueError("JPL ไม่ส่งช่วงข้อมูลเวกเตอร์กลับมา อาจเป็นเวลาที่ไม่รองรับ")
    body = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0].strip()
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        raise ValueError("JPL ส่งข้อมูลเวกเตอร์ว่างกลับมา")
    # CSV vector table 2: JD, calendar date, X, Y, Z, VX, VY, VZ, ...
    import csv
    row = next(csv.reader([lines[0]], skipinitialspace=True))
    if len(row) < 5:
        raise ValueError(f"รูปแบบเวกเตอร์ JPL ไม่ครบคอลัมน์: {lines[0]}")
    try:
        jd = float(row[0])
        x, y, z = float(row[2]), float(row[3]), float(row[4])
    except (ValueError, IndexError) as exc:
        raise ValueError(f"อ่านเวกเตอร์จาก JPL ไม่สำเร็จ: {lines[0]}") from exc
    return x, y, z, f"JD(TDB) {jd:.8f}"


def fetch_body_vector(body_id: str, utc_iso: str) -> dict[str, Any]:
    params = {
        "format": "json",
        "COMMAND": f"'{body_id}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": "'500@399'",
        "TLIST": f"'{utc_iso}'",
        "TLIST_TYPE": "'CAL'",
        "REF_PLANE": "'ECLIPTIC'",
        "OUT_UNITS": "'AU-D'",
        "VEC_TABLE": "'2'",
        "CSV_FORMAT": "'YES'",
    }
    try:
        response = requests.get(HORIZONS_API, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"เชื่อมต่อ JPL Horizons ไม่สำเร็จ: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("JPL Horizons ส่งข้อมูลที่ไม่ใช่ JSON ที่อ่านได้") from exc

    x, y, z, jd_text = _parse_horizons_vector(payload)
    distance = math.sqrt(x*x + y*y + z*z)
    if not math.isfinite(distance) or distance == 0:
        raise ValueError(f"เวกเตอร์ของวัตถุ {body_id} ใช้งานไม่ได้")
    longitude = math.degrees(math.atan2(y, x)) % 360.0
    latitude = math.degrees(math.asin(max(-1.0, min(1.0, z / distance))))
    return {
        "body_id": body_id, "x_au": x, "y_au": y, "z_au": z,
        "distance_au": distance, "longitude_deg": longitude,
        "latitude_deg": latitude, "jd_text": jd_text,
    }


def angular_separation(a: dict[str, Any], b: dict[str, Any]) -> float:
    """Angle between two Earth-centered direction vectors, in degrees."""
    av = (a["x_au"], a["y_au"], a["z_au"])
    bv = (b["x_au"], b["y_au"], b["z_au"])
    an = math.sqrt(sum(v*v for v in av))
    bn = math.sqrt(sum(v*v for v in bv))
    cosine = sum(av[i] * bv[i] for i in range(3)) / (an * bn)
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def encode_00_99(value_degrees: float) -> str:
    """Fixed disclosed encoding: rounded hundredths of a degree, modulo 100."""
    return f"{int(math.floor(value_degrees * 100.0 + 0.5)) % 100:02d}"

with st.sidebar:
    st.header("ตั้งค่าการคำนวณ")
    chosen_date = st.date_input("วันที่", value=date.today())
    chosen_time = st.time_input("เวลา UTC", value=time(0, 0))
    st.caption("เวลาที่ป้อนเป็น UTC ไม่ใช่เวลาไทย (ICT)")
    run = st.button("ดึงข้อมูลจริงและคำนวณ", type="primary", use_container_width=True)
    st.divider()
    st.markdown("**แหล่งข้อมูล**")
    st.markdown("[JPL Horizons API](https://ssd-api.jpl.nasa.gov/doc/horizons.html)")
    st.markdown("[คู่มือระบบ Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html)")

st.subheader("ข้อมูลดาราศาสตร์")
st.write("ระบบจะดึงเวกเตอร์ตำแหน่งแบบ geocentric จาก JPL Horizons ในระนาบสุริยวิถี (ECLIPTIC) ณ เวลา UTC ที่เลือก")

if run:
    utc_iso = f"{chosen_date.isoformat()} {chosen_time.strftime('%H:%M')}"
    results: dict[str, dict[str, Any]] = {}
    progress = st.progress(0, text="กำลังขอข้อมูลจาก JPL Horizons...")
    try:
        for index, (body, body_id) in enumerate(BODIES.items(), start=1):
            progress.progress((index - 1) / len(BODIES), text=f"กำลังดึงข้อมูล: {THAI_NAMES[body]} ({index}/{len(BODIES)})")
            results[body] = fetch_body_vector(body_id, utc_iso)
        progress.progress(1.0, text="ได้รับข้อมูลจาก JPL Horizons ครบแล้ว")
    except Exception as exc:
        progress.empty()
        st.error(f"หยุดการคำนวณ: {exc}")
        st.warning("ไม่มีการใช้ข้อมูลจำลองหรือค่าทดแทน หากดึงข้อมูลจริงไม่สำเร็จ ระบบจะไม่แสดงผลเลข")
        st.stop()

    st.success(f"รับข้อมูลจาก JPL Horizons ครบ {len(results)} วัตถุ ณ {utc_iso} UTC")
    st.caption("เวลามาตรฐานจากคำตอบ JPL: " + results["Sun"]["jd_text"])

    rows = []
    for body, item in results.items():
        rows.append({
            "วัตถุ": THAI_NAMES[body], "JPL target ID": item["body_id"],
            "X (AU)": item["x_au"], "Y (AU)": item["y_au"], "Z (AU)": item["z_au"],
            "ระยะจากโลก (AU)": item["distance_au"],
            "ลองจิจูดสุริยวิถี (°)": item["longitude_deg"],
            "ละติจูดสุริยวิถี (°)": item["latitude_deg"],
            "รหัสจากลองจิจูด 00–99": encode_00_99(item["longitude_deg"]),
        })
    df = pd.DataFrame(rows)
    st.subheader("ตำแหน่งจริงและรหัสที่คำนวณได้")
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     "X (AU)": st.column_config.NumberColumn(format="%.9f"),
                     "Y (AU)": st.column_config.NumberColumn(format="%.9f"),
                     "Z (AU)": st.column_config.NumberColumn(format="%.9f"),
                     "ระยะจากโลก (AU)": st.column_config.NumberColumn(format="%.9f"),
                     "ลองจิจูดสุริยวิถี (°)": st.column_config.NumberColumn(format="%.6f"),
                     "ละติจูดสุริยวิถี (°)": st.column_config.NumberColumn(format="%.6f"),
                 })

    st.subheader("มุมระหว่างวัตถุ")
    pair_rows = []
    bodies = list(results.keys())
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            first, second = bodies[i], bodies[j]
            angle = angular_separation(results[first], results[second])
            pair_rows.append({
                "วัตถุ A": THAI_NAMES[first], "วัตถุ B": THAI_NAMES[second],
                "มุมระหว่างทิศทาง (°)": angle,
                "รหัสมุม 00–99": encode_00_99(angle),
            })
    angle_df = pd.DataFrame(pair_rows)
    st.dataframe(angle_df, use_container_width=True, hide_index=True,
                 column_config={"มุมระหว่างทิศทาง (°)": st.column_config.NumberColumn(format="%.6f")})

    st.subheader("สูตรที่ใช้ — เปิดเผยทุกขั้นตอน")
    st.markdown("""
**ตำแหน่ง:** รับเวกเตอร์ \((x,y,z)\) หน่วย AU จาก JPL Horizons โดยอ้างอิงศูนย์กลางโลกและระนาบ ECLIPTIC

**ลองจิจูดสุริยวิถี:**
\[
\lambda = (\operatorname{atan2}(y,x)\times 180/\pi)\bmod 360
\]

**ละติจูดสุริยวิถี:**
\[
\beta = \arcsin\left(\frac{z}{\sqrt{x^2+y^2+z^2}}\right)\times 180/\pi
\]

**มุมระหว่างวัตถุสองดวง:**
\[
\theta = \arccos\left(\frac{\vec a\cdot\vec b}{|\vec a||\vec b|}\right)\times 180/\pi
\]

**กติกาเข้ารหัสเลขสองหลัก:** \(N = \lfloor 100v + 0.5\rfloor \bmod 100\) แล้วแสดงเป็นเลขสองหลัก โดย \(v\) คือค่าลองจิจูดหรือมุมเป็นองศา

กติกานี้เป็นการเข้ารหัสค่าดาราศาสตร์ที่วัด/คำนวณได้อย่างแน่นอน ไม่ใช่สูตรทางดาราศาสตร์ที่พิสูจน์แล้วว่าสามารถทำนายผลหวยได้
""")

    st.download_button("ดาวน์โหลดตำแหน่งดาว CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"jpl_positions_{chosen_date.isoformat()}_{chosen_time.strftime('%H%M')}UTC.csv",
                       mime="text/csv")
    st.download_button("ดาวน์โหลดมุมระหว่างวัตถุ CSV", data=angle_df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"jpl_angles_{chosen_date.isoformat()}_{chosen_time.strftime('%H%M')}UTC.csv",
                       mime="text/csv")
else:
    st.info("เลือกวันที่และเวลา UTC จากแถบด้านซ้าย แล้วกด ‘ดึงข้อมูลจริงและคำนวณ’ เพื่อเรียกข้อมูลสดจาก JPL Horizons")
    st.markdown("**ไม่มีผลตัวเลขตัวอย่างแสดงไว้ล่วงหน้า** เพราะต้องการให้ทุกผลที่เห็นเกิดจากการดึงข้อมูลจริงในเวลาที่คุณสั่งคำนวณเท่านั้น")

st.divider()
st.caption("ข้อมูลแหล่งที่มา: NASA/JPL Solar System Dynamics — Horizons. ผลลัพธ์ขึ้นกับเวลาที่เลือกและพารามิเตอร์คำขอ; การให้บริการ API เป็นแบบ best effort.")
