import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Music Video Player Pro", layout="wide")

# CSS จัดการหน้าจอให้เหมาะกับการแคปวิดีโอ
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    }
    @keyframes RainbowFlow {
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
    }
    #MainMenu, footer, header {visibility: hidden;}
    .stFileUploader {background: rgba(255,255,255,0.2); border-radius: 15px; padding: 20px; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Music & Video Crossfader")

# ช่องอัปโหลดไฟล์ (เลือกทั้งเพลงและรูปพร้อมกันได้เลย)
uploaded_files = st.file_uploader("เลือกไฟล์เพลง (MP3) และไฟล์รูปปก (JPG/PNG)", type=["mp3", "jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    songs = []
    images = []
    
    for f in uploaded_files:
        b64 = base64.b64encode(f.read()).decode()
        if f.type.startswith("audio"):
            songs.append({"name": f.name, "data": f"data:audio/mp3;base64,{b64}"})
        else:
            images.append(f"data:image/jpeg;base64,{b64}")

    # ถ้าไม่มีรูป ให้ใช้สีพื้นฐาน
    if not images:
        images = ["https://via.placeholder.com/500/AFEEEE/000000?text=Enjoy+Music"]

    player_html = f"""
    <div id="display-container" style="position: relative; width: 100%; height: 500px; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5); background: #000;">
        <div id="visualizer" style="position: absolute; width: 100%; height: 100%; opacity: 0.4;">
             <div style="width:100%;height:100%; background: radial-gradient(circle, #FF7F50, transparent);"></div>
        </div>

        <div style="position: absolute; top: 0; width: 100%; background: rgba(0,0,0,0.6); color: #AFEEEE; padding: 15px; z-index: 10;">
            <marquee id="marquee" style="font-size: 24px; font-weight: bold;">กรุณากดปุ่มเพื่อเริ่มรายการ...</marquee>
        </div>

        <div id="album-cover" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 300px; height: 300px; border: 10px solid #FF7F50; border-radius: 20px; background-size: cover; background-position: center; transition: all 1s ease-in-out; z-index: 5;"></div>
        
        <button id="start-btn" style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); padding: 15px 40px; font-size: 20px; background: #FF7F50; color: white; border: none; border-radius: 50px; cursor: pointer; z-index: 20;">START SESSION</button>
    </div>

    <script>
        const playlist = {songs};
        const covers = {images};
        let currentIndex = 0;
        const fadeTime = 15;

        const btn = document.getElementById('start-btn');
        const marquee = document.getElementById('marquee');
        const albumCover = document.getElementById('album-cover');

        function playTrack(index) {{
            if (index >= playlist.length) index = 0;
            const track = playlist[index];
            const audio = new Audio(track.data);
            audio.volume = 0;
            
            // เปลี่ยนรูปปก (วนลูปรูปที่มี)
            albumCover.style.backgroundImage = "url('" + covers[index % covers.length] + "')";
            marquee.innerText = "NOW PLAYING: " + track.name + " --- NEXT: " + (playlist[index+1] ? playlist[index+1].name : playlist[0].name);
            
            audio.play();
            fadeIn(audio);

            audio.ontimeupdate = function() {{
                const timeLeft = audio.duration - audio.currentTime;
                if (timeLeft <= fadeTime && !audio.isFadingOut) {{
                    audio.isFadingOut = true;
                    fadeOut(audio);
                    playTrack(index + 1);
                }}
            }};
        }}

        function fadeIn(a) {{
            let v = 0;
            const itv = setInterval(() => {{ if(v<1) {{v+=0.02; a.volume=v;}} else clearInterval(itv); }}, (fadeTime*1000)/50);
        }}

        function fadeOut(a) {{
            let v = 1;
            const itv = setInterval(() => {{ if(v>0) {{v-=0.02; a.volume=v;}} else {{clearInterval(itv); a.pause();}} }}, (fadeTime*1000)/50);
        }}

        btn.onclick = () => {{
            btn.style.display = 'none';
            playTrack(0);
        }};
    </script>
    """
    components.html(player_html, height=550)

else:
    st.info("💡 วิธีใช้: เลือกไฟล์เพลง (.mp3) และไฟล์รูป (.jpg/.png) พร้อมกันหลายๆ ไฟล์ได้เลยครับ")
