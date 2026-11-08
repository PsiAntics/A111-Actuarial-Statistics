# CLAUDE.md

This repository holds the code of Sabelo's explainer videos for **ASSA A111 Actuarial Statistics**, the South African subject that follows the IFoA CS1 syllabus (ActEd's CS1 Combined Materials Pack covers it). Each explainer is a few minutes of ManimGL animation in Grant Sanderson's 3Blue1Brown style that makes one syllabus idea click. Sabelo asks for them in a Claude Project that holds his CMP; you plan, build, check and render them in the cloud workspace, send him the video in the chat, and push the code here so he can follow it on GitHub and render it on his PC.

**The repository is public.** Nothing from the CMP or the Core Reading goes in it (see Copyright).

## At the start of a chat

1. Attach and clone this repository (the project instructions say how), or `git pull` if the clone is older than the chat.
2. Run `bash scripts/setup_cloud.sh` in the background. It installs what's missing (LaTeX, dvisvgm, ManimGL in `~/.venvs/manim-gl`, pinned to the commit on Sabelo's PC) and renders a test frame. Several minutes in a fresh workspace, seconds after that.
3. While it runs, find the topic in the CMP. If the CMP chapters table in `syllabus.md` is still empty, fill it in from the CMP's contents (chapter numbers, titles in your own words, syllabus areas) and push it.

## What an explainer is

- **One big idea, explored properly:** what it is, why it's true, two or three examples that build on each other, the trap students fall into, and where it's used later. Bigger topics become a numbered series (02a, 02b).
- **6 to 8 minutes** by default, up to 10 when the idea needs it, and shorter only when Sabelo asks: 10 to 15 scenes in three or four acts, one `InteractiveScene` per beat. Each act opens with a short title on screen, so the video has chapters.
- **No narration.** Short on-screen words carry the story, so the extra length goes into animation (more worked steps, more examples, more "Predict:" pauses), not into more text to read.
- **Grant's arc:** open on a concrete question or puzzle, build intuition with a specific example and pictures, pause on a "Predict:" prompt before each key reveal, derive the general result from the picture, then a summary card with the boxed result and a recall question whose answer appears after a pause.
- **Exam-shaped:** the CMP's definitions, notation and parametrisations, and a worked example that feels like an exam question, with your own numbers.

## Workflow

1. **Brief.** From the request and the CMP: the chapter and syllabus objectives, the one idea in a sentence, what usually confuses students about it (that's where the visuals go), and the worked example with its parameters. Ask Sabelo only what you can't settle yourself.
2. **Storyboard.** Take the next free number and create `explainers/NN-slug/README.md` from the template at the end of this file: the beats with timings, what moves and the words on screen. Send Sabelo the storyboard and wait for his go-ahead; he may change beats. If he isn't around, say what you assumed and carry on. Commit and push.
3. **Build** `main.py` in Grant's style (below). Every number shown on screen comes from constants and functions at the top of the file. Write `check.py` beside it: it imports those, recomputes every number the scenes show, checks the maths (closed forms against numerical sums, posteriors that integrate to 1) and prints a table. See `explainers/01-credibility` for both.
4. **Preview:** `scripts/render.sh preview explainers/NN-slug`. Read its summary: failed scenes, ManimGL warnings, and the margins from `scripts/check_video.py`. Make frame sheets of the busy moments with `~/.venvs/manim-gl/bin/python scripts/sheet.py clip.mp4 sheet.png 3,7.5,12` and look at them with Read: overlaps, clipped or tiny text, a colour on the wrong glyph, the reveal order, the numbers. Fix and re-preview only the scenes you changed. For layout, `scripts/render.sh frame explainers/NN-slug Scene -- -n 0,K` renders the frame after animation K at 1080p in seconds (the last frame is often blank once a scene fades out). Commit and push once the scenes preview cleanly.
5. **Final:** `scripts/render.sh final explainers/NN-slug` runs `check.py`, renders every scene at 1080p30 two at a time, checks each clip and joins them into `videos/NN-slug/A111-NN-slug.mp4`. Rendering takes about 7 minutes per minute of video (45 to 60 minutes for a 7-minute explainer), so run it in the background. Then look at a frame sheet of the joined video, including the seams between scenes.
6. **Deliver:** send `A111-NN-slug.mp4` and `main.py` to Sabelo in the chat, with the idea, the length and the link to the folder on GitHub. Offer a short quiz on the idea.
7. **Push:** in the explainer's README, set the storyboard's times to the final video's (the checks print each scene's length) and the status to final; add the explainer to the index in `README.md` and to `syllabus.md`; commit and push.

