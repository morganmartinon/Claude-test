#!/usr/bin/env python3
"""Monte un reel dont chaque coupe tombe sur un temps du morceau.

Usage : python3 tools/montage_beat.py MUSIQUE.wav SORTIE_AVEC_MUSIQUE.mp4 SORTIE_SANS_MUSIQUE.mp4 [BPM]

Prend les plans déjà découpés (SDR, 1080x1920, 30 fps) dans work/clips/ et applique,
plan par plan : zoom « punch » au début, tremblement, flash blanc, glitch RGB.
Puis étalonnage, fondu final et mixage de la musique (-12 LUFS).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "work", "clips")
TMP = os.path.join(ROOT, "work", "beat_segments")
os.makedirs(TMP, exist_ok=True)

music, out_music, out_silent = sys.argv[1], sys.argv[2], sys.argv[3]
BPM = float(sys.argv[4]) if len(sys.argv) > 4 else 100.0
BEAT = 60.0 / BPM

# (plan, début dans le plan en s, durée en temps, punch, tremblement px, glitch, flash)
TIMELINE = [
    (1, 0.0, 3, 0.10, 0, False, True),     # 0-3   ouverture : flash blanc
    (2, 0.0, 1, 0.14, 10, False, False),   # 3-4
    (3, 0.0, 2, 0.14, 8, False, True),     # 4-6
    (4, 0.0, 2, 0.12, 6, False, False),    # 6-8
    (5, 0.0, 2, 0.16, 14, True, True),     # 8-10  glitch
    (6, 0.0, 1, 0.14, 8, False, False),    # 10-11
    (7, 0.0, 1, 0.14, 8, False, False),    # 11-12
    (8, 0.0, 2, 0.14, 8, False, True),     # 12-14
    (6, 0.9, 1, 0.16, 10, False, False),   # 14-15
    (2, 0.9, 1, 0.20, 12, False, False),   # 15-16 temps de montée
    (4, 0.8, 2, 0.24, 18, True, True),     # 16-18 DROP : flash + glitch
    (3, 1.2, 1, 0.16, 10, False, False),   # 18-19
    (5, 1.3, 1, 0.16, 10, False, False),   # 19-20
    (8, 1.3, 1, 0.18, 12, True, True),     # 20-21
    (7, 0.7, 1, 0.16, 10, False, False),   # 21-22
    (6, 1.4, 1, 0.16, 10, False, False),   # 22-23
    (1, 1.2, 1, 0.20, 14, True, False),    # 23-24
    (9, 0.0, 4, 0.12, 0, False, True),     # 24-28 plan final + image figée
]
HOLD_LAST = 0.5   # image figée à la fin du dernier plan (le plan dure moins que 4 temps)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(" ".join(cmd))
        print(r.stderr[-1500:])
        sys.exit(1)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


segs = []
for i, (plan, off, beats, punch, shake, glitch, flash) in enumerate(TIMELINE):
    src = os.path.join(CLIPS, f"plan_{plan:02d}.mp4")
    dur = beats * BEAT
    last = i == len(TIMELINE) - 1
    avail = duration(src)
    need = dur - (HOLD_LAST if last else 0)
    off = max(0.0, min(off, avail - need - 0.04))
    z = f"(1.05+0.04*t/{dur:.3f}+{punch}*max(0,1-t/0.22))"
    vf = []
    if last:
        vf.append(f"tpad=stop_mode=clone:stop_duration={HOLD_LAST}")
    vf.append(f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame")
    vf.append(f"crop=1080:1920:x='(iw-1080)/2+{shake}*sin(t*85)*max(0,1-t/0.2)':"
              f"y='(ih-1920)/2+{shake * 0.6:.1f}*cos(t*97)*max(0,1-t/0.2)'")
    if glitch:
        vf.append("rgbashift=rh=-16:bh=16:enable='lt(t,0.2)'")
    if flash:
        vf.append("fade=t=in:st=0:d=0.16:color=white")
    vf.append("format=yuv420p")
    path = os.path.join(TMP, f"seg_{i:02d}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{off:.3f}", "-t", f"{dur:.3f}", "-i", src, "-an",
         "-vf", ",".join(vf), "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", path])
    segs.append(path)
    print(f"plan {plan} segment {i + 1}/{len(TIMELINE)} ok")

lst = os.path.join(TMP, "list.txt")
with open(lst, "w") as f:
    for p in segs:
        f.write(f"file '{p}'\n")

total = sum(b for _, _, b, *_ in TIMELINE) * BEAT
concat = os.path.join(TMP, "concat.mp4")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat])

grade = ("colorbalance=bs=-0.05:bm=-0.08:bh=-0.04:gm=0.03,eq=contrast=1.10:saturation=1.12,"
         "unsharp=5:5:0.5:5:5:0,vignette=angle=0.35,"
         f"fade=t=out:st={total - 0.5:.2f}:d=0.5,format=yuv420p")
graded = os.path.join(TMP, "graded.mp4")
run(["ffmpeg", "-v", "error", "-y", "-i", concat, "-an", "-vf", grade, "-c:v", "libx264", "-crf", "18",
     "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", graded])

run(["ffmpeg", "-v", "error", "-y", "-i", graded, "-i", music, "-t", f"{total:.3f}", "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-af", f"afade=t=in:d=0.012,afade=t=out:st={total - 1.0:.2f}:d=1.0,"
     "loudnorm=I=-12:TP=-2:LRA=7,alimiter=limit=0.7:level=0",
     "-ar", "44100", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_music])
run(["ffmpeg", "-v", "error", "-y", "-i", graded, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
     "-t", f"{total:.3f}", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
     "-movflags", "+faststart", out_silent])
print(f"terminé : {total:.1f} s, {len(TIMELINE)} plans")
