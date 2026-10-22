import math
import sqlite3
from pathlib import Path
from datetime import date, datetime
from itertools import combinations

import pandas as pd
import streamlit as st


# =========================================================
# SYNAPSE MYSTIC NUMBER
# Version 1.0
# =========================================================

APP_TITLE = "SYNAPSE MYSTIC NUMBER"
DB_PATH = Path("synapse_mystic.db")

PLANETS = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
]

PLANET_TH = {
    "Sun": "ดวงอาทิตย์",
    "Moon": "ดวงจันทร์",
    "Mercury": "ดาวพุธ",
    "Venus": "ดาวศุกร์",
    "Mars": "ดาวอังคาร",
    "Jupiter": "ดาวพฤหัสบดี",
    "Saturn": "ดาวเสาร์",
    "Uranus": "ดาวยูเรนัส",
    "Neptune": "ดาวเนปจูน",
}


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# COSMIC THEME
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top right,
                #18295b 0%,
                #090f26 45%,
                #030711 100%
            );
        color: #f5f0dc;
    }

    [data-testid="stSidebar"] {
        background: #080d20;
        border-right: 1px solid #c9a85c;
    }

    h1, h2, h3 {
        color: #f1cf78 !important;
    }

    p, label, span {
        color: #e9e8f5;
    }

    .cosmic-card {
        background: rgba(19, 29, 62, 0.88);
        border: 1px solid #a88c4d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 0 18px rgba(201, 168, 92, 0.08);
    }

    .gold-text {
        color: #f1cf78;
        font-weight: bold;
    }

    .big-number {
        color: #f1cf78;
        font-size: 56px;
        font-weight: 800;
        text-align: center;
        letter-spacing: 8px;
    }

    .muted {
        color: #b8bfd8;
        font-size: 13px;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #b08b3d, #e8cd7c);
        color: #11162b;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        min-height: 42px;
    }

    div.stButton > button:hover {
        background: #f7df97;
        color: #11162b;
        border: 1px solid #fff0b5;
    }

    div[data-testid="stMetric"] {
        background: rgba(22, 33, 69, 0.85);
        border: 1px solid #75643e;
        padding: 14px;
        border-radius: 12px;
    }

    hr {
        border-color: #665b43;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                target_date TEXT NOT NULL,
                weekday TEXT NOT NULL,
                result_number TEXT NOT NULL,
                date_value INTEGER,
                weekday_value INTEGER,
                planet_value INTEGER,
                angle_value INTEGER,
                moon_value INTEGER,
                astronomy_status TEXT
            )
            """
        )


def save_calculation(record):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO calculations (
                created_at,
                target_date,
                weekday,
                result_number,
                date_value,
                weekday_value,
                planet_value,
                angle_value,
                moon_value,
                astronomy_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["created_at"],
                record["target_date"],
                record["weekday"],
                record["result_number"],
                record["date_value"],
                record["weekday_value"],
                record["planet_value"],
                record["angle_value"],
                record["moon_value"],
                record["astronomy_status"],
            ),
        )


def load_history():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT *
            FROM calculations
            ORDER BY id DESC
            """,
            conn,
        )


initialize_database()


# =========================================================
# CALENDAR
# =========================================================

THAI_WEEKDAYS = [
    "วันจันทร์",
    "วันอังคาร",
    "วันพุธ",
    "วันพฤหัสบดี",
    "วันศุกร์",
    "วันเสาร์",
    "วันอาทิตย์",
]


def weekday_name(target_date):
    return THAI_WEEKDAYS[target_date.weekday()]


def date_digit_sum(target_date):
    digits = target_date.strftime("%Y%m%d")
    return sum(int(ch) for ch in digits)


def digital_root(number):
    if number == 0:
        return 0

    while number > 9:
        number = sum(int(ch) for ch in str(number))

    return number


# =========================================================
# ASTRONOMY
# =========================================================

@st.cache_resource(show_spinner=False)
def load_ephemeris():
    """
    Load Skyfield's DE421 ephemeris.
    The first successful load may require internet access.
    """
    from skyfield.api import load

    eph = load("de421.bsp")
    timescale = load.timescale()

    return eph, timescale


