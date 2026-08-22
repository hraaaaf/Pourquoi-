from pathlib import Path
import math, os, subprocess
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import p4b4_hook9s_v3 as b

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b4-hook9s-v4'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
b.OUT=OUT; b.FRAMES=FRAMES


def auto_key(im):
    """Remove the flat source background while preserving the validated pointing pose."""
    rgb=im.convert('RGB')
    pts=[rgb.getpixel((4,4)),rgb.getpixel((rgb.width-5,4)),rgb.getpixel((4,rgb.height-5)),rgb.getpixel((rgb.width-5,rgb.height-5))]
    bg=tuple(sum(p[i] for p in pts)//4 for i in range(3))
    diff=ImageChops.difference(rgb,Image.new('RGB',rgb.size,bg)).convert('L')
    mask=diff.point(lambda p:0 if p<20 else min(255,int((p-20)*7)))
    mask=mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(1.3))
    out=im.convert('RGBA'); out.putalpha(mask)
    box=mask.getbbox()
    return out.crop(box) if box else out


def finger_fx(bg,t,x,y):
    d=ImageDraw.Draw(bg,'RGBA')
    pulse=.5+.5*math.sin(t*10)
    for r,a in [(22,210),(42,110),(68,45)]:
        rr=r*(.85+.22*pulse)
        d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=(255,231,65,a),width=max(2,int(7-r/16)))
    for i in range(10):
        a=i*math.tau/10+t*1.7; r=75+12*math.sin(t*5+i)
        b.star(d,x+math.cos(a)*r,y+math.sin(a)*r,8,(255,177,45,220))


def body_beat(bg,pointing,t):
    q=b.ease((t-4.03)/.46)
    # energetic overshoot: 0.72 -> 1.12 -> 1.00
    if q<.72:
        scale=b.lerp(.72,1.13,b.ease(q/.72))
    else:
        scale=b.lerp(1.13,1.0,b.ease((q-.72)/.28))
    scale*=1+.025*math.sin(t*8)
    angle=b.lerp(-4.0,1.2,b.ease((t-4.03)/.7))+1.2*math.sin(t*3.2)
    body=b.contain(pointing,560,650,1.05)
    body=b.transform(body,scale,angle)
    x=330+10*math.sin(t*3.1); y=414+8*math.sin(t*5.0)
    b.rays(bg,365,350,t)
    b.paste_center(bg,body,x,y)
    # approximate fingertip after final placement, intentionally tied to the validated pose
    fx=470+10*math.sin(t*3.1); fy=213+8*math.sin(t*5.0)
    finger_fx(bg,t,fx,fy)
    d=ImageDraw.Draw(bg,'RGBA')
    # short motion streaks instead of a fake articulated arm
    if 4.03<t<4.58:
        p=b.ease((t-4.03)/.55)
        for j in range(5):
            yy=290+j*32
            d.line((110-90*p,yy,255-45*p,yy-18),fill=(255,255,255,120-int(j*12)),width=7)


def main():
    ref=b.restore_ref()
    pointing=auto_key(ref)
    raw=[b.normalize(b.find('portrait.png')) if list(b.KF_ROOT.rglob('portrait.png')) else b.normalize(b.find('01-look-up.png'))]
    raw += [b.normalize(b.find(x)) for x in ['01-look-up.png','02-surprise.png','03-blink.png']]
    poses=[b.white_to_alpha(x) for x in raw]; poses.append(poses[2])

    for fi in range(b.N):
        t=fi/b.FPS
        if t<7.35:
            bg=b.sky(t)
            if t<4.03:
                pos=min(t,3.85)/3.85*(len(poses)-1); idx=min(len(poses)-2,int(pos)); q=b.ease(pos-idx)
                a=b.contain(poses[idx],520,560,1.08); c=b.contain(poses[idx+1],520,560,1.08)
                face=Image.blend(a,c,q)
                face=b.transform(face,1+.06*math.sin(min(1,t/1.1)*math.pi)+.025*math.sin(t*7),2.2*math.sin(t*2.1))
                b.rays(bg,395,360,t); b.paste_center(bg,face,395+8*math.sin(t*2.3),380+10*math.sin(t*3.5))
                d=ImageDraw.Draw(bg,'RGBA')
                for j in range(10):
                    ang=t*1.7+j*.63; rr=150+22*math.sin(t*3+j)
                    d.text((395+math.cos(ang)*rr,360+math.sin(ang)*rr*.55),'?',font=b.fnt(31+int(5*math.sin(j+t))),anchor='mm',fill=(255,255,255,180))
            else:
                body_beat(bg,pointing,t)

            if 1.6<t<6.02:
                b.text_impact(bg,'POURQUOI',865,195,80,t,1.60)
                b.text_impact(bg,'LE CIEL',865,295,76,t,2.05)
                b.text_impact(bg,'EST',865,390,68,t,2.50)
                b.text_impact(bg,'BLEU ?',865,500,92,t,2.95)
                d=ImageDraw.Draw(bg,'RGBA'); q=b.ease((t-3.15)/.55)
                if q>0:d.rounded_rectangle((715,565,715+int(305*q),581),8,fill=(255,222,60,255))
            if t>6.02: bg=b.cloud_wipe(bg,t)
        else:
            bg=b.prism(t)

        # tiny whole-frame recoil on the pointing impact, like a real edited short
        if 4.08<t<4.42:
            z=1+.025*math.sin(math.pi*b.ease((t-4.08)/.34))
            nw,nh=int(b.W*z),int(b.H*z)
            tmp=bg.resize((nw,nh),Image.Resampling.LANCZOS)
            bg=tmp.crop(((nw-b.W)//2,(nh-b.H)//2,(nw+b.W)//2,(nh+b.H)//2))
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=92,subsampling=1)

    out=OUT/'P4-B4-hook-9s-v4.mp4'; wav=b.audio()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(b.FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip())
    assert 8.95<=dur<=9.05,dur
    print('P4_B4_V4_PASS',out,out.stat().st_size,dur)

if __name__=='__main__':main()
