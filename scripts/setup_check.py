from manim_imports_ext import *


class SetupCheck(InteractiveScene):
    def construct(self):
        title = Text("A111 explainers: set-up check", font_size=48)
        formula = NotesTex(
            R"\xoverline{X} \approxsim N(\mu, \sigma^2 / n)",
            t2c={R"\xoverline{X}": BLUE, R"\mu": YELLOW},
            font_size=60,
        )
        chi = NotesTex(R"\hchi^2_{k}", font_size=60)
        group = VGroup(title, formula, chi)
        group.arrange(DOWN, buff=0.6)
        self.add(group)
