"""MomSakhi Reel preview, music (anonymous "Unpopular Opinion" post, SvQAA5Y5DUlUWJrTXnuC): 1080x1920 H.264, 30fps, cuts on the beat of
Mixkit "Bob" (Michael Ramir C., 120 BPM). Run with state/momsakhi/cardvenv/bin/python.

Every frame is rendered by Chromium from one HTML page driven by setT(t): pop-in text, a slow push-in per scene."""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bin"))
import appcard  # noqa: E402,F401  (sets PLAYWRIGHT_BROWSERS_PATH)
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

NAME = "reel-2026-11-19-unpopular-opinion"
MUSIC = os.path.join(HERE, "music", "bob.mp3")
MUSIC_OFFSET = 8.0    # first full groove downbeat of the track, so beat k falls at k*B
B = 0.5               # seconds per beat (120 BPM)
FPS = 30
BEATS = 27
DUR = BEATS * B
POSTER_T = 1.95

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:'Plus Jakarta Sans','Noto Color Emoji',sans-serif;
 background:radial-gradient(1000px 900px at 100% 0%,#FBE4D3 0%,rgba(251,228,211,0) 70%),
 radial-gradient(900px 800px at 0% 100%,#E8F0E8 0%,rgba(232,240,232,0) 70%),
 linear-gradient(180deg,#FCF3EA 0%,#FEF6EE 55%,#FDF3EA 100%)}
.brand{position:absolute;top:230px;width:100%;text-align:center;font:700 74px 'Liberation Serif','Times New Roman',serif;color:#D8704C}
.scene{position:absolute;left:0;right:0;top:380px;height:1160px;display:none;flex-direction:column;align-items:center;justify-content:center;
 transform-origin:50% 50%}
.pop{opacity:0;will-change:transform,opacity}
.h1{width:920px;text-align:center;font-weight:800;font-size:104px;line-height:1.1;color:#2A1D1A;letter-spacing:-3px}
.h1c{width:900px;text-align:center;font-weight:700;font-size:58px;line-height:1.2;color:#2A1D1A;letter-spacing:-1.5px;margin-top:34px}
.h1 em{font-style:normal;color:#D8704C}
.pill{margin-top:56px;padding:20px 44px;border-radius:60px;background:#FFFDFB;font-weight:600;font-size:38px;color:#8A4A32;
 box-shadow:0 0 0 2px rgba(240,225,212,.9),0 10px 28px rgba(180,140,110,.18)}
.lab{font-weight:700;font-size:62px;color:#D8704C;letter-spacing:-1.5px;margin-bottom:44px}
.lab b{font-weight:800}
.row{width:900px;display:flex;align-items:center;background:#FFFDFB;border-radius:44px;padding:28px 44px;margin-bottom:26px;
 box-shadow:0 14px 40px rgba(180,140,110,.18),0 0 0 2px rgba(240,225,212,.8)}
.row .e{font-size:76px;margin-right:34px;flex:none}
.row .x{font-weight:600;font-size:46px;line-height:1.28;color:#2A1D1A;letter-spacing:-1px}
.row .x b{font-weight:800;color:#D8704C}
.q2{width:920px;text-align:center;font-weight:700;font-size:62px;line-height:1.2;color:#8A4A32;letter-spacing:-1.5px;margin-bottom:60px}
.q{width:920px;text-align:center;font-weight:700;font-size:80px;line-height:1.18;color:#2A1D1A;letter-spacing:-2.2px}
.won{margin-top:50px;font-weight:800;font-size:150px;color:#D8704C;letter-spacing:-4px}
.att{margin-top:46px;font-weight:500;font-size:34px;color:#8A847D}
.cta1{font-weight:800;font-size:96px;color:#2A1D1A;letter-spacing:-2.5px}
.cta2{margin-top:34px;padding:26px 60px;border-radius:70px;background:#D8704C;color:#fff;font-weight:800;font-size:76px;letter-spacing:-1.5px;
 box-shadow:0 14px 34px rgba(216,112,76,.35)}
.cta3{margin-top:90px;font-weight:700;font-size:64px;color:#2A1D1A;letter-spacing:-1.5px}
.bio{margin-top:26px;font:400 32px 'Liberation Sans',Arial,sans-serif;color:#8A847D}"""

SCENES = [("s1", 0, 4), ("s2", 4, 12), ("s3", 12, 20), ("s4", 20, 27)]
POPS = {  # element id -> start beat (None: fully shown from the scene's first frame)
    "h1a": None, "h1b": 1, "h1c": 2, "pill": 3,
    "lab": 4, "r1": 5, "r2": 6.5, "r3": 8, "r4": 9.5,
    "q2": 12, "q": 15, "att": 18,
    "c1": 20, "c2": 21, "c3": 23, "bio": 24,
}
BODY = """<div class="brand">MomSakhi</div>
<div class="scene" id="s1"><div class="h1 pop" id="h1a">Unpopular opinion: &#128293;</div>
 <div class="h1 pop" id="h1b" style="margin-top:20px"><em>&ldquo;Enjoy every moment, it goes so fast&rdquo;</em></div>
 <div class="h1c pop" id="h1c">is the most guilt-inducing sentence ever said to a mother.</div>
 <div class="pill pop" id="pill">A real mom's post in the MomSakhi app</div></div>
<div class="scene" id="s2"><div class="lab pop" id="lab">What she does <b>NOT</b> enjoy:</div>
 <div class="row pop" id="r1"><div class="e">&#128722;</div><div class="x">The moment my child <b>licks a shopping cart</b></div></div>
 <div class="row pop" id="r2"><div class="e">&#9200;</div><div class="x">The <b>3 AM wake-up</b></div></div>
 <div class="row pop" id="r3"><div class="e">&#9749;</div><div class="x">The <b>cold coffee</b></div></div>
 <div class="row pop" id="r4"><div class="e">&#128085;</div><div class="x">The <b>fourth outfit change before 9 AM</b></div></div></div>
<div class="scene" id="s3"><div class="q2 pop" id="q2">I enjoy some moments. Lots of them, actually. And that&rsquo;s enough. &#128155;</div>
 <div class="q pop" id="q">What&rsquo;s the &ldquo;helpful&rdquo; advice you secretly ignore?</div>
 <div class="att pop" id="att">Anonymous mom, MomSakhi circle</div></div>
<div class="scene" id="s4"><div class="cta1 pop" id="c1">Join free:</div><div class="cta2 pop" id="c2">momsakhi.com</div>
 <div class="cta3 pop" id="c3">Comment your answer <span id="pt" style="display:inline-block">&#128071;</span></div>
 <div class="bio pop" id="bio">link in bio</div></div>"""

JS = """
const B=%(B)s, SCENES=%(scenes)s, POPS=%(pops)s;
function ease(p){p=Math.min(1,Math.max(0,p));const c=1.9;return 1+(c+1)*Math.pow(p-1,3)+c*Math.pow(p-1,2)}
window.setT=function(t){
 for(const [id,a,b] of SCENES){
  const el=document.getElementById(id), on=t>=a*B && t<b*B-1e-6;
  el.style.display=on?'flex':'none'; if(!on) continue;
  const u=(t-a*B)/((b-a)*B);
  el.style.transform='scale('+(1.0+0.05*u)+')';
  for(const c of el.querySelectorAll('.pop')){
   const s=POPS[c.id], st=(s===null)?-1:s*B, p=(t-st)/0.32, e=ease(p);
   c.style.opacity=Math.min(1,Math.max(0,p*3));
   c.style.transform='translateY('+(60*(1-Math.min(1,Math.max(0,p))))+'px) scale('+(0.7+0.3*e)+')';
  }
 }
 const pt=document.getElementById('pt'); if(pt) pt.style.transform='translateY('+(10*Math.sin(t*9))+'px)';
};
"""


def main() -> None:
    import json
    html = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:'
            'wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>%s</style></head><body>%s<script>%s</script></body></html>'
            % (CSS, BODY, JS % {"B": B, "scenes": json.dumps(SCENES), "pops": json.dumps(POPS)}))
    n = round(DUR * FPS)
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
        for i in range(n):
            t = i / FPS
            pg.evaluate("setT(%s)" % t)
            proc.stdin.write(pg.screenshot(type="jpeg", quality=95))
        pg.evaluate("setT(%s)" % POSTER_T)
        Image.open(io.BytesIO(pg.screenshot())).convert("RGB").save("%s/%s-poster.jpg" % (HERE, NAME), "JPEG", quality=92)
        b.close()
    proc.stdin.close()
    proc.wait()
    af = ("loudnorm=I=-15:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.4,afade=t=out:st=%.2f:d=1.4" % (DUR - 1.4))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-ss", str(MUSIC_OFFSET), "-t", "%.3f" % DUR, "-i", MUSIC,
                    "-map", "0:v", "-map", "1:a", "-af", af, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", "%s/%s.mp4" % (HERE, NAME)], check=True)


if __name__ == "__main__":
    main()
