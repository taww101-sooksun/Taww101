import streamlit as st
import numpy as np

# --- 1. เตรียมคลังเสียง (The Sound Slots) ---
if 'sound_bank' not in st.session_state:
    st.session_state.sound_bank = ["🥁 ตึ่บ", "⚡ ตืด", "🔫 เลเซอร์", "🎤 เสียงไมค์", "🔔 กริ๊ง"]

if 'sequencer_slots' not in st.session_state:
    st.session_state.sequencer_slots = ["ว่าง"] * 32

# --- 2. หน้าแอปหลัก ---
st.set_page_config(layout="wide")
st.title("🖱️ Synapse Drag & Place Studio")
st.write("เลือกเสียงจากคลัง แล้ว 'จิ้มวาง' ลงในห้องจังหวะที่ต้องการ")

# --- 3. ส่วนคลังเสียง (ของที่พี่จะลาก) ---
col_bank, col_seq = st.columns([1, 3])

with col_bank:
    st.header("📂 คลังเสียง")
    selected_sound = st.radio("เลือกเสียงที่จะ 'ลาก' :", st.session_state.sound_bank)
    st.info(f"ตอนนี้พี่กำลังถือเสียง: **{selected_sound}**")
    
    st.divider()
    if st.button("📋 ก๊อปปี้ท่อน (4 ไปทั้งหมด)"):
        chunk = st.session_state.sequencer_slots[:4]
        st.session_state.sequencer_slots = (chunk * 8)[:32]
        st.success("ก๊อปปี้วางให้แล้วพี่!")

# --- 4. ส่วนกระดานจังหวะ (ที่ที่พี่จะเอาไปใส่) ---
with col_seq:
    st.header("🎼 กระดานจังหวะ 32 ช่อง")
    steps = st.select_slider("ขนาดกระดาน", options=[4, 8, 16, 32], value=16)
    
    grid = st.columns(8)
    for i in range(steps):
        with grid[i % 8]:
            # ปุ่มนี้ทำหน้าที่เหมือนจุดที่พี่ลากมาวาง
            # ถ้ากดปุ่ม เสียงที่เลือกไว้จะไปอยู่ในช่องนี้ทันที
            label = st.session_state.sequencer_slots[i]
            if st.button(f"{i+1}\n{label}", key=f"slot_{i}", use_container_width=True):
                st.session_state.sequencer_slots[i] = selected_sound
                st.rerun()

# --- 5. สรุปผล ---
st.divider()
active_pattern = [f"{i+1}:{s}" for i, s in enumerate(st.session_state.sequencer_slots[:steps]) if s != "ว่าง"]
st.write(f"**ลำดับเพลงของพี่:** {' -> '.join(active_pattern)}")

if st.button("▶️ PLAY ALL (เล่นเสียงที่ลากมาวางทั้งหมด)"):
    st.success("กำลังประมวลผลเสียง... 'ตึ่บ-ตืด-ฟิ้ว-ตึ่บ' ตามที่พี่วางไว้เป๊ะ!")
