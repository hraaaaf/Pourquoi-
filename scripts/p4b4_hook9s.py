from pathlib import Path
import base64, hashlib, math, os, subprocess, wave, struct
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b4-hook9s'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
W,H,FPS,DUR=1280,720,24,9; N=FPS*DUR
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'
KF_ROOT=Path(os.environ.get('P4B4_KEYFRAMES','/tmp/p4b3-keyframes'))

def font(size):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def ease(t): t=max(0,min(1,t)); return t*t*(3-2*t)
def lerp(a,b,t): return a+(b-a)*t

def find_asset(name):
    xs=list(KF_ROOT.rglob(name))
    if not xs: raise FileNotFoundError(f'Missing {name} under {KF_ROOT}')
    return xs[0]

def normalize_image(path,out):
    im=Image.open(path).convert('RGBA'); im.load(); im.save(out,'PNG'); return im

def restore_reference():
    payload=''.join((ROOT/f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    raw=base64.b64decode(payload,validate=True)
    assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
    p=OUT/'reference.jpg'; p.write_bytes(raw)
    return Image.open(p).convert('RGBA')

def contain(im,box,zoom=1.0):
    bw,bh=box; s=min(bw/im.width,bh/im.height)*zoom
    return im.resize((max(1,int(im.width*s)),max(1,int(im.height*s))),Image.Resampling.LANCZOS)

def sky_background(t):
    im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im,'RGBA')
    top=(72,158,235); bottom=(196,232,255)
    for y in range(H):
        q=y/(H-1); c=tuple(int(lerp(top[i],bottom[i],q)) for i in range(3))
        d.line((0,y,W,y),fill=(*c,255))
    sunx=1050+18*math.sin(t*.8); suny=110
    for r,a in [(115,25),(75,45),(40,140)]: d.ellipse((sunx-r,suny-r,sunx+r,suny+r),fill=(255,245,170,a))
    for i,(x0,y0,sp) in enumerate([(110,145,1.0),(520,90,.7),(880,210,1.25),(250,310,.55)]):
        x=(x0-55*t*sp)%(W+300)-150; scale=1+.06*math.sin(t*.9+i)
        for dx,dy,r in [(0,10,55),(48,0,70),(108,15,52),(55,28,76)]:
            rr=r*scale; d.ellipse((x+dx-rr,y0+dy-rr*.6,x+dx+rr,y0+dy+rr*.6),fill=(255,255,255,205))
    return im

def paste_center(canvas,im,center):
    x=int(center[0]-im.width/2); y=int(center[1]-im.height/2); canvas.alpha_composite(im,(x,y))

def text_pop(canvas,txt,xy,size,t,start,duration=.45):
    if t<start:return
    q=ease((t-start)/duration); f=font(int(size*(.65+.4*q))); d=ImageDraw.Draw(canvas,'RGBA'); x,y=xy
    d.text((x+5,y+7),txt,font=f,anchor='mm',fill=(20,40,80,90),stroke_width=5,stroke_fill=(20,40,80,40))
    d.text((x,y),txt,font=f,anchor='mm',fill=(255,255,255,255),stroke_width=5,stroke_fill=(26,78,160,235))

def cloud_wipe(frame,t):
    q=ease((t-6.05)/1.4); d=ImageDraw.Draw(frame,'RGBA')
    # white cloud mass sweeps left -> right and fills the frame just before reveal
    lead=-520+q*(W+1040)
    for row in range(3):
        y=85+row*235
        for j in range(7):
            x=lead-420+j*155-row*65
            for dx,dy,r in [(0,15,105),(78,0,135),(170,25,110)]:
                d.ellipse((x+dx-r,y+dy-r*.7,x+dx+r,y+dy+r*.7),fill=(255,255,255,248))
    if q>.82:
        a=int(255*ease((q-.82)/.18)); d.rectangle((0,0,W,H),fill=(255,255,255,a))

def prism_scene(t):
    bg=Image.new('RGBA',(W,H),(21,30,65,255)); d=ImageDraw.Draw(bg,'RGBA')
    for i in range(45):
        x=(37*i*37)%W; y=(91*i*17)%H; a=int(80+70*math.sin(i+t*2)**2); d.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,255,a))
    cx,cy=660,385
    d.line((120,cy,cx-145,cy),fill=(255,245,210,245),width=24)
    d.polygon([(cx-120,cy+145),(cx,cy-150),(cx+125,cy+145)],outline=(240,250,255,255))
    for j,c in enumerate([(244,75,75),(255,150,50),(255,221,74),(80,210,120),(67,155,240),(118,92,210)]):
        y=cy-85+j*34; d.line((cx+65,cy-40+j*14,1160,y),fill=(*c,235),width=18)
    r=65+15*math.sin(t*7); d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,255,255,35))
    return bg

