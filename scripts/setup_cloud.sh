#!/usr/bin/env bash
# Set up ManimGL for the A111 explainers in a Linux workspace (Claude's cloud container).
# Safe to re-run: it installs only what is missing, then renders a test frame.
#
#   bash scripts/setup_cloud.sh
#
# ManimGL is pinned to the commit the Windows PC uses, so a scene renders the same in
# both places. To move to a newer ManimGL, change MANIMGL_COMMIT here and on the PC
# (Documents\Manim\setup\Setup-Manim.ps1), then re-render an explainer to check it.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIMGL_COMMIT=e5298385edabb34a09cf63743c1a4ec983f1ab11   # ManimGL 1.7.2
VENV="${MANIM_VENV:-$HOME/.venvs/manim-gl}"

# 1. System packages: LaTeX and dvisvgm for Tex, Pango headers to build ManimPango,
#    Xvfb for the virtual display ManimGL draws into, ffmpeg to write the videos
PACKAGES=(
  texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-science
  texlive-fonts-recommended texlive-pictures lmodern tipa dvisvgm
  libpango1.0-dev pkg-config xvfb ffmpeg fonts-cmu
)
missing=()
for package in "${PACKAGES[@]}"; do
  dpkg -s "$package" >/dev/null 2>&1 || missing+=("$package")
done
if [ ${#missing[@]} -gt 0 ]; then
  echo "Installing ${missing[*]}"
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends "${missing[@]}" >/dev/null
fi

# 2. ManimGL in its own environment. setuptools stays below 81 because ManimGL still
#    imports pkg_resources, which setuptools 81 removes.
if ! "$VENV/bin/pip" freeze 2>/dev/null | grep -q "$MANIMGL_COMMIT"; then
  echo "Installing ManimGL $MANIMGL_COMMIT into $VENV (a few minutes)"
  [ -x "$VENV/bin/pip" ] || python3 -m venv "$VENV"
  "$VENV/bin/pip" uninstall -y -q manimgl >/dev/null 2>&1 || true
  "$VENV/bin/pip" install -q --disable-pip-version-check \
    "manimgl @ git+https://github.com/3b1b/manim.git@$MANIMGL_COMMIT" "setuptools<81"
fi

# 3. Test frame: Text in CMU Serif, Tex, and the notes' notation through NotesTex
out="$REPO/videos/setup-check"
rm -rf "$out"
mkdir -p "$out"
cd "$REPO"
PYTHONPATH="$REPO" xvfb-run -a "$VENV/bin/manimgl" --config_file "$REPO/custom_config.yml" \
  scripts/setup_check.py SetupCheck -s -w --video_dir "$out" > "$out/SetupCheck.log" 2>&1 || true
if [ -s "$out/SetupCheck.png" ]; then
  echo "Ready: ManimGL $("$VENV/bin/python" -c 'import importlib.metadata as m; print(m.version("manimgl"))') in $VENV"
  echo "Test frame: $out/SetupCheck.png"
else
  echo "The test frame failed; see $out/SetupCheck.log" >&2
  tail -20 "$out/SetupCheck.log" >&2
  exit 1
fi
