from pathlib import Path
import base64, hashlib, shutil
from PIL import Image
from gradio_client import Client, handle_file
from huggingface_hub import hf_hub_download

SPACE='CVPR/Image-Animation-using-Thin-Plate-Spline-Motion-Model'
OUT=Path('artifacts/p4b3-tps'); OUT.mkdir(parents=True,exist_ok=True)
REF_RAW=OUT/'reference.jpg'; REF=OUT/'portrait.png'; DRIVE=OUT/'driving.mp4'; RESULT=OUT/'tps-motion.mp4'
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'

def restore_portrait():
    payload=''.join(Path(f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    REF_RAW.write_bytes(base64.b64decode(payload,validate=True))
    raw=REF_RAW.read_bytes(); assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
    im=Image.open(REF_RAW).convert('RGB')
    # Vox model is trained on faces. Keep head and upper torso, square and clean.
    crop=im.crop((45,25,275,255)).resize((256,256),Image.Resampling.LANCZOS)
    crop.save(REF)
    print('TPS_PORTRAIT_OK',REF,crop.size)

def get_driver():
    src=hf_hub_download(repo_id=SPACE,repo_type='space',filename='assets/driving.mp4')
    shutil.copy2(src,DRIVE)
    print('TPS_DRIVER_OK',DRIVE,DRIVE.stat().st_size)

def extract_path(x):
    if isinstance(x,str): return x
    if isinstance(x,dict):
        if x.get('path'): return x['path']
        v=x.get('video')
        if isinstance(v,str): return v
        if isinstance(v,dict) and v.get('path'): return v['path']
    if isinstance(x,(list,tuple)):
        for y in x:
            p=extract_path(y)
            if p: return p
    return None

def main():
    restore_portrait(); get_driver()
    c=Client(SPACE)
    info=c.view_api(return_format='dict')
    print('TPS_API_INFO',info)
    named=info.get('named_endpoints',{}) if isinstance(info,dict) else {}
    endpoint=None
    for name,spec in named.items():
        if len(spec.get('parameters',[]))==2:
            endpoint=name; break
    if endpoint is None:
        endpoint='/predict'
    print('TPS_ENDPOINT',endpoint)

    # Gradio versions differ in Video serialization. Try the simple legacy payload first.
    errors=[]
    for drive_arg in (handle_file(str(DRIVE)), {'video':handle_file(str(DRIVE)),'subtitles':None}):
        try:
            out=c.predict(handle_file(str(REF)),drive_arg,api_name=endpoint)
            print('TPS_RAW_OUTPUT',out)
            p=extract_path(out)
            if not p: raise RuntimeError(f'No video path in output: {out!r}')
            shutil.copy2(Path(p),RESULT)
            print('TPS_PASS',RESULT,RESULT.stat().st_size)
            return
        except Exception as e:
            errors.append(repr(e)); print('TPS_ATTEMPT_FAIL',repr(e))
    raise RuntimeError(' | '.join(errors))

if __name__=='__main__': main()
