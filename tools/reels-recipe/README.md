# MomSakhi Reels recipe

Everything needed to rebuild two MomSakhi Reels on another machine, in the same style:

- `reel-2026-11-22-winter-remedy-music.mp4` (cold-remedy slides, music only, 15.5 s)
- `reel-2026-11-23-playdoh-solar-system.mp4` (Play-Doh solar-system photo, Ken Burns camera, 17.8 s)

How it works: each frame is an HTML page (1080x1920) rendered in headless Chromium by Playwright. A JS `setT(t)` function sets
the animation state for time `t`. Every frame is screenshotted as a JPEG and piped into ffmpeg (libx264, 30 fps, CRF 18). Then the
music is muxed in with fades, and a poster JPEG is saved.

## Layout

```
bin/appcard.py                                  shared helper (the reel scripts import it; nothing else used from it)
reels/build-2026-11-22-winter-remedy-music-reel.py   BUILD reel 1 (music-only winter remedy)
reels/build-2026-11-22-winter-remedy-reel.py    slide CSS/HTML for reel 1 (its own main() is the voiced variant, needs GEMINI_API_KEY)
reels/build-2026-11-19-unpopular-opinion-reel.py   base CSS + JS animation engine that reel 1 reuses
reels/gemini_tts.py                             Gemini TTS, imported by the voiced variant only (reads GEMINI_API_KEY env var)
reels/prep-2026-11-23-playdoh-photo.py          crops/grades src/playdoh-original.jpg -> playdoh-solar-board.jpg (+ playdoh-solar-post.jpg)
reels/build-2026-11-23-playdoh-solar-reel.py    BUILD reel 2 (Play-Doh solar system)
reels/playdoh-solar-board.jpg                   the prepared photo reel 2 uses (already the prep output)
reels/src/playdoh-original.jpg                  Ritu's original photo
reels/music/well-be-okay.mp3                    reel 1 track
reels/music/mixkit-15.mp3                       reel 2 track
```

Outputs are written next to the scripts in `reels/`: `<name>-silent.mp4`, `<name>.mp4`, `<name>-poster.jpg`.

## Setup

```
python3 -m venv venv
venv/bin/pip install pillow==13.0.0 playwright==1.65.0 greenlet==3.5.6 typing_extensions==4.16.0
venv/bin/playwright install chromium
# ffmpeg on PATH (built with ffmpeg 5.1.9-0+deb12u1, Debian 12; any recent ffmpeg with libx264 + aac works)
```

Python 3.11 was used. If Chromium is installed somewhere non-default, set `PLAYWRIGHT_BROWSERS_PATH`.

## Run

```
cd reels
../venv/bin/python build-2026-11-22-winter-remedy-music-reel.py   # -> reel-2026-11-22-winter-remedy-music.mp4
../venv/bin/python prep-2026-11-23-playdoh-photo.py              # optional: regenerates playdoh-solar-board.jpg
../venv/bin/python build-2026-11-23-playdoh-solar-reel.py         # -> reel-2026-11-23-playdoh-solar-system.mp4
```

Each build takes about 1-3 minutes (one screenshot per frame).

## Fonts

- **Plus Jakarta Sans** (weights 400-800) is loaded from Google Fonts at render time, so the machine needs internet access
  (OFL licence; or install it locally and the page still uses it).
- **Liberation Serif** (the "MomSakhi" wordmark in reel 2) and **Noto Color Emoji**: system fonts.
  Debian/Ubuntu: `apt install fonts-liberation fonts-noto-color-emoji`.

## Music and licences

- `well-be-okay.mp3`: "We'll Be Okay" by Michael Ramir C., Mixkit (https://assets.mixkit.co/music/1081/1081.mp3).
  Audio: 0.8 s fade in, 1.5 s fade out, loudnorm to -16 LUFS.
- `mixkit-15.mp3`: "Keep Smiling" by Ahjay Stelino, Mixkit (https://mixkit.co/free-stock-music/keep-smiling/).
  Audio: -2.9 dB gain, same fades.

Both tracks are under the Mixkit Stock Music Free License (https://mixkit.co/license/#musicFree), which allows commercial and
social-media use with no attribution required.

## Making a new reel in this style

Copy one of the build scripts. Change `NAME`, `MUSIC`, `DUR`, the `SCENES` timings (`[id, start, end]`) and the HTML in `BODY`.
For reel 2 you can also change the photo and the `CAM` keyframes (`[t, focal x, focal y, scale]`).

No credentials are in this folder. The only optional secret is `GEMINI_API_KEY`, used only by the voiced variant.
