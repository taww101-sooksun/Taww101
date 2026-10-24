
"""SYNAPSE MYSTIC NUMBER
ระบบคำนวณจากข้อมูลดาราศาสตร์ JPL Horizons และสมดุลทองคำ
ไม่ใช้ข้อมูลจำลอง ไม่สุ่มตัวเลข และไม่ใช้ผลหวยย้อนหลัง
"""

from __future__ import annotations

import csv
import math
from datetime import date, time
from typing import Any

import pandas as pd
import requests
import streamlit as st


# =========================================================
# 1. ตั้งค่าแอป
# =========================================================

APP_TITLE = "SYNAPSE MYSTIC NUMBER"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
HORIZONS_API = "https://ssd.jpl.nasa.gov/api/horizons.api"
TIMEOUT_SECONDS = 30

BODIES = {
    "ดวงอาทิตย์": "10",
    "ดวงจันทร์": "301",
    "ดาวพุธ": "199",
    "ดาวศุกร์": "299",
    "ดาวอังคาร": "499",
    "ดาวพฤหัสบดี": "599",
    "ดาวเสาร์": "699",
    "ดาวยูเรนัส": "799",
    "ดาวเนปจูน": "899",
}

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌌",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(
            ellipse at top,
            #132c51 0%,
            #071323 48%,
            #030811 100%
        );
        color: #edf4ff;
    }
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    .block-container {
        padding-top: 1.5rem;
        max-width: 1300px;
    }
    .hero {
        padding: 1.5rem;
        border: 1px solid #d6b86a;
        border-radius: 18px;
        background: linear-gradient(
            120deg,
            rgba(16,40,75,.95),
            rgba(4,12,25,.95)
        );
        margin-bottom: 1rem;
    }
    .hero h1 {
        color: #f2d58a;
        margin: 0;
    }
    .hero p {
        color: #c4d5ee;
        margin-bottom: 0;
    }
    .note {
        border-left: 3px solid #d6b86a;
        padding: .8rem 1rem;
        background: rgba(214,184,106,.08);
        border-radius: 6px;
    }
    [data-testid="stMetric"] {
        background: rgba(18,39,68,.7);
        border: 1px solid rgba(214,184,106,.35);
        padding: 12px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🌌 SYNAPSE MYSTIC NUMBER</h1>
        <p>
        REAL ASTRONOMICAL DATA · JPL HORIZONS · GOLDEN RATIO BALANCE
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note">
    <b>หลักการ:</b>
    ใช้ข้อมูลเวกเตอร์จาก JPL Horizons ตามเวลาที่เลือก
    คำนวณตำแหน่งและมุมด้วยสมการทางคณิตศาสตร์
    ใช้ค่าอัตราส่วนทองคำ φ ในการสร้างจุดแบ่งบนส่วนโค้ง
    และแสดงรหัสที่ได้แยกจากค่าดาราศาสตร์จริง
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 2. อ่านข้อมูลเวกเตอร์จาก JPL Horizons
# =========================================================

def parse_horizons_vector(
    payload: dict[str, Any],
) -> tuple[float, float, float, float]:
    """อ่านแถวเวกเตอร์ XYZ จากคำตอบ JSON ของ JPL Horizons."""

    if payload.get("error"):
        raise ValueError(str(payload["error"]))

    result = payload.get("result")

    if not isinstance(result, str):
        raise ValueError("คำตอบจาก JPL ไม่มีข้อมูล result")

    if "$$SOE" not in result or "$$EOE" not in result:
        raise ValueError(
            "ไม่พบข้อมูลเวกเตอร์ในคำตอบ JPL "
            "โปรดตรวจวันที่ เวลา หรือพารามิเตอร์"
        )

    section = result.split("$$SOE", 1)[1]
    section = section.split("$$EOE", 1)[0].strip()

    lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError("JPL ส่งข้อมูลเวกเตอร์ว่างกลับมา")

    row = next(
        csv.reader([lines[0]], skipinitialspace=True)
    )

    if len(row) < 5:
        raise ValueError(
            f"จำนวนคอลัมน์เวกเตอร์ไม่ครบ: {lines[0]}"
        )

    try:
        jd = float(row[0])
        x = float(row[2])
        y = float(row[3])
        z = float(row[4])
    except (ValueError, IndexError) as exc:
        raise ValueError(
            f"อ่านค่าเวกเตอร์ไม่สำเร็จ: {lines[0]}"
        ) from exc

    return x, y, z, jd


def fetch_body_vector(
    body_id: str,
    utc_iso: str,
) -> dict[str, Any]:
    """ดึงเวกเตอร์ตำแหน่งจาก JPL Horizons API."""

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
        response = requests.get(
            HORIZONS_API,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"เชื่อมต่อ JPL Horizons ไม่สำเร็จ: {exc}"
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "คำตอบจาก JPL ไม่ใช่ JSON ที่อ่านได้"
        ) from exc

    x, y, z, jd = parse_horizons_vector(payload)

    distance = math.sqrt(x * x + y * y + z * z)

    if not math.isfinite(distance) or distance == 0:
        raise ValueError(
            f"เวกเตอร์ของวัตถุ {body_id} ไม่ถูกต้อง"
        )

    longitude = math.degrees(
        math.atan2(y, x)
    ) % 360.0

    latitude = math.degrees(
        math.asin(
            max(-1.0, min(1.0, z / distance))
        )
    )

    return {
        "body_id": body_id,
        "x_au": x,
        "y_au": y,
        "z_au": z,
        "distance_au": distance,
        "longitude_deg": longitude,
        "latitude_deg": latitude,
        "julian_date_tdb": jd,
    }


# =========================================================
# 3. สมการทางคณิตศาสตร์
# =========================================================

def angular_separation(
    a: dict[str, Any],
    b: dict[str, Any],
) -> float:
    """มุมระหว่างทิศทางเวกเตอร์สองตัว หน่วยองศา."""

    av = (
        a["x_au"],
        a["y_au"],
        a["z_au"],
    )

    bv = (
        b["x_au"],
        b["y_au"],
        b["z_au"],
    )

    norm_a = math.sqrt(sum(v * v for v in av))
    norm_b = math.sqrt(sum(v * v for v in bv))

    if norm_a == 0 or norm_b == 0:
        raise ValueError("เวกเตอร์มีความยาวเป็นศูนย์")

    dot_product = sum(
        av[i] * bv[i]
        for i in range(3)
    )

    cosine = dot_product / (norm_a * norm_b)
    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


def signed_shortest_arc(
    start_deg: float,
    end_deg: float,
) -> float:
    """ส่วนต่างมุมสั้นที่สุด อยู่ในช่วง [-180, 180)."""

    return (
        (end_deg - start_deg + 180.0) % 360.0
    ) - 180.0


def golden_balance_longitude(
    start_deg: float,
    end_deg: float,
) -> tuple[float, float, float]:
    """
    คืนค่า:
    จุดกึ่งกลางทั่วไป,
    จุดแบ่งทองคำ,
    ส่วนต่างมุมที่สั้นที่สุด

    จุดทองคำอยู่ที่ 1/φ หรือประมาณ 61.803%
    ของส่วนโค้งสั้นที่สุดจากจุดเริ่มต้นไปจุดปลายทาง
    """

    arc = signed_shortest_arc(
        start_deg,
        end_deg,
    )

    midpoint = (
        start_deg + arc / 2.0
    ) % 360.0

    golden_point = (
        start_deg + arc / PHI
    ) % 360.0

    return midpoint, golden_point, arc


def encode_00_99(value_degrees: float) -> str:
    """
    กติกาเข้ารหัสที่เปิดเผย:
    ปัดค่าองศา x 100 เป็นจำนวนเต็ม
    แล้วหาเศษจากการหารด้วย 100
    """

    if not math.isfinite(value_degrees):
        raise ValueError("ค่าที่นำมาเข้ารหัสไม่ใช่จำนวนจริง")

    number = math.floor(
        value_degrees * 100.0 + 0.5
    )

    return f"{int(number) % 100:02d}"


# =========================================================
# 4. แถบตั้งค่าด้านข้าง
# =========================================================

with st.sidebar:
    st.header("ตั้งค่าการคำนวณ")

    chosen_date = st.date_input(
        "วันที่",
        value=date.today(),
    )

    chosen_time = st.time_input(
        "เวลา UTC",
        value=time(0, 0),
    )

    st.caption(
        "เวลาที่ระบุเป็น UTC ไม่ใช่เวลาไทย "
        "(เวลาไทยเร็วกว่า UTC 7 ชั่วโมง)"
    )

    run = st.button(
        "ดึงข้อมูลจริงและคำนวณ",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    st.markdown("### แหล่งข้อมูล")

    st.markdown(
        "[JPL Horizons API]"
        "(https://ssd.jpl.nasa.gov/api/horizons.api)"
    )

    st.markdown(
        "[เอกสาร API]"
        "(https://ssd-api.jpl.nasa.gov/doc/horizons.html)"
    )


# =========================================================
# 5. ดึงข้อมูลและแสดงผล
# =========================================================

st.subheader("ข้อมูลดาราศาสตร์")

st.write(
    "ระบบจะขอเวกเตอร์ตำแหน่งจาก JPL Horizons "
    "โดยอ้างอิงศูนย์กลางโลกและระนาบสุริยวิถี "
    "ณ วันและเวลา UTC ที่คุณเลือก"
)

if not run:
    st.info(
        "เลือกวันและเวลาในแถบด้านซ้าย "
        "แล้วกดปุ่มดึงข้อมูลจริงและคำนวณ"
    )

    st.warning(
        "ก่อนกดคำนวณจะไม่มีการแสดงเลขตัวอย่าง "
        "และไม่มีการสร้างข้อมูลดาวขึ้นมาเอง"
    )

else:
    utc_iso = (
        f"{chosen_date.isoformat()} "
        f"{chosen_time.strftime('%H:%M')}"
    )

    results: dict[str, dict[str, Any]] = {}

    progress = st.progress(
        0,
        text="กำลังติดต่อ JPL Horizons...",
    )

    try:
        total = len(BODIES)

        for index, (name, body_id) in enumerate(
            BODIES.items(),
            start=1,
        ):
            progress.progress(
                (index - 1) / total,
                text=f"กำลังดึงข้อมูล {name} ({index}/{total})",
            )

            results[name] = fetch_body_vector(
                body_id,
                utc_iso,
            )

        progress.progress(
            1.0,
            text="ได้รับข้อมูลครบแล้ว",
        )

    except Exception as exc:
        progress.empty()

        st.error(
            f"ไม่สามารถคำนวณจากข้อมูลจริงได้: {exc}"
        )

        st.warning(
            "ระบบหยุดทำงานโดยไม่ใช้ข้อมูลจำลอง "
            "โปรดตรวจการเชื่อมต่ออินเทอร์เน็ต "
            "และลองใหม่ภายหลัง"
        )

        st.stop()

    st.success(
        f"ดึงข้อมูลจาก JPL Horizons สำเร็จ "
        f"{len(results)} วัตถุ"
    )

    st.caption(f"เวลาอ้างอิง UTC: {utc_iso}")

    jd_values = [
        item["julian_date_tdb"]
        for item in results.values()
    ]

    st.caption(
        "Julian Date (TDB) จากข้อมูล JPL: "
        + ", ".join(f"{v:.8f}" for v in jd_values[:2])
        + " ..."
    )

    # -----------------------------------------------------
    # 5A. ตารางตำแหน่งดาว
    # -----------------------------------------------------

    st.subheader("1. ตำแหน่งจากเวกเตอร์จริง")

    position_rows = []

    for name, item in results.items():
        position_rows.append({
            "วัตถุ": name,
            "JPL Target ID": item["body_id"],
            "X (AU)": item["x_au"],
            "Y (AU)": item["y_au"],
            "Z (AU)": item["z_au"],
            "ระยะจากโลก (AU)": item["distance_au"],
            "ลองจิจูดสุริยวิถี (องศา)": item["longitude_deg"],
            "ละติจูดสุริยวิถี (องศา)": item["latitude_deg"],
            "รหัสจากลองจิจูด": encode_00_99(
                item["longitude_deg"]
            ),
        })

    position_df = pd.DataFrame(position_rows)

    st.dataframe(
        position_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "X (AU)": st.column_config.NumberColumn(
                format="%.9f"
            ),
            "Y (AU)": st.column_config.NumberColumn(
                format="%.9f"
            ),
            "Z (AU)": st.column_config.NumberColumn(
                format="%.9f"
            ),
            "ระยะจากโลก (AU)": st.column_config.NumberColumn(
                format="%.9f"
            ),
            "ลองจิจูดสุริยวิถี (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
            "ละติจูดสุริยวิถี (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
        },
    )

    # -----------------------------------------------------
    # 5B. มุมระหว่างวัตถุทุกคู่
    # -----------------------------------------------------

    st.subheader("2. มุมระหว่างวัตถุ")

    angle_rows = []
    names = list(results.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a = names[i]
            name_b = names[j]

            angle = angular_separation(
                results[name_a],
                results[name_b],
            )

            angle_rows.append({
                "วัตถุ A": name_a,
                "วัตถุ B": name_b,
                "มุมระหว่างทิศทาง (องศา)": angle,
                "รหัสมุม 00–99": encode_00_99(angle),
            })

    angle_df = pd.DataFrame(angle_rows)

    st.dataframe(
        angle_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "มุมระหว่างทิศทาง (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            )
        },
    )

    # -----------------------------------------------------
    # 5C. ระบบสมดุลทองคำ
    # -----------------------------------------------------

    st.subheader("3. ระบบสมดุลทองคำ φ")

    st.markdown(
        r"""
        ค่าอัตราส่วนทองคำมีนิยามว่า

        \[
        \varphi = \frac{1+\sqrt{5}}{2}
        \approx 1.6180339887
        \]

        ระบบนี้หาจุดแบ่งระหว่างลองจิจูดของวัตถุสองดวง
        บนส่วนโค้งที่สั้นที่สุดของวงกลม 360 องศา
        จุดแบ่งทองคำอยู่ที่ประมาณ 61.803% ของส่วนโค้ง
        จากวัตถุ A ไปวัตถุ B
        """
    )

    balance_rows = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a = names[i]
            name_b = names[j]

            lon_a = results[name_a]["longitude_deg"]
            lon_b = results[name_b]["longitude_deg"]

            midpoint, golden_point, arc = (
                golden_balance_longitude(
                    lon_a,
                    lon_b,
                )
            )

            balance_rows.append({
                "วัตถุ A": name_a,
                "ลองจิจูด A (องศา)": lon_a,
                "วัตถุ B": name_b,
                "ลองจิจูด B (องศา)": lon_b,
                "ส่วนโค้งสั้น A→B (องศา)": arc,
                "จุดกึ่งกลาง (องศา)": midpoint,
                "จุดสมดุลทองคำ (องศา)": golden_point,
                "รหัสสมดุล 00–99": encode_00_99(
                    golden_point
                ),
            })

    balance_df = pd.DataFrame(balance_rows)

    st.dataframe(
        balance_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ลองจิจูด A (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
            "ลองจิจูด B (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
            "ส่วนโค้งสั้น A→B (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
            "จุดกึ่งกลาง (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
            "จุดสมดุลทองคำ (องศา)": (
                st.column_config.NumberColumn(
                    format="%.6f"
                )
            ),
        },
    )

    # -----------------------------------------------------
    # 5D. อธิบายสูตร
    # -----------------------------------------------------

    with st.expander("ดูสูตรคำนวณทั้งหมด"):
        st.markdown(
            r"""
            **ลองจิจูดสุริยวิถี**

            \[
            \lambda =
            \left(
            \operatorname{atan2}(y,x)
            \frac{180}{\pi}
            \right)\bmod 360
            \]

            **ละติจูดสุริยวิถี**

            \[
            \beta =
            \arcsin\left(
            \frac{z}{\sqrt{x^2+y^2+z^2}}
            \right)\frac{180}{\pi}
            \]

            **มุมระหว่างเวกเตอร์**

            \[
            \theta =
            \arccos\left(
            \frac{\vec a\cdot\vec b}
            {|\vec a||\vec b|}
            \right)\frac{180}{\pi}
            \]

            **ส่วนต่างมุมที่สั้นที่สุด**

            \[
            d=((B-A+180)\bmod360)-180
            \]

            **จุดกึ่งกลางทั่วไป**

            \[
            M=(A+d/2)\bmod360
            \]

            **จุดแบ่งทองคำ**

            \[
            G=(A+d/\varphi)\bmod360
            \]

            **กติกาสร้างรหัสสองหลัก**

            \[
            N=\lfloor100v+0.5\rfloor\bmod100
            \]

            โดย \(v\) คือค่ามุมองศาที่นำมาเข้ารหัส
            รหัสสองหลักเป็นผลจากกติกาคณิตศาสตร์ของแอป
            ไม่ใช่ข้อมูลเลขหวยจาก NASA
            """
        )

    # -----------------------------------------------------
    # 5E. ดาวน์โหลด CSV
    # -----------------------------------------------------

    st.subheader("4. ดาวน์โหลดผลคำนวณ")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "ดาวน์โหลดตำแหน่งดาว CSV",
            data=position_df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name=(
                f"jpl_positions_{chosen_date.isoformat()}.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "ดาวน์โหลดมุมดาว CSV",
            data=angle_df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name=(
                f"jpl_angles_{chosen_date.isoformat()}.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        st.download_button(
            "ดาวน์โหลดสมดุลทองคำ CSV",
            data=balance_df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name=(
                f"golden_balance_{chosen_date.isoformat()}.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

    # -----------------------------------------------------
    # 5F. คำอธิบายข้อจำกัด
    # -----------------------------------------------------

    st.info(
        "ตำแหน่งและมุมเป็นค่าที่คำนวณจากเวกเตอร์ JPL "
        "ตามเวลาและระบบพิกัดที่กำหนด "
        "ส่วนจุดสมดุลทองคำเป็นการสร้างค่าทางคณิตศาสตร์ "
        "ยังไม่มีหลักฐานว่าค่านี้ทำนายผลหวยได้"
    )


# =========================================================
# 6. ท้ายหน้า
# =========================================================

st.divider()

st.caption(
    "SYNAPSE MYSTIC NUMBER | "
    "แหล่งข้อมูล: NASA/JPL Solar System Dynamics — Horizons. "
    "ผลขึ้นกับเวลาและพารามิเตอร์ที่ใช้ดึงข้อมูล"
                      )
