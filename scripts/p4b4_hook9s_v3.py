from pathlib import Path
import base64, hashlib, math, os, subprocess, wave, struct
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b4-hook9s-v3'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
W,H,FPS,DUR=1280,720,24,9; N=FPS*DUR
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'
KF_ROOT=Path(os.environ.get('P4B4_KEYFRAMES','/tmp/p4b3-keyframes'))

def fnt(n):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
        if Path(p).exists(): return ImageFont.truetype(p,n)
    return ImageFont.load_default()
def clamp(x): return max(0,min(1,x))
def ease(x): x=clamp(x); return x*x*(3-2*x)
def lerp(a,b,t): return a+(b-a)*t

def find(name):
    xs=list(KF_ROOT.rglob(name))
    if not xs: raise FileNotFoundError(name)
    return xs[0]
def normalize(path):
    im=Image.open(path).convert('RGBA'); im.load(); return im

def restore_ref():
    payload=''.join((ROOT/f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    raw=base64.b64decode(payload,validate=True); assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
    p=OUT/'reference.jpg'; p.write_bytes(raw); return Image.open(p).convert('RGBA')

def white_to_alpha(im):
    rgb=im.convert('RGB'); diff=ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).convert('L')
    m=diff.point(lambda p:255 if p>18 else 0).filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MinFilter(19)).filter(ImageFilter.GaussianBlur(2.0))
    out=im.copy(); out.putalpha(m); return out

def contain(im,bw,bh,zoom=1):
    s=min(bw/im.width,bh/im.height)*zoom; return im.resize((int(im.width*s),int(im.height*s)),Image.Resampling.LANCZOS)
def transform(im,scale=1,angle=0):
    if abs(scale-1)>.001: im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.Resampling.LANCZOS)
    if abs(angle)>.05: im=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    return im
def paste_center(bg,im,x,y): bg.alpha_composite(im,(int(x-im.width/2),int(y-im.height/2)))

def sky(t):
    im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im); top=(47,133,232); bot=(184,230,255)
    for y in range(H):
        q=y/(H-1); c=tuple(int(lerp(top[i],bot[i],q)) for i in range(3)); d.line((0,y,W,y),fill=(*c,255))
    sx=1040+22*math.sin(t*.8); sy=112
    for r,c in [(130,(74,164,220,255)),(86,(126,196,235,255)),(47,(255,238,128,255))]: d.ellipse((sx-r,sy-r,sx+r,sy+r),fill=c)
    for i,(x0,y0,sp) in enumerate([(40,120,.75),(460,60,.45),(845,200,1.15),(180,360,.55)]):
        x=(x0-70*t*sp)%(W+340)-160; s=1+.08*math.sin(t*1.3+i)
        for dx,dy,r in [(0,15,52),(55,0,75),(120,18,55),(65,28,82)]:
            rr=r*s; d.ellipse((x+dx-rr,y0+dy-rr*.58,x+dx+rr,y0+dy+rr*.58),fill=(255,255,255,205))
    return im

def rays(bg,cx,cy,t):
    d=ImageDraw.Draw(bg)
    for i in range(18):
        a=i*math.tau/18+t*.3; r1=170; r2=240+18*math.sin(t*4+i)
        d.line((cx+math.cos(a)*r1,cy+math.sin(a)*r1,cx+math.cos(a)*r2,cy+math.sin(a)*r2),fill=(255,232,92,175),width=5)

def text_impact(bg,txt,x,y,size,t,start):
    if t<start:return
    q=clamp((t-start)/.38); fs=max(12,int(size*(.5+.5*ease(q))*(1+.18*math.sin(math.pi*q)*(1-q))))
    d=ImageDraw.Draw(bg); ft=fnt(fs)
    d.text((x+6,y+8),txt,font=ft,anchor='mm',fill=(15,31,75,110),stroke_width=5,stroke_fill=(15,31,75,60))
    d.text((x,y),txt,font=ft,anchor='mm',fill='white',stroke_width=6,stroke_fill=(18,67,158,255))

def arrow(bg,t):
    if not 4.2<t<6.0:return
    q=ease((t-4.2)/.45); d=ImageDraw.Draw(bg); x0,y0=455,445; x1,y1=610,245; x=lerp(x0,x1,q); y=lerp(y0,y1,q)
    d.line((x0,y0,x,y),fill=(255,223,65,255),width=18)
    if q>.75:
        a=math.atan2(y1-y0,x1-x0); s=34
        d.polygon([(x,y),(x-s*math.cos(a-.6),y-s*math.sin(a-.6)),(x-s*math.cos(a+.6),y-s*math.sin(a+.6))],fill=(255,223,65,255))

def star(d,x,y,r,c):
    pts=[]
    for i in range(8):
        a=-math.pi/2+i*math.pi/4; rr=r if i%2==0 else r*.35; pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
    d.polygon(pts,fill=c)

def cloud_wipe(bg,t):
    q=ease((t-6.02)/1.33); d=ImageDraw.Draw(bg)
    cx=-300+q*(W+600); cy=360; scale=.75+1.15*q
    blobs=[(-260,-20,145),(-170,-115,175),(-60,-45,225),(85,-125,180),(190,-25,220),(295,35,155),(-170,100,185),(-10,115,235),(175,100,190)]
    for ox,oy,r in blobs:
        rr=r*scale; x=cx+ox*scale; y=cy+oy*scale; d.ellipse((x-rr,y-rr*.72,x+rr,y+rr*.72),fill=(255,255,255,255))
    # small warm sparkles around the cloud, like the reference energy
    if .18<q<.9:
        for i in range(7):
            a=i*math.tau/7+t*4; rr=330*scale; star(d,cx+math.cos(a)*rr,cy+math.sin(a)*rr*.58,10+4*math.sin(i+t*3),(255,160,55,255))
    if q>.82:
        a=ease((q-.82)/.18); white=Image.new('RGBA',(W,H),'white'); return Image.blend(bg,white,a)
    return bg

