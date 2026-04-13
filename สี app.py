import streamlit as st
import streamlit.components.v1 as components
import os
import random

# แก้ Import เป็นพิมพ์เล็กให้ชัวร์
import streamlit as st

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="SYNAPSE DJ", layout="wide")

music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'idx' not in st.session_state: st.session_state.idx = 0
    curr = music_files[st.session_state.idx]
    nxt = music_files[(st.session_state.idx + 1) % len(music_files)]

    st.title("🎧 SYNAPSE DJ STATION")
    st.info(f"กำลังจะโหลด: {curr}")

    html_code = f"""
    <div style="background:#111; padding:20px; border-radius:15px; text-align:center; border:2px solid #00f2fe;">
        <h2 style="color:#00f2fe; font-family:sans-serif;">DECK A: {curr}</h2>
        <div id="status" style="color:#ff007f; margin:10px;">สถานะ: รอการกดปุ่ม</div>
        <button id="btn" style="padding:15px 30px; background:#00f2fe; border:none; border-radius:10px; font-weight:bold; cursor:pointer;" onclick="start()">กดตรงนี้เพื่อเริ่มเล่น</button>
    </div>

    <script>
        let ctx;
        async function start() {{
            try {{
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                document.getElementById('status').innerText = "กำลังโหลดไฟล์เพลง...";
                document.getElementById('btn').style.display = "none";

                // ใช้ชื่อไฟล์แบบดั้งเดิมก่อน ถ้าไม่ได้จะใช้ encode
                const response = await fetch("./" + encodeURIComponent("{curr}"));
                if (!response.ok) throw new Error("หาไฟล์ไม่เจอ (404)");
                
                const data = await response.arrayBuffer();
                const buffer = await ctx.decodeAudioData(data);
                
                const source = ctx.createBufferSource();
                source.buffer = buffer;
                source.connect(ctx.destination);
                source.start(0);
                
                document.getElementById('status').innerText = "▶️ กำลังเล่น: {curr}";
                document.getElementById('status').style.color = "#39FF14";
            }} catch (err) {{
                document.getElementById('status').innerText = "⚠️ พังเพราะ: " + err.message;
                document.getElementById('btn').style.display = "block";
                document.getElementById('btn').innerText = "ลองกดอีกครั้ง";
            }}
        }}
    </script>
    """
    components.html(html_code, height=250)
else:
    st.error("ไม่เจอไฟล์ .mp3 ในเครื่องเลยเพื่อน เช็กใน GitHub อีกรอบนะ")
