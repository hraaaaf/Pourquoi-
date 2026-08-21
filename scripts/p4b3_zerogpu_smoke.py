from pathlib import Path
import base64
import math
import shutil
import subprocess
from PIL import Image, ImageDraw
from gradio_client import Client, handle_file

OUT = Path('artifacts/p4b3')
OUT.mkdir(parents=True, exist_ok=True)
REF = OUT / 'reference.jpg'
DRIVE = OUT / 'driving.mp4'
RESULT = OUT / 'zerogpu-smoke.mp4'

W, H = 384, 480
FPS = 24
SECONDS = 1.5


def restore_reference():
    parts = [
        Path('assets/p4b3/character.part0.b64'),
        Path('assets/p4b3/character.part1.b64'),
    ]
    payload = ''.join(p.read_text().strip() for p in parts)
    REF.write_bytes(base64.b64decode(payload))
    with Image.open(REF) as im:
        print(f'reference={im.size[0]}x{im.size[1]}')


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def pose(t):
    keys = [
        (0.00, -45, 295, 20, 10, 0.0),
        (0.30, 190, 290, 25, 15, 0.2),
        (0.55, 195, 286, 35, 20, 0.5),
        (0.80, 198, 282, -35, -10, 0.75),
        (1.15, 200, 278, -72, -6, 1.0),
        (1.35, 200, 268, -82, -3, 1.0),
        (1.50, 200, 278, -72, -6, 1.0),
    ]
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = smooth((t - a[0]) / (b[0] - a[0]))
            return tuple(lerp(a[i], b[i], u) for i in range(1, len(a)))
    return keys[-1][1:]


def endpoint(p, length, deg):
    r = math.radians(deg)
    return p[0] + length * math.cos(r), p[1] + length * math.sin(r)


def driver_frame(t):
    cx, cy, right_angle, left_angle, expr = pose(t)
    im = Image.new('RGB', (W, H), (238, 240, 244))
    d = ImageDraw.Draw(im)
    d.ellipse((cx - 60, 432, cx + 60, 450), fill=(210, 213, 220))
    d.rounded_rectangle((cx - 42, cy - 55, cx + 42, cy + 70), radius=20, fill=(218, 45, 38))
    d.ellipse((cx - 38, cy - 142, cx + 38, cy - 66), fill=(241, 184, 139))
    d.pieslice((cx - 40, cy - 150, cx + 40, cy - 78), 180, 360, fill=(69, 42, 30))
    ey = cy - 108 - 5 * expr
    for ex in (-14, 14):
        d.ellipse((cx + ex - 5, ey - 4, cx + ex + 5, ey + 6), fill='white')
        d.ellipse((cx + ex - 1, ey - 2, cx + ex + 4, ey + 4), fill=(30, 25, 22))
    if expr < 0.45:
        d.arc((cx - 12, cy - 90, cx + 12, cy - 70), 10, 170, fill=(100, 45, 40), width=3)
    else:
        d.ellipse((cx - 12, cy - 90, cx + 12, cy - 68), fill=(90, 35, 35))
    rs = (cx + 38, cy - 35)
    re = endpoint(rs, 68, right_angle)
    rh = endpoint(re, 62, right_angle - 8)
    ls = (cx - 38, cy - 35)
    le = endpoint(ls, 62, 180 - left_angle)
    lh = endpoint(le, 58, 180 - left_angle + 8)
    for a, b in ((rs, re), (re, rh), (ls, le), (le, lh)):
        d.line((a[0], a[1], b[0], b[1]), fill=(226, 70, 55), width=17)
    for p in (re, rh, le, lh):
        d.ellipse((p[0]-8, p[1]-8, p[0]+8, p[1]+8), fill=(241, 184, 139))
    if t > 0.75:
        finger = endpoint(rh, 27, right_angle - 25)
        d.line((rh[0], rh[1], finger[0], finger[1]), fill=(241, 184, 139), width=7)
    bounce = 10 * max(0.0, 1.0 - abs(t - 1.35) / 0.20)
    lk = (cx - 18, cy + 145 - bounce)
    rk = (cx + 22, cy + 145 - bounce * 0.7)
    lf = (cx - 28, 425)
    rf = (cx + 34, 425)
    for a, b in (((cx-20, cy+62), lk), (lk, lf), ((cx+20, cy+62), rk), (rk, rf)):
        d.line((a[0], a[1], b[0], b[1]), fill=(48, 68, 112), width=21)
    d.ellipse((lf[0]-18, lf[1]-5, lf[0]+22, lf[1]+10), fill=(215, 65, 55))
    d.ellipse((rf[0]-18, rf[1]-5, rf[0]+22, rf[1]+10), fill=(215, 65, 55))
    return im


def make_driver():
    frame_dir = OUT / 'driver_frames'
    frame_dir.mkdir(exist_ok=True)
    for i in range(int(FPS * SECONDS)):
        driver_frame(i / FPS).save(frame_dir / f'{i:04d}.png')
    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS),
        '-i', str(frame_dir / '%04d.png'), '-c:v', 'libx264', '-pix_fmt',
        'yuv420p', '-crf', '21', '-r', str(FPS), str(DRIVE)
    ], check=True)


def main():
    restore_reference()
    make_driver()
    client = Client('hugging-apps/wan2-2-animate-2-14b')
    output = client.predict(
        handle_file(str(REF)),
        handle_file(str(DRIVE)),
        'same cheerful young cartoon boy, red hoodie, blue jeans and red sneakers, preserve face and clothing identity, he enters frame, looks upward with curiosity, raises one arm and points upward with one finger, smooth natural full-body animation, clean neutral background',
        1.5, 480, 384, 4, 1.0, 5.0,
        'distorted face, identity drift, extra limbs, extra fingers, duplicated body parts, warped hands, text, subtitles, watermark, static frame, flicker, blur',
        23,
        api_name='/animate',
    )
    src = Path(output if isinstance(output, str) else output[0])
    shutil.copy2(src, RESULT)
    print(f'P4-B3 REAL CHARACTER PASS: {RESULT}')


if __name__ == '__main__':
    main()
