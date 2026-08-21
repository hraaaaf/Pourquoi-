from pathlib import Path
import hashlib, math, shutil, subprocess
from PIL import Image, ImageDraw
from gradio_client import Client, handle_file

OUT=Path('artifacts/p4b3'); OUT.mkdir(parents=True,exist_ok=True)
REF=Path('assets/p4b3/character.jpg'); DRIVE=OUT/'driving.mp4'; RESULT=OUT/'zerogpu-smoke.mp4'
W,H,FPS,SECONDS=320,480,24,2.0
EXPECTED_SHA='58e8819c38e9da1941ab449179a73b6e3b8696a88e8f1e5889c2d4577cb18da2'

def validate_ref():
    raw=REF.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    with Image.open(REF) as im:
        im.load(); assert im.size==(W,H), im.size
    assert sha==EXPECTED_SHA, f'character SHA mismatch: {sha}'
    print(f'CHARACTER_OK bytes={len(raw)} sha256={sha} size={W}x{H}')

def smooth(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,b,t): return a+(b-a)*t
def end(p,L,a):
    r=math.radians(a); return p[0]+L*math.cos(r),p[1]+L*math.sin(r)
def pose(t):
    keys=[(0,-45,295,20,10,0),(.35,155,290,25,15,.2),(.7,160,286,35,20,.5),(1.05,163,282,-35,-10,.75),(1.45,165,278,-72,-6,1),(1.7,165,268,-82,-3,1),(2,165,278,-72,-6,1)]
    for a,b in zip(keys,keys[1:]):
        if a[0]<=t<=b[0]:
            u=smooth((t-a[0])/(b[0]-a[0])); return tuple(lerp(a[i],b[i],u) for i in range(1,6))
    return keys[-1][1:]
def frame(t):
    cx,cy,ra,la,e=pose(t); im=Image.new('RGB',(W,H),(240,240,240)); d=ImageDraw.Draw(im)
    d.ellipse((cx-55,430,cx+55,448),fill=(212,212,216))
    d.rounded_rectangle((cx-40,cy-55,cx+40,cy+70),20,fill=(220,45,38))
    d.ellipse((cx-37,cy-142,cx+37,cy-68),fill=(242,185,140)); d.pieslice((cx-39,cy-150,cx+39,cy-80),180,360,fill=(70,43,31))
    ey=cy-108-5*e
    for ex in (-14,14): d.ellipse((cx+ex-5,ey-4,cx+ex+5,ey+6),fill='white'); d.ellipse((cx+ex,ey-1,cx+ex+5,ey+4),fill=(25,25,25))
    d.ellipse((cx-11,cy-88,cx+11,cy-69),fill=(95,35,35)) if e>.45 else d.arc((cx-11,cy-90,cx+11,cy-70),10,170,fill=(100,45,40),width=3)
    rs=(cx+38,cy-35); re=end(rs,68,ra); rh=end(re,62,ra-8); ls=(cx-38,cy-35); le=end(ls,62,180-la); lh=end(le,58,188-la)
    for a,b in ((rs,re),(re,rh),(ls,le),(le,lh)): d.line((*a,*b),fill=(225,65,52),width=17)
    for p in (re,rh,le,lh): d.ellipse((p[0]-8,p[1]-8,p[0]+8,p[1]+8),fill=(242,185,140))
    if t>1: f=end(rh,27,ra-25); d.line((*rh,*f),fill=(242,185,140),width=7)
    bounce=10*max(0,1-abs(t-1.7)/.24); lk=(cx-18,cy+145-bounce); rk=(cx+22,cy+145-.7*bounce); lf=(cx-28,425); rf=(cx+34,425)
    for a,b in (((cx-20,cy+62),lk),(lk,lf),((cx+20,cy+62),rk),(rk,rf)): d.line((*a,*b),fill=(48,68,112),width=21)
    return im

def make_driver():
    fd=OUT/'driver_frames'; fd.mkdir(exist_ok=True)
    for i in range(int(FPS*SECONDS)): frame(i/FPS).save(fd/f'{i:04d}.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(fd/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','21','-r',str(FPS),str(DRIVE)],check=True)

def main():
    validate_ref(); make_driver(); client=Client('hugging-apps/wan2-2-animate-2-14b')
    out=client.predict(handle_file(str(REF)),handle_file(str(DRIVE)),'same cheerful young cartoon boy, red hoodie, blue jeans, red sneakers; preserve face, hair and clothes; enters frame, looks upward, reacts with curiosity, raises one arm and points upward; smooth natural full-body animation; clean neutral background',2.0,480,320,4,1.0,5.0,'distorted face, identity drift, extra limbs, extra fingers, duplicated body parts, warped hands, text, subtitles, watermark, static frame, flicker, blur',23,api_name='/animate')
    src=Path(out if isinstance(out,str) else out[0]); shutil.copy2(src,RESULT); print(f'WAN_REAL_CHARACTER_PASS={RESULT}')
if __name__=='__main__': main()
