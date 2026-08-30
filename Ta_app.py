from datetime import datetime
import math

def calculate_system():
    now = datetime.now()
    
    # 1. คำนวณวัน (อาทิตย์=1 ถึง เสาร์=7)
    # weekday(): จันทร์=0 ... อาทิตย์=6
    wd = now.weekday()
    day_mapping = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
    day_num = day_mapping[wd]
    
    # 2. คำนวณราศีสากลแบบง่าย
    day = now.day
    month = now.month
    zodiacs = [
        ("มังกร (Capricorn)", (12, 22), (1, 19)),
        ("กุมภ์ (Aquarius)", (1, 20), (2, 18)),
        ("มีน (Pisces)", (2, 19), (3, 20)),
        ("เมษ (Aries)", (3, 21), (4, 19)),
        ("พฤษภ (Taurus)", (4, 20), (5, 20)),
        ("เมถุน (Gemini)", (5, 21), (6, 20)),
        ("กรกฎ (Cancer)", (6, 21), (7, 22)),
        ("สิงห์ (Leo)", (7, 23), (8, 22)),
        ("กันย์ (Virgo)", (8, 23), (9, 22)),
        ("ตุลย์ (Libra)", (9, 23), (10, 22)),
        ("พิจิก (Scorpio)", (10, 23), (11, 21)),
        ("ธนู (Sagittarius)", (11, 22), (12, 21))
    ]
    current_zodiac = "มังกร (Capricorn)"
    for name, (m1, d1), (m2, d2) in zodiacs:
        if (month == m1 and day >= d1) or (month == m2 and day <= d2):
            current_zodiac = name
            break

    # 3. ปีนักษัตรไทย
    thai_year = now.year + 543
    animals = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    animal_idx = (thai_year - 2503) % 12
    zodiac_year = animals[animal_idx]

    # 4. ข้างขึ้น / ข้างแรม (คำนวณจากรอบดวงจันทร์ 29.53 วัน)
    base_new_moon = datetime(2026, 1, 19)
    diff_days = (now - base_new_moon).days % 29.5305877
    if diff_days < 15:
        lunar_phase = f"ข้างขึ้น {int(diff_days) + 1} ค่ำ"
    else:
        lunar_phase = f"ข้างแรม {max(1, int(diff_days - 14.76))} ค่ำ"

    # 5. สัดส่วนทองคำ (Golden Ratio: Phi)
    phi = (1 + math.sqrt(5)) / 2
    golden_upper = round(day_num * phi, 4)
    golden_lower = round(day_num / phi, 4)

    # แสดงผลลัพธ์ออกทางหน้าจอ Text ทันที
    print("=" * 40)
    print(f" วันที่ปัจจุบัน: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    print(f"1. ตัวเลขประจำวัน (1-7): {day_num}")
    print(f"2. ดิถีดวงจันทร์: {lunar_phase}")
    print(f"3. ราศี: {current_zodiac}")
    print(f"4. ปีนักษัตร: ปี{zodiac_year} (พ.ศ. {thai_year})")
    print("-" * 40)
    print(f"5. เชื่อมโยงสัดส่วนทองคำ (Phi = {round(phi, 4)}):")
    print(f"   - ค่าขยาย (Day * Phi): {golden_upper}")
    print(f"   - ค่าลดทอน (Day / Phi): {golden_lower}")
    print("=" * 40)

if __name__ == "__main__":
    calculate_system()
