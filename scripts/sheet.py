"""Frame sheet: frames of a clip side by side, two per row, each stamped with its time.

usage: python3 scripts/sheet.py clip.mp4 sheet.png [t1,t2,...]

With no times it takes 8 frames spread evenly through the clip. Open the PNG and look
for overlaps, clipped labels, text that is too small, and numbers that look wrong.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

clip, out = sys.argv[1], sys.argv[2]
if len(sys.argv) > 3:
    times = [float(t) for t in sys.argv[3].split(",")]
else:
    duration = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip],
        capture_output=True, text=True, check=True,
    ).stdout)
    times = [duration * (i + 0.5) / 8 for i in range(8)]

frames = []
with tempfile.TemporaryDirectory() as tmp:
    for t in times:
        path = Path(tmp, f"{t:.2f}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", clip,
                        "-frames:v", "1", str(path)], check=True)
        frame = Image.open(path).convert("RGB").resize((960, 540))
        ImageDraw.Draw(frame).text((8, 8), f"{t:.1f}s", fill=(255, 80, 80))
        frames.append(frame)

rows = (len(frames) + 1) // 2
sheet = Image.new("RGB", (2 * 960 + 8, rows * 548 - 8), (70, 70, 70))
for i, frame in enumerate(frames):
    sheet.paste(frame, ((i % 2) * 968, (i // 2) * 548))
sheet.save(out)
print(f"{out}: {len(frames)} frames at " + ", ".join(f"{t:.1f}s" for t in times))
