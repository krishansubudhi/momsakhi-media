import math, subprocess, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; FPS=30; DUR=24.0
FP="/Users/ritu/lean-jarvis/state/tmp/fonts/PlusJakartaSans.ttf"
def F(sz,w=800):
    f=ImageFont.truetype(FP,sz)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
SERIF="/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
INK=(42,29,26); COR=(216,112,76); BR=(138,74,50)
# background
bg=Image.new("RGB",(W,H)); px=bg.load()
for y in range(H):
    t=y/H; c=(int(252-0*t),int(243+3*t),int(234+4*t))
    for x in range(W): px[x,y]=c
bg=bg.convert("RGBA")
bg=bg.convert("RGB")
for box,col in (((600,-500,1500,400),(251,228,211)),((-500,1500,400,2400),(232,240,232))):
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).ellipse(box,fill=170); m=m.filter(ImageFilter.GaussianBlur(120))
    bg.paste(Image.new("RGB",(W,H),col),(0,0),m)
bg=bg.convert("RGBA")
d=ImageDraw.Draw(bg)
d.text((W/2,134),"MomSakhi",font=ImageFont.truetype(SERIF,74),fill=COR,anchor="mm")
# card
CX,CY,CW,CH=40,230,1000,1180
def rr(img,box,r,fill):
    ImageDraw.Draw(img).rounded_rectangle(box,r,fill=fill)
sm=Image.new("L",(W,H),0); ImageDraw.Draw(sm).rounded_rectangle((CX,CY+24,CX+CW,CY+CH+24),56,fill=80); sm=sm.filter(ImageFilter.GaussianBlur(30))
bg=bg.convert("RGB"); bg.paste(Image.new("RGB",(W,H),(180,140,110)),(0,0),sm); bg=bg.convert("RGBA")
rr(bg,(CX-6,CY-6,CX+CW+6,CY+CH+6),60,(255,253,251))
# night scene inside card
card=Image.new("RGB",(CW,CH)); cp=card.load()
for y in range(CH):
    t=y/CH; c=(int(43+60*t),int(42+40*t),int(94+40*t))
    for x in range(CW): cp[x,y]=c
card=card.convert("RGBA"); cd=ImageDraw.Draw(card)
# moon
cd.ellipse((660,110,880,330),fill=(255,239,190)); cd.ellipse((720,90,940,310),fill=(60,58,112))
glow=Image.new("RGBA",(CW,CH),(0,0,0,0)); ImageDraw.Draw(glow).ellipse((560,60,860,360),fill=(255,230,160,50))
card=Image.alpha_composite(card,glow.filter(ImageFilter.GaussianBlur(40))); cd=ImageDraw.Draw(card)
# hills / cozy bed
cd.ellipse((-200,820,700,1500),fill=(58,70,120)); cd.ellipse((350,900,1300,1600),fill=(70,84,134))
# open book
cd.polygon([(260,1020),(500,980),(500,1130),(260,1170)],fill=(255,247,235)); cd.polygon([(740,1020),(500,980),(500,1130),(740,1170)],fill=(250,238,220))
cd.line([(500,980),(500,1130)],fill=(216,112,76),width=6)
for i in range(4):
    cd.line([(290,1045+i*25-i*3),(470,1010+i*25-i*3)],fill=(222,200,170),width=5); cd.line([(710,1045+i*25-i*3),(530,1010+i*25-i*3)],fill=(222,200,170),width=5)
# duck
def duck(dr,x,y,s=1.0):
    dr.ellipse((x-130*s,y-70*s,x+130*s,y+90*s),fill=(255,214,90))
    dr.polygon([(x-130*s,y-10*s),(x-205*s,y-50*s),(x-160*s,y+30*s)],fill=(255,200,70))
    dr.ellipse((x+50*s,y-190*s,x+170*s,y-70*s),fill=(255,214,90))
    dr.polygon([(x+160*s,y-140*s),(x+225*s,y-120*s),(x+160*s,y-100*s)],fill=(244,140,60))
    dr.ellipse((x+120*s,y-160*s,x+136*s,y-144*s),fill=(42,29,26))
    dr.ellipse((x-60*s,y-20*s,x+60*s,y+60*s),fill=(247,190,60))
duck(cd,330,830,1.15)
# golden egg
def egg(dr,x,y,s=1.0):
    dr.ellipse((x-60*s,y-80*s,x+60*s,y+70*s),fill=(255,196,40)); dr.ellipse((x-35*s,y-55*s,x-12*s,y-20*s),fill=(255,236,150))
