from manim_imports_ext import *
import math


# Illustrative Poisson/gamma model: a driver's yearly claim count is Poi(lambda),
# and lambda varies across the portfolio as Gamma(alpha, beta)
ALPHA = 2
BETA = 4
DRIVER_CLAIMS = [1, 0, 2, 0]
PORTFOLIO_SEED = 326
NOISE_SEED = 2

DATA_COLOR = BLUE
PRIOR_COLOR = TEAL
POSTERIOR_COLOR = YELLOW
Z_COLOR = YELLOW
CLAIM_COLOR = RED


def gamma_pdf(lam, alpha, beta):
    return beta**alpha * lam**(alpha - 1) * np.exp(-beta * lam) / math.gamma(alpha)


def credibility_factor(n, k=BETA):
    return n / (n + k)


def get_rate_axes(width=9, height=4.2):
    axes = Axes((0, 2, 0.25), (0, 2, 0.5), width=width, height=height)
    axes.x_axis.add_numbers(np.arange(0, 2.5, 0.5), num_decimal_places=1, font_size=24)
    axes.to_corner(DL, buff=0.9)
    return axes


def get_rate_label(axes):
    label = Tex(R"\lambda", font_size=40)
    label.next_to(axes.x_axis.get_end(), RIGHT)
    return label


def get_prior_graph(axes):
    graph = axes.get_graph(lambda x: gamma_pdf(x, ALPHA, BETA), x_range=(0, 2, 0.01))
    graph.set_stroke(PRIOR_COLOR, 4)
    return graph


def get_prior_label(axes, font_size=36):
    label = VGroup(
        Text("Prior", font_size=font_size),
        Tex(R"\operatorname{Gamma}(2, 4)", font_size=font_size),
    )
    label.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    label.set_color(PRIOR_COLOR)
    label.next_to(axes.c2p(0.3, gamma_pdf(0.3, ALPHA, BETA)), UR, buff=0.3)
    return label


def get_year_cells(n_years=4, width=1.2, height=0.8):
    cells = VGroup(Rectangle(width, height) for n in range(n_years))
    cells.arrange(RIGHT, buff=0.15)
    cells.set_stroke(GREY_B, 1.5)
    labels = VGroup(
        Text(f"Year {n}", font_size=24).next_to(cell, UP, SMALL_BUFF)
        for n, cell in enumerate(cells, start=1)
    )
    return VGroup(cells, labels)


def get_claim_dots(cell, count, radius=0.1):
    dots = VGroup(Dot(radius=radius) for n in range(count))
    dots.set_fill(CLAIM_COLOR)
    dots.arrange(RIGHT, buff=0.12)
    dots.move_to(cell)
    return dots


def get_driver_dot(radius=0.15):
    return Dot(radius=radius).set_fill(DATA_COLOR)


def get_portfolio(n_rows=10, n_cols=10, radius=0.09):
    drivers = VGroup(Dot(radius=radius) for n in range(n_rows * n_cols))
    drivers.arrange_in_grid(n_rows, n_cols, buff=0.12)
    drivers.set_fill(GREY_B)
    return drivers