**Feedback** comes as timestamps ("1:12 too fast"). The storyboard's timings give the scene. Fix it, preview it, then `scripts/render.sh final explainers/NN-slug Scene`: the fixed scene is joined with the earlier final renders of the others. Re-render every scene whose code or shared helpers changed.

## Grant's style

Grant's own code is the reference: github.com/3b1b/videos, or `videos-master` if Sabelo has shared it. `_2023/clt` is a good model for distributions and sampling. Take his patterns, not his custom modules (pi creatures, Dropbox paths): only `manimlib` and this repo's `manim_imports_ext.py` are available.

Code:

- `from manim_imports_ext import *` first; then the parameters and colours as constants; then `get_*` helper functions; then the scenes in playing order; `SCENES_IN_ORDER = [...]` at the bottom.
- In `construct`, short comment headers name each beat (`# Show the posterior`) and match the storyboard.
- Scene settings as class attributes (`n_years = 4`); `frame = self.frame` for camera moves.
- `Tex(R"...")` with raw strings and `t2c` for colour; `NotesTex` whenever the formula uses the notes' notation; `TexText` / `NotesTexText` for words with inline maths; `Text` for plain words.
- Build groups declaratively: `VGroup(get_dot(x) for x in values)`, `color_gradient(colors, n)`. Lay out with `.arrange()`, `.next_to()`, `.move_to()`, `.align_to()` rather than coordinate arithmetic.
- Live values with `ValueTracker`, `f_always` / `always`, `always_redraw` and `make_number_changeable`.
- Animations: `Write`, `FadeIn(mob, shift)`, `ShowCreation`, `TransformFromCopy`, `ReplacementTransform`, `FadeTransform`, `LaggedStartMap`, `FlashAround`, `Indicate`; `TransformMatchingTex` only for small rearrangements.
- Blank lines completely empty. No Manim Community names (`MathTex`, `Create`, `config.`).
- Scaffolding first, as Grant does: write the `get_*` helpers that build the axes, curves and tables, then the scenes, which should then read like the storyboard.
- `rate_func=linear` when an animation stands for time passing or a count stepping up steadily; the default smooth easing for everything else.
- When a scene carries on from the last one, rebuild the last scene's end state with the same helpers and `self.add` it first, so the joined video has no seam.

Look:

- `custom_config.yml` sets Grant's black background, saturation 1.5 and centred text, with CMU Serif for all text. Don't change it per explainer.
- Give colours a meaning, name it in a constant (`DATA_COLOR = BLUE`) and keep it through the explainer, and across the series where you can: BLUE for data and samples, TEAL for the prior, population or model, YELLOW for the key quantity and the result, RED for claims, deaths and errors, GREY_B for secondary words.
- Sizes: titles 40 to 48, body text 32 to 40, labels 24 to 30, formulas 36 to 52. Nothing under 24 at 1080p.
- Keep everything at least 0.4 units inside the frame; `check_video.py` measures it.
- Pacing: 1 to 3 seconds per animation, `self.wait(1.5)` to `self.wait(3)` after each new idea, 3 to 4 seconds on results and on the recall question.

## Notation

`NotesTex` loads `tex/actuarial-notation.sty`, collected from Sabelo's LaTeX study notes. Use its macros wherever the notes would:

| Macro | Gives |
|---|---|
| `\xoverline{X}` | the sample-mean bar, sized to the letter |
| `\hchi^2_{k}` | the notes' chi-square chi |
| `\approxsim` | "is approximately distributed as" (a ~ with a dot above and below) |
| `\C{n}{k}` | binomial coefficient |
| `\overbar{M}` | a shorter bar |
| `\p{x}{t}`, `\q{x}{t}`, `\l{x}`, `\e{x}`, `\fom{x}`, `\annuity{a}{n}{}` ... | survival and annuity symbols (CM1; rarely needed in A111) |

For the rest, write what the notes write: `\mathbb{E}[\mathbb{V}(X \mid \lambda)]` (outer brackets, inner parentheses), `\operatorname{Gamma}(\alpha, \beta)`, `\operatorname{Poi}(\lambda)`, `N(\mu, \sigma^2)`. Parametrisations and definitions follow the CMP and the Formulae and Tables; say which on screen when it matters (gamma with a rate, for instance). If Sabelo's notes and the CMP disagree, use the CMP's convention in the notes' look and tell him.

## Correctness

- Every number on screen is computed in `main.py` and checked by `check.py`; the final render won't start if `check.py` fails.
- Invented parameters are fine; label them "illustrative" on screen when they could pass for real data. Use real data only when Sabelo supplies it.
- Fix the seed of anything random so renders repeat.
- Before the final, read the storyboard against the CMP once more: every claim on screen should be something the CMP would accept.

## ManimGL notes (commit e5298385, ManimGL 1.7.2)

