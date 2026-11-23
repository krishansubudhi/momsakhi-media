"""MomSakhi Reel (Ritu's Play-Doh solar-system project): her edited photo (playdoh-solar-board.jpg) in a card on the cream MomSakhi
page, a Ken Burns camera across it, six short text slides, end card. Mixkit "Keep Smiling" (Ahjay Stelino), no voice.
Run with state/momsakhi/cardvenv/bin/python."""
import base64
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bin"))
import appcard  # noqa: E402,F401  (sets PLAYWRIGHT_BROWSERS_PATH)
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

NAME = "reel-2026-11-23-playdoh-solar-system"
MUSIC = os.path.join(HERE, "music", "mixkit-15.mp3")
FPS, DUR = 30, 17.8
SCENES = [["s1", 0.0, 3.0], ["s2", 3.0, 6.6], ["s3", 6.6, 9.6], ["s4", 9.6, 12.8], ["s5", 12.8, 15.6], ["s6", 15.6, DUR]]
CAM = [[0.0, 500, 627, 1.0], [3.0, 500, 560, 1.12], [6.6, 650, 300, 1.45], [9.6, 300, 560, 1.5], [12.8, 330, 1000, 1.4],
       [15.6, 500, 627, 1.12]]   # t, focal x, focal y (image px, 1000 wide), scale
