from datetime import datetime
import math

class AuspiciousGoldenCalculator:
    def __init__(self, target_date=None):
        self.date = target_date if target_date else datetime.now()
        # สัดส่วนทองคำ (Golden Ratio)
        self.phi = (1 + math.sqrt(5)) / 2

    def get_day_number(self):
        # อาทิตย์ = 1 ถึง เสาร์ = 7 (Python ดึง 0=จันทร์ ถึง 6=อาทิตย์ จึงต้องปรับสูตร)
        # weekday(): จันทร์=0, อังคาร=1, ..., เสาร์=5, อาทิตย์=6
        wd = self.date.weekday()
        day_mapping = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
        return day_mapping[wd]

    def get_zodiac_sign(self):
        # ราศีแบบสากล (Tropical Zodiac) คำนวณคร่าวๆ ตามช่วงวันเกิด
        day = self.date.day
        month = self.date.month
        
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
        
        for name, (m1, d1), (m2, d2) in zodiacs:
            if (month == m1 and day >= d1) or (month == m2 and day <= d2):
                return name
        return "มังกร (Capricorn)"

    def get_zodiac_year(self):
        # ปีนักษัตรไทย (นับปีตามปี พ.ศ. โดยเปลี่ยนปีนักษัตรช่วงขึ้น 1 ค่ำ เดือน 5 แต่เพื่อความแม่นยำในโค้ดทั่วไป ใช้ปี พ.ศ. % 12)
        thai_year = self.date.year + 543
        animals = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
        # ปี พ.ศ. 2503 (ค.ศ. 1960) เป็นปีชวด (index 0)
        index = (thai_year - 2503) % 12
        return animals[index]

    def get_lunar_phase_approximation(self):
        # คำนวณข้างขึ้น-ข้างแรมโดยประมาณจากรอบดวงจันทร์ (Synodic Month ≈ 29.53 วัน)
        # อ้างอิงวันที่จันทร์ดับ (New Moon) ล่าสุดที่เป็นฐานคำนวณ
        base_new_moon = datetime(2026, 1, 19) # วันจันทร์ดับอ้างอิง
        diff_days = (self.date - base_new_moon).days % 29.5305877
        
        if diff_days < 15:
            day_count = int(diff_days) + 1
            return f"ข้างขึ้น {day_count} ค่ำ"
        else:
            day_count = int(diff_days - 14.76)
            if day_count < 1: 
                day_count = 1
            return f"ข้างแรม {day_count} ค่ำ"

    def calculate_golden_ratio_metrics(self):
        # นำค่าตัวเลขประจำวันมาประยุกต์ร่วมกับสัดส่วนทองคำ (Golden Ratio)
        day_num = self.get_day_number()
        
        # คำนวณสัดส่วนสมดุลเชิงคณิตศาสตร์ (เช่น การกระจายพลังงานหรือความกว้าง-ยาวเชิงโครงสร้าง)
        golden_harmonic = day_num * self.phi
        inverse_harmonic = day_num / self.phi
        
        return {
            "base_value": day_num,
            "golden_ratio": round(self.phi, 4),
            "harmonic_upper": round(golden_harmonic, 4),
            "harmonic_lower": round(inverse_harmonic, 4)
        }

    def generate_report(self):
        day_num = self.get_day_number()
        zodiac = self.get_zodiac_sign()
        year_zodiac = self.get_zodiac_year()
        lunar = self.get_lunar_phase_approximation()
        golden = self.calculate_golden_ratio_metrics()

        print(f"--- รายงานข้อมูลประจำวันที่ {self.date.strftime('%Y-%m-%d')} ---")
        print(f"1. ตัวเลขประจำวัน (อาทิตย์=1 ถึง เสาร์=7): {day_num}")
        print(f"2. ดิถีดวงจันทร์: {lunar}")
        print(f"3. ราศีสากล: {zodiac}")
        print(f"4. ปีนักษัตรไทย: ปี{year_zodiac}")
        print(f"5. การเชื่อมโยงกับสัดส่วนทองคำ (Golden Ratio: {golden['golden_ratio']}):")
        print(f"   - ค่าสอดประสานขั้นสูง (Base * Phi): {golden['harmonic_upper']}")
        print(f"   - ค่าสอดประสานขั้นต่ำ (Base / Phi): {golden['harmonic_lower']}")

if __name__ == "__main__":
    # รันแอปด้วยวันที่ปัจจุบัน
    app = AuspiciousGoldenCalculator()
    app.generate_report()
