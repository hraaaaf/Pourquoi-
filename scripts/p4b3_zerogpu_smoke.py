from pathlib import Path
import base64, hashlib, math, shutil, subprocess
from PIL import Image, ImageDraw
from gradio_client import Client, handle_file

OUT=Path('artifacts/p4b3'); OUT.mkdir(parents=True,exist_ok=True)
REF=OUT/'reference.jpg'; DRIVE=OUT/'driving.mp4'; RESULT=OUT/'zerogpu-smoke.mp4'
W,H,FPS,SECONDS=320,480,24,2.0
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'

def restore_ref():
    payload=''.join(Path(f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    REF.write_bytes(base64.b64decode(payload,validate=True))
    raw=REF.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    with Image.open(REF) as im: im.load(); size=im.size
    assert size==(W,H),size; assert sha==EXPECTED_SHA,(sha,len(raw))
    print(f'CHARACTER_OK bytes={len(raw)} sha256={sha} size={size}')

def sm(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

def lp(a,b,t): return a+(b-a)*t

def ep(p,L,a):
    r=math.radians(a); return p[0]+L*math.cos(r),p[1]+L*math.sin(r)

def pose(t):
    # Conservative pose transfer: keep subject centered and preserve silhouette.
    # Only a mild head/body shift plus one-arm raise over 2 seconds.
    k=[
        (0.00,160,286,18,10,0.00),
        (0.45,160,284,24,12,0.12),
        (0.90,161,282,34,14,0.25),
        (1.30,161,280,48,16,0.38),
        (1.65,160,279,58,17,0.45),
        (2.00,160,280,54,16,0.40),
    ]
    for a,b in zip(k,k[1:]):
        if a[0] <= t <= b[0]:
            u=sm((t-a[0])/(b[0]-a[0]))
            return tuple(lp(a[i],b[i],u) for i in range(1,6))
    return k[-1][1:]

def frame(t):
    cx,cy,ra,la,e=pose(t)
    im=Image.new('RGB',(W,H),(247,245,240)); d=ImageDraw.Draw(im)
    d.ellipse((cx-52,430,cx+52,446),fill=(220,218,215))
    d.rounded_rectangle((cx-39,cy-54,cx+39,cy+70),20,fill=(215,42,35))
    d.ellipse((cx-36,cy-141,cx+36,cy-69),fill=(242,185,140))
    d.pieslice((cx-39,cy-150,cx+39,cy-80),180,360,fill=(70,43,31))
    ey=cy-108-3*e
    for ex in (-14,14):
        d.ellipse((cx+ex-5,ey-4,cx+ex+5,ey+6),fill='white')
        d.ellipse((cx+ex,ey-1,cx+ex+5,ey+4),fill=(25,25,25))
    d.arc((cx-11,cy-90,cx+11,cy-70),10,170,fill=(100,45,40),width=3)
    rs=(cx+38,cy-35); re=ep(rs,66,ra); rh=ep(re,58,ra-6)
    ls=(cx-38,cy-35); le=ep(ls,60,180-la); lh=ep(le,54,188-la)
    for a,b in ((rs,re),(re,rh),(ls,le),(le,lh)):
        d.line((*a,*b),fill=(225,65,52),width=16)
    for p in (re,rh,le,lh):
        d.ellipse((p[0]-8,p[1]-8,p[0]+8,p[1]+8),fill=(242,185,140))
    # Keep legs almost static to preserve overall identity and proportions.
    lk=(cx-18,cy+145); rk=(cx+22,cy+145); lf=(cx-27,425); rf=(cx+33,425)
    for a,b in (((cx-20,cy+62),lk),(lk,lf),((cx+20,cy+62),rk),(rk,rf)):
        d.line((*a,*b),fill=(48,68,112),width=21)
    return im

def make_driver():
    fd=OUT/'driver_frames'; fd.mkdir(exist_ok=True)
    for i in range(int(FPS*SECONDS)):
        frame(i/FPS).save(fd/f'{i:04d}.png')
    subprocess.run([
        'ffmpeg','-y','-loglevel','error','-framerate',str(FPS),
        '-i',str(fd/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p',
        '-crf','20','-r',str(FPS),str(DRIVE)
    ],check=True)

def main():
    restore_ref(); make_driver()
    c=Client('hugging-apps/wan2-2-animate-2-14b')
    o=c.predict(
        handle_file(str(REF)),
        handle_file(str(DRIVE)),
        'same cheerful young cartoon boy, red hoodie, blue jeans, red sneakers; strictly preserve face, hair, body proportions and clothes; subtle natural motion; gently raises one arm and looks slightly upward; stable full-body animation; clean neutral background',
        2.0,480,320,6,1.0,5.0,
        'distorted face, identity drift, extra limbs, extra fingers, duplicated body parts, warped hands, deformed body, flicker, blur, noise, text, subtitles, watermark',
        23,
        api_name='/animate'
    )
    src=Path(o if isinstance(o,str) else o[0])
    shutil.copy2(src,RESULT)
    print(f'WAN_REAL_CHARACTER_PASS={RESULT}')

if __name__=='__main__': main()