- In the cloud ManimGL needs a virtual display (`xvfb-run -a`) and `manim_imports_ext` on `PYTHONPATH`; `render.sh` does both. Even a plain `import manimlib` needs the display.
- Avoid `\!` in Tex: ManimGL's LaTeX template loads `tipa`, which redefines it.
- Don't put relation symbols (`=`, `\approx`, `\sim`, `<`) in `t2c` or `isolate`: isolated parts become ordinary atoms and lose their spacing. Colour what's on either side.
- Unisolated lookups (`tex["..."]`, `make_number_changeable`) work by counting symbols. `manim_imports_ext.py` fixes the counter (commands followed by punctuation, commands that draw nothing like `\mathbb`, the notes' macros that draw several glyphs). If a lookup lands on the wrong glyph, or a log says "does not match", add the command to `TEX_TO_SYMBOL_COUNT` there with the number of glyphs it draws, or put the part in `isolate` / `t2c` so ManimGL finds it by colour.
- With two `make_number_changeable` calls on one Tex, replace the later number first.
- `TransformMatchingTex` makes a mess of big rearrangements: transform the pieces explicitly.
- `Axes` always cross at (0, 0), even when 0 is off a range: use `CornerAxes`.
- An updater on a group that is never added to the scene never runs; put it on what the animation adds.
- Random draws throw outliers past the drawn geometry; clip or redraw them.
- `GlowDot` isn't a VMobject: group it with `Group`, not `VGroup`.
- `arrange_in_grid` places a group's direct children, so build a table as one flat group of cells, arrange it, then regroup the cells into rows.
- `set_opacity` on a curve also sets its fill and turns it into a filled shape: dim curves with `set_stroke(opacity=...)` and text with `set_fill(opacity=...)`.
- A 3D `Rotate` about an axis in the screen (a flip) goes through the perspective camera, and the near half swells past the frame edges: reflect with `mob.animate.apply_matrix(M, about_point=...)` instead (`np.diag([-1, 1, 1])` for the y-axis, the swap matrix for `y = x`), which folds flat onto the mirror and out again.
- Grant's own `custom_config.yml` has settings this ManimGL doesn't know (`invert_zoom_scroll`); don't copy it.

Changing `manim_imports_ext.py` or `custom_config.yml` changes every explainer. Add to them rather than change what's there, and after a change render a frame or two of each earlier explainer with `scripts/render.sh frame` to check nothing moved.

## Git

- Commit and push to `main` at each milestone so Sabelo can follow along: the storyboard, scenes previewing cleanly, the final. Messages like `A111-02 MLE: storyboard`, `A111-02 MLE: final render, 3:05`.
- Code and text only. `videos/` is ignored; the videos travel in the chat.
- Never commit CMP files, extracts, screenshots or quotations.
- When something would have saved you time (a new gotcha, a preference Sabelo states), add it to this file in the same push.

## Copyright

The CMP (ActEd) and the Core Reading (IFoA) are copyright. Use them to decide what to teach and how the syllabus frames it, then explain in your own words with your own examples. On screen and in this repository: formulas, standard results and references like "CMP Chapter 15" are fine; their sentences, worked examples and question text are not.

## Repository

| | |
|---|---|
| `manim_imports_ext.py` | what every explainer imports: ManimGL, `NotesTex`, CMU Serif, `CornerAxes`, the symbol-count fixes |
| `custom_config.yml` | Grant's look, passed to ManimGL by the launchers |
| `tex/actuarial-notation.sty` | the notes' notation |
| `fonts/` | CMU Serif and CMU Typewriter Text (SIL Open Font License) |
| `explainers/NN-slug/` | one explainer: `README.md` (storyboard and status), `main.py`, `check.py` |
| `scripts/setup_cloud.sh` | sets up the cloud workspace |
| `scripts/render.sh` | preview, frame and final renders, with checks and joining |
| `scripts/check_video.py`, `scripts/sheet.py`, `scripts/scenes.py` | clip checks, frame sheets, scene order |
| `render.cmd` | renders on Sabelo's Windows PC |
| `syllabus.md` | the A111 syllabus areas, CMP chapters and which explainers cover them |
| `docs/project-instructions.md` | the Claude Project's instructions |

## Explainer README template

```markdown
# A111-NN Title

**The idea:** one sentence.
**Syllabus:** area and objective; CMP chapter (and section).
**Length:** m:ss, N scenes. **Status:** storyboard | building | final (date).

## Storyboard

### Act 1: Title

| Time | Scene | What happens | Words on screen |
|---|---|---|---|
| 0:00 | SceneName | ... | ... |

### Act 2: Title

...

## Recall

Question, then the answer.

## Render

Cloud: `scripts/render.sh final explainers/NN-slug`
PC: `.\render explainers\NN-slug\main.py -a -w`
```
