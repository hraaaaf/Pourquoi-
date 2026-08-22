from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
IN = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'input' / 'P4-B6-full-pilot-75s-v4.mp4'
OUT_DIR = ROOT / 'artifacts' / 'p4b6-quality-1080p'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / 'P4-B6-full-pilot-75s-v4-1080p-HQ.mp4'

if not IN.exists():
    raise FileNotFoundError(IN)

vf = (
    'scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int,'
    'unsharp=5:5:0.55:3:3:0.20'
)

cmd = [
    'ffmpeg','-y','-loglevel','error',
    '-i',str(IN),
    '-vf',vf,
    '-c:v','libx264','-preset','slow','-tune','animation','-crf','12',
    '-profile:v','high','-pix_fmt','yuv420p',
    '-c:a','copy','-movflags','+faststart',
    str(OUT),
]
subprocess.run(cmd, check=True)

probe = subprocess.check_output([
    'ffprobe','-v','error',
    '-show_entries','stream=codec_name,width,height,r_frame_rate',
    '-show_entries','format=duration,size,bit_rate',
    '-of','default=nw=1',str(OUT)
], text=True)
print(probe)
print('P4_B6_QUALITY_1080P_PASS', OUT, OUT.stat().st_size)
