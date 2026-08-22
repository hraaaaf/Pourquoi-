from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw
import p4b6_full_pilot as v1
import p4b4_hook9s_v3 as b
import p4b4_hook9s_v5 as v5
import p4b5_opening_v2 as b5

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b6-full-pilot-v2'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
v1.OUT=OUT; b.OUT=OUT; b.FRAMES=FRAMES; v5.OUT=OUT; v5.FRAMES=FRAMES; b5.OUT=OUT; b5.FRAMES=FRAMES
W,H,FPS,DUR,N=v1.W,v1.H,v1.FPS,v1.DUR,v1.N

def camera(bg,t,z0=1.025,zamp=.025,drift=18):
    z=z0+zamp*math.sin(t*1.35)
    nw,nh=int(W*z),int(H*z); im=bg.resize((nw,nh),Image.Resampling.LANCZOS)
    cx=(nw-W)//2+int(math.sin(t*.8)*drift); cy=(nh-H)//2+int(math.cos(t*.65)*drift*.35)
    cx=max(0,min(nw-W,cx)); cy=max(0,min(nh-H,cy))
    return im.crop((cx,cy,cx+W,cy+H)).convert('RGBA')

def impact(bg,t,beats,color=(255,222,60),radius=240):
    d=ImageDraw.Draw(bg,'RGBA')
    for beat in beats:
        if beat<=t<beat+.32:
            q=(t-beat)/.32; a=int(210*(1-q)); r=40+radius*v1.ease(q)
            d.ellipse((W/2-r,H/2-r,W/2+r,H/2+r),outline=(*color,a),width=max(3,int(12*(1-q))))
            for i in range(14):
                ang=i*math.tau/14+t*2; r1=r+15; r2=r+75*(1-q)
                d.line((W/2+math.cos(ang)*r1,H/2+math.sin(ang)*r1,W/2+math.cos(ang)*r2,H/2+math.sin(ang)*r2),fill=(*color,a),width=5)
    return bg

def scene_light(t):
    bg=v1.scene_light(t)
    # distinct shot sizes: source -> prism -> rainbow
    if t<2.8:
        crop=bg.crop((0,130,760,620)).resize((W,H),Image.Resampling.LANCZOS)
        bg=crop.convert('RGBA')
    elif t<6.2:
        bg=camera(bg,t,1.035,.018,10)
    else:
        crop=bg.crop((390,120,W,650)).resize((W,H),Image.Resampling.LANCZOS)
        bg=crop.convert('RGBA')
    return impact(bg,t,[0.15,2.8,6.2],(255,210,72),180)

def scene_atmos(t):
    bg=v1.scene_atmos(t)
    # three internal cuts: field -> molecule -> scatter
    if t<5.2:
        bg=camera(bg,t,1.015,.015,14)
    elif t<10.5:
        crop=bg.crop((280,120,860,620)).resize((W,H),Image.Resampling.LANCZOS)
        bg=crop.convert('RGBA')
        d=ImageDraw.Draw(bg,'RGBA')
        v1.txt(bg,'UNE MOLÉCULE',920,120,44)
        v1.txt(bg,'RENCONTRE LA LUMIÈRE',920,178,36)
    else:
        bg=camera(bg,t,1.065,.02,8)
        d=ImageDraw.Draw(bg,'RGBA')
        for i in range(7):
            ang=t*1.8+i*math.tau/7; v1.star(d,640+math.cos(ang)*245,355+math.sin(ang)*170,9,(255,230,80,210))
    return impact(bg,t,[.2,5.2,10.5],(74,160,255),210)

def scene_waves(t):
    bg=v1.DARK.copy(); d=ImageDraw.Draw(bg,'RGBA')
    if t<3.8:
        v1.pop(bg,'ROUGE',190,110,68,t,.15)
        v1.pop(bg,'ONDE PLUS LONGUE',390,170,42,t,.55)
        pts=v1.wave_points(100,390,1000,65,3,t*2.2); d.line(pts,fill=(248,76,76,255),width=18)
        for i in range(5):
            x=210+i*210; d.ellipse((x-9,550-9,x+9,550+9),fill=(248,76,76,210))
    elif t<7.6:
        v1.pop(bg,'BLEU',190,110,68,t,3.8)
        v1.pop(bg,'ONDE PLUS COURTE',390,170,42,t,4.2)
        pts=v1.wave_points(100,390,1000,52,8,t*4.2); d.line(pts,fill=(75,157,255,255),width=18)
        for i in range(12):
            a=i*math.tau/12+t; r=150+15*math.sin(t*3+i); d.line((640,390,640+math.cos(a)*r,390+math.sin(a)*r),fill=(75,157,255,120),width=6)
    else:
        v1.pop(bg,'LE BLEU EST DAVANTAGE DIFFUSÉ',640,115,50,t,7.6)
        red=v1.wave_points(100,315,780,32,3,t*2); blue=v1.wave_points(100,475,780,26,8,t*4)
        d.line(red,fill=(248,76,76,255),width=12); d.line(blue,fill=(75,157,255,255),width=12)
        for i in range(16):
            a=i*math.tau/16+t*.7; r=110+65*v1.ease((t-7.6)/1.4); d.line((950,475,950+math.cos(a)*r,475+math.sin(a)*r),fill=(75,157,255,175),width=6)
        v1.txt(bg,'→',930,315,56,fill=(255,160,160)); v1.txt(bg,'→ PARTOUT !',1030,475,38,fill=(170,215,255))
    return impact(bg,t,[0,3.8,7.6],(255,223,75),200)

