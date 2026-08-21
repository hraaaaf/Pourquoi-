from pathlib import Path
import base64, hashlib, shutil
from PIL import Image
from gradio_client import Client, handle_file
from huggingface_hub import hf_hub_download

OUT=Path('artifacts/p4b3'); OUT.mkdir(parents=True,exist_ok=True)
REF=OUT/'reference.jpg'; DRIVE=OUT/'driving-real.mp4'; RESULT=OUT/'zerogpu-real-driver.mp4'
W,H=320,480
EXPECTED_SHA='b22805f30e0f88e66ea1a5b56b60f51c11b837fc5439ca527ca6a8d1ed6be064'

def restore_ref():
    payload=''.join(Path(f'assets/p4b3/character.{i}.b64').read_text().strip() for i in range(7))
    REF.write_bytes(base64.b64decode(payload,validate=True))
    raw=REF.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    with Image.open(REF) as im:
        im.load(); size=im.size
    assert size==(W,H),size
    assert sha==EXPECTED_SHA,(sha,len(raw))
    print(f'CHARACTER_OK bytes={len(raw)} sha256={sha} size={size}')

def get_real_driver():
    src=hf_hub_download(
        repo_id='hugging-apps/wan2-2-animate-2-14b',
        repo_type='space',
        filename='examples/animate_driving.mp4'
    )
    shutil.copy2(src,DRIVE)
    print(f'REAL_DRIVER_OK={DRIVE} bytes={DRIVE.stat().st_size}')

def main():
    restore_ref(); get_real_driver()
    c=Client('hugging-apps/wan2-2-animate-2-14b')
    o=c.predict(
        handle_file(str(REF)),
        handle_file(str(DRIVE)),
        'same cheerful young cartoon boy, red hoodie, blue jeans, red sneakers; preserve face, hair, body proportions and clothes; transfer the natural body motion and expression from the driving video; stable full-body cartoon animation; clean neutral background',
        2.0,480,320,6,1.0,5.0,
        'distorted face, identity drift, extra limbs, extra fingers, duplicated body parts, warped hands, deformed body, flicker, blur, noise, text, subtitles, watermark',
        23,
        api_name='/animate'
    )
    src=Path(o if isinstance(o,str) else o[0])
    shutil.copy2(src,RESULT)
    print(f'WAN_REAL_DRIVER_PASS={RESULT}')

if __name__=='__main__':
    main()
