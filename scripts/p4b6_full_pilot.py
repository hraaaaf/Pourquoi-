from pathlib import Path
import math, subprocess, wave, struct
from PIL import Image, ImageDraw, ImageFont
import p4b4_hook9s_v3 as b
import p4b4_hook9s_v5 as v5
import p4b5_opening_v2 as b5

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b6-full-pilot-v1'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
W,H,FPS,DUR=1280,720,24,75; N=FPS*DUR
b.OUT=OUT; b.FRAMES=FRAMES; v5.OUT=OUT; v5.FRAMES=FRAMES; b5.OUT=OUT; b5.FRAMES=FRAMES


def fnt(n):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
        if Path(p).exists(): return ImageFont.truetype(p,n)
    return ImageFont.load_default()
def ease(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,c,t): return a+(c-a)*t

def gradient(c1,c2):
    im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        q=y/(H-1); c=tuple(int(lerp(c1[i],c2[i],q)) for i in range(3)); d.line((0,y,W,y),fill=(*c,255))
    return im
SKY=gradient((52,139,235),(199,233,255))
DARK=gradient((12,24,67),(36,54,101))
SUNSET=gradient((77,70,153),(255,151,85))


def txt(bg,text,x,y,size,fill='white',stroke=(18,55,120),anchor='mm'):
    d=ImageDraw.Draw(bg,'RGBA'); ft=fnt(size)
    d.text((x+4,y+6),text,font=ft,anchor=anchor,fill=(10,20,50,95),stroke_width=5,stroke_fill=(10,20,50,50))
    d.text((x,y),text,font=ft,anchor=anchor,fill=fill,stroke_width=5,stroke_fill=stroke)

def pop(bg,text,x,y,size,t,start,dur=.35):
    if t<start:return
    q=ease((t-start)/dur); fs=max(12,int(size*(.62+.38*q)))
    txt(bg,text,x,y,fs)
def star(d,x,y,r,c):
    pts=[]
    for i in range(8):
        a=-math.pi/2+i*math.pi/4; rr=r if i%2==0 else r*.34; pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
    d.polygon(pts,fill=c)
def flash(bg,q,strength=.35):
    return Image.blend(bg,Image.new('RGBA',(W,H),'white'),max(0,min(strength,q)))
def beam(d,p1,p2,width=22,color=(255,248,220,240)):
    d.line((*p1,*p2),fill=color,width=width)

def hook_frame(poses,pointing,t):
    if t<4.03:
        return b5.opening_frame(poses,t)
    if t<7.35:
        bg=v5.pointing_frame(pointing,t)
        if t<6.02:
            b.text_impact(bg,'POURQUOI',875,190,76,t,1.60); b.text_impact(bg,'LE CIEL',875,286,72,t,2.05)
            b.text_impact(bg,'EST',875,376,64,t,2.50); b.text_impact(bg,'BLEU ?',875,480,88,t,2.95)
            d=ImageDraw.Draw(bg,'RGBA'); uq=b.ease((t-3.15)/.55)
            if uq>0:d.rounded_rectangle((725,545,725+int(300*uq),561),8,fill=(255,222,60,255))
        if 6.02<t<7.35:bg=b.cloud_wipe(bg,t)
        if 4.03<=t<4.16:
            q=1-b.ease((t-4.03)/.13); bg=Image.blend(bg,Image.new('RGBA',(W,H),(255,244,194,255)),.24*q)
        return bg
    return b.prism(t)

def scene_light(t):
    bg=DARK.copy(); d=ImageDraw.Draw(bg,'RGBA')
    # sun / source
    sx,sy=130,340
    for r,a in [(92,45),(65,85),(38,255)]: d.ellipse((sx-r,sy-r,sx+r,sy+r),fill=(255,225,96,a))
    beam(d,(220,340),(530,340),30)
    # prism
    d.polygon([(530,485),(650,205),(770,485)],fill=(35,55,105,255),outline=(235,247,255,255))
    cols=[(245,70,72),(255,145,45),(255,220,62),(64,204,116),(57,150,244),(121,86,218)]
    spread=ease((t-1.6)/1.0)
    for j,c in enumerate(cols):
        yy=230+j*50; endx=770+395*spread; d.line((690,315+j*12,endx,yy),fill=(*c,240),width=22)
    pop(bg,'LA LUMIÈRE DU SOLEIL',640,80,54,t,.2)
    pop(bg,'PARAÎT BLANCHE',640,145,60,t,.65)
    if t>4.2: pop(bg,'MAIS ELLE CONTIENT',640,570,44,t,4.2)
    if t>4.8: pop(bg,'TOUTES CES COULEURS',640,625,48,t,4.8)
    for i in range(10):
        a=i*math.tau/10+t*.7; star(d,640+math.cos(a)*300,350+math.sin(a)*220,7,(255,255,255,120))
    return bg

