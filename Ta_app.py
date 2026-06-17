import os
import sys
import customtkinter as ctk
import pygame
from PIL import Image

# ตั้งค่าเริ่มต้นโหมดการแสดงผล (ใช้ Dark Mode สีดำสนิท)
ctk.set_appearance_mode("Dark")

class NeonMusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # สโลแกนประจำตัวของนาย
        self.slogan = "อยู่นิ่งๆ ไม่เจ็บตัว"
        
        # ตั้งค่าหน้าต่างโปรแกรม
        self.title("SYNAPSE NEON PLAYER")
        self.geometry("450x650")
        self.resizable(False, False)
        
        # สีนีออนหลักตามสั่ง (แดง, น้ำเงิน, ม่วง, เขียว, ขาว, ดำ)
        self.COLOR_BG = "#050505"         # ดำลึก
        self.COLOR_TEXT = "#FFFFFF"       # ขาว
        self.COLOR_NEON_BLUE = "#00f3ff"  # น้ำเงินนีออน
        self.COLOR_NEON_PURPLE = "#bd00ff"# ม่วงนีออน
        self.COLOR_NEON_RED = "#ff0055"   # แดงนีออน
        self.COLOR_NEON_GREEN = "#00ff66" # เขียวนีออน
        
        self.configure(fg_color=self.COLOR_BG)

        # เริ่มต้นระบบเสียงด้วย Pygame Mixer
        pygame.mixer.init()
        
        # ตัวแปรระบบเพลง
        self.song_list = []
        self.current_song_index = -1
        self.is_playing = False
        
        # โหลดคลังเพลง .mp3 ในโฟลเดอร์ปัจจุบัน
        self.scan_mp3_files()

        # สร้างหน้าต่าง UI
        self.create_widgets()
        
    def scan_mp3_files(self):
        """ค้นหาไฟล์ .mp3 ที่อยู่ในโฟลเดอร์เดียวกับโค้ดจริง"""
        current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
        self.song_list = [f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")]
        if self.song_list:
            self.current_song_index = 0

    def create_widgets(self):
        # 1. ขอบเรืองแสงด้านบนสุด (Neon Border Top)
        top_bar = ctk.CTkFrame(self, height=4, fg_color=self.COLOR_NEON_PURPLE)
        top_bar.pack(fill="x", side="top")

        # 2. พื้นที่ใส่โลโก้ logo1.png
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(pady=20)
        
        try:
            # ดึงภาพ logo1.png จากโฟลเดอร์เดียวกันมาแสดง
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo1.png")
            pil_img = Image.open(img_path)
            # ปรับขนาดภาพให้พอดีหน้าต่างเครื่องเล่น
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(120, 120))
            self.logo_label = ctk.CTkLabel(self.logo_frame, image=logo_img, text="")
            self.logo_label.pack()
        except Exception:
            # ถ้าไม่เจอไฟล์รูป จะแสดงเป็นกล่องสัญลักษณ์นีออนจำลองให้แทน (โค้ดไม่พังชัวร์)
            self.logo_label = ctk.CTkLabel(
                self.logo_frame, 
                text="[ 🧬 ]", 
                font=("Orbitron", 50), 
                text_color=self.COLOR_NEON_BLUE
            )
            self.logo_label.pack()

        # 3. ข้อมูลเพลงที่กำลังเล่น
        self.track_label = ctk.CTkLabel(
            self, 
            text="READY TO SIGNAL", 
            font=("Arial", 16, "bold"), 
            text_color=self.COLOR_TEXT,
            wraplength=380
        )
        self.track_label.pack(pady=5)

        self.status_label = ctk.CTkLabel(
            self, 
            text=f"STATUS: IDLE | {self.slogan}", 
            font=("Arial", 11, "italic"), 
            text_color=self.COLOR_NEON_GREEN
        )
        self.status_label.pack(pady=2)

        # 4. รายชื่อเพลง (Scrollable Listbox)
        self.playlist_frame = ctk.CTkScrollableFrame(
            self, 
            width=380, 
            height=200, 
            fg_color="#0d0d11", 
            border_width=1, 
            border_color=self.COLOR_NEON_BLUE
        )
        self.playlist_frame.pack(pady=15)

        self.song_buttons = []
        if not self.song_list:
            no_song_lbl = ctk.CTkLabel(self.playlist_frame, text="ไม่พบไฟล์ .mp3 ในโฟลเดอร์นี้", text_color=self.COLOR_NEON_RED)
            no_song_lbl.pack(pady=20)
        else:
            for idx, song in enumerate(self.song_list):
                btn = ctk.CTkButton(
                    self.playlist_frame,
                    text=f"🎵 {song}",
                    anchor="w",
                    fg_color="transparent",
                    text_color=self.COLOR_TEXT,
                    hover_color="rgba(0, 243, 255, 0.2)",
                    command=lambda i=idx: self.select_and_play(i)
                )
                btn.pack(fill="x", padx=5, pady=2)
                self.song_buttons.append(btn)

        # 5. แผงปุ่มควบคุมดีไซน์ไซไฟ (Control Panel)
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(pady=20)

        # ปุ่มย้อนไปเพลงก่อนหน้า
        self.prev_btn = ctk.CTkButton(
            ctrl_frame, text="⏮", width=60, height=50, font=("Arial", 20),
            fg_color="#1a1a24", border_width=1, border_color=self.COLOR_NEON_BLUE,
            text_color=self.COLOR_NEON_BLUE, hover_color=self.COLOR_NEON_BLUE,
            command=self.prev_song
        )
        self.prev_btn.grid(row=0, column=0, padx=10)

        # ปุ่มเล่น / พักเพลง
        self.play_btn = ctk.CTkButton(
            ctrl_frame, text="▶ PLAY", width=120, height=50, font=("Arial", 16, "bold"),
            fg_color="#1a1a24", border_width=2, border_color=self.COLOR_NEON_GREEN,
            text_color=self.COLOR_NEON_GREEN, hover_color=self.COLOR_NEON_GREEN,
            command=self.toggle_play
        )
        self.play_btn.grid(row=0, column=1, padx=10)

        # ปุ่มข้ามไปเพลงถัดไป
        self.next_btn = ctk.CTkButton(
            ctrl_frame, text="⏭", width=60, height=50, font=("Arial", 20),
            fg_color="#1a1a24", border_width=1, border_color=self.COLOR_NEON_BLUE,
            text_color=self.COLOR_NEON_BLUE, hover_color=self.COLOR_NEON_BLUE,
            command=self.next_song
        )
        self.next_btn.grid(row=0, column=2, padx=10)

        # 6. แถบเลื่อนปรับความดัง (Neon Volume Slider)
        vol_frame = ctk.CTkFrame(self, fg_color="transparent")
        vol_frame.pack(pady=10, fill="x", padx=40)
        
        vol_lbl = ctk.CTkLabel(vol_frame, text="VOL:", font=("Arial", 11), text_color=self.COLOR_TEXT)
        vol_lbl.pack(side="left", padx=5)
        
        self.vol_slider = ctk.CTkSlider(
            vol_frame, from_=0, to=1, number_of_steps=100,
            button_color=self.COLOR_NEON_RED, button_hover_color=self.COLOR_TEXT,
            progress_color=self.COLOR_NEON_RED, fg_color="#222",
            command=self.set_volume
        )
        self.vol_slider.set(0.7)  # ค่าเริ่มต้นความดัง 70%
        pygame.mixer.music.set_volume(0.7)
        self.vol_slider.pack(side="left", fill="x", expand=True, padx=5)

    def select_and_play(self, index):
        """เลือกเพลงจากลิสต์บ็อกซ์แล้วสั่งเล่นทันที"""
        if 0 <= index < len(self.song_list):
            self.current_song_index = index
            self.play_current_song()

    def play_current_song(self):
        """เล่นเสียงเพลงปัจจุบันตามหลักความจริง"""
        if not self.song_list or self.current_song_index == -1:
            return

        song_name = self.song_list[self.current_song_index]
        current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
        full_path = os.path.join(current_dir, song_name)

        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()
            self.is_playing = True
            
            # อัปเดตสถานะและสี UI แบบ Realtime
            self.track_label.configure(text=song_name.upper(), text_color=self.COLOR_NEON_BLUE)
            self.status_label.configure(text="STATUS: INJECTING AUDIO SIGNAL...", text_color=self.COLOR_NEON_GREEN)
            self.play_btn.configure(text="⏸ PAUSE", border_color=self.COLOR_NEON_RED, text_color=self.COLOR_NEON_RED)
            
            # ไฮไลท์เพลงที่กำลังเลือกใน Listbox
            for idx, btn in enumerate(self.song_buttons):
                if idx == self.current_song_index:
                    btn.configure(fg_color="rgba(0, 243, 255, 0.15)", text_color=self.COLOR_NEON_BLUE)
                else:
                    btn.configure(fg_color="transparent", text_color=self.COLOR_TEXT)
        except Exception as e:
            self.track_label.configure(text="AUDIO DECODE ERROR", text_color=self.COLOR_NEON_RED)

    def toggle_play(self):
        """ฟังก์ชันสลับสถานะ เล่น/หยุดชั่วคราว"""
        if not self.song_list:
            return

        if not self.is_playing:
            if pygame.mixer.music.get_pos() == -1: # ถ้ายังไม่ได้เริ่มเล่นเลยสักเพลง
                self.play_current_song()
            else:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.play_btn.configure(text="⏸ PAUSE", border_color=self.COLOR_NEON_RED, text_color=self.COLOR_NEON_RED)
                self.status_label.configure(text="STATUS: RESUMED STREAM", text_color=self.COLOR_NEON_GREEN)
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_btn.configure(text="▶ PLAY", border_color=self.COLOR_NEON_GREEN, text_color=self.COLOR_NEON_GREEN)
            self.status_label.configure(text="STATUS: AUDIO PAUSED", text_color=self.COLOR_NEON_RED)

    def next_song(self):
        """เปลี่ยนไปเพลงถัดไปแบบวนลูป"""
        if self.song_list:
            self.current_song_index = (self.current_song_index + 1) % len(self.song_list)
            self.play_current_song()

    def prev_song(self):
        """ย้อนกลับไปเพลงก่อนหน้า"""
        if self.song_list:
            self.current_song_index = (self.current_song_index - 1) % len(self.song_list)
            self.play_current_song()

    def set_volume(self, value):
        """ปรับระดับความดังเสียง"""
        pygame.mixer.music.set_volume(float(value))

if __name__ == "__main__":
    # เปิดการทำงานของโปรแกรม
    app = NeonMusicPlayer()
    app.mainloop()
    # เมื่อปิดหน้าต่าง ให้ปิดระบบเสียงป้องกันโปรแกรมค้างหลังบ้าน
    pygame.mixer.quit()
