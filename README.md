# A111 Actuarial Statistics: explainers

3Blue1Brown-style explainer videos for ASSA A111 Actuarial Statistics (the IFoA CS1 syllabus), written in Grant Sanderson's ManimGL style. Claude makes them on request in a Claude Project that holds the Combined Materials Pack, sends the videos in the chat, and pushes the code here.

## Explainers

| # | Explainer | Syllabus | Length | The idea |
|---|---|---|---|---|
| 01 | [Credibility: why the premium is a weighted average](explainers/01-credibility) | 5 Bayesian statistics: credibility | 3:34 | In the Poisson/gamma model the Bayesian estimate is exactly Z·x̄ + (1 − Z)·μ, with Z = n/(n + β). |

[syllabus.md](syllabus.md) maps the syllabus and what's covered so far.

## On your PC

Clone the repository once, into a folder outside OneDrive (OneDrive and git both lock files in `.git`), for example from a terminal:

```
cd %USERPROFILE%\source\repos
git clone https://github.com/PsiAntics/A111-Actuarial-Statistics.git
```

Then, in that folder, `git pull` fetches whatever Claude has pushed since.

`render.cmd` renders an explainer with the ManimGL environment that `Documents\Manim\setup` made, with Grant's look and the notation from your notes:

```
.\render explainers\01-credibility\main.py WhoseNumber           live window
.\render explainers\01-credibility\main.py WhoseNumber -w        1080p30 video
.\render explainers\01-credibility\main.py -a -w                 every scene, in order
```

Videos go to `videos\<explainer>\`, which git ignores.

## How the explainers are made

- [docs/project-instructions.md](docs/project-instructions.md): the Claude Project's instructions, and how to set the project up.
- [CLAUDE.md](CLAUDE.md): the playbook Claude follows: workflow, style, notation, checks and git routine.
- Each explainer's folder has a README with its storyboard, `main.py` with the scenes and `check.py`, which recomputes every number on screen.

## Layout

| | |
|---|---|
| `explainers/` | one folder per explainer |
| `manim_imports_ext.py` | what every explainer imports: ManimGL, `NotesTex` with your notation, CMU Serif, `CornerAxes`, fixes for ManimGL's Tex |
| `custom_config.yml` | Grant's look: black background, saturation 1.5, centred text, CMU Serif |
| `tex/actuarial-notation.sty` | the notation from your LaTeX notes |
| `fonts/` | CMU Serif and CMU Typewriter Text (SIL Open Font License) |
| `scripts/` | set-up, rendering and checks for Claude's cloud workspace |
| `render.cmd` | rendering on your PC |

The repository is public. Course material (the CMP, Core Reading, ActEd questions) never goes in it; the explainers are in our own words.
