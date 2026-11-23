"""MomSakhi Reel preview, Gemini voiceover (Ritu's "go-to cold remedy" post, yu9xWaveqZXBSVL0sXXR): the 11-19 look, one Gemini TTS call
for the whole short script (voice Kore); slide and pop times come from the audio's pauses. Loudness -14 LUFS (two-pass).
Run with state/momsakhi/cardvenv/bin/python. DRY=1 stops before rendering."""
import importlib.util
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bin"))
sys.path.insert(0, HERE)
import appcard  # noqa: E402,F401
import gemini_tts  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

spec = importlib.util.spec_from_file_location("base", os.path.join(HERE, "build-2026-11-19-unpopular-opinion-reel.py"))
assert spec and spec.loader
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

NAME = "reel-2026-11-22-winter-remedy"
VOICE = os.environ.get("GEMINI_VOICE", "Kore")
STYLE = ("Say casually and warmly, like a mom talking to a friend, with natural pauses and a small laugh "
         "at the cough symphony line:\n\n")
FPS, LEAD, TAIL, LEADIN = 30, 0.3, 0.7, 0.12
RAW = os.path.join(HERE, "gemini-2026-11-22", "script.wav")
FAST = RAW.replace("script.wav", "script-fast.wav")
SPEED = 1.12  # the take runs 35.9s; a mild tempo-up brings it near 30s
# where each segment's speech starts in the SPEED=1 take (pause ends between sentences, read off silencedetect)
STARTS1 = [0.28, 6.5, 11.75, 13.45, 14.67, 16.14, 17.86, 20.36, 24.22, 26.07, 31.09]

EXTRA_CSS = """.row{padding:22px 44px;margin-bottom:20px}
.note{margin-top:40px;width:880px;text-align:center;font-weight:500;font-size:34px;line-height:1.3;color:#8A847D}
.h1s{width:920px;text-align:center;font-weight:800;font-size:84px;line-height:1.1;color:#2A1D1A;letter-spacing:-2.5px}"""

BODY = """<div class="brand">MomSakhi</div>
<div class="scene" id="s1"><div class="h1c pop" id="h1a" style="margin:0 0 30px;font-size:64px;color:#8A4A32">Cold &amp; flu season is here &#129319;</div>
 <div class="h1s pop" id="h1b">Your go-to remedy when the little ones catch a cold? <span style="font-size:80px">&#127861;</span></div>
 <div class="pill pop" id="pill">A question from the MomSakhi app</div></div>
<div class="scene" id="s2"><div class="lab pop" id="lab">Every mom swears by <b>something</b>:</div>
 <div class="row pop" id="r1"><div class="e">&#129371;</div><div class="x"><b>Haldi doodh</b></div></div>
 <div class="row pop" id="r2"><div class="e">&#127807;</div><div class="x"><b>Ajwain potli</b></div></div>
 <div class="row pop" id="r3"><div class="e">&#128168;</div><div class="x"><b>Steam</b> with Vicks</div></div>
 <div class="row pop" id="r4"><div class="e">&#127855;</div><div class="x">A spoon of <b>honey &amp; ginger</b></div></div>
 <div class="row pop" id="r5"><div class="e">&#127916;</div><div class="x">Extra <b>cuddles</b> &amp; a movie day</div></div></div>
<div class="scene" id="s3"><div class="q pop" id="q">Passed down from your <em style="font-style:normal;color:#D8704C">mom or nani</em>?</div>
 <div class="q2 pop" id="q2" style="margin:44px 0 0">Or did you figure it out yourself? &#128155;</div>
 <div class="note pop" id="att">Babies under 1: always check with your pediatrician first, especially before giving honey.</div></div>
<div class="scene" id="s4"><div class="cta1 pop" id="c1" style="font-size:80px;text-align:center;width:900px;line-height:1.1">Our winter remedy list &#127861;</div>
 <div class="cta3 pop" id="c3" style="margin-top:60px">Comment yours <span id="pt" style="display:inline-block">&#128071;</span></div>
 <div class="cta2 pop" id="c2" style="margin-top:70px">momsakhi.com</div>
 <div class="bio pop" id="bio">link in bio</div></div>"""

# (scene, text, pops that appear when this text starts)
SEGMENTS = [
    ("s1", "Okay, it's officially cold and flu season... and my house already sounds like a cough symphony. Ha!", ["h1a"]),
    ("s1", "So tell me... what's your go-to remedy when the little ones catch a cold?", ["h1b", "pill"]),
    ("s2", "Is it haldi doodh?", ["lab", "r1"]),
    ("s2", "Ajwain potli?", ["r2"]),
    ("s2", "Steam with Vicks?", ["r3"]),
    ("s2", "A spoon of honey and ginger?", ["r4"]),
    ("s2", "Or just extra cuddles and a movie day?", ["r5"]),
    ("s3", "And I'm so curious... was it passed down from your mom or nani?", ["q"]),
    ("s3", "Or did you figure it out yourself?", ["q2"]),
    ("s3", "And always check with your pediatrician for babies under one, especially before giving honey.", ["att"]),
    ("s4", "Share yours in the comments, and let's build a MomSakhi winter remedy list together.", ["c1"]),
]


