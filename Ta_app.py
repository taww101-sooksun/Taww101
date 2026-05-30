import os
import threading
import time
import tkinter as tk
from tkinter import messagebox
# ต้องติดตั้งเพิ่มเติม: pip install pygame
import pygame


class MultiApp:

    def __init__(self, root):
        self.root = root
        self.root.title("ระบบรวม GPS, แชต, เพลง")
        self.root.geometry("500x400")

        # 1. ตั้งค่าระบบเพลง (ดึงไฟล์จากโฟลเดอร์เดียวกับ .py)
        pygame.mixer.init()
        # หาโฟลเดอร์ปัจจุบันที่ไฟล์ .py นี้เซฟอยู่
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        # เปลี่ยนชื่อไฟล์ให้ตรงกับที่มีในโฟลเดอร์จริง
        self.music_file = os.path.join(self.current_dir, "song.mp3")

        # ตัวแปรจำลองระบบ
        self.gps_status = "กำลังค้นหาสัญญาณ..."
        self.chat_history = []

        # สเกลหน้าจอ GUI
        self.create_widgets()

        # 2. เริ่มทำงานเบื้องหลัง (Background Threads) เพื่อไม่ให้หน้าจอค้าง
        self.start_threads()

    def create_widgets(self):
        # ส่วนแสดงผล GPS
        self.lbl_gps = tk.Label(
            self.root, text=f"GPS: {self.gps_status}", fg="blue"
        )
        self.lbl_gps.pack(pady=10)

        # ส่วนระบบเพลง
        self.btn_play = tk.Button(
            self.root, text="เล่นเพลง (song.mp3)", command=self.play_music
        )
        self.btn_play.pack(pady=5)

        # ส่วนแชต (จำลองหน้าต่างแชต)
        self.txt_chat = tk.Text(self.root, height=10, width=50)
        self.txt_chat.pack(pady=10)

        self.entry_msg = tk.Entry(self.root, width=40)
        self.entry_msg.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_send = tk.Button(
            self.root, text="ส่งแชต", command=self.send_message
        )
        self.btn_send.pack(side=tk.LEFT, pady=5)

    def start_threads(self):
        # แยกเธรดสำหรับอัปเดต GPS เพื่อไม่ให้ขัดจังหวะการพิมพ์แชตหรือเล่นเพลง
        gps_thread = threading.Thread(target=self.update_gps_loop, daemon=True)
        gps_thread.start()

        # แยกเธรดสำหรับรับข้อมูลแชตจาก Server (ถ้ามีระบบ Backend Network)
        chat_thread = threading.Thread(
            target=self.receive_chat_loop, daemon=True
        )
        chat_thread.start()

    # --- ฟังก์ชันจัดการเสียงเพลง ---
    def play_music(self):
        if os.path.exists(self.music_file):
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play()
                messagebox.showinfo("ระบบเพลง", "กำลังเล่นเสียง...")
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเล่นเพลงได้: {e}")
        else:
            messagebox.showwarning(
                "ไม่พบไฟล์",
                f"กรุณานำไฟล์ 'song.mp3' ไปวางไว้ที่เดียวกับไฟล์โปรแกรม\n{self.current_dir}",
            )

    # --- ฟังก์ชันจำลอง GPS Real-time (ทำงานแยกใน Thread) ---
    def update_gps_loop(self):
        import random  # ใช้จำลองพิกัดเปลี่ยนไปเรื่อยๆ

        while True:
            # ของจริงจุดนี้จะดึงค่าจากโมดูล Hardware GPS หรือ GPS API
            lat = round(random.uniform(13.0, 14.0), 4)
            lng = round(random.uniform(100.0, 101.0), 4)

            # อัปเดตข้อความบนหน้าจอหลักอย่างปลอดภัย
            self.lbl_gps.config(text=f"GPS Real-time พิกัด: {lat}, {lng}")
            time.sleep(2)  # อัปเดตทุกๆ 2 วินาที โดยไม่ทำให้โปรแกรมค้าง

    # --- ฟังก์ชันระบบแชต ---
    def send_message(self):
        msg = self.entry_msg.get()
        if msg:
            # ในระบบจริง คุณต้องส่งค่า msg นี้ไปที่ Server (Socket / Webhook)
            self.txt_chat.insert(tk.END, f"คุณ: {msg}\n")
            self.entry_msg.delete(0, tk.END)

    def receive_chat_loop(self):
        # จำลองการรอรับข้อมูลแชตจากคนอื่นเข้ามาในระบบ
        while True:
            time.sleep(5)  # สมมุติว่าทุก 5 วินาที มีข้อความใหม่เข้า
            # ของจริงจะต้องเขียนโค้ดดึงข้อมูลจาก Socket connection ตรงนี้
            # self.txt_chat.insert(tk.END, "เพื่อน: สวัสดีพิกัดนายอยู่ไหนนะ?\n")
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiApp(root)
    root.mainloop()
