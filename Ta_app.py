from pathlib import Path
import base64
import json
import mimetypes

import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# SYNAPSE NEON VISUALIZER STUDIO
# Put app.py, logo1.jpg and music files in the same folder.
# ============================================================

APP_DIR = Path(__file__).resolve().parent
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}

st.set_page_config(
    page_title="SYNAPSE NEON VISUALIZER STUDIO",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background: #03040b !important;
        color: #eafcff !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], footer, #MainMenu {
        display: none !important;
    }
    .block-container {
        max-width: 100% !important;
        padding: 0.25rem 0.35rem 0.25rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

music_files = sorted(
    [p for p in APP_DIR.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS],
    key=lambda p: p.name.lower(),
)

if not music_files:
    st.error("ยังไม่พบไฟล์เพลง กรุณาวางไฟล์ MP3/WAV ไว้ในโฟลเดอร์เดียวกับ app.py")
    st.code("app.py\nlogo1.jpg\n01-song.mp3\n02-song.mp3\n...")
    st.stop()

# Embed the tracks so the browser player can read the files directly.
# For faster loading, keep each MP3 reasonably compressed.
tracks = []
for p in music_files:
    tracks.append({
        "name": p.stem,
        "src": data_uri(p),
        "type": mimetypes.guess_type(p.name)[0] or "audio/mpeg",
    })

logo_path = APP_DIR / "logo1.jpg"
logo_uri = data_uri(logo_path) if logo_path.exists() else ""

payload = json.dumps(
    {"tracks": tracks, "logo": logo_uri},
    ensure_ascii=False,
).replace("</", "<\\/")

html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;min-height:100%;background:#03040b;color:#eaffff;font-family:Arial,Helvetica,sans-serif}
body{overflow-x:hidden}
:root{--cyan:#00f5ff;--blue:#168bff;--purple:#9b42ff;--pink:#ff2bc2;--gold:#ffd66b}
.shell{width:100%;max-width:1050px;margin:0 auto;padding:3px 5px 4px;position:relative}
.topline{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:0 2px 4px}
.brand{font-size:clamp(15px,3vw,23px);font-weight:900;letter-spacing:3px;color:#eaffff;text-shadow:0 0 7px #00eaff,0 0 18px #007cff}
.brand span{color:#ff4bd2}
.live{font-size:10px;letter-spacing:2px;color:#8dfcff;border:1px solid #00d9ff66;padding:5px 8px;border-radius:20px;box-shadow:0 0 12px #00d9ff33}
.stage-wrap{position:relative;width:100%;margin:auto;border:1px solid #1ddfff66;border-radius:16px;overflow:hidden;background:#030611;box-shadow:0 0 12px #00d9ff55,0 0 35px #6b20ff33,inset 0 0 35px #071b3a}
.stage{position:relative;width:100%;height:clamp(220px,36vh,320px);min-height:220px;overflow:hidden;background:#030611}
.stage.landscape{height:clamp(190px,30vh,280px);min-height:190px}
canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
.overlay{position:absolute;inset:0;pointer-events:none;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:5.5% 5% 6%}
.visual-title{text-align:center;width:100%;margin-top:1%;font-size:clamp(17px,4.5vw,30px);font-weight:900;letter-spacing:2px;text-transform:uppercase;color:#fff;text-shadow:0 0 5px #fff,0 0 12px #00eaff,0 0 25px #087dff;animation:titlePulse 2.2s ease-in-out infinite}
.subtitle{font-size:clamp(8px,2vw,12px);letter-spacing:4px;color:#9bfaff;margin-top:5px;text-shadow:0 0 10px #00eaff}
.logo-zone{position:relative;width:min(65%,310px);aspect-ratio:1/1;display:grid;place-items:center;margin:auto}
.orbit{position:absolute;inset:0;border:2px solid #00f5ff88;border-radius:50%;box-shadow:0 0 12px #00eaff, inset 0 0 15px #00eaff55;animation:spin 12s linear infinite}
.orbit.o2{inset:7%;border-color:#bd45ff99;box-shadow:0 0 13px #b52bff;animation:spin 8s linear infinite reverse}
.orbit.o3{inset:-7%;border:1px dashed #ff3fc9aa;animation:spin 18s linear infinite}
.logo-core{width:64%;height:64%;border-radius:50%;display:grid;place-items:center;overflow:hidden;background:radial-gradient(circle,#17264a,#060a18 65%,#000);border:2px solid #7dfaff;box-shadow:0 0 14px #00f5ff,0 0 34px #146cff,0 0 65px #8c26ff77}
.logo-core img{width:100%;height:100%;object-fit:contain}
.logo-fallback{font-size:clamp(30px,9vw,68px);font-weight:900;color:#fff;text-shadow:0 0 12px #00eaff,0 0 30px #a32cff}
.track-bottom{text-align:center;width:100%;margin-bottom:1%}
.track-bottom .track-name{font-size:clamp(14px,3.5vw,24px);font-weight:800;letter-spacing:1.5px;color:#fff;text-shadow:0 0 7px #00eaff,0 0 17px #a52dff;animation:titlePulse 2.8s infinite}
.track-bottom .tag{font-size:9px;letter-spacing:4px;color:#ffc7f2;margin-top:7px;text-shadow:0 0 9px #ff2bc2}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes titlePulse{0%,100%{filter:brightness(1);text-shadow:0 0 7px #00eaff,0 0 18px #8c31ff}50%{filter:brightness(1.55);text-shadow:0 0 10px #fff,0 0 25px #00eaff,0 0 42px #ff2bc2}}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:4px;margin:4px 1px 3px}
.group{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
button,select{font:700 11px Arial;letter-spacing:.5px;color:#eaffff;background:linear-gradient(145deg,#101c36,#090d1d);border:1px solid #00dfff88;border-radius:9px;padding:9px 11px;box-shadow:0 0 9px #00dfff22;cursor:pointer}
button:active{transform:scale(.96);box-shadow:0 0 16px #00eaff}
button.primary{background:linear-gradient(100deg,#006c9b,#6b1e9b);border-color:#70faff;box-shadow:0 0 15px #00dfff66}
button.record{border-color:#ff3d83;color:#ffb8d0}
button.recording{background:#8e123c;color:white;box-shadow:0 0 17px #ff2677}
select{max-width:100%;padding:8px}
.seek-row{display:grid;grid-template-columns:36px 1fr 36px;gap:5px;align-items:center;margin:2px 3px;color:#9cefff;font-size:9px}
input[type=range]{width:100%;accent-color:#00eaff}
.panel{border:1px solid #1b8eaa88;border-radius:10px;background:linear-gradient(135deg,#081426ee,#10091fee);padding:5px 7px;margin-top:3px;box-shadow:inset 0 0 18px #00aaff13,0 0 12px #00bfff18}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:3px}
.panel-title{font-size:11px;font-weight:900;letter-spacing:3px;color:#8ffaff;text-shadow:0 0 9px #00eaff}
.song-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:3px;max-height:118px;overflow:auto}
.song{display:flex;align-items:center;gap:5px;text-align:left;min-width:0;padding:4px 6px;border:1px solid #263c62;background:#080f20;border-radius:8px;color:#c9eaff;font-size:10px}
.song.active{border-color:#ff3bc7;background:linear-gradient(90deg,#17264a,#35103b);box-shadow:0 0 12px #ff2bc255;color:#fff}
.song .num{color:#00f5ff;font-weight:900}
.song .songtext{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.options{display:flex;gap:6px;flex-wrap:wrap}
.note{display:none;font-size:9px;color:#83a8c8;line-height:1.3;margin:3px 2px 0}
.status{font-size:10px;color:#9cfaff;min-height:14px}
@media(min-width:700px){.stage{height:clamp(260px,42vh,380px);min-height:260px}.logo-zone{width:min(34%,250px)}.overlay{padding:2% 5%}.song-list{grid-template-columns:repeat(5,minmax(0,1fr));max-height:75px}}
@media(max-width:420px){.shell{padding:2px 4px}.toolbar{gap:3px;margin:3px 1px}.group{gap:3px}button{padding:6px 7px;font-size:9px;border-radius:7px}.song-list{grid-template-columns:1fr 1fr;max-height:118px}.stage{height:clamp(210px,34vh,285px);min-height:210px}.logo-zone{width:min(55%,220px)}.visual-title{font-size:15px}.subtitle{font-size:8px}.track-bottom .track-name{font-size:14px}}
</style>
</head>
<body>
<div class="shell">
  <div class="topline">
    <div class="brand">SYNAPSE <span>VISUALIZER</span></div>
    <div class="live">● LIVE AUDIO REACTIVE</div>
  </div>

  <div class="stage-wrap">
    <div class="stage" id="stage">
      <canvas id="visual"></canvas>
      <div class="overlay">
        <div style="width:100%;text-align:center">
          <div class="visual-title">SOUND • LIGHT • ENERGY</div>
          <div class="subtitle">NEON MUSIC EXPERIENCE</div>
        </div>
        <div class="logo-zone">
          <div class="orbit o3"></div><div class="orbit"></div><div class="orbit o2"></div>
          <div class="logo-core" id="logoCore"></div>
        </div>
        <div class="track-bottom">
          <div class="track-name" id="stageTrack">SYNAPSE MUSIC STUDIO</div>
          <div class="tag">FEEL THE FREQUENCY</div>
        </div>
      </div>
    </div>
  </div>

  <div class="toolbar">
    <div class="group">
      <button id="prev">|◀</button><button class="primary" id="play">▶ PLAY</button><button id="next">▶|</button>
      <button id="shuffle">🔀</button><button id="repeat">↻</button>
    </div>
    <div class="group">
      <button id="fullscreen">⛶ FULL SCREEN</button>
    </div>
  </div>

  <div class="seek-row">
    <span id="elapsed">0:00</span><input id="seek" type="range" min="0" max="1000" value="0"><span id="duration">0:00</span>
  </div>
  <div class="toolbar" style="margin-top:0">
    <div class="group"><span style="font-size:10px;color:#9cefff">VOLUME</span><input id="volume" type="range" min="0" max="1" step=".01" value=".85" style="width:100px"></div>
    <div class="status" id="status">Ready — เลือกเพลงแล้วกด PLAY</div>
  </div>

  <div class="panel">
    <div class="panel-head"><div class="panel-title">✦ SONG LIBRARY</div><div id="count" class="status"></div></div>
    <div class="song-list" id="songList"></div>
  </div>
  <div class="note">การบันทึกจะจับภาพ Visualizer และเสียงเพลงรวมเป็นไฟล์วิดีโอจากเบราว์เซอร์ หากอุปกรณ์ไม่รองรับการบันทึก WebM ปุ่มบันทึกจะแจ้งสถานะให้ทราบ</div>
</div>

<script>
const DATA = __PAYLOAD__;
const tracks = DATA.tracks || [];
const audio = new Audio();
audio.preload = "auto";
audio.volume = 0.85;
let current = 0, playing = false, shuffled = false, repeating = false;
let audioCtx = null, analyser = null, sourceNode = null;
let recorder = null, chunks = [], recording = false;
const canvas = document.getElementById("visual");
const ctx = canvas.getContext("2d");
const stage = document.getElementById("stage");
const $ = id => document.getElementById(id);
const status = msg => $("status").textContent = msg;
const fmt = n => { if(!isFinite(n)) return "0:00"; let m=Math.floor(n/60),s=Math.floor(n%60);return m+":"+String(s).padStart(2,"0"); };
const boost = v => Math.min(1, Math.pow(Math.max(0,(v-0.02)/0.98),0.55)*1.6);

if(DATA.logo){
  const img=document.createElement("img"); img.src=DATA.logo; img.alt="SYNAPSE"; $("logoCore").appendChild(img);
}else{
  $("logoCore").innerHTML='<div class="logo-fallback">S</div>';
}

$("count").textContent = tracks.length + " TRACKS";
tracks.forEach((t,i)=>{
  const b=document.createElement("button"); b.className="song"; b.innerHTML='<span class="num">'+String(i+1).padStart(2,"0")+'</span><span class="songtext"></span>';
  b.querySelector(".songtext").textContent=t.name;
  b.addEventListener("click",()=>loadTrack(i,true)); $("songList").appendChild(b);
});

function drawList(){
  [...$("songList").children].forEach((el,i)=>el.classList.toggle("active",i===current));
  $("stageTrack").textContent=tracks[current]?.name || "SYNAPSE MUSIC STUDIO";
}
function loadTrack(i,autoplay=false){
  if(!tracks.length)return;
  current=(i+tracks.length)%tracks.length;
  audio.src=tracks[current].src; audio.load(); drawList();
  if(autoplay) playAudio();
  else status("เลือกเพลง: "+tracks[current].name);
}
async function initAudio(){
  if(audioCtx)return;
  const AC=window.AudioContext||window.webkitAudioContext;
  if(!AC)throw new Error("อุปกรณ์นี้ไม่รองรับ Web Audio");
  audioCtx=new AC();
  analyser=audioCtx.createAnalyser(); analyser.fftSize=1024; analyser.smoothingTimeConstant=.12; analyser.minDecibels=-88; analyser.maxDecibels=-12;
  sourceNode=audioCtx.createMediaElementSource(audio);
  sourceNode.connect(analyser); analyser.connect(audioCtx.destination);
}
async function playAudio(){
  try{
    await initAudio();
    if(audioCtx.state==="suspended")await audioCtx.resume();
    if(!audio.src)loadTrack(current,false);
    await audio.play(); playing=true; $("play").textContent="Ⅱ PAUSE"; status("กำลังเล่น: "+tracks[current].name);
  }catch(e){status("เล่นเพลงไม่สำเร็จ: "+e.message);}
}
function pauseAudio(){audio.pause();playing=false;$("play").textContent="▶ PLAY";status("หยุดชั่วคราว");}
$("play").addEventListener("click",()=>playing?pauseAudio():playAudio());
$("prev").addEventListener("click",()=>loadTrack(current-1,true));
$("next").addEventListener("click",()=>loadTrack(current+1,true));
$("shuffle").addEventListener("click",()=>{shuffled=!shuffled;$("shuffle").style.color=shuffled?"#ff7bdd":"#eaffff";status(shuffled?"เปิดสุ่มเพลง":"ปิดสุ่มเพลง");});
$("repeat").addEventListener("click",()=>{repeating=!repeating;$("repeat").style.color=repeating?"#ff7bdd":"#eaffff";status(repeating?"เปิดเล่นซ้ำ":"ปิดเล่นซ้ำ");});
audio.addEventListener("ended",()=>{if(repeating){audio.currentTime=0;playAudio();}else if(shuffled){let n=current;if(tracks.length>1)while(n===current)n=Math.floor(Math.random()*tracks.length);loadTrack(n,true);}else if(current<tracks.length-1)loadTrack(current+1,true);else pauseAudio();});
audio.addEventListener("timeupdate",()=>{if(audio.duration){$("seek").value=audio.currentTime/audio.duration*1000;$("elapsed").textContent=fmt(audio.currentTime);$("duration").textContent=fmt(audio.duration);}});
$("seek").addEventListener("input",()=>{if(audio.duration)audio.currentTime=Number($("seek").value)/1000*audio.duration;});
$("volume").addEventListener("input",e=>audio.volume=Number(e.target.value));
$("fullscreen").addEventListener("click",async()=>{
  try{if(!document.fullscreenElement)await stage.requestFullscreen();else await document.exitFullscreen();}
  catch(e){status("เบราว์เซอร์นี้ไม่อนุญาต Full Screen");}
});
loadTrack(0,false);

// Canvas animation: spectrum, bass pulse, laser beams, particles and rotating energy rings.
let W=0,H=0,dpr=1,particles=[];
function resize(){
  const r=stage.getBoundingClientRect(); dpr=Math.min(window.devicePixelRatio||1,2);
  W=Math.max(1,r.width);H=Math.max(1,r.height);
  canvas.width=Math.floor(W*dpr);canvas.height=Math.floor(H*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  particles=Array.from({length:Math.max(45,Math.floor(W*H/8500))},()=>({
    x:Math.random()*W,y:Math.random()*H,z:.4+Math.random()*1.8,
    vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35,
    r:.5+Math.random()*1.8,phase:Math.random()*6.28
  }));
}
window.addEventListener("resize",resize);setTimeout(resize,100);
let tick=0;
function frame(){
  requestAnimationFrame(frame);tick+=.016;
  if(!W||!H)return;
  ctx.clearRect(0,0,W,H);
  const bg=ctx.createRadialGradient(W*.5,H*.48,5,W*.5,H*.5,Math.max(W,H)*.72);
  bg.addColorStop(0,"#101632");bg.addColorStop(.55,"#070b1b");bg.addColorStop(1,"#02030a");
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
  let bins=new Uint8Array(analyser?analyser.frequencyBinCount:512);
  if(analyser)analyser.getByteFrequencyData(bins);
  let bass=0,treble=0;
  for(let i=1;i<Math.min(28,bins.length);i++)bass+=bins[i];
  for(let i=65;i<Math.min(230,bins.length);i++)treble+=bins[i];
  bass=boost((bass/27)/255);treble=boost((treble/165)/255);
  const cx=W/2,cy=H*.5,base=Math.min(W,H)*.19;
  // Moving luminous laser sheets.
  ctx.save();ctx.globalCompositeOperation="screen";
  for(let i=0;i<7;i++){
    const y=(tick*38+i*H/7)%(H+100)-50;
    const grad=ctx.createLinearGradient(0,y, W,y+30);
    grad.addColorStop(0,"transparent");grad.addColorStop(.5,i%2?"#b52cff33":"#00eaff3b");grad.addColorStop(1,"transparent");
    ctx.fillStyle=grad;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y+18+Math.sin(tick+i)*12);ctx.lineTo(W,y+27);ctx.lineTo(0,y+9);ctx.fill();
  }
  for(let i=0;i<5;i++){
    const x=(Math.sin(tick*.35+i*1.7)*.5+.5)*W;
    const g=ctx.createLinearGradient(x,0,x+Math.sin(tick+i)*W*.22,H);
    g.addColorStop(0,"transparent");g.addColorStop(.48,i%2?"#ff2bc244":"#00eaff3d");g.addColorStop(1,"transparent");
    ctx.strokeStyle=g;ctx.lineWidth=2+Math.sin(tick+i)*1.5;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x+Math.sin(tick+i)*W*.22,H);ctx.stroke();
  }
  ctx.restore();
  // Particle field.
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(const p of particles){
    p.x+=p.vx*p.z;p.y+=p.vy*p.z;
    if(p.x<0)p.x=W;if(p.x>W)p.x=0;if(p.y<0)p.y=H;if(p.y>H)p.y=0;
    const a=.28+.5*(.5+.5*Math.sin(tick*2+p.phase));
    ctx.fillStyle=`rgba(115,225,255,${a})`;ctx.shadowBlur=8;ctx.shadowColor="#00cfff";
    ctx.beginPath();ctx.arc(p.x,p.y,p.r*p.z,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
  // Center reactive energy rings.
  ctx.save();ctx.translate(cx,cy);ctx.globalCompositeOperation="lighter";
  for(let ring=0;ring<4;ring++){
    const rad=base*(.82+ring*.16)+bass*base*(ring%2? .13:.24);
    ctx.beginPath();
    for(let a=0;a<=Math.PI*2+.02;a+=.025){
      const idx=Math.floor((a/(Math.PI*2))*bins.length)%bins.length;
      const v=boost(bins[idx]/255);
      const rr=rad+v*base*.34*Math.sin(a*9+tick*2+ring);
      const x=Math.cos(a+tick*(ring%2?.12:-.09))*rr;
      const y=Math.sin(a+tick*(ring%2?.12:-.09))*rr;
      if(a===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    }
    ctx.closePath();ctx.strokeStyle=["#00f5ff","#a34dff","#ff39c8","#ffd66b"][ring];
    ctx.lineWidth=1.4+ bass*2;ctx.shadowBlur=14+bass*18;ctx.shadowColor=ctx.strokeStyle;ctx.stroke();
  }
  // Large central radial spectrum burst: every audio spike stays around the logo.
  const count=200;
  for(let i=0;i<count;i++){
    const a=i/count*Math.PI*2;
    const v=boost((bins[Math.floor(i/count*bins.length)]||0)/255);
    const inner=base*.60;
    const outer=inner+14+v*base*2.55;
    const hue=i%3===0?"#ff45d4":(i%3===1?"#27f6ff":"#a76aff");
    ctx.strokeStyle=hue;ctx.lineWidth=i%5===0?3.5:2.1;
    ctx.shadowBlur=17+v*32;ctx.shadowColor=hue;
    ctx.beginPath();ctx.moveTo(Math.cos(a)*inner,Math.sin(a)*inner);
    ctx.lineTo(Math.cos(a)*outer,Math.sin(a)*outer);ctx.stroke();
  }
  // Bass shockwave expands from the centre on each beat.
  const pulse=base*(.90+bass*.85);
  ctx.beginPath();ctx.arc(0,0,pulse,0,Math.PI*2);
  ctx.strokeStyle=`rgba(0,245,255,${.18+bass*.5})`;
  ctx.lineWidth=2+bass*5;ctx.shadowBlur=22+bass*30;ctx.shadowColor="#00efff";ctx.stroke();
  ctx.restore();
  // Subtle moving grid.
  ctx.save();ctx.strokeStyle="#2a8fb51b";ctx.lineWidth=1;
  const step=34,offset=(tick*10)%step;
  for(let x=-step+offset;x<W;x+=step){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
  for(let y=-step+offset;y<H;y+=step){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
  ctx.restore();
}
frame();

</script>
</body>
</html>
""".replace("__PAYLOAD__", payload)

components.html(html, height=620, scrolling=False)
