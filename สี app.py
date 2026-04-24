# --- [ ส่วนจัดการ NAVIGATION: เช็กย่อหน้าให้ตรงกัน ] ---

# 1. หน้า HOME
if st.session_state.page == "HOME":
    st.markdown(f"<h1 class='neon-text' style='color:{st.session_state.main_color};'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. DJ STATION", use_container_width=True): 
            st.session_state.page = "1"
            st.rerun()
    with col2:
        if st.button("🧠 3. INTELLIGENCE CENTER", use_container_width=True): 
            st.session_state.page = "3"
            st.rerun()

# 2. หน้า 1: DJ STATION
elif st.session_state.page == "1":
    if st.button("⬅️ กลับ"): 
        st.session_state.page = "HOME"
        st.rerun()
    st.write("### 🎧 DJ Station Mode")
    # ใส่โค้ดส่วนหน้า 1 ของคุณต๊ะตรงนี้

# 3. หน้า 3: INTELLIGENCE CENTER (ส่วนที่คุณต๊ะ Error บรรทัด 79)
elif st.session_state.page == "3":
    if st.button("⬅️ กลับหน้าหลัก"): 
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown("<h2 style='text-align:center;'>🧠 INTELLIGENCE ENGINE</h2>", unsafe_allow_html=True)
    
    # ช่องกรอกแค่วันที่ (1960-2026)
    input_dt = st.date_input("เลือกวันที่เพื่อสแกนพิกัด", 
                            value=datetime.date.today(),
                            min_value=datetime.date(1960,1,1),
                            max_value=datetime.date(2026,12,31))

    if st.button("RUN FULL DECODER", use_container_width=True):
        # ดึงข้อมูลจากฟังก์ชันคำนวณ (เรียกใช้ get_synapse_report)
        res = get_synapse_report(input_dt) 
        
        st.write("---")
        # แสดงผล 7 หัวข้อที่คุณต๊ะต้องการ
        st.markdown(f"""
        ### 📋 รายงานพิกัดดิจิทัล:
        * **วัน:** {res['day']} ({res['day_val']})
        * **วันที่:** {res['date']}
        * **เดือน:** {res['month']} ({res['month_val']})
        * **ปีนักษัตร:** {res['zodiac']} ({res['z_val']})
        * **ข้างขึ้น/แรม:** {res['phase']} ({res['l_logic_text']})
        * **ธาตุ:** {res['elem']} ({res['e_val']})
        * **ราศี:** {res['rasi']}
        """)
        
        # แสดงรหัสผลลัพธ์
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.main_color}; border-radius:15px; background:black;">
                <h1 style="color:{st.session_state.main_color}; margin:0;">CODE: {res['code']}</h1>
                <p style="color:gray;">LUNAR BALANCE 1.618</p>
            </div>
        """, unsafe_allow_html=True)