def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def silences(path, noise="-35dB", d=0.12):
    log = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=n=%s:d=%s" % (noise, d), "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    out, start = [], None
    for ln in log.splitlines():
        if "silence_start:" in ln:
            start = float(ln.split("silence_start:")[1].split()[0])
        elif "silence_end:" in ln and start is not None:
            out.append((start, float(ln.split("silence_end:")[1].split()[0])))
            start = None
    return out


def synth():
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    if not os.path.exists(RAW):
        gemini_tts.synth(STYLE + " ".join(t for _, t, _ in SEGMENTS), VOICE, RAW)  # ONE call; a rerun reuses the file
    if not os.path.exists(FAST):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", RAW, "-af", "atempo=%s" % SPEED, FAST], check=True)
    return FAST


def timeline(raw):
    """-> (segment start times in the raw audio, speech start, speech end): proportional to text length, snapped to a pause."""
    total = probe(raw)
    sil = silences(raw)
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    end = sil[-1][0] if sil and sil[-1][1] > total - 0.05 else total
    inner = [s for s in sil if s[0] > lead + 0.1 and s[1] < end - 0.1]
    starts = []
    for m in STARTS1:
        est = m / SPEED
        near = [s[1] for s in inner if abs(s[1] - est) < 0.2]
        starts.append(min(near, key=lambda v: abs(v - est)) if near else est)
    print("raw %.2f lead %.2f end %.2f pauses %s" % (total, lead, end, [(round(a, 2), round(b, 2)) for a, b in inner]))
    print("seg starts", [round(s, 2) for s in starts])
    return starts, lead, end


def main():
    raw = synth()
    starts, lead, end = timeline(raw)
    dur_total = LEAD + end + TAIL
    t = [LEAD + s for s in starts]
    pops, scenes = {}, []
    for (sid, _, pp), st in zip(SEGMENTS, t):
        for p in pp:
            pops[p] = st - LEADIN
        if not scenes or scenes[-1][0] != sid:
            if scenes:
                scenes[-1][2] = st - LEADIN
            scenes.append([sid, 0.0 if not scenes else st - LEADIN, dur_total])
    pops["h1a"] = None
    pops["pill"] += 0.4
    span = LEAD + end - t[-1]
    pops["c3"] = pops["c1"] + 0.25 * span
    pops["c2"] = pops["c1"] + 0.7 * span
    pops["bio"] = pops["c2"] + 0.5
    print("scenes", [(a, round(b, 2), round(c, 2)) for a, b, c in scenes])
    print("pops", {k: (None if v is None else round(v, 2)) for k, v in pops.items()}, "total %.2f" % dur_total)
    if os.environ.get("DRY"):
        return

    html = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:'
            'wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>%s%s</style></head><body>%s<script>%s</script></body></html>'
            % (base.CSS, EXTRA_CSS, BODY, base.JS % {"B": 1, "scenes": json.dumps(scenes), "pops": json.dumps(pops)}))
    n = round(dur_total * FPS)
    silent = "%s/%s-silent.mp4" % (HERE, NAME)
    enc = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-crf", "18", "-movflags", "+faststart", "-an", silent]
    proc = subprocess.Popen(enc, stdin=subprocess.PIPE)
    assert proc.stdin
    poster_t = scenes[0][2] * 0.97
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(html, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        for i in range(n):
            pg.evaluate("setT(%s)" % (i / FPS))
            proc.stdin.write(pg.screenshot(type="jpeg", quality=95))
        pg.evaluate("setT(%s)" % poster_t)
        Image.open(io.BytesIO(pg.screenshot())).convert("RGB").save("%s/%s-poster.jpg" % (HERE, NAME), "JPEG", quality=92)
        b.close()
    proc.stdin.close()
    proc.wait()

    pre = "aresample=44100,adelay=%d|%d,apad,atrim=0:%.3f" % (int(LEAD * 1000), int(LEAD * 1000), dur_total)
    tgt = "I=-14:TP=-1.5:LRA=11"
    m = subprocess.run(["ffmpeg", "-i", raw, "-af", pre + ",loudnorm=%s:print_format=json" % tgt, "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = ("loudnorm=%s:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
          % (tgt, j["input_i"], j["input_tp"], j["input_lra"], j["input_thresh"], j["target_offset"]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", raw, "-af", pre + "," + ln,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                    "-t", "%.3f" % dur_total, "-movflags", "+faststart", "%s/%s.mp4" % (HERE, NAME)], check=True)


if __name__ == "__main__":
    main()
