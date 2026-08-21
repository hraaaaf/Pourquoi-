from pathlib import Path
import base64, hashlib, shutil
from PIL import Image
from gradio_client import Client, handle_file
from huggingface_hub import hf_hub_download

OUT=Path('artifacts/p4b3-liveportrait'); OUT.mkdir(parents=True,exist_ok=True)
REF_RAW=OUT/'reference.jpg'; REF=OUT/'portrait.png'; DRIVE=OUT/'driving.mp4'; RESULT=OUT/'liveportrait.mp4'
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'

def restore_and_crop():
    payload=''.join(Path(f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    REF_RAW.write_bytes(base64.b64decode(payload,validate=True))
    raw=REF_RAW.read_bytes(); sha=hashlib.sha256(raw).hexdigest(); assert sha==EXPECTED_SHA
    im=Image.open(REF_RAW).convert('RGB')
    crop=im.crop((55,35,265,285)).resize((512,512),Image.Resampling.LANCZOS)
    crop.save(REF)
    print('PORTRAIT_OK',REF,crop.size)

def get_driver():
    src=hf_hub_download(repo_id='KlingTeam/LivePortrait',repo_type='space',filename='assets/examples/driving/d0.mp4')
    shutil.copy2(src,DRIVE)
    print('LIVEPORTRAIT_DRIVER_OK',DRIVE,DRIVE.stat().st_size)

def video_path_from(x):
    if isinstance(x,str): return x
    if isinstance(x,dict):
        if x.get('path'): return x['path']
        video=x.get('video')
        if isinstance(video,str): return video
        if isinstance(video,dict) and video.get('path'): return video['path']
    return None

def main():
    restore_and_crop(); get_driver()
    c=Client('KlingTeam/LivePortrait')
    endpoint='/gpu_wrapped_execute_video'
    print('LIVEPORTRAIT_ENDPOINT',endpoint)
    # Gradio Video component expects VideoData, not a bare filepath.
    drive_data={'video': handle_file(str(DRIVE)), 'subtitles': None}
    out=c.predict(handle_file(str(REF)),drive_data,True,True,True,api_name=endpoint)
    print('RAW_OUTPUT',out)
    candidates=[]
    seq=out if isinstance(out,(list,tuple)) else [out]
    for x in seq:
        p=video_path_from(x)
        if p: candidates.append(p)
    if not candidates: raise RuntimeError(f'No video path in output: {out!r}')
    src=Path(candidates[0]); shutil.copy2(src,RESULT)
    print('LIVEPORTRAIT_PASS',RESULT,RESULT.stat().st_size)

if __name__=='__main__': main()