egg(cd,720,900,1.2)
mask=Image.new("L",(CW,CH),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,CW,CH),50,fill=255)
CARD=card; CMASK=mask
def star(dr,x,y,r,col):
    dr.polygon([(x,y-r),(x+r*.25,y-r*.25),(x+r,y),(x+r*.25,y+r*.25),(x,y+r),(x-r*.25,y+r*.25),(x-r,y),(x-r*.25,y-r*.25)],fill=col)
random.seed(4); STARS=[(random.randint(40,960),random.randint(40,640),random.randint(8,20),random.random()*6) for _ in range(26)]
SC=[
 ("The bedtime story my kid makes me tell <em>EVERY. SINGLE. NIGHT.</em>",0,4.4,62),
 ("At our house it&rsquo;s the duck that laid <em>golden eggs</em>",4.4,8.0,64),
 ("And now he&rsquo;s the director: <em>&ldquo;Do the poor man&rsquo;s greedy voice!&rdquo;</em>",8.0,12.0,60),
 ("When the poor man cuts the duck open, he gasps like it&rsquo;s <em>the first time. Every time.</em>",12.0,16.0,56),
 ("Last night he changed the ending: the duck flies away and lays golden eggs <em>only for kind people</em>",16.0,20.0,52),
 ("Which story is on <em>repeat</em> at your house?",20.0,22.6,62),
]
import re
def layout(txt,sz,maxw=920):
    toks=re.findall(r'<em>|</em>|[^\s<]+',txt.replace("&rsquo;","’").replace("&ldquo;","“").replace("&rdquo;","”"))
    f=F(sz); em=False; words=[]
    for t in toks:
        if t=="<em>": em=True
        elif t=="</em>": em=False
        else: words.append((t,em))
    lines=[];cur=[];w=0;sp=f.getlength(" ")
    for t,e in words:
        tw=f.getlength(t)
        if cur and w+sp+tw>maxw: lines.append(cur);cur=[];w=0
        w+=(sp if cur else 0)+tw; cur.append((t,e,tw))
    lines.append(cur); return f,lines,sp
def textlayer(txt,sz):
    L=Image.new("RGBA",(W,420),(0,0,0,0)); dr=ImageDraw.Draw(L); f,lines,sp=layout(txt,sz)
    lh=int(sz*1.18); y=(420-lh*len(lines))/2
    for ln in lines:
        tw=sum(t[2] for t in ln)+sp*(len(ln)-1); x=(W-tw)/2
        for t,e,w in ln:
            dr.text((x,y),t,font=f,fill=COR if e else INK); x+=w+sp
        y+=lh
    return L
TL=[textlayer(s[0],s[3]) for s in SC]
def ease(p):
    p=min(1,max(0,p)); return 1+2.9*(p-1)**3+1.9*(p-1)**2
def frame(t):
    im=bg.copy()
    end=t>=22.6
    if not end:
        c=CARD.copy(); cd=ImageDraw.Draw(c)
        for x,y,r,ph in STARS:
            a=0.5+0.5*math.sin(t*2+ph); v=int(150+105*a); star(cd,x,y,r*(0.7+0.3*a),(255,v,int(v*.8)+30) if False else (255,244,200))
        # bob egg glow
        im.paste(c,(CX,CY),CMASK)
        for i,(s,a,b,_) in enumerate(SC):
            if a<=t<b:
                p=ease((t-a)/0.4); o=min(1,(b-t)/0.25) if True else 1
                al=max(0,min(1,p))*max(0,min(1,o)); L=TL[i].copy()
                L.putalpha(L.getchannel("A").point(lambda v:int(v*al)))
                dy=int((1-p)*40); im.alpha_composite(L,(0,1440+dy))
    else:
        dr=ImageDraw.Draw(im); p=ease((t-22.6)/0.5)
        # brand removed on end card: cover
        im.paste(bg.crop((0,60,W,220)).resize((W,160)),(0,60)) 
        L=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(L)
        d2.text((W/2,820),"Find your village",font=F(104),fill=INK,anchor="mm")
        d2.text((W/2,960),"MomSakhi app",font=F(64,700),fill=BR,anchor="mm")
        d2.rounded_rectangle((250,1030,830,1150),60,fill=COR); d2.text((W/2,1092),"momsakhi.com",font=F(66),fill=(255,255,255),anchor="mm")
        L.putalpha(L.getchannel("A").point(lambda v:int(v*min(1,p)))); im.alpha_composite(L)
    return im.convert("RGB")
if __name__=="__main__":
    import sys
    if sys.argv[1]=="poster":
        frame(2.6).save("/tmp/bt/poster.jpg",quality=90); sys.exit()
    enc=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-i","-","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-r","30","/tmp/bt/silent.mp4"],stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)):
        b=__import__("io").BytesIO(); frame(i/FPS).save(b,"JPEG",quality=92); enc.stdin.write(b.getvalue())
    enc.stdin.close(); enc.wait()