def get_histogram_points(axes, rates, bin_width=0.1):
    """Where each dot lands when the dots are stacked into a density histogram of the rates"""
    dot_height = 1 / (len(rates) * bin_width)
    heights = dict()
    points = []
    for rate in rates:
        index = int(rate // bin_width)
        level = heights.get(index, 0)
        points.append(axes.c2p((index + 0.5) * bin_width, (level + 0.5) * dot_height))
        heights[index] = level + 1
    return points


def get_marker(axes, value, color, label_tex, height=1.9, font_size=36):
    line = DashedLine(axes.c2p(value, 0), axes.c2p(value, height))
    line.set_stroke(color, 2)
    label = NotesTex(label_tex, font_size=font_size)
    label.set_color(color)
    label.next_to(line, UP, SMALL_BUFF)
    return VGroup(line, label)


class WhoseNumber(InteractiveScene):
    def construct(self):
        # One driver's record
        question = Text("How many claims should we expect from this driver next year?", font_size=38)
        question.to_edge(UP)

        driver = get_driver_dot()
        record = get_year_cells()
        record.next_to(driver, RIGHT, buff=0.9)
        VGroup(driver, record).to_corner(UL, buff=0.8).shift(1.0 * DOWN + 0.5 * RIGHT)
        driver_label = Text("This driver", font_size=28)
        driver_label.set_color(DATA_COLOR)
        driver_label.next_to(driver, DOWN)

        claim_dots = VGroup(
            get_claim_dots(cell, count)
            for cell, count in zip(record[0], DRIVER_CLAIMS)
        )
        xbar_eq = NotesTex(R"\xoverline{x} = \frac{1 + 0 + 2 + 0}{4} = 0.75", t2c={R"\xoverline{x}": DATA_COLOR})
        xbar_eq.next_to(record, DOWN, buff=0.6)

        self.play(FadeIn(question, lag_ratio=0.1, run_time=1.5))
        self.wait()
        self.play(
            GrowFromCenter(driver),
            FadeIn(driver_label, 0.25 * DOWN),
            LaggedStartMap(FadeIn, record[0], lag_ratio=0.2),
            LaggedStartMap(FadeIn, record[1], lag_ratio=0.2),
        )
        self.play(LaggedStart(
            *(LaggedStartMap(GrowFromCenter, dots) for dots in claim_dots if len(dots) > 0),
            lag_ratio=0.4,
        ))
        self.wait()
        self.play(Write(xbar_eq))
        self.wait(2)

        # The rest of the portfolio
        portfolio = get_portfolio()
        portfolio.to_corner(UR, buff=0.8).shift(0.6 * DOWN)
        mu_eq = Tex(R"\mu = 0.5", t2c={R"\mu": PRIOR_COLOR})
        mu_label = VGroup(Text("Portfolio average", font_size=28), mu_eq)
        mu_label.arrange(DOWN)
        mu_label.next_to(portfolio, DOWN)

        self.play(FadeIn(portfolio, lag_ratio=0.01, run_time=2))
        self.play(FadeIn(mu_label, 0.25 * DOWN))
        self.wait(2)

        # Two candidate answers
        number_line = NumberLine((0, 1.5, 0.25), width=9)
        number_line.add_numbers(np.arange(0, 1.75, 0.25), num_decimal_places=2, font_size=24)
        number_line.to_edge(DOWN, buff=1.0)
        line_label = Text("Claims per year", font_size=24)
        line_label.next_to(number_line, RIGHT)
        line_label.shift(0.1 * DOWN)

        def get_pointer(value, tex, color):
            arrow = Vector(0.6 * DOWN, thickness=4)
            arrow.set_color(color)
            arrow.next_to(number_line.n2p(value), UP, SMALL_BUFF)
            label = NotesTex(tex)
            label.set_color(color)
            label.next_to(arrow, UP, SMALL_BUFF)
            return VGroup(arrow, label)

        mu_pointer = get_pointer(0.5, R"\mu", PRIOR_COLOR)
        xbar_pointer = get_pointer(0.75, R"\xoverline{x}", DATA_COLOR)
        unknown = Text("?", font_size=60)
        unknown.set_color(Z_COLOR)
        unknown.next_to(number_line.n2p(0.625), UP, buff=0.5)

        self.play(
            ShowCreation(number_line),
            FadeIn(line_label),
        )
        self.play(
            TransformFromCopy(mu_eq[R"\mu"][0], mu_pointer[1]),
            GrowArrow(mu_pointer[0]),
            TransformFromCopy(xbar_eq[R"\xoverline{x}"][0], xbar_pointer[1]),
            GrowArrow(xbar_pointer[0]),
            run_time=1.5
        )
        self.wait(1.5)
        self.play(Write(unknown))
        self.wait(3)

        # Only the portfolio carries on
        self.play(FadeOut(Group(*(mob for mob in self.mobjects if mob is not portfolio))))
        self.wait(0.5)


class PortfolioPrior(InteractiveScene):
    def construct(self):
        # Every driver has their own claim rate
        axes = get_rate_axes()
        rate_label = get_rate_label(axes)
        portfolio = get_portfolio()
        portfolio.to_corner(UR, buff=0.8).shift(0.6 * DOWN)
        rates = np.random.default_rng(PORTFOLIO_SEED).gamma(ALPHA, 1 / BETA, size=len(portfolio))

        caption = TexText(R"Each driver has their own claim rate, $\lambda$", font_size=40)
        caption.to_edge(UP)

        self.add(portfolio)
        self.play(FadeIn(caption, lag_ratio=0.1))
        self.wait()

        example_indices = [10, 50, 90]
        examples = VGroup(portfolio[n] for n in example_indices)
        example_labels = VGroup(
            Tex(Rf"\lambda = {rates[n]:.2f}", font_size=28).next_to(portfolio[n], LEFT)
            for n in example_indices
        )
        self.play(
            LaggedStart(*(dot.animate.set_fill(WHITE).scale(1.5) for dot in examples), lag_ratio=0.3),
            LaggedStartMap(FadeIn, example_labels, shift=0.2 * LEFT, lag_ratio=0.3),
        )
        self.wait(2)
        self.play(
            *(dot.animate.set_fill(GREY_B).scale(1 / 1.5) for dot in examples),
            FadeOut(example_labels),
        )

        # Sort the portfolio by claim rate
        self.play(
            ShowCreation(axes),
            FadeIn(rate_label),
        )
        points = get_histogram_points(axes, rates)
        order = np.argsort(rates)
        self.play(
            LaggedStart(
                *(portfolio[n].animate.move_to(points[n]) for n in order),
                lag_ratio=0.01,
            ),
            run_time=5
        )
        self.wait(1.5)

        # The shape of the portfolio
        prior_graph = get_prior_graph(axes)
        prior_label = get_prior_label(axes)
        prior_eq = Tex(R"\lambda \sim \operatorname{Gamma}(\alpha, \beta)", font_size=40)
        prior_eq.to_corner(UR, buff=0.8).shift(0.4 * DOWN)
        params = Tex(R"\alpha = 2, \quad \beta = 4", font_size=40)
        params.set_color(PRIOR_COLOR)
        params.next_to(prior_eq, DOWN, aligned_edge=LEFT)
        mean_eq = Tex(R"\mu = \frac{\alpha}{\beta} = 0.5", t2c={R"\mu": PRIOR_COLOR}, font_size=40)
        mean_eq.next_to(params, DOWN, buff=0.4, aligned_edge=LEFT)
        mean_marker = get_marker(axes, 0.5, PRIOR_COLOR, R"\mu")

        self.play(
            portfolio.animate.set_fill(opacity=0.5),
            ShowCreation(prior_graph, run_time=2),
            FadeIn(prior_eq),
            FadeOut(caption, UP),
        )
        self.play(FadeIn(params, 0.25 * DOWN))
        self.wait(1.5)
        self.play(
            ShowCreation(mean_marker[0]),
            Write(mean_marker[1]),
            FadeIn(mean_eq, 0.25 * DOWN),
        )
        self.wait(2)

        # Our driver is one of these, but which?
        driver = get_driver_dot()
        driver.next_to(mean_eq, DOWN, buff=0.8, aligned_edge=LEFT)
        driver_label = Tex(R"\lambda = \, ?", font_size=40)
        driver_label.next_to(driver, RIGHT)
        driver_label.set_color(DATA_COLOR)

        self.play(GrowFromCenter(driver), Write(driver_label))
        self.wait(3)

        # Keep only the curve for what comes next
        self.play(
            FadeOut(portfolio),
            FadeOut(VGroup(prior_eq, params, mean_eq, mean_marker, driver, driver_label)),
            FadeIn(prior_label),
        )
        self.wait()


class YearByYear(InteractiveScene):
    def construct(self):
        axes = get_rate_axes()
        rate_label = get_rate_label(axes)
        prior_graph = get_prior_graph(axes)
        prior_label = get_prior_label(axes)
        self.add(axes, rate_label, prior_graph, prior_label)

        # The driver's record, one year at a time
        driver = get_driver_dot()
        record = get_year_cells()
        record.next_to(driver, RIGHT, buff=0.5)
        VGroup(driver, record).to_corner(UL, buff=0.6)
        claim_dots = VGroup(
            get_claim_dots(cell, count)
            for cell, count in zip(record[0], DRIVER_CLAIMS)
        )

        self.play(
            GrowFromCenter(driver),
            FadeIn(record, lag_ratio=0.1),
        )
        self.play(LaggedStartMap(GrowFromCenter, claim_dots[0]))

        # Likelihood of what we saw, for every possible rate
        likelihood_scale = 3
        likelihood = axes.get_graph(lambda x: likelihood_scale * x * np.exp(-x), x_range=(0, 2, 0.01))
        likelihood.set_stroke(DATA_COLOR, 4)
        likelihood_label = Tex(R"\mathbb{P}(1 \text{ claim} \mid \lambda) = \lambda e^{-\lambda}", font_size=34)
        likelihood_label.set_color(DATA_COLOR)
        likelihood_label.next_to(axes.c2p(1.0, likelihood_scale * math.exp(-1)), UP, buff=0.25)

        self.play(
            ShowCreation(likelihood),
            FadeIn(likelihood_label, 0.25 * UP),
        )
        self.wait(2)

        # Multiply and rescale
        a_tracker = ValueTracker(ALPHA + DRIVER_CLAIMS[0])
        b_tracker = ValueTracker(BETA + 1)

        def posterior_func(x):
            return gamma_pdf(x, a_tracker.get_value(), b_tracker.get_value())

        posterior = axes.get_graph(posterior_func, x_range=(0, 2, 0.01))
        posterior.set_stroke(POSTERIOR_COLOR, 5)

        bayes_rule = Tex(R"\text{posterior} \propto \text{prior} \times \text{likelihood}", font_size=36)
        bayes_rule["posterior"].set_color(POSTERIOR_COLOR)
        bayes_rule["prior"].set_color(PRIOR_COLOR)
        bayes_rule["likelihood"].set_color(DATA_COLOR)
        bayes_rule.to_corner(UR, buff=0.6).shift(0.3 * DOWN)

        posterior_label = VGroup(
            Text("Posterior", font_size=36),
            Tex(R"\operatorname{Gamma}(3, 5)", font_size=36),
        )
        posterior_label.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        posterior_label.set_color(POSTERIOR_COLOR)
        posterior_label.next_to(axes.c2p(1.15, 1.2), RIGHT)
        b_dec = posterior_label[1].make_number_changeable("5")
        a_dec = posterior_label[1].make_number_changeable("3")

        self.play(FadeIn(bayes_rule, lag_ratio=0.1))
        self.wait()
        self.play(
            TransformFromCopy(prior_graph, posterior),
            TransformFromCopy(likelihood, posterior),
            FadeOut(likelihood_label),
            run_time=2
        )
        self.play(
            FadeIn(posterior_label, 0.25 * DOWN),
            FadeOut(likelihood),
            prior_graph.animate.set_stroke(opacity=0.4),
            prior_label.animate.set_opacity(0.4),
        )
        self.wait(2)

        # Each new year updates it again
        axes.bind_graph_to_func(posterior, posterior_func)
        a_dec.f_always.set_value(a_tracker.get_value)
        b_dec.f_always.set_value(b_tracker.get_value)

        update_rule = Tex(
            R"\operatorname{Gamma}\big(\alpha + \textstyle\sum x, \; \beta + n\big)",
            font_size=36,
        )
        update_rule.next_to(bayes_rule, DOWN, buff=0.4, aligned_edge=LEFT)

        self.play(FadeIn(update_rule, 0.25 * DOWN))
        for n in range(2, len(DRIVER_CLAIMS) + 1):
            new_claims = claim_dots[n - 1]
            self.play(
                LaggedStartMap(GrowFromCenter, new_claims) if len(new_claims) > 0 else Indicate(record[0][n - 1]),
                a_tracker.animate.set_value(ALPHA + sum(DRIVER_CLAIMS[:n])),
                b_tracker.animate.set_value(BETA + n),
                run_time=2.5
            )
            self.wait(1.5)

        arithmetic = Tex(R"\alpha + \textstyle\sum x = 2 + 3, \quad \beta + n = 4 + 4", font_size=32)
        arithmetic.next_to(update_rule, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(arithmetic, 0.25 * DOWN))
        self.wait(2)

        # Sharper, and pulled toward the record
        summary = Text("Sharper, and pulled toward\nthis driver's record", font_size=30)
        summary.next_to(arithmetic, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(summary, lag_ratio=0.1))
        self.wait(2)
        self.play(FadeOut(VGroup(driver, record, claim_dots, bayes_rule, update_rule, arithmetic, summary, posterior_label, prior_label)))


class WhereIsTheMean(InteractiveScene):
    def construct(self):
        axes = get_rate_axes()
        rate_label = get_rate_label(axes)
        prior_graph = get_prior_graph(axes)
        prior_graph.set_stroke(opacity=0.4)
        n_years = len(DRIVER_CLAIMS)
        post_alpha = ALPHA + sum(DRIVER_CLAIMS)
        post_beta = BETA + n_years
        posterior = axes.get_graph(lambda x: gamma_pdf(x, post_alpha, post_beta), x_range=(0, 2, 0.01))
        posterior.set_stroke(POSTERIOR_COLOR, 5)
        plot = VGroup(axes, rate_label, prior_graph, posterior)
        self.add(plot)

        # Predict
        mu_marker = get_marker(axes, ALPHA / BETA, PRIOR_COLOR, R"\mu")
        xbar_marker = get_marker(axes, np.mean(DRIVER_CLAIMS), DATA_COLOR, R"\xoverline{x}")
        prompt = Text("Predict: where is the mean of the yellow curve?", font_size=36)
        prompt.to_edge(UP)

        self.play(FadeIn(prompt, lag_ratio=0.1))
        self.play(
            LaggedStart(
                ShowCreation(mu_marker[0]), Write(mu_marker[1]),
                ShowCreation(xbar_marker[0]), Write(xbar_marker[1]),
                lag_ratio=0.3,
            )
        )
        self.wait(3.5)

        # Reveal
        post_mean = post_alpha / post_beta
        mean_marker = get_marker(axes, post_mean, POSTERIOR_COLOR, R"0.625", height=1.9)
        mean_marker[1].next_to(mean_marker[0], UP, buff=0.5)
        halfway = Text("Exactly halfway", font_size=30)
        halfway.set_color(POSTERIOR_COLOR)
        halfway.next_to(mean_marker[1], UP, SMALL_BUFF)

        self.play(
            ShowCreation(mean_marker[0]),
            FadeIn(mean_marker[1], 0.25 * DOWN),
        )
        self.play(FadeIn(halfway, lag_ratio=0.1))
        self.wait(2.5)

        # Make room for the algebra
        plot.add(mu_marker, xbar_marker, mean_marker)
        self.play(
            FadeOut(prompt, UP),
            FadeOut(halfway),
            plot.animate.scale(0.6, about_edge=DL),
        )

        # The posterior mean, rearranged
        t2c = {
            R"\xoverline{x}": DATA_COLOR,
            R"\mu": PRIOR_COLOR,
            "Z": Z_COLOR,
        }
        lines = VGroup(
            NotesTex(R"\text{Posterior mean} = \frac{\alpha + \sum x}{\beta + n}", t2c=t2c),
            NotesTex(R"= \frac{n}{n + \beta} \cdot \frac{\sum x}{n} + \frac{\beta}{n + \beta} \cdot \frac{\alpha}{\beta}", t2c=t2c),
            NotesTex(R"= Z \, \xoverline{x} + (1 - Z) \, \mu", t2c=t2c),
        )
        for line in lines:
            line.scale(0.85)
        lines.arrange(DOWN, buff=0.45)
        for line in lines[1:]:
            line.align_to(lines[0]["="][0], LEFT)
        lines.to_corner(UR, buff=0.7)

        z_def = NotesTex(R"Z = \frac{n}{n + \beta}", t2c=t2c)
        z_def.scale(0.85)
        z_def.next_to(lines, DOWN, buff=0.6)
        z_rect = SurroundingRectangle(z_def, buff=0.2)
        z_rect.set_stroke(Z_COLOR, 2)

        self.play(Write(lines[0]))
        self.wait(1.5)
        self.play(FadeIn(lines[1], 0.5 * DOWN))
        self.wait(2)

        source = lines[1].copy()
        target = lines[2]
        self.play(
            ReplacementTransform(source["="][0], target["="][0]),
            FadeTransform(source[R"\frac{n}{n + \beta}"][0], target["Z"][0]),
            FadeTransform(source[R"\cdot \frac{\sum x}{n}"][0], target[R"\xoverline{x}"][0]),
            ReplacementTransform(source["+"][1], target["+"][0]),
            FadeTransform(source[R"\frac{\beta}{n + \beta}"][0], target["(1 - Z)"][0]),
            FadeTransform(source[R"\cdot \frac{\alpha}{\beta}"][0], target[R"\mu"][0]),
            run_time=2
        )
        self.add(target)
        self.wait(1.5)
        self.play(
            Write(z_def),
            ShowCreation(z_rect),
        )
        self.wait(2)

        # Plug in this driver's numbers
        numbers = VGroup(
            NotesTex(R"Z = \frac{4}{4 + 4} = 0.5", t2c={"Z": Z_COLOR}),
            NotesTex(R"0.5 \times 0.75 + 0.5 \times 0.5 = 0.625", t2c={"0.625": POSTERIOR_COLOR}),
        )
        numbers.scale(0.75)
        numbers.arrange(DOWN, buff=0.3)
        numbers.next_to(z_rect, DOWN, buff=0.5)
        self.play(FadeIn(numbers[0], lag_ratio=0.05))
        self.wait()
        self.play(FadeIn(numbers[1], lag_ratio=0.05))
        self.play(FlashAround(mean_marker[1], run_time=2, time_width=1.5))
        self.wait(2.5)
        self.play(FadeOut(Group(*self.mobjects)))


class BalanceBeam(InteractiveScene):
    max_weight_side = 1.6

    def construct(self):
        # A number line of claim rates, zoomed in on the two candidates
        mu = ALPHA / BETA
        xbar = np.mean(DRIVER_CLAIMS)
        number_line = NumberLine((0.4, 0.85, 0.05), width=12)
        number_line.add_numbers(np.arange(0.4, 0.86, 0.1), num_decimal_places=1, font_size=28)
        number_line.to_edge(DOWN, buff=1.2)

        title = Text("A weighted average is a balance point", font_size=40)
        title.to_edge(UP)

        # The beam, its two weights, and the fulcrum
        n_tracker = ValueTracker(0)
        get_n = n_tracker.get_value
        beam_y = number_line.get_y() + 2.2

        beam = Line(number_line.n2p(mu), number_line.n2p(xbar))
        beam.set_y(beam_y)
        beam.set_stroke(WHITE, 6)

        def get_weight(value, weight, color):
            side = self.max_weight_side * math.sqrt(weight / 40)
            square = Square(max(side, 1e-3))
            square.set_fill(color, 0.85)
            square.set_stroke(WHITE, 1)
            square.move_to(beam.get_center(), DOWN)
            square.set_x(number_line.n2p(value)[0])
            return square

        beta_weight = get_weight(mu, BETA, PRIOR_COLOR)
        n_weight = always_redraw(lambda: get_weight(xbar, get_n(), DATA_COLOR))

        beta_label = Tex(R"\beta = 4", font_size=36)
        beta_label.set_color(PRIOR_COLOR)
        beta_label.next_to(beta_weight, UP)
        n_label = Tex(R"n = 0", font_size=36)
        n_label.set_color(DATA_COLOR)
        n_label.make_number_changeable("0").f_always.set_value(get_n)
        n_label.always.next_to(n_weight, UP)

        def get_balance_point():
            return credibility_factor(get_n()) * xbar + (1 - credibility_factor(get_n())) * mu

        fulcrum = Triangle()
        fulcrum.set_shape(0.6, 0.5)
        fulcrum.set_fill(GREY_C, 1)
        fulcrum.set_stroke(WHITE, 1)
        fulcrum.f_always.move_to(lambda: number_line.n2p(get_balance_point()) + (beam_y - number_line.get_y() - 0.25) * UP)

        drop_line = always_redraw(lambda: DashedLine(
            fulcrum.get_bottom(),
            number_line.n2p(get_balance_point()),
        ).set_stroke(Z_COLOR, 2))

        endpoint_labels = VGroup(
            NotesTex(R"\mu", font_size=40).set_color(PRIOR_COLOR).next_to(number_line.n2p(mu), DOWN, buff=0.6),
            NotesTex(R"\xoverline{x}", font_size=40).set_color(DATA_COLOR).next_to(number_line.n2p(xbar), DOWN, buff=0.6),
        )

        readout = NotesTex(
            R"Z = \frac{n}{n + \beta} = 0.00",
            t2c={"Z": Z_COLOR, "n": DATA_COLOR, R"\beta": PRIOR_COLOR},
            font_size=40,
        )
        readout.make_number_changeable("0.00").f_always.set_value(lambda: credibility_factor(get_n()))
        estimate = Tex(R"\text{Estimate} = 0.500", font_size=40)
        estimate.make_number_changeable("0.500").f_always.set_value(get_balance_point)
        estimate.set_color(Z_COLOR)
        readouts = VGroup(readout, estimate)
        readouts.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        readouts.to_corner(UL, buff=0.8).shift(0.4 * DOWN)

        self.play(FadeIn(title, lag_ratio=0.1))
        self.play(
            ShowCreation(number_line),
            FadeIn(endpoint_labels),
        )
        self.play(
            ShowCreation(beam),
            FadeIn(beta_weight, 0.5 * DOWN),
            FadeIn(beta_label, 0.5 * DOWN),
            FadeIn(fulcrum, UP),
        )
        self.add(n_weight, n_label, drop_line)
        self.play(FadeIn(readouts))
        self.wait(2)

        # Pile on the years
        for n_years in [1, 4, 12, 36, 100]:
            self.play(n_tracker.animate.set_value(n_years), run_time=3)
            self.wait(2.5)

        limit_words = TexText(R"As $n \to \infty$, $Z \to 1$: the record speaks for itself", font_size=40)
        limit_words.move_to(title)
        self.play(FadeTransform(title, limit_words))
        self.wait(3)
        self.play(FadeOut(Group(*self.mobjects)))


class WithinVsBetween(InteractiveScene):
    def construct(self):
        # The question
        title = TexText(R"Why $\beta$? Two kinds of variation", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, lag_ratio=0.1))
        self.wait()

        # Noise within one driver
        counts = np.random.default_rng(NOISE_SEED).poisson(ALPHA / BETA, size=20)
        within_axes = Axes((0, 20, 5), (0, 3, 1), width=5.5, height=1.8)
        within_axes.move_to(3.4 * LEFT + 0.8 * UP)
        bars = VGroup(
            Rectangle(within_axes.x_axis.get_unit_size() * 0.7, max(within_axes.y_axis.get_unit_size() * count, 1e-3))
            for count in counts
        )
        for n, bar in enumerate(bars):
            bar.move_to(within_axes.c2p(n + 0.5, 0), DOWN)
        bars.set_fill(CLAIM_COLOR, 0.85)
        bars.set_stroke(width=0)
        within_title = Text("Within one driver", font_size=32)
        within_title.next_to(within_axes, UP, buff=0.35)
        year_label = Text("Year", font_size=24)
        year_label.next_to(within_axes.x_axis, DOWN, buff=0.2)
        within_eq = Tex(
            R"\mathbb{E}[\mathbb{V}(X \mid \lambda)] = \mathbb{E}(\lambda) = \frac{\alpha}{\beta} = 0.5",
            font_size=34,
        )
        within_eq.next_to(year_label, DOWN, buff=0.35)

        self.play(
            FadeIn(within_title),
            ShowCreation(within_axes),
            FadeIn(year_label),
        )
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.1, run_time=3))
        self.wait()
        self.play(Write(within_eq))
        self.wait(2)

        # Spread between drivers
        between_axes = Axes((0, 2, 0.5), (0, 2, 0.5), width=5.5, height=1.8)
        between_axes.move_to(3.4 * RIGHT + 0.8 * UP)
        between_axes.x_axis.add_numbers(np.arange(0, 2.5, 0.5), num_decimal_places=1, font_size=20)
        prior_graph = get_prior_graph(between_axes)
        sd = math.sqrt(ALPHA) / BETA
        spread = between_axes.get_area_under_graph(prior_graph, x_range=(ALPHA / BETA - sd, ALPHA / BETA + sd))
        spread.set_fill(PRIOR_COLOR, 0.35)
        between_title = Text("Between drivers", font_size=32)
        between_title.next_to(between_axes, UP, buff=0.35)
        between_title.match_y(within_title)
        rate_label = Tex(R"\lambda", font_size=30)
        rate_label.next_to(between_axes.x_axis.get_end(), RIGHT)
        between_eq = Tex(
            R"\mathbb{V}[\mathbb{E}(X \mid \lambda)] = \mathbb{V}(\lambda) = \frac{\alpha}{\beta^2} = 0.125",
            font_size=34,
        )
        between_eq.match_x(between_axes)
        between_eq.match_y(within_eq)

        self.play(
            FadeIn(between_title),
            ShowCreation(between_axes),
            FadeIn(rate_label),
            ShowCreation(prior_graph),
        )
        self.play(FadeIn(spread))
        self.wait()
        self.play(Write(between_eq))
        self.wait(2)

        # Together they make up all the variation in a random driver's claims
        within_part = R"\mathbb{E}[\mathbb{V}(X \mid \lambda)]"
        between_part = R"\mathbb{V}[\mathbb{E}(X \mid \lambda)]"
        total_eq = Tex(
            R"\mathbb{V}(X) = \mathbb{E}[\mathbb{V}(X \mid \lambda)] + \mathbb{V}[\mathbb{E}(X \mid \lambda)] = 0.5 + 0.125",
            font_size=40,
        )
        total_eq.to_edge(UP)
        total_rest = VGroup(*(
            glyph for glyph in total_eq
            if glyph not in total_eq[within_part][0] and glyph not in total_eq[between_part][0]
        ))

        self.play(
            FadeOut(title, UP),
            TransformFromCopy(within_eq[within_part][0], total_eq[within_part][0]),
            TransformFromCopy(between_eq[between_part][0], total_eq[between_part][0]),
            FadeIn(total_rest),
            run_time=1.5
        )
        self.add(total_eq)
        self.wait(2.5)

        # Their ratio is k
        k_eq = NotesTex(
            R"k = \frac{\mathbb{E}[\mathbb{V}(X \mid \lambda)]}{\mathbb{V}[\mathbb{E}(X \mid \lambda)]} = \frac{0.5}{0.125} = 4 = \beta",
            t2c={R"\beta": PRIOR_COLOR},
            font_size=40,
        )
        k_eq.next_to(VGroup(within_eq, between_eq), DOWN, buff=0.6)
        k_eq.set_x(0)

        numer = k_eq[within_part][0]
        denom = k_eq[between_part][0]
        tail = k_eq[R"= \frac{0.5}{0.125} = 4 = \beta"][0]
        head = VGroup(*(glyph for glyph in k_eq if glyph not in numer and glyph not in denom and glyph not in tail))

        self.play(
            TransformFromCopy(within_eq[within_part][0], numer),
            TransformFromCopy(between_eq[between_part][0], denom),
            FadeIn(head),
            run_time=1.5
        )
        self.wait()
        self.play(Write(tail))
        self.add(k_eq)
        self.wait(2)

        # What that means
        noisy = Text("Noisier records: bigger k, slower to trust the record", font_size=30)
        varied = Text("More varied drivers: smaller k, quicker to trust it", font_size=30)
        lessons = VGroup(noisy, varied)
        lessons.arrange(DOWN, aligned_edge=LEFT)
        lessons.to_edge(UP)
        self.play(FadeOut(total_eq, UP), FadeIn(noisy, lag_ratio=0.1))
        self.wait(2)
        self.play(FadeIn(varied, lag_ratio=0.1))
        self.wait(3)
        self.play(FadeOut(Group(*self.mobjects)))