def scene_atmos(t):
    bg=SKY.copy(); d=ImageDraw.Draw(bg,'RGBA')
    # horizon / atmosphere layers
    d.rectangle((0,520,W,H),fill=(72,173,104,255))
    d.rectangle((0,500,W,530),fill=(126,205,138,150))
    # white sunlight entering from upper left
    beam(d,(30,120),(470,310),22,(255,250,226,245))
    # molecules
    for i in range(34):
        x=(70+i*137+int(t*35*(1 if i%2 else -1)))%(W+120)-60
        y=155+(i*73)%330 + 12*math.sin(t*1.7+i)
        r=11+(i%3)*3
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,145),outline=(150,210,245,220),width=2)
    # blue scattering from a focal molecule
    cx,cy=545,325
    d.ellipse((cx-17,cy-17,cx+17,cy+17),fill=(255,255,255,245),outline=(100,180,245,255),width=3)
    q=ease((t-2.0)/1.0)
    for i in range(18):
        a=i*math.tau/18+t*.08; rr=230*q
        d.line((cx,cy,cx+math.cos(a)*rr,cy+math.sin(a)*rr),fill=(65,151,255,205),width=8)
    pop(bg,"DANS L'ATMOSPHÈRE...",930,95,52,t,.25)
    if t>3.4: pop(bg,'LES MOLÉCULES',945,165,48,t,3.4)
    if t>4.0: pop(bg,'DIFFUSENT LA LUMIÈRE',945,225,45,t,4.0)
    if t>8.0:
        txt(bg,'LE BLEU PART',930,420,55)
        txt(bg,'DANS TOUTES LES DIRECTIONS',930,485,38)
    return bg

def wave_points(x0,y0,length,amp,waves,phase):
    pts=[]
    for x in range(int(length)+1):
        q=x/length; pts.append((x0+x,y0+math.sin(q*math.tau*waves+phase)*amp))
    return pts

def scene_waves(t):
    bg=DARK.copy(); d=ImageDraw.Draw(bg,'RGBA')
    pop(bg,'TOUTES LES COULEURS',640,90,54,t,.1)
    pop(bg,"N'ONT PAS LA MÊME ONDE",640,155,48,t,.55)
    # red long wave
    pts=wave_points(120,300,860,34,3,t*2); d.line(pts,fill=(248,76,76,255),width=12)
    txt(bg,'ROUGE : ONDE PLUS LONGUE',1000,300,34,fill=(255,145,145))
    # blue short wave
    pts=wave_points(120,470,860,26,8,t*4); d.line(pts,fill=(75,157,255,255),width=12)
    txt(bg,'BLEU : ONDE PLUS COURTE',1000,470,34,fill=(150,205,255))
    if t>5.2:
        d.rounded_rectangle((280,580,1000,650),20,fill=(24,72,145,220))
        txt(bg,'LES ONDES COURTES SONT DAVANTAGE DIFFUSÉES',640,615,31)
    return bg

def scene_violet(t):
    bg=gradient((83,55,180),(44,130,225)); d=ImageDraw.Draw(bg,'RGBA')
    # large question orb
    cx,cy=360,360; pulse=1+.08*math.sin(t*3)
    for rr,a in [(155,35),(120,70),(82,220)]:
        r=rr*pulse; d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(155,92,245,a))
    txt(bg,'?',cx,cy,150,fill=(255,255,255),stroke=(95,45,180))
    pop(bg,'ET LE VIOLET ?',860,170,68,t,.2)
    if t>2.0: pop(bg,'LUI AUSSI EST TRÈS DIFFUSÉ',860,275,40,t,2.0)
    if t>4.6:
        d.rounded_rectangle((635,355,1145,530),28,fill=(24,61,130,220))
        txt(bg,'MAIS LE CIEL',890,405,43)
        txt(bg,'NOUS PARAÎT SURTOUT BLEU',890,470,35)
    return bg