def scene_violet(t):
    if t<3.0:
        bg=v1.scene_violet(t)
        return camera(bg,t,1.03,.02,10)
    if t<6.0:
        bg=v1.gradient((120,55,220),(76,70,210)); d=ImageDraw.Draw(bg,'RGBA')
        for i in range(24):
            a=i*math.tau/24+t*.4; r=55+260*v1.ease((t-3)/1.0); d.line((640,360,640+math.cos(a)*r,360+math.sin(a)*r),fill=(200,145,255,160),width=8)
        v1.txt(bg,'LE VIOLET',640,260,74,fill=(245,225,255),stroke=(95,45,180))
        v1.txt(bg,'EST AUSSI TRÈS DIFFUSÉ',640,360,46)
        v1.txt(bg,'MAIS...',640,465,58,fill=(255,225,90))
        return impact(bg,t,[3.0],(230,180,255),230)
    bg=v1.gradient((92,63,200),(41,145,235)); d=ImageDraw.Draw(bg,'RGBA')
    d.rounded_rectangle((100,140,590,580),30,fill=(105,60,195,210)); d.rounded_rectangle((690,140,1180,580),30,fill=(35,115,220,220))
    v1.txt(bg,'VIOLET',345,245,62,fill=(235,210,255),stroke=(95,45,180)); v1.txt(bg,'BLEU',935,245,62,fill=(200,230,255))
    v1.txt(bg,'TRÈS DIFFUSÉ',345,360,36); v1.txt(bg,'LE CIEL NOUS',935,345,38); v1.txt(bg,'PARAÎT SURTOUT BLEU',935,405,32)
    v1.txt(bg,'✓',935,500,70,fill=(255,230,80),stroke=(25,80,160))
    return impact(bg,t,[6.0],(255,225,80),220)

def scene_sunset(t):
    bg=v1.scene_sunset(t)
    if t<3.7:
        # start wide
        bg=camera(bg,t,1.01,.012,8)
    elif t<7.3:
        # punch into long path / scattering arrows
        crop=bg.crop((230,170,1120,620)).resize((W,H),Image.Resampling.LANCZOS); bg=crop.convert('RGBA')
        v1.txt(bg,"PLUS D'AIR = PLUS DE DIFFUSION",640,100,42)
    else:
        bg=camera(bg,t,1.06,.018,10)
        d=ImageDraw.Draw(bg,'RGBA')
        for i in range(6):
            x=650+i*85; y=370-i*10; d.line((x,y,x+65,y-70),fill=(75,157,255,150),width=7)
        v1.txt(bg,'LE ROUGE ET L’ORANGE ARRIVENT JUSQU’À TOI',640,650,34,fill=(255,235,180),stroke=(110,55,35))
    return impact(bg,t,[.1,3.7,7.3],(255,145,60),210)

def main():
    pointing=v5.load_pointing()
    neutral=b.normalize(b.find('portrait.png')) if list(b.KF_ROOT.rglob('portrait.png')) else b.normalize(b.find('01-look-up.png'))
    raw=[neutral,b.normalize(b.find('01-look-up.png')),b.normalize(b.find('02-surprise.png')),b.normalize(b.find('03-blink.png'))]
    poses=[b5.clean_bg(x) for x in raw]
    cuts=[9,20,38,49,58,69]
    for fi in range(N):
        t=fi/FPS
        if t<9: bg=v1.hook_frame(poses,pointing,t)
        elif t<20: bg=scene_light(t-9)
        elif t<38: bg=scene_atmos(t-20)
        elif t<49: bg=scene_waves(t-38)
        elif t<58: bg=scene_violet(t-49)
        elif t<69: bg=scene_sunset(t-58)
        else: bg=v1.scene_challenge(t-69,pointing)
        bg=v1.transition(bg,t,cuts)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=91,subsampling=1)
    wav=v1.make_audio(); out=OUT/'P4-B6-full-pilot-75s-v2.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip()); assert 74.9<=dur<=75.1
    print('P4_B6_FULL_PILOT_V2_PASS',out,out.stat().st_size,dur)
if __name__=='__main__':main()
