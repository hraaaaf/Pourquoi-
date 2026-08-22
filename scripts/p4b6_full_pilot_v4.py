from pathlib import Path
import p4b6_full_pilot_v3 as v3

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'p4b6-full-pilot-v4'; FRAMES=OUT/'frames'
OUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True)

# Re-point all shared render state to the v4 artifact directory.
v3.OUT=OUT; v3.FRAMES=FRAMES
v3.v1.OUT=OUT
v3.b.OUT=OUT; v3.b.FRAMES=FRAMES
v3.v5.OUT=OUT; v3.v5.FRAMES=FRAMES
v3.b5.OUT=OUT; v3.b5.FRAMES=FRAMES

_original_sunset=v3.scene_sunset

def clean_sunset(t):
    if t<7.3:
        return _original_sunset(t)
    # Final beat: use the safe wide composition from v1. It already contains
    # the red/orange conclusion; no second label, no zoom-induced clipping.
    bg=v3.v1.scene_sunset(t)
    return v3.v2.impact(bg,t,[7.3],(255,145,60),210)

v3.scene_sunset=clean_sunset

if __name__=='__main__':
    v3.main()
    src=OUT/'P4-B6-full-pilot-75s-v3.mp4'
    dst=OUT/'P4-B6-full-pilot-75s-v4.mp4'
    src.replace(dst)
    print('P4_B6_FULL_PILOT_V4_PASS',dst,dst.stat().st_size)