class CredibilitySummary(InteractiveScene):
    def construct(self):
        # The formula
        t2c = {
            R"\xoverline{x}": DATA_COLOR,
            R"\mu": PRIOR_COLOR,
            "Z": Z_COLOR,
        }
        premium = NotesTex(R"\text{Credibility premium} = Z \, \xoverline{x} + (1 - Z) \, \mu", t2c=t2c, font_size=52)
        z_def = NotesTex(R"Z = \frac{n}{n + k}", t2c=t2c, font_size=52)
        k_def = NotesTex(
            R"k = \frac{\mathbb{E}[\mathbb{V}(X \mid \lambda)]}{\mathbb{V}[\mathbb{E}(X \mid \lambda)]}",
            font_size=44,
        )
        poisson_note = TexText(R"Poisson claims, Gamma$(\alpha, \beta)$ prior: $k = \beta$", font_size=32)
        poisson_note.set_fill(GREY_B)
        defs = VGroup(z_def, k_def)
        defs.arrange(RIGHT, buff=1.2)
        summary = VGroup(premium, defs, poisson_note)
        summary.arrange(DOWN, buff=0.6)
        summary.to_edge(UP, buff=0.8)
        rect = SurroundingRectangle(summary, buff=0.35)
        rect.set_stroke(Z_COLOR, 2)

        self.play(Write(premium))
        self.wait()
        self.play(FadeIn(defs, lag_ratio=0.2))
        self.wait()
        self.play(FadeIn(poisson_note, lag_ratio=0.1), ShowCreation(rect))
        self.wait(3)

        # Recall
        recall = VGroup(
            Text("Recall", font_size=32).set_color(Z_COLOR),
            TexText(R"With $\beta = 4$, how many years of claims give $Z = 0.8$?", font_size=36),
        )
        recall.arrange(RIGHT, buff=0.3)
        recall.next_to(rect, DOWN, buff=0.8)
        answer = NotesTex(R"\frac{n}{n + 4} = 0.8 \quad \Rightarrow \quad n = 16", t2c={"16": Z_COLOR}, font_size=44)
        answer.next_to(recall, DOWN, buff=0.5)

        self.play(FadeIn(recall, 0.25 * UP))
        self.wait(4)
        self.play(Write(answer))
        self.wait(4)


SCENES_IN_ORDER = [
    WhoseNumber,
    PortfolioPrior,
    YearByYear,
    WhereIsTheMean,
    BalanceBeam,
    WithinVsBetween,
    CredibilitySummary,
]
