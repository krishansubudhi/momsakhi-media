"""A MomSakhi app-style post card, 1080x1080 JPEG, rendered from HTML in Chromium.

    python3 appcard.py --title T [--body B] [--meta "Mom · Toddler"] [--when now] --out card.jpg

Matches the 2026-11-02..11-05 cards (daycare, brave, veggies, toddler-no): cream
gradient with a peach corner and a mint corner, serif MomSakhi wordmark, a white post
card (avatar, "Anonymous mom", bookmark and more buttons, Plus Jakarta Sans title and
body, Hug / Been there / Helpful pills, reply count), `momsakhi.com • link in bio`.
Needs playwright + Pillow (the lean-jarvis venv). The font loads from Google Fonts.
"""

import argparse
import html
import io
import os

# PLAYWRIGHT_BROWSERS_PATH: set it yourself if chromium lives somewhere non-default (see README).

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1080px;position:relative;overflow:hidden;font-family:'Plus Jakarta Sans',sans-serif;
 background:radial-gradient(900px 700px at 100% 0%,#FBE4D3 0%,rgba(251,228,211,0) 70%),
 radial-gradient(800px 600px at 0% 100%,#E8F0E8 0%,rgba(232,240,232,0) 70%),
 linear-gradient(180deg,#FCF3EA 0%,#FEF6EE 55%,#FDF3EA 100%)}
.brand{position:absolute;top:44px;width:100%;text-align:center;font:700 62px 'Liberation Serif','Times New Roman',serif;color:#D8704C}
.tag{position:absolute;top:126px;width:100%;text-align:center;font:400 26px 'Liberation Sans',Arial,sans-serif;color:#8A847D}
.card{position:absolute;left:102px;width:876px;top:__TOP__px;background:#FFFDFB;border-radius:44px;padding:44px 40px 40px;
 box-shadow:0 14px 40px rgba(180,140,110,.18),0 0 0 2px rgba(240,225,212,.8)}
.top{display:flex;align-items:center;height:98px}
.av{width:98px;height:98px;border-radius:50%;background:linear-gradient(135deg,#E9D6C8,#D9BFAE);display:flex;align-items:center;justify-content:center}
.who{margin-left:24px;flex:1}
.name{font-weight:700;font-size:36px;color:#2A1D1A;letter-spacing:-1px;line-height:1.2}
.meta{font-weight:500;font-size:30px;color:#9A918A;margin-top:8px;letter-spacing:-.5px}
.btn{width:98px;height:98px;border-radius:50%;background:#fff;box-shadow:0 4px 14px rgba(150,120,100,.16);margin-left:28px;display:flex;align-items:center;justify-content:center}
h1{margin-top:56px;font-weight:700;font-size:42px;line-height:1.27;color:#2A1D1A;letter-spacing:-1px}
p{margin-top:12px;font-weight:400;font-size:36px;line-height:1.45;color:#4A4642;letter-spacing:-.8px}
.row{margin-top:36px;display:flex;align-items:center}
.pill{white-space:nowrap;height:82px;padding:0 26px;border-radius:41px;background:#FFF4EC;display:flex;align-items:center;font-weight:500;font-size:31px;color:#5E5651;margin-right:14px}
.pill span{font-size:36px;margin-right:12px}
.rc{display:flex;align-items:center;margin-left:8px;font-weight:500;font-size:34px;color:#8D837C}
.rc svg{margin-right:14px}
.foot{position:absolute;bottom:40px;width:100%;text-align:center;font:400 27px 'Liberation Sans',Arial,sans-serif;color:#8A847D}
.foot b{color:#D8704C}
</style></head><body>
<div class="brand">MomSakhi</div><div class="tag">A safe circle for every stage of motherhood</div>
<div class="card" id="card">
 <div class="top">
  <div class="av"><svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="#8A4A32" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4.5 21c.6-4.2 3.7-6.5 7.5-6.5s6.9 2.3 7.5 6.5"/></svg></div>
  <div class="who"><div class="name">Anonymous mom</div><div class="meta">__META__</div></div>
  <div class="btn"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#2A1D1A" stroke-width="2.2" stroke-linejoin="round"><path d="M6 3h12v18l-6-4.5L6 21z"/></svg></div>
  <div class="btn"><svg width="40" height="40" viewBox="0 0 24 24" fill="#2A1D1A"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg></div>
 </div>
 <h1>__TITLE__</h1>__BODY__
 <div class="row">
  <div class="pill"><span>\U0001F917</span>Hug</div><div class="pill"><span>\U0001F64B\U0001F3FD‍♀️</span>Been there</div><div class="pill"><span>\U0001F4A1</span>Helpful</div>
  <div class="rc"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#8D837C" stroke-width="1.9" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>__REPLIES__</div>
 </div>
</div>
<div class="foot">momsakhi.com • <b>link in bio</b></div>
</body></html>"""


def build(title: str, body: str, meta: str, replies: str = "0") -> str:
    e = html.escape
    nlines = max(1, -(-len(title) // 30))
    card_h = 44 + 98 + 56 + nlines * 53 + (12 + 52 * max(1, -(-len(body) // 40)) if body else 0) + 36 + 82 + 40
    top = max(205, (205 + 975 - card_h) // 2 + 20)
    return (PAGE.replace("__TOP__", str(top)).replace("__META__", e(meta))
            .replace("__TITLE__", e(title)).replace("__REPLIES__", e(replies))
            .replace("__BODY__", "<p>%s</p>" % e(body) if body else ""))


def render(title: str, body: str, meta: str, out: str, replies: str = "0") -> str:
    from PIL import Image
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        pg.set_content(build(title, body, meta, replies), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        png = pg.screenshot()
        b.close()
    Image.open(io.BytesIO(png)).convert("RGB").save(out, "JPEG", quality=92)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", default="")
    ap.add_argument("--meta", default="Mom · Toddler")
    ap.add_argument("--when", default="now")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print(render(a.title, a.body, "%s · %s" % (a.meta, a.when), a.out))
