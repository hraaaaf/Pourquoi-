from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw
import p4b6_full_pilot as v1
import p4b6_full_pilot_v2 as v2
import p4b4_hook9s_v3 as b
import p4b4_hook9s_v5 as v5
import p4b5_opening_v2 as b5

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b6-full-pilot-v3'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)
v1.OUT=OUT; b.OUT=OUT; b.FRAMES=FRAMES; v5.OUT=OUT; v5.FRAMES=FRAMES; b5.OUT=OUT; b5.FRAMES=FRAMES
W,H,FPS,DUR,N=v1.W,v1.H,v1.FPS,v1.DUR,v1.N

def scene_light(t):
    bg=v1.DARK.copy(); d=ImageDraw.Draw(bg,'RGBA')
    sx,sy=155,375
    for r,a in [(92,45),(65,85),(38,255)]: d.ellipse((sx-r,sy-r,sx+r,sy+r),fill=(255,225,96,a))
    cols=[(245,70,72),(255,145,45),(255,220,62),(64,204,116),(57,150,244),(121,86,218)]
    if t<2.8:
        v1.beam(d,(235,375),(565,375),30)
        d.polygon([(560,540),(680,245),(800,540)],fill=(35,55,105,255),outline=(235,247,255,255))
        v1.pop(bg,'LA LUMIÈRE PARAÎT BLANCHE',640,105,50,t,.15)
        for i in range(12):
            a=i*math.tau/12+t*.5; v1.star(d,640+math.cos(a)*330,385+math.sin(a)*230,7,(255,255,255,130))
    elif t<6.2:
        v1.beam(d,(235,375),(515,375),30)
        d.polygon([(500,535),(620,240),(740,535)],fill=(35,55,105,255),outline=(235,247,255,255))
        q=v1.ease((t-2.8)/.7)
        for j,c in enumerate(cols): d.line((675,335+j*12,710+420*q,220+j*58),fill=(*c,245),width=22)
        v1.pop(bg,'ELLE SE SÉPARE',640,100,54,t,2.8)
        v1.pop(bg,'EN PLUSIEURS COULEURS',640,165,44,t,3.25)
    else:
        # Full safe-frame rainbow composition, no cropped legacy text.
        d.polygon([(245,545),(365,245),(485,545)],fill=(35,55,105,255),outline=(235,247,255,255))
        for j,c in enumerate(cols): d.line((420,335+j*12,1120,185+j*72),fill=(*c,245),width=26)
        v1.pop(bg,'LA LUMIÈRE BLANCHE CONTIENT',640,105,42,t,6.2)
        v1.pop(bg,'TOUTES CES COULEURS',640,165,56,t,6.65)
        labels=['ROUGE','ORANGE','JAUNE','VERT','BLEU','VIOLET']
        for j,(lab,c) in enumerate(zip(labels,cols)):
            d.rounded_rectangle((930,205+j*72,1160,254+j*72),14,fill=(*c,205))
            v1.txt(bg,lab,1045,230+j*72,25,stroke=(25,40,80))
    return v2.impact(bg,t,[0.15,2.8,6.2],(255,210,72),180)

def scene_atmos(t):
    if t<5.2:
        return v2.impact(v2.camera(v1.scene_atmos(t),t,1.015,.015,14),t,[.2],(74,160,255),210)
    if t<10.5:
        bg=v1.SKY.copy(); d=ImageDraw.Draw(bg,'RGBA')
        d.rectangle((0,565,W,H),fill=(78,175,105,255))
        cx,cy=620,355
        # incoming white beam
        v1.beam(d,(75,195),(cx-55,cy-20),25,(255,250,226,245))
        # molecule nucleus
        for r,a in [(72,45),(48,95),(24,255)]: d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,255,255,a),outline=(120,190,245,220),width=3)
        q=v1.ease((t-5.2)/.8)
        for i in range(20):
            a=i*math.tau/20+t*.08; rr=255*q
            d.line((cx,cy,cx+math.cos(a)*rr,cy+math.sin(a)*rr),fill=(65,151,255,205),width=9)
        for i in range(18):
            x=70+(i*137)%1140; y=160+(i*91)%330; r=9+(i%3)*3
            d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,130))
        v1.pop(bg,'UNE MOLÉCULE RENCONTRE LA LUMIÈRE',640,95,42,t,5.2)
        v1.pop(bg,'ET LE BLEU PART DANS TOUTES LES DIRECTIONS',640,625,34,t,6.4)
        return v2.impact(bg,t,[5.2],(74,160,255),220)
    bg=v1.scene_atmos(t)
    # modest camera only, preserving safe text.
    bg=v2.camera(bg,t,1.025,.012,6)
    return v2.impact(bg,t,[10.5],(74,160,255),210)

def scene_sunset(t):
    if t<3.7:
        return v2.impact(v2.camera(v1.scene_sunset(t),t,1.01,.012,8),t,[.1],(255,145,60),210)
    if t<7.3:
        bg=v1.SUNSET.copy(); d=ImageDraw.Draw(bg,'RGBA')
        d.rectangle((0,570,W,H),fill=(64,72,80,255))
        # close-up long path, no inherited text to crop
        d.line((1125,500,835,430,520,360,180,320),fill=(255,215,120,240),width=34)
        d.line((520,360,180,320),fill=(255,118,55,245),width=18)
        for i in range(12):
            x=820-i*48; y=430-i*8; ang=-1.15-i*.035; rr=85+6*i
            d.line((x,y,x+math.cos(ang)*rr,y+math.sin(ang)*rr),fill=(65,150,255,175),width=8)
        for r,a in [(92,35),(62,80),(36,255)]: d.ellipse((1090-r,505-r,1090+r,505+r),fill=(255,190,72,a))
        v1.pop(bg,"PLUS D'AIR = PLUS DE DIFFUSION",640,105,46,t,3.7)
        v1.pop(bg,'LE BLEU EST DISPERSÉ AVANT DE T’ATTEINDRE',640,625,32,t,4.6)
        return v2.impact(bg,t,[3.7],(255,145,60),220)
    bg=v1.scene_sunset(t)
    bg=v2.camera(bg,t,1.045,.012,6)
    d=ImageDraw.Draw(bg,'RGBA')
    v1.txt(bg,'ROUGE + ORANGE ARRIVENT JUSQU’À TOI',640,660,30,fill=(255,235,180),stroke=(110,55,35))
    return v2.impact(bg,t,[7.3],(255,145,60),210)

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
        elif t<49: bg=v2.scene_waves(t-38)
        elif t<58: bg=v2.scene_violet(t-49)
        elif t<69: bg=scene_sunset(t-58)
        else: bg=v1.scene_challenge(t-69,pointing)
        bg=v1.transition(bg,t,cuts)
        bg.convert('RGB').save(FRAMES/f'{fi:04d}.jpg',quality=91,subsampling=1)
    wav=v1.make_audio(); out=OUT/'P4-B6-full-pilot-75s-v3.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(FRAMES/'%04d.jpg'),'-i',str(wav),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True).strip()); assert 74.9<=dur<=75.1
    print('P4_B6_FULL_PILOT_V3_PASS',out,out.stat().st_size,dur)
if __name__=='__main__':main()
