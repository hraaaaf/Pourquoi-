from pathlib import Path
import base64, hashlib, shutil
from PIL import Image
from gradio_client import Client, handle_file

SPACE='fffiloni/expression-editor'
OUT=Path('artifacts/p4b3-expression'); OUT.mkdir(parents=True,exist_ok=True)
REF_RAW=OUT/'reference.jpg'; REF=OUT/'portrait.png'; RESULT=OUT/'surprise-up.png'
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

def main():
    restore_portrait()
    c=Client(SPACE)
    info=c.view_api(return_format='dict')
    named=info.get('named_endpoints',{}) if isinstance(info,dict) else {}
    endpoint=None
    for name,spec in named.items():
        if len(spec.get('parameters',[]))==17:
            endpoint=name; break
    if endpoint is None:
        raise RuntimeError(f'No 17-input expression endpoint: {list(named)}')
    print('EXPRESSION_ENDPOINT',endpoint)
    out=c.predict(
        handle_file(str(REF)),
        -8, 0, 0,
        0, 8, 0, 0, -8,
        35, 0, 0, 0.22,
        1, 1, 'All', 1.7,
        api_name=endpoint,
    )
    print('EXPRESSION_RAW_OUTPUT',out)
    p=extract_path(out)
    if not p: raise RuntimeError(f'No image path in output: {out!r}')
    shutil.copy2(Path(p),RESULT)
    with Image.open(RESULT) as im:
        im.load(); print('EXPRESSION_PASS',RESULT,im.size,RESULT.stat().st_size)

if __name__=='__main__': main()
