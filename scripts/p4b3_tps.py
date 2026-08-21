from pathlib import Path
import shutil, urllib.request
from gradio_client import Client

SPACE='CVPR/Image-Animation-using-Thin-Plate-Spline-Motion-Model'
OUT=Path('artifacts/p4b3-tps'); OUT.mkdir(parents=True,exist_ok=True)
REF=OUT/'stock-source.png'; DRIVE=OUT/'stock-driving.mp4'; RESULT=OUT/'tps-motion.mp4'
BASE='https://raw.githubusercontent.com/yoyo-nb/Thin-Plate-Spline-Motion-Model/main/assets'

def get_stock_assets():
    urllib.request.urlretrieve(f'{BASE}/source.png',REF)
    urllib.request.urlretrieve(f'{BASE}/driving.mp4',DRIVE)
    print('TPS_STOCK_ASSETS_OK',REF.stat().st_size,DRIVE.stat().st_size)

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
    get_stock_assets()
    c=Client(SPACE)
    print('TPS_HEALTH_ENDPOINT fn_index=2')
    out=c.predict(str(REF),str(DRIVE),fn_index=2)
    print('TPS_HEALTH_RAW_OUTPUT',out)
    p=extract_path(out)
    if not p: raise RuntimeError(f'No video path in stock-assets output: {out!r}')
    shutil.copy2(Path(p),RESULT)
    print('TPS_STOCK_HEALTH_PASS',RESULT,RESULT.stat().st_size)

if __name__=='__main__': main()