POSTER_T = 2.6

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:'Plus Jakarta Sans','Noto Color Emoji',sans-serif;
 background:radial-gradient(1000px 900px at 100% 0%,#FBE4D3 0%,rgba(251,228,211,0) 70%),
 radial-gradient(900px 800px at 0% 100%,#E8F0E8 0%,rgba(232,240,232,0) 70%),
 linear-gradient(180deg,#FCF3EA 0%,#FEF6EE 55%,#FDF3EA 100%)}
.brand{position:absolute;top:96px;width:100%;text-align:center;font:700 74px 'Liberation Serif','Times New Roman',serif;color:#D8704C}
#card{position:absolute;left:40px;top:230px;width:1000px;height:1180px;border-radius:56px;overflow:hidden;background:#BFE3F5;
 box-shadow:0 24px 60px rgba(180,140,110,.28),0 0 0 6px #FFFDFB}
#pic{position:absolute;left:0;top:0;width:1000px;height:1255px;transform-origin:0 0;will-change:transform}
.scene{position:absolute;left:80px;right:80px;top:1470px;height:380px;display:none;flex-direction:column;align-items:center;justify-content:center}
.pop{opacity:0;will-change:transform,opacity}
.t{width:920px;text-align:center;font-weight:800;font-size:66px;line-height:1.14;color:#2A1D1A;letter-spacing:-2px}
.t.sm{font-size:58px;letter-spacing:-1.5px}
.t em{font-style:normal;color:#D8704C}
.end{position:absolute;left:0;right:0;top:0;bottom:0;display:none;flex-direction:column;align-items:center;justify-content:center}
.e1{font-weight:800;font-size:104px;color:#2A1D1A;letter-spacing:-3px}
.e2{margin-top:50px;font-weight:700;font-size:64px;color:#8A4A32;letter-spacing:-1.5px}
.e3{margin-top:44px;padding:26px 64px;border-radius:70px;background:#D8704C;color:#fff;font-weight:800;font-size:76px;letter-spacing:-1.5px;
 box-shadow:0 14px 34px rgba(216,112,76,.35)}"""

BODY = """<div class="brand" id="brand">MomSakhi</div>
<div id="card"><img id="pic" src="data:image/jpeg;base64,%(img)s"></div>
<div class="scene" id="s1"><div class="t pop" id="t1">We made the solar system&hellip; <em>out of Play-Doh</em> &#129680;</div></div>
<div class="scene" id="s2"><div class="t sm pop" id="t2">8 planets + dwarf planets: <em>Pluto, Ceres, Eris, Makemake &amp; Haumea</em> &#128301;</div></div>
<div class="scene" id="s3"><div class="t pop" id="t3">My son picked every planet&rsquo;s <em>color</em> &#127912;</div></div>
<div class="scene" id="s4"><div class="t sm pop" id="t4">A fun, educational play idea for kids: <em>learn through play!</em> &#127775;</div></div>
<div class="scene" id="s5"><div class="t sm pop" id="t5">What&rsquo;s your favorite learn-through-play project? &#128071;</div></div>
<div class="end" id="s6"><div class="e1 pop" id="e1">Find your village</div><div class="e2 pop" id="e2">MomSakhi app</div>
 <div class="e3 pop" id="e3">momsakhi.com</div></div>"""

JS = """
const SCENES=%(scenes)s, CAM=%(cam)s, END=%(end)s;
function ease(p){p=Math.min(1,Math.max(0,p));const c=1.9;return 1+(c+1)*Math.pow(p-1,3)+c*Math.pow(p-1,2)}
function sm(u){u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)}
function cam(t){
 let i=0; while(i<CAM.length-2 && t>=CAM[i+1][0]) i++;
 const a=CAM[i], b=CAM[i+1], u=sm((t-a[0])/(b[0]-a[0]));
 const L=(k)=>a[k]+(b[k]-a[k])*u, s=L(3);
 let tx=500-L(1)*s, ty=590-L(2)*s;
 tx=Math.min(0,Math.max(1000-1000*s,tx)); ty=Math.min(0,Math.max(1180-1255*s,ty));
 return 'translate('+tx+'px,'+ty+'px) scale('+s+')';
}
window.setT=function(t){
 document.getElementById('pic').style.transform=cam(t);
 const card=document.getElementById('card'), ended=t>=END;
 const f=ended?Math.max(0,1-(t-END)/0.35):1;
 card.style.opacity=f; card.style.transform='scale('+(0.94+0.06*f)+')';
 document.getElementById('brand').style.display=ended?'none':'block';
 for(const [id,a,b] of SCENES){
  const el=document.getElementById(id), on=t>=a && t<b-1e-6;
  el.style.display=on?'flex':'none'; if(!on) continue;
  const kids=el.querySelectorAll('.pop');
  kids.forEach((c,k)=>{
   const p=(t-a-0.12*k)/0.34, e=ease(p);
   c.style.opacity=Math.min(1,Math.max(0,p*3));
   c.style.transform='translateY('+(50*(1-Math.min(1,Math.max(0,p))))+'px) scale('+(0.78+0.22*e)+')';
  });
 }
};
"""


def main():
    with open(os.path.join(HERE, "playdoh-solar-board.jpg"), "rb") as f:
        img = base64.b64encode(f.read()).decode()
    html = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:'
            'wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>%s</style></head><body>%s<script>%s</script></body></html>'
            % (CSS, BODY % {"img": img}, JS % {"scenes": json.dumps(SCENES), "cam": json.dumps(CAM), "end": SCENES[-1][1]}))
    silent = "%s/%s-silent.mp4" % (HERE, NAME)
    enc = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-crf", "18", "-movflags", "+faststart", "-an", silent]
    proc = subprocess.Popen(enc, stdin=subprocess.PIPE)
    assert proc.stdin
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(html, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        for i in range(round(DUR * FPS)):
            pg.evaluate("setT(%s)" % (i / FPS))
            proc.stdin.write(pg.screenshot(type="jpeg", quality=95))
        pg.evaluate("setT(%s)" % POSTER_T)
        Image.open(io.BytesIO(pg.screenshot())).convert("RGB").save("%s/%s-poster.jpg" % (HERE, NAME), "JPEG", quality=92)
        b.close()
    proc.stdin.close()
    proc.wait()
    af = "volume=-2.9dB,afade=t=in:st=0:d=0.8,afade=t=out:st=%.2f:d=1.5" % (DUR - 1.5)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-t", "%.3f" % DUR, "-i", MUSIC,
                    "-map", "0:v", "-map", "1:a", "-af", af, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", "%s/%s.mp4" % (HERE, NAME)], check=True)


if __name__ == "__main__":
    main()
