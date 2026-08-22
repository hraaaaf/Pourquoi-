from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw, ImageFilter
import p4b4_hook9s_v3 as b
import p4b4_hook9s_v5 as v5

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b5-opening-v2'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
b.OUT=OUT; b.FRAMES=FRAMES; v5.OUT=OUT; v5.FRAMES=FRAMES


def clean_bg(im):
    # Remove only the background connected to the outer border. This keeps
    # white eyes/hoodie details instead of chroma-keying every pale pixel.
    rgb=im.convert('RGB')
    work=rgb.copy()
    marker=(255,0,255)
    for xy in [(0,0),(rgb.width-1,0),(0,rgb.height-1),(rgb.width-1,rgb.height-1)]:
        ImageDraw.floodfill(work,xy,marker,thresh=52)
    wp=work.load(); alpha=Image.new('L',rgb.size,255); ap=alpha.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            if wp[x,y]==marker: ap[x,y]=0
    # Pull transparency one pixel into the matte and feather it, killing the halo.
    alpha=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.75))
    out=im.convert('RGBA'); out.putalpha(alpha)
    bb=out.getbbox()
    if bb:
        l,t,r,bt=bb
        pad=4
        out=out.crop((max(0,l-pad),max(0,t-pad),min(out.width,r+pad),min(out.height,bt+pad)))
    return out


def flash(bg,t,at,dur=.12,strength=.28):
    if not at<=t<at+dur:return bg
    q=1-b.ease((t-at)/dur)
    return Image.blend(bg,Image.new('RGBA',(b.W,b.H),(255,244,190,255)),strength*q)


def burst(bg,cx,cy,t,phase=0):
    d=ImageDraw.Draw(bg,'RGBA')
    for i in range(24):
        a=i*math.tau/24+phase
        r1=145+10*math.sin(t*5+i)
        r2=225+24*math.sin(t*3+i*.7)
        d.line((cx+math.cos(a)*r1,cy+math.sin(a)*r1,cx+math.cos(a)*r2,cy+math.sin(a)*r2),fill=(255,230,86,180),width=5)
    for i in range(8):
        a=i*math.tau/8+t*1.9
        r=258+12*math.sin(t*4+i)
        b.star(d,cx+math.cos(a)*r,cy+math.sin(a)*r*.62,10,(255,164,48,220))


def pose_on(bg,pose,t,start,end,center,base_scale=1.0,rot0=0,rot1=0,zoom0=1.2,zoom1=1.0):
    q=b.ease((t-start)/(end-start))
    im=b.contain(pose,570,630,base_scale)
    z=b.lerp(zoom0,zoom1,q); ang=b.lerp(rot0,rot1,q)
    im=b.transform(im,z,ang)
    sx=1+.025*math.sin((t-start)*8)
    im=im.resize((max(1,int(im.width*sx)),max(1,int(im.height*(2-sx)))),Image.Resampling.LANCZOS)
    x=center[0]+10*math.sin((t-start)*5)
    y=center[1]+10*math.sin((t-start)*6.3)
    b.paste_center(bg,im,x,y)


def opening_frame(poses,t):
    bg=b.sky(t)
    if t<.82:
        burst(bg,385,360,t)
        # Immediate face-dominant crop: the hook starts on the eyes, not the torso.
        pose_on(bg,poses[0],t,0,.82,(380,398),1.48,-4,0,1.30,1.00)
    elif t<1.56:
        burst(bg,395,350,t,.22)
        pose_on(bg,poses[1],t,.82,1.56,(397,392),1.34,6,0,1.22,1.00)
        bg=flash(bg,t,.82)
    elif t<2.36:
        burst(bg,410,352,t,.48)
        # Surprise cut punches much closer for a visibly different shot size.
        pose_on(bg,poses[2],t,1.56,2.36,(410,402),1.52,-6,0,1.28,.98)
        bg=flash(bg,t,1.56,.13,.34)
    else:
        blink_window=2.66<=t<2.80
        p=poses[3] if blink_window else poses[2]
        burst(bg,405,350,t,.72)
        pose_on(bg,p,t,2.36,4.03,(405,398),1.16,3,-1,1.14,1.00)
        bg=flash(bg,t,2.36,.10,.22)

    d=ImageDraw.Draw(bg,'RGBA')
    for j in range(6):
        ang=t*2.35+j*math.tau/6
        rr=165+17*math.sin(t*4+j)
        d.text((400+math.cos(ang)*rr,355+math.sin(ang)*rr*.55),'?',font=b.fnt(39),anchor='mm',fill=(255,255,255,195))

    b.text_impact(bg,'POURQUOI',890,175,82,t,1.02)
    b.text_impact(bg,'LE CIEL',890,278,78,t,1.46)
    b.text_impact(bg,'EST',890,370,66,t,1.92)
    b.text_impact(bg,'BLEU ?',890,485,96,t,2.30)
    uq=b.ease((t-2.65)/.45)
    if uq>0:d.rounded_rectangle((735,550,735+int(315*uq),568),9,fill=(255,222,60,255))

    if t>3.55:
        q=b.ease((t-3.55)/.48); a=int(205*q)
        for j in range(8):
            y=78+j*79
            d.line((0,y,190+int(180*q),y-30),fill=(255,255,255,max(0,a-j*11)),width=7)
    return bg


def main():
    pointing=v5.load_pointing()
    neutral=b.normalize(b.find('portrait.png')) if list(b.KF_ROOT.rglob('portrait.png')) else b.normalize(b.find('01-look-up.png'))
    raw=[neutral,b.normalize(b.find('01-look-up.png')),b.normalize(b.find('02-surprise.png')),b.normalize(b.find('03-blink.png'))]
    poses=[clean_bg(x) for x in raw]

    for fi in range(b.N):
        t=fi/b.FPS
        if t<4.03:
            bg=opening_frame(poses,t)
        elif t<7.35:
            bg=v5.pointing_frame(pointing,t)
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

    out=OUT/'P4-B5-opening-0-4s-v2.mp4'; wav=b.audio()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(b.FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip())
    assert 8.95<=dur<=9.05,dur
    print('P4_B5_OPENING_V2_PASS',out,out.stat().st_size,dur)

if __name__=='__main__':main()