def prism(t):
    bg=Image.new('RGBA',(W,H),(18,29,75,255)); d=ImageDraw.Draw(bg); cx,cy=650,390; p=ease((t-7.35)/.32)
    for i in range(60):
        x=(73*i*29)%W; y=(91*i*13)%H; v=100+int(95*abs(math.sin(t*2+i))); d.ellipse((x-2,y-2,x+2,y+2),fill=(v,v,v,255))
    # concentric glow rings, no opaque white disc
    for rr,c in [(150,(45,67,120,255)),(110,(60,87,145,255)),(72,(78,110,170,255))]: d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=c,width=10)
    d.line((120,cy,cx-135,cy),fill=(255,247,220,255),width=26)
    d.polygon([(cx-120,cy+150),(cx,cy-155),(cx+130,cy+150)],fill=(36,56,104,255),outline=(228,245,255,255))
    cols=[(246,66,73),(255,144,45),(255,221,62),(64,205,118),(55,151,245),(119,87,219)]
    for j,c in enumerate(cols):
        yy=cy-92+j*36; end=700+430*p; d.line((cx+70,cy-42+j*14,end,yy),fill=(*c,255),width=20)
    # reveal flash fades immediately
    if t<7.58: bg=Image.blend(bg,Image.new('RGBA',(W,H),'white'),1-ease((t-7.35)/.23))
    text_impact(bg,'LA LUMIÈRE SE SÉPARE !',650,88,58,t,7.42)
    return bg

def audio():
    sr=48000; p=OUT/'temp-bed.wav'; data=bytearray()
    for i in range(sr*DUR):
        tt=i/sr; v=.035*math.sin(2*math.pi*220*tt)+.025*math.sin(2*math.pi*330*tt); beat=(tt*3)%1
        if beat<.055:v+=.12*(1-beat/.055)*math.sin(2*math.pi*82*tt)
        for hit in [1.6,2.05,2.5,2.95,4.2,7.38]:
            if hit<tt<hit+.12:
                q=(tt-hit)/.12; v+=.16*(1-q)*math.sin(2*math.pi*(95+520*q)*tt)
        if 6<tt<7.2:
            q=(tt-6)/1.2; v+=.12*math.sin(2*math.pi*(150+1100*q)*tt)*(math.sin(math.pi*q)**2)
        data.extend(struct.pack('<h',int(max(-1,min(1,v))*32767)))
    with wave.open(str(p),'w') as wf:wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr);wf.writeframes(data)
    return p

def main():
    ref=white_to_alpha(restore_ref()); raw=[normalize(find('portrait.png')) if list(KF_ROOT.rglob('portrait.png')) else normalize(find('01-look-up.png'))]
    raw += [normalize(find(x)) for x in ['01-look-up.png','02-surprise.png','03-blink.png']]; poses=[white_to_alpha(x) for x in raw]; poses.append(poses[2])
    for fi in range(N):
        t=fi/FPS
        if t<7.35:
            bg=sky(t)
            if t<4.05:
                pos=min(t,3.85)/3.85*(len(poses)-1); idx=min(len(poses)-2,int(pos)); q=ease(pos-idx)
                a=contain(poses[idx],520,560,1.08); b=contain(poses[idx+1],520,560,1.08); face=Image.blend(a,b,q)
                face=transform(face,1+.06*math.sin(min(1,t/1.1)*math.pi)+.025*math.sin(t*7),2.2*math.sin(t*2.1)); rays(bg,395,360,t); paste_center(bg,face,395+8*math.sin(t*2.3),380+10*math.sin(t*3.5))
                d=ImageDraw.Draw(bg)
                for j in range(10):
                    ang=t*1.7+j*.63; rr=150+22*math.sin(t*3+j); d.text((395+math.cos(ang)*rr,360+math.sin(ang)*rr*.55),'?',font=fnt(31+int(5*math.sin(j+t))),anchor='mm',fill=(255,255,255,180))
            else:
                body=transform(contain(ref,400,600,1.0),1+.035*math.sin(t*5),2.2*math.sin(t*3.3)); paste_center(bg,body,290,410+9*math.sin(t*4)); rays(bg,300,365,t); arrow(bg,t)
            if 1.6<t<6.02:
                text_impact(bg,'POURQUOI',865,195,80,t,1.60);text_impact(bg,'LE CIEL',865,295,76,t,2.05);text_impact(bg,'EST',865,390,68,t,2.50);text_impact(bg,'BLEU ?',865,500,92,t,2.95)
                d=ImageDraw.Draw(bg); q=ease((t-3.15)/.55)
                if q>0:d.rounded_rectangle((715,565,715+int(305*q),581),8,fill=(255,222,60,255))
            if t>6.02: bg=cloud_wipe(bg,t)
        else: bg=prism(t)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=91,subsampling=1)
    out=OUT/'P4-B4-hook-9s-v3.mp4'; wav=audio(); subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip()); assert 8.95<=dur<=9.05
    print('P4_B4_V3_PASS',out,out.stat().st_size,dur)
if __name__=='__main__':main()