def calculate_planet_positions(target_date):
    """
    Calculate approximate geocentric apparent ecliptic longitudes.

    Results are returned in degrees from 0 to less than 360.
    This calculation requires Skyfield and a downloaded ephemeris.
    """
    from skyfield.api import load

    eph, timescale = load_ephemeris()

    year = target_date.year
    month = target_date.month
    day = target_date.day

    # Use noon UTC to represent the selected calendar date.
    t = timescale.utc(year, month, day, 12, 0, 0)

    earth = eph["earth"]

    body_keys = {
        "Sun": "sun",
        "Moon": "moon",
        "Mercury": "mercury",
        "Venus": "venus",
        "Mars": "mars",
        "Jupiter": "jupiter barycenter",
        "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter",
        "Neptune": "neptune barycenter",
    }

    positions = {}

    for planet in PLANETS:
        body = eph[body_keys[planet]]
        apparent = earth.at(t).observe(body).apparent()

        # Ecliptic longitude, measured in degrees.
        _, longitude, _ = apparent.ecliptic_latlon(epoch="date")

        positions[planet] = float(longitude.degrees) % 360.0

    return positions


def angular_separation(longitude_a, longitude_b):
    """
    Smallest separation between two ecliptic longitudes.
    Result ranges from 0 to 180 degrees.
    """
    difference = abs(longitude_a - longitude_b) % 360.0
    return min(difference, 360.0 - difference)


