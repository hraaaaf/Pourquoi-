from pathlib import Path
import base64, hashlib, math, os, subprocess, wave, struct
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b4-hook9s-v2'; FRAMES=OUT/'frames'
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
    rgb=im.convert('RGB'); white=Image.new('RGB',rgb.size,'white')
    diff=ImageChops.difference(rgb,white).convert('L')
    m=diff.point(lambda p:255 if p>18 else 0)
    # close holes so white eyes/teeth remain part of the subject silhouette
    m=m.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MinFilter(19)).filter(ImageFilter.GaussianBlur(2.2))
    out=im.copy(); out.putalpha(m); return out

def contain(im,bw,bh,zoom=1):
    s=min(bw/im.width,bh/im.height)*zoom
    return im.resize((int(im.width*s),int(im.height*s)),Image.Resampling.LANCZOS)

def transform(im,scale=1,angle=0):
    if abs(scale-1)>.001: im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.Resampling.LANCZOS)
    if abs(angle)>.05: im=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    return im

def paste_center(bg,im,x,y): bg.alpha_composite(im,(int(x-im.width/2),int(y-im.height/2)))

def sky(t):
    im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im,'RGBA'); top=(47,133,232); bot=(184,230,255)
    for y in range(H):
        q=y/(H-1); c=tuple(int(lerp(top[i],bot[i],q)) for i in range(3)); d.line((0,y,W,y),fill=(*c,255))
    sx=1040+22*math.sin(t*.8); sy=112
    for r,a in [(130,24),(86,45),(47,180)]:d.ellipse((sx-r,sy-r,sx+r,sy+r),fill=(255,240,135,a))
    for i,(x0,y0,sp) in enumerate([(40,120,.75),(460,60,.45),(845,200,1.15),(180,360,.55)]):
        x=(x0-70*t*sp)%(W+340)-160; s=1+.08*math.sin(t*1.3+i)
        for dx,dy,r in [(0,15,52),(55,0,75),(120,18,55),(65,28,82)]:
            rr=r*s; d.ellipse((x+dx-rr,y0+dy-rr*.58,x+dx+rr,y0+dy+rr*.58),fill=(255,255,255,195))
    return im

def rays(bg,cx,cy,t,alpha=120):
    d=ImageDraw.Draw(bg,'RGBA')
    for i in range(18):
        a=i*math.tau/18+t*.3; r1=170; r2=245+18*math.sin(t*4+i)
        d.line((cx+math.cos(a)*r1,cy+math.sin(a)*r1,cx+math.cos(a)*r2,cy+math.sin(a)*r2),fill=(255,242,120,alpha),width=5)

def text_impact(bg,txt,x,y,size,t,start):
    if t<start:return
    q=clamp((t-start)/.38); overshoot=1.0+0.20*math.sin(math.pi*clamp(q*1.3))*(1-q)
    fs=max(12,int(size*(.5+.5*ease(q))*overshoot)); d=ImageDraw.Draw(bg,'RGBA'); ft=fnt(fs)
    d.text((x+6,y+8),txt,font=ft,anchor='mm',fill=(15,31,75,100),stroke_width=5,stroke_fill=(15,31,75,40))
    d.text((x,y),txt,font=ft,anchor='mm',fill='white',stroke_width=6,stroke_fill=(18,67,158,245))

def arrow(bg,t):
    if not 4.2<t<6.15:return
    q=ease((t-4.2)/.45); d=ImageDraw.Draw(bg,'RGBA'); x0,y0=455,445; x1,y1=610,245
    x=lerp(x0,x1,q); y=lerp(y0,y1,q)
    d.line((x0,y0,x,y),fill=(255,223,65,245),width=18)
    if q>.75:
        a=math.atan2(y1-y0,x1-x0); s=34
        p1=(x-s*math.cos(a-.6),y-s*math.sin(a-.6)); p2=(x-s*math.cos(a+.6),y-s*math.sin(a+.6))
        d.polygon([(x,y),p1,p2],fill=(255,223,65,255))

def cloud_burst(bg,t):
    q=ease((t-6.02)/1.35); d=ImageDraw.Draw(bg,'RGBA')
    # dense cloud wave races across screen
    for row in range(4):
        y=60+row*190
        for j in range(9):
            x=-980+q*(W+1900)+j*155-row*70
            for dx,dy,r in [(0,18,110),(80,0,142),(180,25,118)]:d.ellipse((x+dx-r,y+dy-r*.62,x+dx+r,y+dy+r*.62),fill=(255,255,255,250))
    if q>.72:
        d.rectangle((0,0,W,H),fill=(255,255,255,int(255*ease((q-.72)/.28))))

