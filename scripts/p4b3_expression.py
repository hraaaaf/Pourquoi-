from pathlib import Path
import base64, hashlib, shutil, subprocess
from PIL import Image
from gradio_client import Client, handle_file

SPACE='fffiloni/expression-editor'
OUT=Path('artifacts/p4b3-expression'); OUT.mkdir(parents=True,exist_ok=True)
REF_RAW=OUT/'reference.jpg'; REF=OUT/'portrait.png'; VIDEO=OUT/'p4b3-liveportrait-microclip.mp4'
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'

def restore_portrait():
    payload=''.join(Path(f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    REF_RAW.write_bytes(base64.b64decode(payload,validate=True))
    raw=REF_RAW.read_bytes(); assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
    im=Image.open(REF_RAW).convert('RGB')
    crop=im.crop((45,20,275,270)).resize((512,512),Image.Resampling.LANCZOS)
    crop.save(REF)
    print('EXPRESSION_PORTRAIT_OK',REF,crop.size)

def extract_path(x):
    if isinstance(x,str): return x
    if isinstance(x,dict):
        if x.get('path'): return x['path']
        if x.get('name'): return x['name']
    if isinstance(x,(list,tuple)):
        for y in x:
            p=extract_path(y)
            if p: return p
    return None

def edit(c, endpoint, name, vals):
    out=c.predict(
        handle_file(str(REF)),
        vals['pitch'], vals.get('yaw',0), vals.get('roll',0),
        vals.get('blink',0), vals.get('eyebrow',0), vals.get('wink',0),
        vals.get('pupil_x',0), vals.get('pupil_y',0),
        vals.get('aaa',0), vals.get('eee',0), vals.get('woo',0), vals.get('smile',0),
        1, 1, 'All', 1.7,
        api_name=endpoint,
    )
    p=extract_path(out)
    if not p: raise RuntimeError(f'No image path for {name}: {out!r}')
    dst=OUT/f'{name}.png'; shutil.copy2(Path(p),dst)
    with Image.open(dst) as im: im.load(); print('KEYFRAME_PASS',name,im.size,dst.stat().st_size)
    return dst

def build_video(frames):
    seqdir=OUT/'sequence'; seqdir.mkdir(exist_ok=True)
    # Build a 6-pose arc, then let ffmpeg motion-compensate between the learned keyframes.
    arc=list(frames)
    if len(arc)>1: arc += arc[-2::-1]
    while len(arc)<6:
        arc += arc[-2::-1] if len(arc)>1 else arc
    arc=arc[:6]
    for i,p in enumerate(arc):
        shutil.copy2(p,seqdir/f'{i:03d}.png')
    subprocess.run([
        'ffmpeg','-y','-loglevel','error','-framerate','3','-i',str(seqdir/'%03d.png'),
        '-vf','minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,scale=512:512:flags=lanczos',
        '-t','2.0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(VIDEO)
    ],check=True)
    print('MICROCLIP_PASS',VIDEO,VIDEO.stat().st_size)

def main():
    restore_portrait()
    c=Client(SPACE)
    info=c.view_api(return_format='dict')
    named=info.get('named_endpoints',{}) if isinstance(info,dict) else {}
    endpoint=next((n for n,s in named.items() if len(s.get('parameters',[]))==17),None)
    if endpoint is None: raise RuntimeError(f'No 17-input expression endpoint: {list(named)}')
    print('EXPRESSION_ENDPOINT',endpoint)

    neutral=OUT/'00-neutral.png'; shutil.copy2(REF,neutral)
    specs=[
        ('01-look-up', dict(pitch=-7,pupil_y=-8,eyebrow=4,smile=.12)),
        ('02-surprise', dict(pitch=-9,pupil_y=-10,eyebrow=10,aaa=35,smile=.05)),
        ('03-blink', dict(pitch=-6,pupil_y=-6,eyebrow=5,blink=4,aaa=5,smile=.10)),
        ('04-smile', dict(pitch=-5,pupil_y=-5,eyebrow=3,aaa=8,smile=.75)),
    ]
    frames=[neutral]
    for name,vals in specs:
        try:
            frames.append(edit(c,endpoint,name,vals))
        except Exception as e:
            print('KEYFRAME_FAIL',name,repr(e))
    if len(frames)<2: raise RuntimeError('No learned LivePortrait keyframe generated')
    build_video(frames)
    print('KEYFRAMES_TOTAL',len(frames))

if __name__=='__main__': main()
