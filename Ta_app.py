# =======================================================
# หมายเลขลึกลับของ SYNAPSE
# ตอนที่ 1 จาก 2
# บันทึกไฟล์นี้เป็น Ta_app.py จากนั้นเพิ่มส่วนที่ 2 ต่อท้าย
# =======================================================

นำเข้าคณิตศาสตร์
นำเข้า sqlite3
จากการนำเข้า datetime, date, datetime
จาก itertools นำเข้า combinations
จาก pathlib นำเข้า Path

import pandas as pd
import streamlit as st

APP_TITLE = "SYNAPSE MYSTIC NUMBER"
DB_PATH = Path("synapse_mystic.db")

ดาวเคราะห์ = [
    "ดวงอาทิตย์", "ดวงจันทร์", "ดาวพุธ", "ดาวศุกร์", "ดาวอังคาร"
    "ดาวพฤหัสบดี", "ดาวเสาร์", "ดาวยูเรนัส", "ดาวเนปจูน"
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

THAI_WEEKDAYS = [
    "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี",
    "วันศุกร์", "วัน", "sunday",
]

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌌",
    เลย์เอาต์="กว้าง"
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        พื้นหลัง: การไล่ระดับสีแบบรัศมี (วงกลมที่มุมบนขวา)
        #18295b 0%, #090f26 45%, #030711 100%);
        สี: #f5f0dc;
    }
    [data-testid="stSidebar"] {
        พื้นหลัง: #080d20;
        ขอบขวา: 1px solid #c9a85c;
    }
    h1, h2, h3 { color: #f1cf78 !important; }
    p, label, span { color: #e9e8f5; }
    .cosmic-card {
        พื้นหลัง: rgba(19, 29, 62, 0.88);
        ขอบ: 1px ทึบ #a88c4d;
        ขอบโค้งมน: 16px;
        padding: 20px;
        ระยะขอบล่าง: 14px;
        box-shadow: 0 0 18px rgba(201, 168, 92, 0.08);
    }
    .big-number {
        สี: #f1cf78;
        ขนาดตัวอักษร: 56px;
        น้ำหนักตัวอักษร: 800;
        จัดแนวข้อความ: กึ่งกลาง;
        ระยะห่างระหว่างตัวอักษร: 8px;
    }
    .muted { color: #b8bfd8; font-size: 13px; }
    div.stButton > ปุ่ม {
        พื้นหลัง: การไล่ระดับสีเชิงเส้น (90 องศา, #b08b3d, #e8cd7c);
        สี: #11162b;
        ขอบ: ไม่มี;
        ขอบโค้งมน: 10px;
        font-weight: bold;
        ความสูงขั้นต่ำ: 42px;
    }
    div.stButton > ปุ่ม:hover {
        พื้นหลัง: #f7df97;
        สี: #11162b;
        ขอบ: 1px ทึบ #fff0b5;
    }
    div[data-testid="stMetric"] {
        พื้นหลัง: rgba(22, 33, 69, 0.85);
        ขอบ: 1px ทึบ #75643e;
        ระยะห่าง: 14px;
        ขอบโค้งมน: 12px;
    }
    hr { border-color: #665b43; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------- ฐานข้อมูล -------------------------

def get_connection():
    ส่งคืน sqlite3.connect(DB_PATH)


def initialize_database():
    ด้วย get_connection() เป็น conn:
        conn.execute(
            """
            สร้างตาราง IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                target_date TEXT NOT NULL,
                วันธรรมดา ข้อความไม่ว่างเปล่า
                result_number TEXT NOT NULL,
                ค่าวันที่ จำนวนเต็ม ไม่เป็นค่าว่าง
                ค่าวันในสัปดาห์ จำนวนเต็ม ไม่เป็นค่าว่าง
                planet_value INTEGER NOT NULL,
                ค่ามุม จำนวนเต็ม ไม่เป็นค่าว่าง
                moon_value INTEGER NOT NULL,
                สถานะดาราศาสตร์ ข้อความ ห้ามเป็นค่าว่าง
            )
            """
        )


def save_calculation(record):
    ด้วย get_connection() เป็น conn:
        conn.execute(
            """
            แทรกเข้าไปในการคำนวณ (
                สร้างเมื่อ, วันที่เป้าหมาย, วันในสัปดาห์, หมายเลขผลลัพธ์
                ค่าวันที่, ค่าวันในสัปดาห์, ค่าดาวเคราะห์, ค่ามุม
                ค่าดวงจันทร์ สถานะทางดาราศาสตร์
            ) ค่า (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                บันทึก["created_at"],
                บันทึก["target_date"],
                บันทึก["weekday"],
                บันทึก["result_number"],
                บันทึก["date_value"],
                บันทึก["weekday_value"],
                บันทึก["planet_value"],
                บันทึก["ค่ามุม"],
                บันทึก["moon_value"],
                บันทึก["astronomy_status"],
            ),
        )


def load_history():
    ด้วย get_connection() เป็น conn:
        ส่งคืน pd.read_sql_query(
            "SELECT * FROM calculations ORDER BY id DESC",
            เชื่อมต่อ
        )


initialize_database()


# ------------------------- ปฏิทิน -------------------------

def weekday_name(target_date):
    คืนค่า THAI_WEEKDAYS[target_date.weekday()]



def date_digit_sum(target_date):
    return sum(int(ch) for ch in target_date.strftime("%Y%m%d"))


def digital_root(number):
    while number > 9:
        number = sum(int(ch) for ch in str(number))
    return number


# ------------------------- ดาราศาสตร์ -------------------------

@st.cache_resource(show_spinner=False)
def load_ephemeris():
    จาก skyfield.api นำเข้า load
    ephemeris = load("de421.bsp")
    ไทม์สเกล = โหลดไทม์สเกล()
    ส่งคืนปฏิทินดาราศาสตร์, มาตราเวลา


def calculate_planet_positions(target_date):
    """
    คำนวณลองจิจูดสุริยวิถีแบบปรากฏ ณ จุดศูนย์กลางโลก สำหรับวันที่เลือก
    ใช้เวลาเที่ยงวันตามเวลา UTC และข้อมูลวงโคจร DE421 ของ Skyfield
    การใช้งานครั้งแรกอาจต้องเชื่อมต่ออินเทอร์เน็ตเพื่อดาวน์โหลดข้อมูลวงโคจรของดวงจันทร์
    """
    ปฏิทินดาราศาสตร์, มาตราส่วนเวลา = โหลดปฏิทินดาราศาสตร์()
    t = timescale.utc(
        ปีของวันที่เป้าหมาย, เดือนของวันที่เป้าหมาย, วันของวันที่เป้าหมาย, 12, 0, 0
    )
    โลก = ปฏิทินดาราศาสตร์["โลก"]

    body_keys = {
        "ดวงอาทิตย์": "sun",
        "Moon": "moon",
        "ปรอท": "ปรอท"
        "วีนัส": "วีนัส"
        "Mars": "mars",
        "Jupiter": "jupiter barycenter",
        "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter",
        "Neptune": "neptune barycenter",
    }

    ตำแหน่ง = {}
    สำหรับดาวเคราะห์, body_key ใน body_keys.items():
        apparent = earth.at(t).observe(ephemeris[body_key]).apparent()
        _, ลองจิจูด, _ = apparent.ecliptic_latlon(epoch="date")
        positions[planet] = float(longitude.degrees) % 360.0

    def


def angular_separation(longitude_a, longitude_b):
    ความแตกต่าง = ค่าสัมบูรณ์ของลองจิจูด a - ลองจิจูด b % 360.0
    ส่งคืนค่าต่ำสุดของผลต่าง (360.0 - ผลต่าง)


def calculate_angular_table(positions):
    แถว = []
    สำหรับลำดับที่หนึ่งและลำดับที่สองใน combinations(positions.keys(), 2):
        separation = angular_separation(positions[first], positions[second])
        rows.append({
            "ดาวดวงที่ 1": PLANET_TH[first],
            "ดาวดวงที่ 2": PLANET_TH[second],
            " ระยะทางเชิงมุม (องศา)": กลม(แยก, 4),
        })
    ส่งคืน pd.DataFrame(rows)


# ------------------------- สูตรตัวเลข -------------------------

def calculate_number(target_date, positions):
    """
    สูตรคงที่แบบทดลอง:
    D = รากที่สองของตัวเลข YYYYMMDD
    W = รหัสวันในสัปดาห์ (วันจันทร์=1 ... วันอาทิตย์=7)
    P = ผลรวมถ่วงน้ำหนักของลองจิจูดของดาวเคราะห์ * 100, มอดูล 100
    A = ผลรวมของระยะห่างเชิงมุมระหว่างคู่ทั้งหมด * 100, มอดูล 100
    M = ลองจิจูดของดวงจันทร์ * 100, มอดูล 100
    ผลลัพธ์ = (3D + 2W + P + A + M) มอดูล 100

    นี่เป็นการเปลี่ยนแปลงเชิงทดลอง ไม่ใช่การทำนายที่ได้รับการตรวจสอบแล้ว
    """
    ค่าวันที่ = รากดิจิทัล(ผลรวมตัวเลขวันที่(วันที่เป้าหมาย))
    ค่าวันในสัปดาห์ = วันในสัปดาห์ของวันที่เป้าหมาย + 1

    weighted_longitudes = sum(
        (ดัชนี + 1) * ตำแหน่ง[ดาวเคราะห์]
        สำหรับดัชนี ดาวเคราะห์ ในการแจงนับ (PLANETS)
    )
    ค่าดาวเคราะห์ = ปัดเศษ (ลองจิจูดถ่วงน้ำหนัก * 100) % 100

    การแยก = [
        angular_separation(positions[first], positions[second])
        สำหรับอันดับแรก อันดับที่สองในการรวมกัน (ดาวเคราะห์, 2)
    ]
    ค่ามุม = ปัดเศษ (ผลรวมของระยะห่าง) * 100 % 100
    ค่าดวงจันทร์ = ปัดเศษ (positions["ดวงจันทร์"] * 100) % 100

    ผลลัพธ์ = (
        3 * ค่าวันที่
        + 2 * ค่าวันในสัปดาห์
        + planet_value
        + ค่ามุม
        + moon_value
    ) % 100

    ส่งคืน {
        "result_number": f"{result:02d}",
        "date_value": date_value,
        "weekday_value": weekday_value,
        "planet_value": planet_value,
        "angle_value": angle_value,
        "moon_value": moon_value,
    }


# ------------------------- ตัวช่วยในการนำเข้าไฟล์ CSV -------------------------

def normalize_number(value):
    ถ้า pd.isna(value):
        ส่งคืนค่าไม่มี

    ค่าข้อความ = str(ค่า).strip()
    ถ้าค่าข้อความลงท้ายด้วย ".0":
        ค่าข้อความ = ค่าข้อความ[:-2]
    ถ้าค่าข้อความไม่ใช่ตัวเลข:
        ส่งคืนค่าไม่มี

    ส่งคืนค่าข้อความ


def analyze_lottery_csv(uploaded_file):
    df = pd.read_csv(
        ไฟล์ที่อัปโหลด
        dtype=str,
        keep_default_na=False,
    )
    df.columns = [column.strip().lower() for column in df.columns]

    required = {"date", "lottery", "category", "number"}
    ขาดหายไป = จำเป็น - ตั้งค่า (df.columns)
    หากหายไป:
        คืนค่า None, (
            " ไฟล์ CSV จะต้องมีวันที่, ลอตเตอรี, หมวดหมู่, หมายเลข "
            f" โดยยัง หายไป: {', '.join(sorted(missing))}"
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

    ถ้า df ว่างเปล่า:
        return ไม่มี, "ไม่พบแถวนั้นสามารถใช้งานได้ในไฟล์ CSV"

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df["last_two_digits"] = df["number"].apply(
        ค่าแลมบ์ดา: value[-2:].zfill(2)
    )
    คืนค่า df, ไม่มี
# =======================================================
# หมายเลขลึกลับของ SYNAPSE
# ตอนที่ 2 จาก 2
# เพิ่มส่วนนี้ทั้งหมดต่อจากส่วนที่ 1 โดยตรง
# =======================================================

# ------------------------- แถบด้านข้าง -------------------------

st.sidebar.markdown("# 🌌 SYNAPSE")
st.sidebar.markdown("### MYSTIC NUMBER")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "องค์ประกอบ",
    [
        "หน้าหลัก",
        "องค์ประกอบเว็บเพจ",
        "วิเคราะห์ผลการวิเคราะห์",
        "องค์ประกอบเว็บเพจ",
        "ระบบ"
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("ข้อมูลจักรวาล • ดาราศาสตร์ • การวิเคราะห์ตัวเลข")
st.sidebar.caption("ทดลอง • โปร่งใส • สามารถทำซ้ำได้")


# ------------------------- ส่วนหัว -------------------------

st.markdown(
    """
    <div class="cosmic-card">
        <div style="font-size:14px; color:#c9b77d;">
            ข้อมูลจักรวาล • ดาราศาสตร์ • การวิเคราะห์ตัวเลข
        </div>
        <h1 style="font-size:34px;">🌌 หมายเลขลึกลับของ SYNAPSE</h1>
        <div style="color:#c5cbe1;">
            ข้อมูลตำแหน่งดาวและสูตรข้อมูลเป็น
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------- หน้าหลัก -------------------------

ถ้าเพจ == "หน้าหลัก":
    st.subheader("📅 เลือกสิ่งที่จะเขียนลงในหน้าเว็บ")

    selected_date = st.date_input(
        "ต้องเลือก",
        ค่า = วันที่วันนี้(),
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("วันที่", selected_date.strftime("%d/%m/%Y"))
    col2.metric("วันในสัปดาห์", weekday_name(selected_date))
    col3.metric("ผลรวมตัวเลขวันที่", date_digit_sum(selected_date))

    st.info(
        "ระบบใช้เวลา 12:00 UTC วันที่อ้างอิงของวันที่เลือก "
        "องค์ประกอบที่ควบคุมได้และควบคุมได้"
    )

    ถ้า st.button("🪐 คำนวณวันที่และตำแหน่งดาว", use_container_width=True):
        with st.spinner("กำลังประมวลผลข้อมูลการป้อน..."):
            ลองดู:
                positions = calculate_planet_positions(selected_date)
                สูตร = calculate_number(selected_date, positions)

                st.session_state["last_positions"] = positions
                st.session_state["last_formula"] = สูตร
                st.session_state["last_date"] = selected_date.isoformat()
                st.session_state["last_astronomy_status"] = "สถานะ"
                st.success(" จัดการดาว")

            ยกเว้นข้อยกเว้นตาม exc:
                st.session_state["last_positions"] = None
                st.session_state["last_formula"] = None
                st.session_state["last_date"] = selected_date.isoformat()
                st.session_state["last_astronomy_status"] = " ไม่สำเร็จ"
                st.error(
                    st.subheader("Planet Positions")
                    "Skyfield และ Skyfield"
                )
                st.caption(f"รายละเอียดสำหรับหน้าเว็บ: {exc}")

    ถ้า (
        st.session_state.get("last_date") == selected_date.isoformat()
        และ st.session_state.get("last_formula")
    ):
        สูตร = st.session_state["last_formula"]

        st.markdown("---")
        st.subheader("🔢 ส่วนหัวจากสูตรทดลอง")

        st.markdown(
            f"""
            <div class="cosmic-card">
                <div style="text-align:center;">
                    <div style="color:#c9b77d;">
                        ผลลัพธ์สองหลักแบบทดลอง
                    </div>
                    <div class="big-number">{formula["result_number"]}</div>
                    <div class="muted">
                        ผลจากสูตรทดสอบผลรวมของผลรวม
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)
        a.metric("D: วันที่", formula["date_value"])
        b.metric("W: วันในสัปดาห์", formula["weekday_value"])
        c.metric("P: ดาวเคราะห์ดาว", formula["planet_value"])

        d, e = st.columns(2)
        d.metric("A: ระยะทางเชิงมุม", สูตร["angle_value"])
        e.metric("M: ตำแหน่งตัวเลข", formula["moon_value"])

        with st.expander("ดูสูตรและองค์ประกอบ"):
            st.code("ผลลัพธ์ = (3D + 2W + P + A + M) % 100")
            st.write("D = ผลรวมขององค์ประกอบที่เป็นตัวหลักเดียว")
            st.write("W = รหัสวันวันจันทร์ 1 ถึงวันอาทิตย์ 7")
            st.write("P = ผลรวมลองจิจูดดาวแบบน้ำหนักคูณ 100 แล้ว mod 100")
            st.write("A = ผลรวมระยะห่างเชิงมุมของดาวทุกคู่ คูณ 100 แล้ว mod 100")
            st.write("M = ลองดูจิจูดของคูณ 100 แล้ว mod 100")

        if st.button("💾 แสดงผลบน"):
            บันทึก = {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "target_date": selected_date.isoformat(),
                "weekday": weekday_name(selected_date),
                "result_number": formula["result_number"],
                "date_value": formula["date_value"],
                "weekday_value": formula["weekday_value"],
                "planet_value": formula["planet_value"],
                "angle_value": formula["angle_value"],
                "moon_value": formula["moon_value"],
                "astronomy_status": "สถานะ",
            }
            บันทึกการคำนวณ (บันทึก)
            st.success("ความสำเร็จลงบล็อกแล้ว")


# ------------------------- หน้าดาราศาสตร์ -------------------------

elif page == " คำนวณการเงิน":
    st.subheader("🪐 ตำแหน่งดาวและหัวเรื่องย่อย")

    astro_date = st.date_input(
        "องค์ประกอบสำหรับดูดาว",
        ค่า = วันที่วันนี้(),
        key="astro_date",
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )

    if st.button("ปุ่มดาว", use_container_width=True):
        with st.spinner("กำลังโหลดข้อมูลการป้อนข้อมูล..."):
            ลองดู:
                positions = calculate_planet_positions(astro_date)
                st.session_state["astro_positions"] = positions
                st.session_state["astro_date_saved"] = astro_date.isoformat()
                st.success(" ประเมินความสำเร็จ")
            ยกเว้นข้อยกเว้นตาม exc:
                st.error(
                    " คำนวณไม่สำเร็จการตัดสกายฟิลด์ "
                    "และปฏิทินดาราศาสตร์"
                )
                st.caption(f" รายละเอียด: {exc}")

    ถ้า st.session_state.get("astro_date_saved") == astro_date.isoformat():
        positions = st.session_state.get("astro_positions")

        ถ้าตำแหน่ง:
            planet_df = pd.DataFrame([
                {
                    "ดาว": PLANET_TH[ชื่อ],
                    "ลองจิจูดสุริยวิถี (องศา)": รอบ(ค่า, 5),
                }
                
# สร้างตารางตำแหน่งดาว
planet_df = pd.DataFrame([
    {"ชื่อดาว": name, "ตำแหน่ง": value}
    for name, value in positions.items()
])

st.markdown("### ตำแหน่งดาว")
st.dataframe(
    planet_df,
    use_container_width=True,
    hide_index=True
)

# ตารางองค์ประกอบและมุมสัมพันธ์ระหว่างดาว
st.markdown("### เรียงองค์ประกอบบนดาว")
st.caption(
    "ตารางนี้แสดงมุมสัมพันธ์ระหว่างตำแหน่งดาว "
    "ที่คำนวณจากข้อมูลตำแหน่งดาวในวันที่เลือก "
    "ผลลัพธ์เป็นค่าที่คำนวณตามสูตรทางดาราศาสตร์ "
    "ไม่ใช่การยืนยันเหตุการณ์หรือผลลัพธ์ในชีวิตจริง"
)

angle_df = calculate_angular_table(positions)

st.dataframe(
    angle_df,
    use_container_width=True,
    hide_index=True
)

# ดาวน์โหลดตารางมุมสัมพันธ์เป็น CSV
csv_data = angle_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "ดาวน์โหลดตารางมุมดาวเป็น CSV",
    data=csv_data,
    file_name=f"planet_angles_{astro_date.isoformat()}.csv",
    mime="text/csv",
)

# ------------------------- หน้าวิเคราะห์ประวัติศาสตร์ -------------------------

elif page == " วิเคราะห์ผลย้อนหลัง":
    st.subheader("🎟️ เอฟเฟกต์สลาก")

    st.write(
        "รายละเอียดของไฟล์ CSV ที่สลากจริง ระบบจะวิเคราะห์เลขสองหลักท้าย "
        "กับ จัดการและจัดการองค์ประกอบ"
    )
    st.warning(
        "ผลรวมของผลไม่แสดงผลรวมของผล"
        "และผลที่ตามมาของสลากและผลที่ตามมา"
    )

    st.markdown(
        """
        **ไฟล์ CSV**

        ต้องมี `วันที่`, `ลอตเตอรี่`, `หมวดหมู่`, `หมายเลข`

        ตัวอย่างด้านล่างเป็นข้อมูลสมมติผลสลากจริง):

        ```csv
        วันที่, ลอตเตอรี่, หมวดหมู่, หมายเลข
        2026-01-16,Thai,การ์ตูน,123456
        2026-02-01,Thai,การ์ตูน,000123
        2026-02-10,ตัวอย่าง,ตัวอย่าง,45
        ```
        """
    )

    uploaded_file = st.file_uploader(
        "ไฟล์ CSV ผลสลาก",
        type=["csv"],
    )

    ถ้า uploaded_file ไม่ใช่ None:
        historical_df, error = analyze_lottery_csv(uploaded_file)

        หากเกิดข้อผิดพลาด:
            st.error(ข้อผิดพลาด)
        elif historical_df is not None:
            st.success(f" อ่านข้อมูลสำเร็จ {len(historical_df)} รายการ")
            st.dataframe(
                historical_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("### อินเทอร์เฟซเว็บเพจ")
            calculated_df = load_history()

            ถ้า calculated_df ว่างเปล่า:
                st.info(
                    "มีองค์ประกอบที่เว็บเพจ"
                    "ไปที่หน้าหลักเพื่อจัดการและจัดการข้อมูลก่อน"
                )
            อื่นๆ:
                historical_df["date"] = historical_df["date"].astype(str)
                calculated_df["target_date"] = (
                    calculated_df["target_date"].astype(str)
                )

                joined = historical_df.merge(
                    calculated_df[["target_date", "result_number"]],
                    left_on="date",
                    ถูกต้องตาม "target_date"
                    how="inner",
                )

                ถ้าเชื่อมต่อแล้วว่างเปล่า:
                    st.info(
                        "องค์ประกอบนี้มีผลต่อผลลัพธ์ของหน้าเว็บ"
                        "กับที่ที่มันทำงานอยู่"
                    )
                อื่นๆ:
                    joined[" ] = (
                        joined["last_two_digits"] == joined["result_number"]
                    )

                    hit_count = int(joined["จำนวน"].sum())
                    อัตรา = เข้าร่วม["ในเรื่อง"].mean() * 100

                    m1, m2, m3 = st.columns(3)
                    m1.metric("ความยาวพอ", len(joined))
                    m2.metric("จำนวนการเข้าชม", hit_count)
                    m3.metric(" อัตรา", f"{rate:.2f}%")

                    st.dataframe(
                        เข้าร่วม[
                            [
                                "วันที่", "ลอตเตอรี่", "ประเภท", "หมายเลข",
                                "result_number", "last_two_digits", "ตัวเลข",
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.caption(
                        "ใช้เฉพาะแผนที่เท่านั้นที่สามารถใช้งานได้จริง"
                        " ฝังไว้ก่อนทราบผล ฝัง ฝัง ฝังให้"
                    )

                    result_csv = joined.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        "ดาวน์โหลดตัวอย่าง CSV",
                        data=result_csv,
                        file_name="synapse_historical_comparison.csv",
                        mime="text/csv",
                    )


# ------------------------- หน้าประวัติการคำนวณ -------------------------

elif page == "ประวัติความทรงจำ":
    st.subheader("💾 ซับเฮดเดอร์")

    history_df = load_history()
    ถ้า history_df ว่างเปล่า:
        st.info("ฉันพยายามคำนวณจากหน้าหลักก่อนครับ")
    อื่นๆ:
        st.metric("ประวัติย่อ", len(history_df))
        st.dataframe(history_df, use_container_width=True, hide_index=True)

        csv_data = history_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "สร้างองค์ประกอบเป็น CSV"
            data=csv_data,
            file_name="synapse_calculation_history.csv",
            mime="text/csv",
        )


# ------------------------- เกี่ยวกับหน้า -------------------------

elif page == "เกี่ยวกับระบบ":
    st.subheader("ℹ️เกี่ยวกับ SYNAPSE MYSTIC NUMBER")

    st.markdown(
        """
        ### อินเทอร์เฟซ

        SYNAPSE MYSTIC NUMBER เป็นโครงการทดลองที่นำข้อมูลปฏิทิน
        ตำแหน่งดาวและสูตรข้อมูลเป็นข้อมูลมาศึกษา

        ### ระบบในเว็บเพจนี้

        - แสดงวันในเว็บเพจจากด้านบน
        - คำนวณตำแหน่งดาวด้วยข้อมูลชั่วคราวผ่าน Skyfield
        - จัดการองค์ประกอบนี้ให้อยู่ในรูปแบบที่คล้ายกับจินาดของดาว
        - สร้างเว็บเพจด้วยสูตรการตัดต่อ
        - ไฟล์นำเข้า CSV ผลสลากย้อนหลังเพื่อเปรียบเทียบ
        - จัดเก็บและดาวน์โหลด

        ### สำคัญ

        ตำแหน่งดาวเป็นข้อมูล อัปเดตข้อมูล ตำแหน่งดาวเป็นข้อมูล
        เป็นสูตรทดสอบการยกขึ้นเอง ของคอมพิวเตอร์ที่ยกขึ้น
        ฟังก์ชันนี้มีผลสลากที่สามารถทำได้ดีกว่าฟังก์ชันนี้

        ระบบนี้ทำงานโดยมีผลสลากไทย ความถี่และภาษาเวียดนามจากเว็บไซต์
        เราต้องนำเข้าองค์ประกอบที่สามารถรับและแยกองค์ประกอบ
        หน้าเว็บเพจ หน้าเว็บเพจและวันที่ออกหน้าเว็บเพจให้

        ### หลัก หลัก

        สร้างผลลัพธ์ที่เพิ่มขึ้นเองและควรค่าแก่การจดจำ
        ความถี่ที่ความถี่ในการสังเกตก่อนทราบผล
        และทดสอบกับองค์ประกอบที่พิมพ์สูตร
        """
    )


# ------------------------- ส่วนท้าย -------------------------

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#b6a36c; padding:10px;">
        หมายเลขลึกลับของ SYNAPSE • ห้องปฏิบัติการข้อมูลจักรวาล
    </div>
    """,
    unsafe_allow_html=True,
)