def prism(t):
    bg=Image.new('RGBA',(W,H),(18,29,75,255)); d=ImageDraw.Draw(bg,'RGBA')
    for i in range(55):
        x=(73*i*29)%W; y=(91*i*13)%H; a=80+int(100*abs(math.sin(t*2+i))); d.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,255,a))
    cx,cy=650,390; pulse=ease((t-7.35)/.28)
    # flash halo
    rr=110+120*pulse; d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=(255,255,255,int(35*pulse)))
    d.line((120,cy,cx-135,cy),fill=(255,247,220,255),width=26)
    d.polygon([(cx-120,cy+150),(cx,cy-155),(cx+130,cy+150)],outline=(235,248,255,255))
    cols=[(246,66,73),(255,144,45),(255,221,62),(64,205,118),(55,151,245),(119,87,219)]
    for j,c in enumerate(cols):
        yy=cy-92+j*36; end=700+430*pulse
        d.line((cx+70,cy-42+j*14,end,yy),fill=(*c,245),width=20)
    text_impact(bg,'LA LUMIÈRE SE SÉPARE !',650,88,58,t,7.35)
    return bg

def audio():
    sr=48000; p=OUT/'temp-bed.wav'; data=bytearray()
    for i in range(sr*DUR):
        tt=i/sr; v=.035*math.sin(2*math.pi*220*tt)+.025*math.sin(2*math.pi*330*tt)
        beat=(tt*3.0)%1
        if beat<.055:v+=.12*(1-beat/.055)*math.sin(2*math.pi*82*tt)
        for hit in [1.65,2.1,2.55,3.0,4.25,7.35]:
            if hit<tt<hit+.12:
                q=(tt-hit)/.12; v+=.16*(1-q)*math.sin(2*math.pi*(95+520*q)*tt)
        if 6.0<tt<7.2:
            q=(tt-6)/1.2; v+=.12*math.sin(2*math.pi*(150+1100*q)*tt)*(math.sin(math.pi*q)**2)
        data.extend(struct.pack('<h',int(max(-1,min(1,v))*32767)))
    with wave.open(str(p),'w') as wf:wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr);wf.writeframes(data)
    return p

def main():
    ref=white_to_alpha(restore_ref())
    raw=[normalize(find('portrait.png')) if list(KF_ROOT.rglob('portrait.png')) else normalize(find('01-look-up.png'))]
    raw += [normalize(find(x)) for x in ['01-look-up.png','02-surprise.png','03-blink.png']]
    poses=[white_to_alpha(x) for x in raw]; poses.append(poses[2])
    for fi in range(N):
        t=fi/FPS
        if t<7.35:
            bg=sky(t)
            if t<4.05:
                # real facial poses with camera punches and subtle rotation
                pos=min(t,3.85)/3.85*(len(poses)-1); idx=min(len(poses)-2,int(pos)); q=ease(pos-idx)
                a=contain(poses[idx],520,560,1.08); b=contain(poses[idx+1],520,560,1.08)
                face=Image.blend(a,b,q)
                punch=1+.06*math.sin(min(1,t/1.1)*math.pi)+.025*math.sin(t*7)
                face=transform(face,punch,2.2*math.sin(t*2.1))
                rays(bg,395,360,t,85); paste_center(bg,face,395+8*math.sin(t*2.3),380+10*math.sin(t*3.5))
                d=ImageDraw.Draw(bg,'RGBA')
                for j in range(10):
                    ang=t*1.7+j*.63; rr=150+22*math.sin(t*3+j); x=395+math.cos(ang)*rr; y=360+math.sin(ang)*rr*.55
                    d.text((x,y),'?',font=fnt(31+int(5*math.sin(j+t))),anchor='mm',fill=(255,255,255,160))
            else:
                body=contain(ref,400,600,1.0); sc=1+.035*math.sin(t*5); body=transform(body,sc,2.2*math.sin(t*3.3)); paste_center(bg,body,290,410+9*math.sin(t*4))
                rays(bg,300,365,t,72); arrow(bg,t)
            if 1.6<t<6.05:
                text_impact(bg,'POURQUOI',865,195,80,t,1.60); text_impact(bg,'LE CIEL',865,295,76,t,2.05)
                text_impact(bg,'EST',865,390,68,t,2.50); text_impact(bg,'BLEU ?',865,500,92,t,2.95)
                d=ImageDraw.Draw(bg,'RGBA'); q=ease((t-3.15)/.55)
                if q>0:d.rounded_rectangle((715,565,715+int(305*q),581),8,fill=(255,222,60,245))
            if t>6.02: cloud_burst(bg,t)
        else: bg=prism(t)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=91,subsampling=1)
    out=OUT/'P4-B4-hook-9s-v2.mp4'; wav=audio()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip()); assert 8.95<=dur<=9.05
    print('P4_B4_V2_PASS',out,out.stat().st_size,dur)
if __name__=='__main__':main()
