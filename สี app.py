def room_sensor():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center; font-family:Orbitron;'>📟 SYNAPSE SENSOR HUB</h2>", unsafe_allow_html=True)
    
    # รวม JS ทั้งหมดไว้ในตัวเดียวเพื่อประสิทธิภาพ
    all_sensors_js = f"""
    <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 20px; font-family: 'Orbitron', monospace; color: white;">
        
        <div style="overflow: hidden; white-space: nowrap; background: #0a0a0a; border: 1px solid {st.session_state.theme_color}55; border-radius: 5px; margin-bottom: 15px; padding: 5px;">
            <p id="mText" style="display: inline-block; padding-left: 100%; font-size: 14px; color: {st.session_state.theme_color}; animation: marquee 15s linear infinite;">
                SYSTEM ONLINE >>> MONITORING REAL-TIME DATA >>> SONIC & MOTION SCANNER ACTIVE...
            </p>
        </div>

        <div style="border: 1px solid {st.session_state.theme_color}33; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <small style="color: {st.session_state.theme_color};">🔊 SONIC ANALYZER</small>
            <canvas id="visualizer" style="width: 100%; height: 80px; background: #050505; border-radius: 5px; margin: 10px 0;"></canvas>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                <div><small>VOLUME</small><h2 id="vol_val" style="color: #0f0; margin:0;">0</h2></div>
                <div><small>PITCH (Hz)</small><h2 id="freq_val" style="color: #00ffff; margin:0;">0</h2></div>
            </div>
        </div>

        <div style="border: 1px solid {st.session_state.theme_color}33; padding: 15px; border-radius: 10px;">
            <small style="color: {st.session_state.theme_color};">📳 MOTION DETECTOR</small>
            <div style="text-align: center; margin-top: 10px;">
                <small>MAGNITUDE (G)</small>
                <h1 id="mag_val" style="font-size: 45px; color: #f0f; margin:0;">1.000</h1>
            </div>
            <div style="display: flex; justify-content: space-around; font-size: 12px; margin-top: 10px; color: #888;">
                <span>X: <b id="x_v">0</b></span>
                <span>Y: <b id="y_v">0</b></span>
                <span>Z: <b id="z_v">0</b></span>
            </div>
        </div>

        <button id="startBtn" style="width: 100%; margin-top: 15px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; border-radius: 10px; color: {st.session_state.theme_color}; font-family: Orbitron; cursor: pointer; font-weight: bold;">
            [ INITIALIZE SENSOR ARRAY ]
        </button>
    </div>

    <style>
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        h2, h1 {{ text-shadow: 0 0 10px currentColor; }}
    </style>

    <script>
        const btn = document.getElementById('startBtn');
        const v_canvas = document.getElementById('visualizer');
        const v_ctx = v_canvas.getContext('2d');
        
        btn.onclick = async () => {{
            btn.style.display = 'none';
            
            // --- AUDIO SYSTEM ---
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                const aCtx = new (window.AudioContext || window.webkitAudioContext)();
                const analyser = aCtx.createAnalyser();
                const source = aCtx.createMediaStreamSource(stream);
                analyser.fftSize = 128;
                source.connect(analyser);
                const dataArray = new Uint8Array(analyser.frequencyBinCount);

                function updateAudio() {{
                    requestAnimationFrame(updateAudio);
                    analyser.getByteFrequencyData(dataArray);
                    v_ctx.clearRect(0, 0, v_canvas.width, v_canvas.height);
                    let sum = 0, maxV = 0, maxI = 0;
                    for (let i = 0; i < dataArray.length; i++) {{
                        let v = dataArray[i]; sum += v;
                        if(v > maxV) {{ maxV = v; maxI = i; }}
                        v_ctx.fillStyle = '{st.session_state.theme_color}';
                        v_ctx.fillRect(i * (v_canvas.width / dataArray.length), v_canvas.height - v/2, 2, v/2);
                    }}
                    document.getElementById('vol_val').innerText = Math.round(sum/dataArray.length);
                    document.getElementById('freq_val').innerText = (sum/dataArray.length > 5) ? Math.round(maxI * aCtx.sampleRate / analyser.fftSize) : 0;
                }}
                updateAudio();
            }} catch(e) {{ alert("Audio Error: " + e); }}

            // --- MOTION SYSTEM ---
            if (typeof DeviceMotionEvent.requestPermission === 'function') {{
                await DeviceMotionEvent.requestPermission();
            }}
            window.addEventListener('devicemotion', (e) => {{
                const acc = e.accelerationIncludingGravity;
                if (!acc) return;
                let x = acc.x || 0, y = acc.y || 0, z = acc.z || 0;
                let mag = Math.sqrt(x*x + y*y + z*z) / 9.80665;
                document.getElementById('x_v').innerText = x.toFixed(2);
                document.getElementById('y_v').innerText = y.toFixed(2);
                document.getElementById('z_v').innerText = z.toFixed(2);
                document.getElementById('mag_val').innerText = mag.toFixed(3);
                document.getElementById('mag_val').style.color = (mag > 1.1 || mag < 0.9) ? "#f00" : "#f0f";
            }});
        }};
    </script>
    """
    components.html(all_sensors_js, height=550)
    
    st.markdown("---")
    st.info("💡 เคล็ดลับ: วางมือถือนิ่งๆ เพื่อดูแรงโน้มถ่วงโลก (1.00G) หรือลองผิวปากใส่ไมค์เพื่อดูคลื่นความถี่ครับ")
