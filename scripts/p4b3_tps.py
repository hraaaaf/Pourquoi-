from pathlib import Path
import base64, hashlib, shutil, urllib.request
from PIL import Image
from gradio_client import Client

SPACE='CVPR/Image-Animation-using-Thin-Plate-Spline-Motion-Model'
OUT=Path('artifacts/p4b3-tps'); OUT.mkdir(parents=True,exist_ok=True)
REF_RAW=OUT/'reference.jpg'; REF=OUT/'portrait.png'; DRIVE=OUT/'driving.mp4'; RESULT=OUT/'tps-motion.mp4'
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'

def restore_portrait():
    payload=''.join(Path(f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    REF_RAW.write_bytes(base64.b64decode(payload,validate=True))
    raw=REF_RAW.read_bytes(); assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
    im=Image.open(REF_RAW).convert('RGB')
    crop=im.crop((45,25,275,255)).resize((256,256),Image.Resampling.LANCZOS)
    crop.save(REF)
    print('TPS_PORTRAIT_OK',REF,crop.size)

def get_driver():
    url='https://raw.githubusercontent.com/yoyo-nb/Thin-Plate-Spline-Motion-Model/main/assets/driving.mp4'
    urllib.request.urlretrieve(url,DRIVE)
    print('TPS_DRIVER_OK',DRIVE,DRIVE.stat().st_size)

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

def main():
    restore_portrait(); get_driver()
    c=Client(SPACE)
    print('TPS_ENDPOINT fn_index=2')
    out=c.predict(str(REF),str(DRIVE),fn_index=2)
    print('TPS_RAW_OUTPUT',out)
    p=extract_path(out)
    if not p: raise RuntimeError(f'No video path in output: {out!r}')
    shutil.copy2(Path(p),RESULT)
    print('TPS_PASS',RESULT,RESULT.stat().st_size)

if __name__=='__main__': main()
