from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw, ImageFile
import p4b4_hook9s_v3 as b

ImageFile.LOAD_TRUNCATED_IMAGES=True
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b4-hook9s-v5'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
b.OUT=OUT; b.FRAMES=FRAMES
POINTING=ROOT/'assets'/'p4b4'/'validated-pointing-scene.jpg'


def pointing_frame(src,t):
    local=max(0,t-4.03); q=b.ease(min(1,local/.38))
    if q < .72: z=b.lerp(1.00,1.115,b.ease(q/.72))
    else: z=b.lerp(1.115,1.065,b.ease((q-.72)/.28))
    if local>.38: z=1.065+.018*b.ease(min(1,(local-.38)/1.5))+.006*math.sin(local*3.2)
    base=src.resize((b.W,b.H),Image.Resampling.LANCZOS); nw,nh=int(b.W*z),int(b.H*z)
    zoom=base.resize((nw,nh),Image.Resampling.LANCZOS)
    drift=b.ease(min(1,local/1.65)); cx=nw/2-18*drift; cy=nh/2-8*drift
    left=int(max(0,min(nw-b.W,cx-b.W/2))); top=int(max(0,min(nh-b.H,cy-b.H/2)))
    frame=zoom.crop((left,top,left+b.W,top+b.H)).convert('RGBA'); d=ImageDraw.Draw(frame,'RGBA')
    fx=(405/960)*nw-left; fy=(169/540)*nh-top; pulse=.5+.5*math.sin(local*10)
    for rr,a,w in [(18,230,5),(36,125,6),(62,55,8)]:
        r=rr*(.88+.18*pulse); d.ellipse((fx-r,fy-r,fx+r,fy+r),outline=(255,226,54,a),width=w)
    for i in range(8):
        ang=i*math.tau/8+local*2.2; r=74+9*math.sin(local*5+i)
        b.star(d,fx+math.cos(ang)*r,fy+math.sin(ang)*r,8,(255,166,45,220))
    if local<.42:
        a=int(180*(1-local/.42))
        for j in range(6):
            yy=105+j*90; d.line((0,yy,165,yy-35),fill=(255,255,255,max(0,a-j*12)),width=7)
    if local<.34:
        shake=5*math.sin(local*55)*(1-local/.34); tmp=Image.new('RGBA',(b.W,b.H),(30,130,225,255))
        tmp.alpha_composite(frame,(int(shake),int(-shake*.45))); frame=tmp
    return frame


def main():
    if not POINTING.exists(): raise FileNotFoundError(POINTING)
    pointing=Image.open(POINTING); pointing.load(); pointing=pointing.convert('RGB')
    assert pointing.size==(960,540), pointing.size
    print('POINTING_ASSET_OK',pointing.size,POINTING.stat().st_size)
    raw=[b.normalize(b.find('portrait.png')) if list(b.KF_ROOT.rglob('portrait.png')) else b.normalize(b.find('01-look-up.png'))]
    raw += [b.normalize(b.find(x)) for x in ['01-look-up.png','02-surprise.png','03-blink.png']]
    poses=[b.white_to_alpha(x) for x in raw]; poses.append(poses[2])
    for fi in range(b.N):
        t=fi/b.FPS
        if t<4.03:
            bg=b.sky(t); pos=min(t,3.85)/3.85*(len(poses)-1); idx=min(len(poses)-2,int(pos)); q=b.ease(pos-idx)
            a=b.contain(poses[idx],520,560,1.08); c=b.contain(poses[idx+1],520,560,1.08); face=Image.blend(a,c,q)
            face=b.transform(face,1+.06*math.sin(min(1,t/1.1)*math.pi)+.025*math.sin(t*7),2.2*math.sin(t*2.1))
            b.rays(bg,395,360,t); b.paste_center(bg,face,395+8*math.sin(t*2.3),380+10*math.sin(t*3.5)); d=ImageDraw.Draw(bg,'RGBA')
            for j in range(10):
                ang=t*1.7+j*.63; rr=150+22*math.sin(t*3+j)
                d.text((395+math.cos(ang)*rr,360+math.sin(ang)*rr*.55),'?',font=b.fnt(31+int(5*math.sin(j+t))),anchor='mm',fill=(255,255,255,180))
        elif t<7.35: bg=pointing_frame(pointing,t)
        else: bg=b.prism(t)
        if 1.6<t<6.02:
            b.text_impact(bg,'POURQUOI',875,190,76,t,1.60); b.text_impact(bg,'LE CIEL',875,286,72,t,2.05)
            b.text_impact(bg,'EST',875,376,64,t,2.50); b.text_impact(bg,'BLEU ?',875,480,88,t,2.95)
            d=ImageDraw.Draw(bg,'RGBA'); uq=b.ease((t-3.15)/.55)
            if uq>0:d.rounded_rectangle((725,545,725+int(300*uq),561),8,fill=(255,222,60,255))
        if 6.02<t<7.35: bg=b.cloud_wipe(bg,t)
        if 4.03<=t<4.16:
            f=1-b.ease((t-4.03)/.13); bg=Image.blend(bg,Image.new('RGBA',(b.W,b.H),(255,244,194,255)),.24*f)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=93,subsampling=1)
    out=OUT/'P4-B4-hook-9s-v5.mp4'; wav=b.audio()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(b.FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip())
    assert 8.95<=dur<=9.05,dur; print('P4_B4_V5_PASS',out,out.stat().st_size,dur)

if __name__=='__main__':main()
