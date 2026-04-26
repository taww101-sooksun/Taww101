import math
import time
import numpy as np

# --- 1. ระบบพิกัด GPS & Chat ---
def get_gps_distance(lat1, lon1, lat2, lon2):
    """สูตร Haversine คำนวณระยะทางจริงบนผิวโลก (หน่วย: กม.)"""
    R = 6371.0
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def send_chat(user, msg, lat, lon):
    timestamp = time.strftime("%H:%M:%S")
    return f"[{timestamp}] {user}: {msg} | Loc: {lat}, {lon}"


# --- 2. ระบบเครื่องเล่นเพลง (DJ & MP3 Logic) ---
class MusicPlayer:
    def __init__(self):
        self.is_playing = False
        self.volume = 0.5
        self.current_track = ""

    def play_track(self, track_name):
        self.current_track = track_name
        self.is_playing = True
        return f"💿 กำลังเล่น: {track_name} (Vol: {int(self.volume*100)}%)"

    def dj_crossfade(self, track_a, track_b):
        return f"🎚️ กำลัง Mix ระหว่าง {track_a} และ {track_b}"


# --- 3. สูตรคำนวณตัวเลข (2 แบบแยกกัน) ---
def formula_v1_growth(old, new):
    """สูตร 1: หาอัตราการเติบโต/เปลี่ยนแปลง (%)"""
    if old == 0: return 0
    return ((new - old) / old) * 100

def formula_v2_scale(value, in_min, in_max, out_min, out_max):
    """สูตร 2: การ Map ค่า (เช่น แปลงค่าเสียง 0-100 เป็นความสว่างไฟ 0-255)"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# --- 4. ระบบวัดค่าเสียงและความสั่น (Simulation Logic) ---
def analyze_audio(vocal_data):
    """วัดความดัง (dB) จาก Array ข้อมูลเสียงจริง"""
    rms = np.sqrt(np.mean(np.array(vocal_data)**2))
    return 20 * np.log10(rms) if rms > 0 else 0

def phone_vibrate(intensity):
    """สั่งสั่นตามระดับความแรง (0.0 - 1.0)"""
    return f"📳 สั่นสะเทือนที่ระดับ: {intensity * 100}%"


# --- 5. ระบบเปลี่ยนสีธีม (Theme Management) ---
def get_theme_style(mode):
    themes = {
        "neon_red": {"bg": "#000000", "accent": "#FF0000", "text": "#FFCCCC"},
        "neon_green": {"bg": "#000000", "accent": "#00FF00", "text": "#CCFFCC"},
        "dark_sky": {"bg": "#0B0D17", "accent": "#AFEEEE", "text": "#FFFFFF"}
    }
    return themes.get(mode, themes["dark_sky"])
