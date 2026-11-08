#!/usr/bin/env bash
# Render an explainer's scenes with ManimGL, two at a time (the cloud workspace has 2 CPUs).
#
#   scripts/render.sh preview explainers/02-mle                 every scene at 480p15
#   scripts/render.sh preview explainers/02-mle Intro Payoff    just these scenes
#   scripts/render.sh frame explainers/02-mle Intro -- -n 0,7   the frame after animation 7, as a
#                                                               1080p PNG (without -n: the last
#                                                               frame, often blank after a fade)
#   scripts/render.sh final explainers/02-mle                   check.py, every scene at 1080p30,
#                                                               then one joined MP4
# Arguments after -- go to manimgl, e.g. -- -n 3,7 previews only animations 3 to 7.
#
# Output goes to videos/<explainer>/<mode>/ (git ignores videos/), one log per scene. At the
# end it prints each scene's result, render time and ManimGL warnings, then the checks from
# scripts/check_video.py. Once every scene has a final render, they are joined in playing
# order into videos/<explainer>/A111-<explainer>.mp4.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${MANIM_VENV:-$HOME/.venvs/manim-gl}"
PY="$VENV/bin/python"
JOBS="${JOBS:-2}"

usage() { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
[ $# -ge 2 ] || usage
mode=$1
dir="$(cd "$2" 2>/dev/null && pwd)" || { echo "No folder $2" >&2; exit 2; }
shift 2
name="$(basename "$dir")"
file="$dir/main.py"
[ -f "$file" ] || { echo "No main.py in $dir" >&2; exit 2; }

scenes=()
extra=()
while [ $# -gt 0 ]; do
  if [ "$1" = "--" ]; then shift; extra=("$@"); break; fi
  scenes+=("$1"); shift
done
[ "$mode" = final ] && [ ${#extra[@]} -gt 0 ] && { echo "A final render takes whole scenes: no -- arguments" >&2; exit 2; }
mapfile -t all_scenes < <("$PY" "$REPO/scripts/scenes.py" "$file")
[ ${#scenes[@]} -gt 0 ] || scenes=("${all_scenes[@]}")

case $mode in
  preview) flags=(-w -l --fps 15); ext=mp4 ;;
  frame) flags=(-w -s --hd); ext=png ;;
  final) flags=(-w --hd); ext=mp4 ;;
  *) usage ;;
esac
out="$REPO/videos/$name/$mode"
mkdir -p "$out"

# Every number on screen comes from main.py; check.py prints them and checks the maths
if [ "$mode" = final ] && [ -f "$dir/check.py" ]; then
  echo "Numbers: $dir/check.py"
  (cd "$REPO" && PYTHONPATH="$REPO" xvfb-run -a "$PY" -W ignore "$dir/check.py") \
    || { echo "check.py failed; fix the numbers before the final render" >&2; exit 1; }
  echo
fi

render() {
  local scene=$1
  local start
  start=$(date +%s)
  rm -f "$out/$scene.$ext"
  (cd "$REPO" && COLUMNS=400 PYTHONPATH="$REPO" xvfb-run -a "$VENV/bin/manimgl" \
    --config_file "$REPO/custom_config.yml" "$file" "$scene" "${flags[@]}" \
    --video_dir "$out" --file_name "$scene" "${extra[@]}" > "$out/$scene.log" 2>&1)
  echo "$? $(( $(date +%s) - start ))" > "$out/$scene.status"
}

echo "Rendering ${#scenes[@]} scene(s) of $name ($mode) into $out"
for scene in "${scenes[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  render "$scene" &
  sleep 2  # xvfb-run -a picks a free display; two starting at once can pick the same one
done
wait

failed=0
printf "\n%-26s %-7s %6s  %s\n" Scene Result Time Warnings
for scene in "${scenes[@]}"; do
  read -r code secs < "$out/$scene.status"
  result=ok
  if [ "$code" != 0 ] || [ ! -s "$out/$scene.$ext" ] || grep -q "Traceback" "$out/$scene.log"; then
    result=FAILED
    failed=1
  fi
  warnings=$(tr '\r' '\n' < "$out/$scene.log" | grep -E "WARNING|does not match" | grep -v SyntaxWarning \
    | sed -E 's/\x1b\[[0-9;]*m//g; s/^\[[0-9:]+\] +//; s/ +[a-z_]+\.py:[0-9]+ *$//' | sort | uniq | head -5)
  printf "%-26s %-7s %5ss  %s\n" "$scene" "$result" "$secs" "$(echo "$warnings" | head -1)"
  echo "$warnings" | tail -n +2 | sed 's/^/                                            /'
  if [ "$result" = FAILED ]; then
    echo "  last lines of $out/$scene.log:"
    tr '\r' '\n' < "$out/$scene.log" | grep -v "^\s*$" | tail -12 | sed 's/^/    /'
  fi
done
[ $failed = 0 ] || exit 1
[ "$ext" = mp4 ] || exit 0

echo
check_flags=()
[ "$mode" = preview ] && check_flags=(--preview)
clips=()
for scene in "${scenes[@]}"; do clips+=("$out/$scene.mp4"); done
"$PY" "$REPO/scripts/check_video.py" "${check_flags[@]}" "${clips[@]}" || failed=1

# Final: join the scenes in playing order into one video once every scene has a final
# render (so after fixing one scene, re-render just that one and it is joined with the rest)
if [ "$mode" = final ] && [ $failed = 0 ]; then
  missing=()
  for scene in "${all_scenes[@]}"; do [ -s "$out/$scene.mp4" ] || missing+=("$scene"); done
  if [ ${#missing[@]} -gt 0 ]; then
    echo "Not joined yet: no final render of ${missing[*]}"
  else
    joined="$REPO/videos/$name/A111-$name.mp4"
    for scene in "${all_scenes[@]}"; do echo "file '$out/$scene.mp4'"; done > "$out/concat.txt"
    ffmpeg -v error -y -f concat -safe 0 -i "$out/concat.txt" -c copy "$joined"
    echo
    [ ${#scenes[@]} -lt ${#all_scenes[@]} ] && echo "Joined with the earlier final renders of the other scenes"
    "$PY" "$REPO/scripts/check_video.py" "$joined" || failed=1
  fi
fi
exit $failed
