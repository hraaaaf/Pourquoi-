from pathlib import Path
import math
import shutil
import subprocess
from PIL import Image, ImageDraw
from gradio_client import Client, handle_file

OUT = Path('artifacts/p4b3')
OUT.mkdir(parents=True, exist_ok=True)
REF = OUT / 'reference.png'
DRIVE = OUT / 'driving.mp4'
RESULT = OUT / 'zerogpu-smoke.mp4'

W, H = 384, 480


def draw_character(path: Path):
    im = Image.new('RGB', (W, H), (105, 190, 245))
    d = ImageDraw.Draw(im)
    d.ellipse((15, 15, 90, 90), fill=(255, 240, 160))
    d.rectangle((0, 360, W, H), fill=(90, 180, 80))
    # legs
    d.line((175, 350, 155, 440), fill=(40, 70, 120), width=28)
    d.line((215, 350, 240, 440), fill=(40, 70, 120), width=28)
    # red hoodie torso
    d.rounded_rectangle((120, 180, 270, 360), radius=38, fill=(220, 40, 35))
    # head + hair
    d.ellipse((130, 75, 260, 210), fill=(248, 176, 120))
    d.polygon([(130,120),(145,78),(180,60),(220,66),(260,105),(235,90),(215,112),(190,85),(165,115)], fill=(75,45,30))
    # eyes + smile
    d.ellipse((160,125,180,150), fill='white'); d.ellipse((210,125,230,150), fill='white')
    d.ellipse((167,132,176,143), fill=(40,25,20)); d.ellipse((217,132,226,143), fill=(40,25,20))
    d.arc((175,145,220,185), 10, 170, fill=(90,30,25), width=5)
    # pointing arm
    d.line((245,220,320,125), fill=(220,40,35), width=34)
    d.ellipse((306,105,334,135), fill=(248,176,120))
    d.line((322,119,330,75), fill=(248,176,120), width=12)
    # other arm
    d.line((130,225,75,280), fill=(220,40,35), width=34)
    im.save(path)


def draw_driver_frame(t: float) -> Image.Image:
    im = Image.new('RGB', (W, H), (30, 45, 80))
    d = ImageDraw.Draw(im)
    cx = 192 + 10 * math.sin(t * math.pi * 2)
    cy = 235 + 8 * math.sin(t * math.pi * 4)
    # head
    d.ellipse((cx-45, cy-145, cx+45, cy-55), fill=(230,180,140))
    # torso
    d.rounded_rectangle((cx-55, cy-55, cx+55, cy+85), radius=24, fill=(220,40,35))
    # legs
    d.line((cx-25, cy+80, cx-50, cy+180), fill='white', width=18)
    d.line((cx+25, cy+80, cx+55, cy+180), fill='white', width=18)
    # left arm swings; right arm raises and points
    a = -1.2 + 0.65 * math.sin(t * math.pi)
    x2 = cx + math.cos(a) * 115; y2 = cy-25 + math.sin(a) * 115
    d.line((cx+35, cy-30, x2, y2), fill=(245,180,140), width=18)
    d.line((x2, y2, x2+8, y2-45), fill=(245,180,140), width=10)
    b = 2.6 + 0.4 * math.sin(t * math.pi * 2)
    lx = cx + math.cos(b) * 95; ly = cy-20 + math.sin(b) * 95
    d.line((cx-35, cy-25, lx, ly), fill=(245,180,140), width=18)
    return im


def make_driver():
    frame_dir = OUT / 'driver_frames'
    frame_dir.mkdir(exist_ok=True)
    fps = 24
    seconds = 2.0
    for i in range(int(fps * seconds)):
        draw_driver_frame(i/(fps*seconds)).save(frame_dir / f'{i:04d}.png')
    subprocess.run([
        'ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',str(frame_dir/'%04d.png'),
        '-c:v','libx264','-pix_fmt','yuv420p','-crf','24',str(DRIVE)
    ], check=True)


def main():
    draw_character(REF)
    make_driver()
    client = Client('hugging-apps/wan2-2-animate-2-14b')
    output = client.predict(
        handle_file(str(REF)),
        handle_file(str(DRIVE)),
        'cheerful 2D educational cartoon boy in a red hoodie, blue sky background, curious energetic expression, smooth natural character motion',
        2.0, 480, 384, 6, 1.0, 5.0,
        'static frame, blurry details, distorted face, extra limbs, extra fingers, text, subtitles, watermark',
        0,
        api_name='/animate',
    )
    src = Path(output if isinstance(output, str) else output[0])
    shutil.copy2(src, RESULT)
    print(f'P4-B3 ZERO-GPU PASS: {RESULT}')


if __name__ == '__main__':
    main()
