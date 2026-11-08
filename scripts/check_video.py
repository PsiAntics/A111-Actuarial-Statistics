"""Check rendered clips before they go to Sabelo.

usage: python3 scripts/check_video.py clip.mp4 [clip2.mp4 ...] [--min-margin 0.4]

For each clip:
  stream    resolution, frame rate and duration (ffprobe)
  decode    any error while decoding every frame (ffmpeg -v error -f null)
  margins   the closest approach of anything on screen to each edge of the frame, in
            Manim units, with the time it happened (2 samples a second; content is any
            pixel more than 40 away from the black background in some channel)

A margin under --min-margin is flagged. Fix it unless the frame at that time shows an
entrance or exit animation passing the edge. Exits with status 1 when a clip fails to
decode or is not 1920x1080 at 30 fps (pass --preview to accept 854x480 at 15 fps).
"""
import argparse
import json
import subprocess

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("clips", nargs="+")
parser.add_argument("--min-margin", type=float, default=0.4)
parser.add_argument("--preview", action="store_true")
args = parser.parse_args()

BACKGROUND = np.array([0, 0, 0])
FRAME_HEIGHT = 8.0  # Manim units
expected = ((854, 480), 15) if args.preview else ((1920, 1080), 30)
failed = False

for clip in args.clips:
    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate:format=duration", "-of", "json", clip],
        capture_output=True, text=True, check=True,
    ).stdout)
    stream = probe["streams"][0]
    size = (stream["width"], stream["height"])
    num, den = map(int, stream["r_frame_rate"].split("/"))
    fps = num / den
    duration = float(probe["format"]["duration"])

    errors = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-f", "null", "-"],
                            capture_output=True, text=True).stderr.strip()

    # One frame at a time, so a long video doesn't fill the memory
    reader = subprocess.Popen(["ffmpeg", "-v", "error", "-i", clip, "-vf", "fps=2,scale=960:540",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frame_bytes = 540 * 960 * 3
    units_per_pixel = FRAME_HEIGHT / 540
    worst = dict(left=np.inf, right=np.inf, top=np.inf, bottom=np.inf)
    when = dict.fromkeys(worst, None)
    i = -1
    while len(data := reader.stdout.read(frame_bytes)) == frame_bytes:
        i += 1
        frame = np.frombuffer(data, np.uint8).reshape(540, 960, 3).astype(np.int16)
        ys, xs = np.nonzero(np.abs(frame - BACKGROUND).max(axis=2) > 40)
        if len(xs) == 0:
            continue
        gaps = dict(left=xs.min(), right=959 - xs.max(), top=ys.min(), bottom=539 - ys.max())
        for side, gap in gaps.items():
            if gap < worst[side]:
                worst[side], when[side] = gap, i / 2
    reader.wait()

    bad_stream = size != expected[0] or abs(fps - expected[1]) > 0.01
    failed |= bad_stream or bool(errors)
    print(f"{clip}")
    print(f"  stream   {size[0]}x{size[1]} at {fps:g} fps, {int(duration // 60)}:{duration % 60:04.1f}"
          + ("   <-- expected %dx%d at %d fps" % (*expected[0], expected[1]) if bad_stream else ""))
    print(f"  decode   {'clean' if not errors else 'ERRORS: ' + errors.splitlines()[0]}")
    margins = []
    for side in worst:
        if when[side] is None:
            margins.append(f"{side} -")
            continue
        margin = worst[side] * units_per_pixel
        flag = " <--" if margin < args.min_margin else ""
        margins.append(f"{side} {margin:.2f} at {when[side]:.1f}s{flag}")
    print("  margins  " + ", ".join(margins))

raise SystemExit(1 if failed else 0)
