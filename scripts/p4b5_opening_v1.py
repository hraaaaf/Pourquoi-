from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import p4b4_hook9s_v3 as b
import p4b4_hook9s_v5 as v5

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b5-opening-v1'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
b.OUT=OUT; b.FRAMES=FRAMES; v5.OUT=OUT; v5.FRAMES=FRAMES


def clean_white(im):
    rgb=im.convert('RGB')
    diff=ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).convert('L')
    def a(p):
        if p<=6:return 0
        if p>=42:return 255
        return int((p-6)/36*255)
    m=diff.point(a).filter(ImageFilter.GaussianBlur(.7))
    out=im.convert('RGBA'); out.putalpha(m)
    bb=out.getbbox()
    return out.crop(bb) if bb else out


def flash(bg,t,at,dur=.12,strength=.28):
    if not at<=t<at+dur:return bg
    q=1-b.ease((t-at)/dur)
    return Image.blend(bg,Image.new('RGBA',(b.W,b.H),(255,244,190,255)),strength*q)


def burst(bg,cx,cy,t,phase=0):
    d=ImageDraw.Draw(bg,'RGBA')
    for i in range(22):
        a=i*math.tau/22+phase
        r1=135+10*math.sin(t*5+i)
        r2=205+22*math.sin(t*3+i*.7)
        d.line((cx+math.cos(a)*r1,cy+math.sin(a)*r1,cx+math.cos(a)*r2,cy+math.sin(a)*r2),fill=(255,230,86,170),width=5)
    for i in range(8):
        a=i*math.tau/8+t*1.9
        r=245+12*math.sin(t*4+i)
        b.star(d,cx+math.cos(a)*r,cy+math.sin(a)*r*.62,10,(255,164,48,210))


def pose_on(bg,pose,t,start,end,center,base_scale=1.0,rot0=0,rot1=0,zoom0=1.2,zoom1=1.0):
    q=b.ease((t-start)/(end-start))
    im=b.contain(pose,520,590,base_scale)
    z=b.lerp(zoom0,zoom1,q)
    ang=b.lerp(rot0,rot1,q)
    im=b.transform(im,z,ang)
    # subtle breathing / squash
    sx=1+.025*math.sin((t-start)*8)
    im=im.resize((max(1,int(im.width*sx)),max(1,int(im.height*(2-sx)))),Image.Resampling.LANCZOS)
    x=center[0]+8*math.sin((t-start)*5)
    y=center[1]+9*math.sin((t-start)*6.3)
    b.paste_center(bg,im,x,y)


def opening_frame(poses,t):
    bg=b.sky(t)
    # four editorial micro-cuts instead of one slow morph
    if t<.82:
        burst(bg,390,365,t)
        pose_on(bg,poses[0],t,0,.82,(390,390),1.15,-3,0,1.32,1.04)
    elif t<1.56:
        burst(bg,390,350,t,.2)
        pose_on(bg,poses[1],t,.82,1.56,(400,382),1.12,5,0,1.24,1.0)
        bg=flash(bg,t,.82)
    elif t<2.36:
        burst(bg,400,350,t,.45)
        pose_on(bg,poses[2],t,1.56,2.36,(400,382),1.18,-5,0,1.30,1.0)
        bg=flash(bg,t,1.56,.13,.34)
    else:
        # surprise base, with a blink hit in the middle of the shot
        blink_window=2.66<=t<2.80
        p=poses[3] if blink_window else poses[2]
        burst(bg,405,350,t,.7)
        pose_on(bg,p,t,2.36,4.03,(405,388),1.10,2,-1,1.12,1.02)
        bg=flash(bg,t,2.36,.10,.22)

    d=ImageDraw.Draw(bg,'RGBA')
    # orbiting questions: fewer, larger, faster, cleaner
    for j in range(6):
        ang=t*2.25+j*math.tau/6
        rr=150+16*math.sin(t*4+j)
        d.text((400+math.cos(ang)*rr,355+math.sin(ang)*rr*.55),'?',font=b.fnt(38),anchor='mm',fill=(255,255,255,190))

    # kinetic title lands earlier and with stronger hierarchy
    b.text_impact(bg,'POURQUOI',890,175,82,t,1.02)
    b.text_impact(bg,'LE CIEL',890,278,78,t,1.46)
    b.text_impact(bg,'EST',890,370,66,t,1.92)
    b.text_impact(bg,'BLEU ?',890,485,96,t,2.30)
    uq=b.ease((t-2.65)/.45)
    if uq>0:d.rounded_rectangle((735,550,735+int(315*uq),568),9,fill=(255,222,60,255))

    # speed streaks prepare the hard cut into the pointing pose
    if t>3.55:
        q=b.ease((t-3.55)/.48)
        a=int(190*q)
        for j in range(7):
            y=92+j*82
            d.line((0,y,180+int(160*q),y-28),fill=(255,255,255,max(0,a-j*12)),width=7)
    return bg


def main():
    pointing=v5.load_pointing()
    neutral=b.normalize(b.find('portrait.png')) if list(b.KF_ROOT.rglob('portrait.png')) else b.normalize(b.find('01-look-up.png'))
    raw=[neutral,b.normalize(b.find('01-look-up.png')),b.normalize(b.find('02-surprise.png')),b.normalize(b.find('03-blink.png'))]
    poses=[clean_white(x) for x in raw]

    for fi in range(b.N):
        t=fi/b.FPS
        if t<4.03:
            bg=opening_frame(poses,t)
        elif t<7.35:
            bg=v5.pointing_frame(pointing,t)
            # preserve validated B4 title and underline from this point onward
            if t<6.02:
                b.text_impact(bg,'POURQUOI',875,190,76,t,1.60)
                b.text_impact(bg,'LE CIEL',875,286,72,t,2.05)
                b.text_impact(bg,'EST',875,376,64,t,2.50)
                b.text_impact(bg,'BLEU ?',875,480,88,t,2.95)
                d=ImageDraw.Draw(bg,'RGBA'); uq=b.ease((t-3.15)/.55)
                if uq>0:d.rounded_rectangle((725,545,725+int(300*uq),561),8,fill=(255,222,60,255))
            if 6.02<t<7.35:bg=b.cloud_wipe(bg,t)
            if 4.03<=t<4.16:
                f=1-b.ease((t-4.03)/.13)
                bg=Image.blend(bg,Image.new('RGBA',(b.W,b.H),(255,244,194,255)),.24*f)
        else:
            bg=b.prism(t)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=93,subsampling=1)

    out=OUT/'P4-B5-opening-0-4s-v1.mp4'; wav=b.audio()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(b.FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip())
    assert 8.95<=dur<=9.05,dur
    print('P4_B5_OPENING_PASS',out,out.stat().st_size,dur)

if __name__=='__main__':main()
