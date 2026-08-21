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
    # Tight portrait crop: keep head + shoulders and upscale for face motion fidelity.
    crop=im.crop((55,35,265,285)).resize((512,512),Image.Resampling.LANCZOS)
    crop.save(REF)
    print('PORTRAIT_OK',REF,crop.size)

def get_driver():
    src=hf_hub_download(repo_id='KlingTeam/LivePortrait',repo_type='space',filename='assets/examples/driving/d0.mp4')
    shutil.copy2(src,DRIVE)
    print('LIVEPORTRAIT_DRIVER_OK',DRIVE,DRIVE.stat().st_size)

def pick_endpoint(client):
    info=client.view_api(return_format='dict')
    print('API_INFO',info)
    named=info.get('named_endpoints',{}) if isinstance(info,dict) else {}
    # Animation endpoint has 5 inputs: source portrait, driving video, relative, crop, paste-back.
    for name,spec in named.items():
        params=spec.get('parameters',[]) if isinstance(spec,dict) else []
        if len(params)==5:
            return name
    for candidate in ('/gpu_wrapped_execute_video','/predict','/animate'):
        if candidate in named:
            return candidate
    raise RuntimeError(f'No LivePortrait animation endpoint found: {list(named)}')

def main():
    restore_and_crop(); get_driver()
    c=Client('KlingTeam/LivePortrait')
    endpoint=pick_endpoint(c)
    print('LIVEPORTRAIT_ENDPOINT',endpoint)
    out=c.predict(handle_file(str(REF)),handle_file(str(DRIVE)),True,True,True,api_name=endpoint)
    print('RAW_OUTPUT',out)
    candidates=[]
    if isinstance(out,str): candidates=[out]
    elif isinstance(out,(list,tuple)):
        for x in out:
            if isinstance(x,str): candidates.append(x)
            elif isinstance(x,dict) and x.get('path'): candidates.append(x['path'])
    if not candidates: raise RuntimeError(f'No video path in output: {out!r}')
    src=Path(candidates[0]); shutil.copy2(src,RESULT)
    print('LIVEPORTRAIT_PASS',RESULT,RESULT.stat().st_size)

if __name__=='__main__': main()