def make_audio():
    sr=48000; p=OUT/'temp-bed.wav'
    with wave.open(str(p),'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        data=bytearray()
        for i in range(sr*DUR):
            tt=i/sr; v=.05*math.sin(2*math.pi*220*tt)+.035*math.sin(2*math.pi*330*tt)
            beat=(tt*2.5)%1
            if beat<.08:v+=.10*(1-beat/.08)*math.sin(2*math.pi*95*tt)
            if 6<tt<6.8:
                q=(tt-6)/.8; v+=.12*math.sin(2*math.pi*(180+900*q)*tt)*(math.sin(math.pi*q)**2)
            if 7.45<tt<7.65:
                q=(tt-7.45)/.2; v+=.22*(1-q)*math.sin(2*math.pi*70*tt)
            data.extend(struct.pack('<h',int(max(-1,min(1,v))*32767)))
        wf.writeframes(data)
    return p

def main():
    ref=restore_reference(); kfs=[]
    for i,n in enumerate(['01-look-up.png','02-surprise.png','03-blink.png']):
        kfs.append(normalize_image(find_asset(n),OUT/f'kf-{i+1}.png'))
    portrait=normalize_image(find_asset('portrait.png'),OUT/'kf-neutral.png') if list(KF_ROOT.rglob('portrait.png')) else kfs[0]
    seq=[portrait,kfs[0],kfs[1],kfs[2],kfs[1]]
    for fi in range(N):
        t=fi/FPS
        if t<7.45:
            frame=sky_background(t)
            if t<4:
                pos=min(t,3.8)/3.8*(len(seq)-1); idx=min(len(seq)-2,int(pos)); q=ease(pos-idx)
                a=contain(seq[idx],(520,520),1.02); b=contain(seq[idx+1],(520,520),1.02)
                face=Image.blend(a,b,q); paste_center(frame,face,(430,385+8*math.sin(t*3.2)))
                d=ImageDraw.Draw(frame,'RGBA')
                for j in range(8):
                    ang=t*1.2+j*.8; r=130+20*math.sin(t*2+j); x=430+math.cos(ang)*r; y=350+math.sin(ang)*r*.55
                    d.text((x,y),'?',font=font(34),anchor='mm',fill=(255,255,255,145))
            else:
                paste_center(frame,contain(ref,(390,570),.95),(305,390+5*math.sin(t*3)))
            if 1.65<t<6.25:
                text_pop(frame,'POURQUOI',(860,220),76,t,1.65); text_pop(frame,'LE CIEL',(860,315),72,t,2.15)
                text_pop(frame,'EST',(860,400),64,t,2.65); text_pop(frame,'BLEU ?',(860,500),86,t,3.05)
                d=ImageDraw.Draw(frame,'RGBA'); q=ease((t-3.2)/.7)
                if q>0:d.rounded_rectangle((730,558,730+int(265*q),572),7,fill=(255,221,79,235))
            if t>6.05: cloud_wipe(frame,t)
        else:
            frame=prism_scene(t); text_pop(frame,'LA LUMIÈRE SE SÉPARE !',(640,92),55,t,7.45,.35)
        frame.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=90,subsampling=1)
    audio=make_audio(); out=OUT/'P4-B4-hook-9s-v1.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(audio),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip())
    assert 8.95<=dur<=9.05,dur
    print('P4_B4_HOOK_PASS',out,out.stat().st_size,'duration',dur)
if __name__=='__main__': main()