def scene_sunset(t):
    bg=SUNSET.copy(); d=ImageDraw.Draw(bg,'RGBA')
    # ground and low sun
    d.rectangle((0,565,W,H),fill=(64,72,80,255))
    sx,sy=1050,520
    for r,a in [(95,35),(65,75),(38,255)]:d.ellipse((sx-r,sy-r,sx+r,sy+r),fill=(255,191,72,a))
    # curved-ish long atmospheric path
    q=ease((t-1.4)/1.2)
    d.line((1060,500,650,390,170,330),fill=(255,215,120,230),width=28)
    # blue scattered away
    for i in range(10):
        x=640-i*45; y=390-i*5
        rr=100*q*(.45+.05*i)
        a=-1.2-i*.18
        d.line((x,y,x+math.cos(a)*rr,y+math.sin(a)*rr),fill=(65,150,255,160),width=7)
    # red/orange reach viewer
    d.line((610,390,160,330),fill=(255,120,58,245),width=18)
    pop(bg,'AU COUCHER DU SOLEIL...',520,95,52,t,.2)
    if t>2.2: pop(bg,'LA LUMIÈRE TRAVERSE',470,165,42,t,2.2)
    if t>2.7: pop(bg,"BEAUCOUP PLUS D'AIR",470,220,42,t,2.7)
    if t>6.1:
        d.rounded_rectangle((120,430,740,550),24,fill=(65,50,100,205))
        txt(bg,'LE BLEU EST DIFFUSÉ AVANT',430,470,32)
        txt(bg,"D'ARRIVER À TES YEUX",430,515,35)
    if t>8.8:
        txt(bg,'→ ROUGE + ORANGE',965,620,42,fill=(255,235,180),stroke=(120,55,35))
    return bg

def scene_challenge(t,pointing):
    base=pointing.resize((W,H),Image.Resampling.LANCZOS)
    z=1.02+.025*ease(t/6); nw,nh=int(W*z),int(H*z); im=base.resize((nw,nh),Image.Resampling.LANCZOS)
    left=(nw-W)//2; top=(nh-H)//2; bg=im.crop((left,top,left+W,top+H)).convert('RGBA')
    d=ImageDraw.Draw(bg,'RGBA')
    d.rounded_rectangle((620,70,1190,620),34,fill=(13,42,103,205))
    pop(bg,'DÉFI !',905,145,72,t,.15)
    if t>.8: pop(bg,'DEMAIN, OBSERVE',905,250,42,t,.8)
    if t>1.25: pop(bg,'LE COUCHER DU SOLEIL',905,305,40,t,1.25)
    if t>2.6: pop(bg,'COMBIEN DE COULEURS',905,420,38,t,2.6)
    if t>3.1: pop(bg,'VOIS-TU ?',905,485,58,t,3.1)
    for i in range(8):
        a=t*1.8+i*math.tau/8; r=88+8*math.sin(t*3+i); star(d,905+math.cos(a)*r,555+math.sin(a)*r*.35,8,(255,221,71,220))
    return bg

def transition(bg,t,starts):
    for s in starts:
        if s<=t<s+.16:
            q=1-ease((t-s)/.16); return flash(bg,.22*q,.22)
    return bg

def make_audio():
    sr=48000; p=OUT/'motion-bed.wav'; data=bytearray(); hits=[9,20,38,49,58,69]
    for i in range(sr*DUR):
        tt=i/sr
        v=.022*math.sin(2*math.pi*220*tt)+.018*math.sin(2*math.pi*330*tt)+.012*math.sin(2*math.pi*440*tt)
        beat=(tt*2.6)%1
        if beat<.045:v+=.055*(1-beat/.045)*math.sin(2*math.pi*95*tt)
        for h in hits:
            if h<tt<h+.28:
                q=(tt-h)/.28; v+=.08*(1-q)*math.sin(2*math.pi*(140+850*q)*tt)
        data.extend(struct.pack('<h',int(max(-1,min(1,v))*32767)))
    with wave.open(str(p),'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(data)
    return p

def main():
    pointing=v5.load_pointing()
    neutral=b.normalize(b.find('portrait.png')) if list(b.KF_ROOT.rglob('portrait.png')) else b.normalize(b.find('01-look-up.png'))
    raw=[neutral,b.normalize(b.find('01-look-up.png')),b.normalize(b.find('02-surprise.png')),b.normalize(b.find('03-blink.png'))]
    poses=[b5.clean_bg(x) for x in raw]
    cuts=[9,20,38,49,58,69]
    for fi in range(N):
        t=fi/FPS
        if t<9: bg=hook_frame(poses,pointing,t)
        elif t<20: bg=scene_light(t-9)
        elif t<38: bg=scene_atmos(t-20)
        elif t<49: bg=scene_waves(t-38)
        elif t<58: bg=scene_violet(t-49)
        elif t<69: bg=scene_sunset(t-58)
        else: bg=scene_challenge(t-69,pointing)
        bg=transition(bg,t,cuts)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=90,subsampling=1)
    wav=make_audio(); out=OUT/'P4-B6-full-pilot-75s-v1.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip())
    assert 74.9<=dur<=75.1,dur
    print('P4_B6_FULL_PILOT_PASS',out,out.stat().st_size,dur)
if __name__=='__main__': main()
