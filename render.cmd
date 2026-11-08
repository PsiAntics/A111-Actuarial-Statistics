@echo off
rem Render an A111 explainer on this PC, with the ManimGL environment that
rem Documents\Manim\setup made. Run it from this folder:
rem
rem   render explainers\01-credibility\main.py WhoseNumber          live window
rem   render explainers\01-credibility\main.py WhoseNumber -w       1080p30 video
rem   render explainers\01-credibility\main.py WhoseNumber -w -l    quick 480p video
rem   render explainers\01-credibility\main.py -a -w                every scene, in order
rem
rem Videos go to videos\<explainer>\ in this folder, which git ignores.
setlocal
set "REPO=%~dp0"
set "REPO=%REPO:~0,-1%"
for %%I in ("%~dp1.") do set "NAME=%%~nxI"
set "PYTHONPATH=%REPO%"
"%USERPROFILE%\.venvs\manim-gl\Scripts\manimgl.exe" --config_file "%REPO%\custom_config.yml" --video_dir "%REPO%\videos\%NAME%" %*