def calculate_angular_table(positions):
    rows = []

    for first, second in combinations(positions.keys(), 2):
        separation = angular_separation(
            positions[first],
            positions[second],
        )

        rows.append(
            {
                "ดาวดวงที่ 1": PLANET_TH[first],
                "ดาวดวงที่ 2": PLANET_TH[second],
                "ระยะห่างเชิงมุม (องศา)": round(separation, 4),
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# EXPERIMENTAL NUMBER FORMULA
# =========================================================

def calculate_number(target_date, positions):
    """
    Fixed experimental formula.

    D = digital root of YYYYMMDD
    W = weekday code, Monday=1 through Sunday=7
    P = weighted sum of planetary longitudes, scaled by 100
    A = sum of pairwise longitude separations, scaled by 100
    M = Moon longitude, scaled by 100

    Final result = (3D + 2W + P + A + M) mod 100

    This is an experimental number transformation.
    It is not a scientifically validated lottery prediction.
    """

    date_value = digital_root(date_digit_sum(target_date))
    weekday_value = target_date.weekday() + 1

    if not positions:
        return None

    weighted_longitudes = sum(
        (index + 1) * positions[planet]
        for index, planet in enumerate(PLANETS)
    )

    planet_value = round(weighted_longitudes * 100) % 100

    all_separations = [
        angular_separation(
            positions[first],
            positions[second],
        )
        for first, second in combinations(PLANETS, 2)
    ]

    angle_value = round(sum(all_separations) * 100) % 100

    moon_value = round(positions["Moon"] * 100) % 100

    result = (
        3 * date_value
        + 2 * weekday_value
        + planet_value
        + angle_value
        + moon_value
    ) % 100

    return {
        "result_number": f"{result:02d}",
        "date_value": date_value,
        "weekday_value": weekday_value,
        "planet_value": planet_value,
        "angle_value": angle_value,
        "moon_value": moon_value,
    }


# =========================================================
# LOTTERY HISTORY CSV
# =========================================================

def normalize_number(value):
    """
    Keep lottery numbers as text to preserve leading zeroes.
    """
    if pd.isna(value):
        return None

    text_value = str(value).strip()

    if text_value.endswith(".0"):
        text_value = text_value[:-2]

    if not text_value.isdigit():
        return None

    return text_value


def analyze_lottery_csv(uploaded_file):
    df = pd.read_csv(
        uploaded_file,
        dtype=str,
        keep_default_na=False,
    )

    df.columns = [column.strip().lower() for column in df.columns]

    required = {"date", "lottery", "category", "number"}
    missing = required - set(df.columns)

    if missing:
        return None, (
            "ไฟล์ CSV ต้องมีคอลัมน์: date, lottery, category, number "
            f"โดยยังขาด: {', '.join(sorted(missing))}"
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["number"] = df["number"].apply(normalize_number)

    df = df.dropna(subset=["date", "number"]).copy()

    df["lottery"] = df["lottery"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()

    df = df[
        (df["lottery"] != "")
        & (df["category"] != "")
        & (df["number"] != "")
    ].copy()

    if df.empty:
        return None, "ไม่พบแถวข้อมูลที่ใช้งานได้ในไฟล์ CSV"

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    df["last_two_digits"] = df["number"].apply(
        lambda value: value[-2:].zfill(2)
    )

    return df, None


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("# 🌌 SYNAPSE")
st.sidebar.markdown("### MYSTIC NUMBER")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "เลือกเมนู",
    [
        "หน้าหลัก",
        "คำนวณดวงดาว",
        "วิเคราะห์ผลย้อนหลัง",
        "ประวัติการคำนวณ",
        "เกี่ยวกับระบบ",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("COSMIC NUMEROLOGY LAB")
st.sidebar.caption("Experimental • Transparent • Reproducible")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="cosmic-card">
        <div style="font-size:14px; color:#c9b77d;">
            COSMIC DATA • ASTRONOMY • NUMBER ANALYSIS
        </div>
        <h1 style="font-size:34px;">
            🌌 SYNAPSE MYSTIC NUMBER
        </h1>
        <div style="color:#c5cbe1;">
            สำรวจความสัมพันธ์ระหว่างวันที่ ตำแหน่งดาว
            และการแปลงข้อมูลเป็นตัวเลข
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PAGE: HOME
# =========================================================

if page == "หน้าหลัก":

    st.subheader("📅 เลือกวันที่สำหรับคำนวณ")

    selected_date = st.date_input(
        "วันที่ต้องการวิเคราะห์",
        value=date.today(),
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("วันที่", selected_date.strftime("%d/%m/%Y"))

    with col2:
        st.metric("วันในสัปดาห์", weekday_name(selected_date))

    with col3:
        st.metric("ผลรวมตัวเลขวันที่", date_digit_sum(selected_date))

    st.info(
        "ระบบจะใช้เวลา 12:00 UTC เป็นเวลาอ้างอิงของวันที่เลือก "
        "เพื่อให้การคำนวณแต่ละครั้งมีหลักเกณฑ์เดียวกัน"
    )

    if st.button("🪐 คำนวณวันที่และตำแหน่งดาว", use_container_width=True):

        with st.spinner("กำลังคำนวณข้อมูลดาราศาสตร์..."):
            try:
                positions = calculate_planet_positions(selected_date)

                formula = calculate_number(
                    selected_date,
                    positions,
                )

                st.session_state["last_positions"] = positions
                st.session_state["last_formula"] = formula
                st.session_state["last_date"] = selected_date.isoformat()
                st.session_state["last_astronomy_status"] = "สำเร็จ"

                st.success("คำนวณตำแหน่งดาวเรียบร้อยแล้ว")

            except Exception as exc:
                st.session_state["last_positions"] = None
                st.session_state["last_formula"] = None
                st.session_state["last_date"] = selected_date.isoformat()
                st.session_state["last_astronomy_status"] = "ไม่สำเร็จ"

                st.error(
                    "ยังคำนวณตำแหน่งดาวไม่ได้ "
                    "ตรวจสอบการติดตั้งไลบรารีและการเชื่อมต่ออินเทอร์เน็ต"
                )

                st.caption(f"รายละเอียดสำหรับตรวจสอบ: {exc}")

    if (
        st.session_state.get("last_date") == selected_date.isoformat()
        and st.session_state.get("last_formula")
    ):
        formula = st.session_state["last_formula"]

        st.markdown("---")
        st.subheader("🔢 ผลลัพธ์จากสูตรทดลอง")

        st.markdown(
            f"""
            <div class="cosmic-card">
                <div style="text-align:center;">
                    <div style="color:#c9b77d;">
                        EXPERIMENTAL TWO-DIGIT OUTPUT
                    </div>
                    <div class="big-number">
                        {formula["result_number"]}
                    </div>
                    <div class="muted">
                        ไม่ใช่คำรับประกันผลสลาก
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)

        a.metric("ค่า D: วันที่", formula["date_value"])
        b.metric("ค่า W: วันในสัปดาห์", formula["weekday_value"])
        c.metric("ค่า P: ตำแหน่งดาว", formula["planet_value"])

        d, e = st.columns(2)

        d.metric("ค่า A: ระยะห่างเชิงมุม", formula["angle_value"])
        e.metric("ค่า M: ตำแหน่งดวงจันทร์", formula["moon_value"])

        with st.expander("ดูสูตรที่ใช้คำนวณ"):
            st.code(
                "ผลลัพธ์ = "
                "(3D + 2W + P + A + M) % 100"
            )

            st.write(
                "D = ผลรวมตัวเลขวันที่ที่ย่อเป็นเลขหลักเดียว"
            )
            st.write(
                "W = รหัสวัน ตั้งแต่วันจันทร์ 1 ถึงวันอาทิตย์ 7"
            )
            st.write(
                "P = ผลรวมลองจิจูดของดาวที่ถ่วงน้ำหนัก "
                "คูณ 100 แล้วหาเศษจาก 100"
            )
            st.write(
                "A = ผลรวมระยะห่างเชิงมุมของดาวทุกคู่ "
                "คูณ 100 แล้วหาเศษจาก 100"
            )
            st.write(
                "M = ลองจิจูดดวงจันทร์คูณ 100 "
                "แล้วหาเศษจาก 100"
            )

        if st.button("💾 บันทึกผลการคำนวณ"):
            record = {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "target_date": selected_date.isoformat(),
                "weekday": weekday_name(selected_date),
                "result_number": formula["result_number"],
                "date_value": formula["date_value"],
                "weekday_value": formula["weekday_value"],
                "planet_value": formula["planet_value"],
                "angle_value": formula["angle_value"],
                "moon_value": formula["moon_value"],
                "astronomy_status": "สำเร็จ",
            }

            save_calculation(record)
            st.success("บันทึกผลลงฐานข้อมูลแล้ว")


# =========================================================
# PAGE: ASTRONOMY
# =========================================================

elif page == "คำนวณดวงดาว":

    st.subheader("🪐 ตำแหน่งดาวและระยะห่างเชิงมุม")

    astro_date = st.date_input(
        "เลือกวันที่สำหรับดูตำแหน่งดาว",
        value=date.today(),
        key="astro_date",
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )

    if st.button("ตรวจสอบตำแหน่งดาว", use_container_width=True):

        with st.spinner("กำลังโหลดข้อมูลดาราศาสตร์..."):
            try:
                positions = calculate_planet_positions(astro_date)

                st.session_state["astro_positions"] = positions
                st.session_state["astro_date_saved"] = astro_date.isoformat()

                st.success("คำนวณสำเร็จ")

            except Exception as exc:
                st.error(
                    "คำนวณไม่สำเร็จ ตรวจสอบการติดตั้ง Skyfield "
                    "และการดาวน์โหลด ephemeris"
                )
                st.caption(f"รายละเอียด: {exc}")

    if st.session_state.get("astro_date_saved") == astro_date.isoformat():
        positions = st.session_state.get("astro_positions")

        if positions:
            planet_df = pd.DataFrame(
                [
                    {
                        "ดาว": PLANET_TH[name],
                        "ลองจิจูดสุริยวิถี (องศา)": round(value, 5),
                    }
                    for name, value in positions.items()
                ]
            )

            st.markdown("### ตำแหน่งดาว")
            st.dataframe(
                planet_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("### ระยะห่างเชิงมุมระหว่างดาว")

            angle_df = calculate_angular_table(positions)

            st.caption(
                "แสดงระยะห่างของลองจิจูดบนสุริยวิถี "
                "ไม่ใช่ระยะห่างจริงระหว่างดาวในอวกาศ"
            )

            st.dataframe(
                angle_df,
                use_container_width=True,
                hide_index=True,
            )

            csv_data = angle_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "ดาวน์โหลดตารางระยะห่างเป็น CSV",
                data=csv_data,
                file_name=f"planet_angles_{astro_date.isoformat()}.csv",
                mime="text/csv",
            )


# =========================================================
# PAGE: HISTORICAL ANALYSIS
# =========================================================

elif page == "วิเคราะห์ผลย้อนหลัง":

    st.subheader("🎟️ เปรียบเทียบกับผลสลากย้อนหลัง")

    st.write(
        "นำเข้าไฟล์ CSV ที่มีผลสลากจริง "
        "ระบบจะเปรียบเทียบเลขที่คำนวณไว้กับเลขสองหลักท้าย"
    )

    st.warning(
        "การตรงกันในอดีตไม่ได้รับประกันผลในอนาคต "
    
