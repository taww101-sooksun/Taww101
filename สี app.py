import streamlit as st
import time

# --- 🎭 1. จัดเต็ม CSS: สายรุ้งวิ่ง 10s + ปุ่มมีมิติ ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    }
    @keyframes RainbowFlow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    
    /* โลโก้ Logo3.jpg กะพริบเรืองแสง */
    .logo-glow { border: 5px solid #00ff00; box-shadow: 0 0 20px #00ff00; border-radius: 50%; animation: glow 1s infinite alternate; }
    @keyframes glow { from { border-color: #ff0000; box-shadow: 0 0 10px #ff0000; } to { border-color: #00ff00; box-shadow: 0 0 30px #00ff00; } }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัวเครื่อง (Logo3.jpg + 🕒) ---
c1, c2 = st.columns([1, 4])
with c1: st.markdown('<div class="logo-glow"><img src="Logo3.jpg" width="100" onerror="this.src=\'https://via.placeholder.com/100?text=Logo3\'"></div>', unsafe_allow_html=True)
with c2: 
    st.markdown(f"<h1>SYNAPSE 8-LAYERS ENGINE</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#00ff00; text-align:right;'>🕒 {time.strftime('%H:%M:%S')} | 6 มี.ค. 26</h3>", unsafe_allow_html=True)

# --- 🎼 3. กระดานเสียง 8 บรรทัด (8 Layers) ---
st.divider()
tabs = st.tabs(["[ 04 ]", "[ 08 ]", "[ 16 ]", "[ 32 ]"])

# รายชื่อเสียงให้เลือก
sound_options = ["🔴 ตึ่บ (KICK)", "🔵 จิ้ว (BASS)", "🟢 แชะ (HAT)", "🟣 ปึ้ง (SNARE)", "🟡 ฟิ้ว (LEAD)", "🟠 แป๊ว (SYNTH)", "⚪ วิ้ง (PERC)", "🟤 ครืด (NOISE)"]

def create_layer_grid(steps):
    for layer in range(8): # 8 บรรทัดตามสั่ง!
        c_sound, c_grid, c_control = st.columns([2, 5, 3])
        
        with c_sound:
            # เลือกเสียงได้หลากหลาย
            choice = st.selectbox(f"L-{layer+1}", sound_options, key=f"sel_{steps}_{layer}")
        
        with c_grid:
            # กระดานแบ่งห้อง
            cols = st.columns(8)
            for i in range(min(steps, 8)): # โชว์ตัวอย่างในหน้าจอ
                cols[i].checkbox("", key=f"ck_{steps}_{layer}_{i}")
        
        with c_control:
            # กดเสียงไหน ลูกเล่น 3 ปุ่มสไลด์จะขึ้นบอก (Balance/Level/FX)
            with st.expander("🎚️ 3-SLIDERS"):
                st.slider("BALANCE", 0, 100, 50, key=f"b_{steps}_{layer}")
                st.slider("LEVEL", 0, 100, 80, key=f"l_{steps}_{layer}")
                st.slider("FX-DEPTH", 0, 100, 20, key=f"f_{steps}_{layer}")

with tabs[0]: create_layer_grid(4)
with tabs[1]: create_layer_grid(8)
with tabs[2]: create_layer_grid(16)
with tabs[3]: create_layer_grid(32)

# --- 🚀 4. ปุ่มสั่งการมหาประลัย ---
st.divider()
st.button("🔴 EXECUTE REAL SOUND", use_container_width=True)
st.markdown("<p style='text-align:center;'>\"อยู่นิ่งๆ ไม่เจ็บตัว\"</p>", unsafe_allow_html=True)
