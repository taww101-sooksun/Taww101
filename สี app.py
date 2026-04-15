import numpy as np
import librosa

def dynamic_stretch_engine(file_short, file_long, target_duration):
    # 1. โหลดข้อมูลจาก 2 ไฟล์ (สั้น และ ยาว)
    y_short, sr = librosa.load(file_short)
    y_long, _ = librosa.load(file_long)
    
    # 2. คำนวณหา "จุดเหมาะสม" (Weight)
    # ถ้า target_duration อยู่ใกล้ไฟล์ไหนมากกว่า ระบบจะดึงเนื้อเสียงจากไฟล์นั้นมาเยอะกว่า
    # นี่คือการ "ปรับให้พอดี" โดยไม่ฝืนคณิตศาสตร์
    duration_short = len(y_short) / sr
    duration_long = len(y_long) / sr
    
    # หาค่าความต่าง (Interpolation Factor)
    weight = (target_duration - duration_short) / (duration_long - duration_short)
    weight = np.clip(weight, 0, 1) # ล็อคไว้ไม่ให้เกินช่วง 0-1
    
    # 3. ผสมเนื้อเสียง (Mixing DNA)
    # เราไม่ได้ยืดเสียงด้วยโปรแกรม แต่เราผสม "คลื่นเสียง" เข้าด้วยกัน
    # วิธีนี้จะลดเสียงกังวานแมลงหวี่ได้ดีที่สุด
    min_len = min(len(y_short), len(y_long))
    combined_vocal = (y_short[:min_len] * (1 - weight)) + (y_long[:min_len] * weight)
    
    return combined_vocal
