"""MomSakhi Reel preview, music (Ritu's "go-to cold remedy" post, yu9xWaveqZXBSVL0sXXR): the 11-22 winter-remedy slides, no voice,
Mixkit "We'll Be Okay" (Michael Ramir C.), ~3.5-4s a slide. Run with state/momsakhi/cardvenv/bin/python."""
import importlib.util
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bin"))
import appcard  # noqa: E402,F401
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = load("build-2026-11-19-unpopular-opinion-reel")
voice = load("build-2026-11-22-winter-remedy-reel")

NAME = "reel-2026-11-22-winter-remedy-music"
MUSIC = os.path.join(HERE, "music", "well-be-okay.mp3")
FPS, DUR = 30, 15.5
SCENES = [["s1", 0.0, 3.5], ["s2", 3.5, 7.7], ["s3", 7.7, 11.7], ["s4", 11.7, DUR]]
POPS = {"h1a": None, "h1b": 0.3, "pill": 1.4,
        "lab": 3.5, "r1": 4.0, "r2": 4.5, "r3": 5.0, "r4": 5.5, "r5": 6.0,
        "q": 7.7, "q2": 8.9, "att": 10.0,
        "c1": 11.7, "c3": 12.5, "c2": 13.2, "bio": 13.8}


def main():
    html = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:'
            'wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>%s%s</style></head><body>%s<script>%s</script></body></html>'
            % (base.CSS, voice.EXTRA_CSS, voice.BODY, base.JS % {"B": 1, "scenes": json.dumps(SCENES), "pops": json.dumps(POPS)}))
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
        pg.evaluate("setT(%s)" % (SCENES[0][2] * 0.97))
        Image.open(io.BytesIO(pg.screenshot())).convert("RGB").save("%s/%s-poster.jpg" % (HERE, NAME), "JPEG", quality=92)
        b.close()
    proc.stdin.close()
    proc.wait()
    af = "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.8,afade=t=out:st=%.2f:d=1.5" % (DUR - 1.5)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-t", "%.3f" % DUR, "-i", MUSIC,
                    "-map", "0:v", "-map", "1:a", "-af", af, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", "%s/%s.mp4" % (HERE, NAME)], check=True)


if __name__ == "__main__":
    main()
