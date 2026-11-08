"""What every A111 explainer imports: `from manim_imports_ext import *`.

Grant Sanderson starts each video file in his repository (3b1b/videos) with that line,
and his manim_imports_ext gives ManimGL plus his own helpers. This one gives ManimGL plus
what the A111 explainers share:

    NotesTex, NotesTexText  Tex and TexText with the symbols of the study notes
                            (tex/actuarial-notation.sty), e.g.
                            NotesTex(R"\\xoverline{X} \\approxsim N(\\mu, \\sigma^2 / n)")
    FONT, MONO_FONT         CMU Serif, the default font of all Text and numbers, and
                            CMU Typewriter Text for code
    CornerAxes              Axes whose lines meet at the lower-left corner of the ranges

It also corrects how ManimGL counts the symbols in a formula, which it uses to find the
parts of one (see num_tex_symbols and TEX_TO_SYMBOL_COUNT below), and uses the ffmpeg
that comes with imageio-ffmpeg when no ffmpeg is on the PATH, as on the Windows set-up.
"""
from manimlib import *
from manimlib.config import manim_config
from manimlib.utils.tex import remove_tex_environments
from manimlib.utils.tex_to_symbol_count import TEX_TO_SYMBOL_COUNT
import manimlib.mobject.svg.tex_mobject
import manimlib.utils.tex

import os
import re
import shutil
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent

# Fonts: Computer Modern Unicode, the font of the maths, for all text
FONT = "CMU Serif"
MONO_FONT = "CMU Typewriter Text"


def register_fonts(font_dir=REPO_DIR / "fonts"):
    import manimpango
    if {FONT, MONO_FONT} <= set(manimpango.list_fonts()):
        return
    for path in sorted(font_dir.glob("*.ttf")):
        manimpango.register_font(str(path))


register_fonts()
manim_config.text.font = FONT

# The study notes' notation. LaTeX finds the package through TEXINPUTS from any working
# folder, and through its absolute path unless the path has spaces, which \usepackage
# can't take. The manim option keeps the notes' 12pt proportions at Manim's 10pt.
TEX_DIR = REPO_DIR / "tex"
os.environ["TEXINPUTS"] = f"{TEX_DIR.as_posix()}{os.pathsep}" + os.environ.get("TEXINPUTS", "")
NOTATION_PACKAGE = (TEX_DIR / "actuarial-notation").as_posix()
if " " in NOTATION_PACKAGE:
    NOTATION_PACKAGE = "actuarial-notation"
NOTES_PREAMBLE = "\n".join([
    R"\usepackage{lmodern}",
    R"\usepackage[T1]{fontenc}",
    Rf"\usepackage[manim]{{{NOTATION_PACKAGE}}}",
])


class NotesTex(Tex):
    """Tex with the study notes' notation loaded"""
    def __init__(self, *tex_strings, **kwargs):
        kwargs.setdefault("additional_preamble", NOTES_PREAMBLE)
        super().__init__(*tex_strings, **kwargs)


class NotesTexText(TexText):
    """TexText (text with $inline maths$) with the study notes' notation loaded"""
    def __init__(self, *tex_strings, **kwargs):
        kwargs.setdefault("additional_preamble", NOTES_PREAMBLE)
        super().__init__(*tex_strings, **kwargs)


# ManimGL finds an unisolated part of a formula (tex["..."], make_number_changeable) by
# counting symbols, so a wrong count points it at the wrong glyph. Two corrections:
#
# 1. Its counter reads a command followed by , - . / : ; < > or ! as one command, so
#    "\alpha, \beta" counts 2 symbols instead of 3. This counter reads commands the way
#    TeX does: a backslash and letters, or a backslash and one other character.
def num_tex_symbols(tex: str) -> int:
    tex = remove_tex_environments(tex)
    total = 0
    pos = 0
    for match in re.finditer(r"\\sqrt\[[0-9]+\]|\\[a-zA-Z]+|\\.", tex, re.DOTALL):
        total += sum(1 for char in tex[pos:match.start()] if char not in "^{} \n\t_$\\&")
        command = match.group()
        if command.startswith(R"\sqrt["):
            total += len(command) - 5
        elif command not in ("\\\\", "\\ ", "\\\n", "\\\t"):  # line breaks and spaces draw nothing
            total += TEX_TO_SYMBOL_COUNT.get(command, 1)
        pos = match.end()
    total += sum(1 for char in tex[pos:] if char not in "^{} \n\t_$\\&")
    return total


manimlib.utils.tex.num_tex_symbols = num_tex_symbols
manimlib.mobject.svg.tex_mobject.num_tex_symbols = num_tex_symbols

# 2. One symbol per command, unless this table says otherwise. These commands restyle or
#    position their arguments and draw nothing themselves, or draw several glyphs.
TEX_TO_SYMBOL_COUNT.update({
    **{cmd: 0 for cmd in [
        R"\mathrm", R"\mathbf", R"\mathit", R"\mathsf", R"\mathtt", R"\mathnormal",
        R"\mathbb", R"\mathfrak", R"\mathscr", R"\boldsymbol", R"\operatorname",
        R"\textrm", R"\textit", R"\textsf", R"\texttt", R"\textup", R"\textnormal",
        R"\stackrel", R"\overset", R"\underset",
    ]},
    R"\binom": 2,       # the two brackets
    R"\C": 2,           # the notes' binomial coefficient, \C{n}{k}
    R"\approxsim": 3,   # the notes' ~ with a dot above and below
    R"\l": 1,           # the notes' \l{x} draws an l (LaTeX's own \l draws nothing in maths)
})


# ManimGL's Axes always cross at (0, 0), even when 0 is off a range
def axes_crossing(axis_range):
    """Where the other axis crosses: at 0 if 0 is on the range, otherwise at the nearer end"""
    return min(max(0, axis_range[0]), axis_range[1])


class CornerAxes(Axes):
    """Axes that cross at the lower-left corner when 0 is off a range, e.g. ages 20 to 100"""
    def create_axis(self, range_terms, axis_config, length):
        axis = NumberLine(range_terms, width=length, **axis_config)
        axis.shift(-axis.n2p(axes_crossing(range_terms)))
        return axis

    def coords_to_point(self, *coords):
        origin = self.x_axis.number_to_point(axes_crossing(self.x_range))
        return origin + sum(
            axis.number_to_point(coord) - origin
            for axis, coord in zip(self.get_axes(), coords)
        )


# ffmpeg: the PC's ManimGL environment ships one with imageio-ffmpeg instead of the PATH
def use_bundled_ffmpeg():
    writer_config = manim_config.file_writer
    if shutil.which(writer_config.ffmpeg_bin) or os.path.isfile(writer_config.ffmpeg_bin):
        return
    try:
        import imageio_ffmpeg
        writer_config.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass


use_bundled_ffmpeg()
