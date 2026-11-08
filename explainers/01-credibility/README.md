# A111-01 Credibility: why the premium is a weighted average

**The idea:** in the Poisson/gamma model, the Bayesian estimate of a driver's claim rate is exactly Z·x̄ + (1 − Z)·μ with Z = n/(n + β), and β is the ratio of the variation within one driver to the variation between drivers.
**Syllabus:** 5 Bayesian statistics: credibility theory (Bayesian credibility, the Poisson/gamma model, and the k of empirical Bayes credibility). CMP: the credibility theory chapters.
**Length:** 3:34, 7 scenes. **Status:** final (8 November 2026).

## Storyboard

| Time | Scene | What happens | Words on screen |
|---|---|---|---|
| 0:00 | WhoseNumber | One driver's four years: 1, 0, 2, 0 claims. Their average 0.75 and the portfolio's 0.5 sit on a number line with a question mark between them. | How many claims should we expect from this driver next year? x̄ = 0.75, μ = 0.5 |
| 0:26 | PortfolioPrior | A hundred drivers, each with their own claim rate, stack into a histogram; the Gamma(2, 4) curve fits it, mean 0.5. Our driver's λ is unknown. | Each driver has their own claim rate, λ. λ ~ Gamma(α, β), μ = α/β = 0.5 |
| 0:54 | YearByYear | Each year's claims update the curve: Gamma(3, 5) after year 1, then Gamma(α + Σx, β + n), ending at Gamma(5, 8). | posterior ∝ prior × likelihood. Sharper, and pulled toward this driver's record |
| 1:27 | WhereIsTheMean | Predict where the posterior mean is. It is 0.625, exactly halfway between μ and x̄. The algebra splits the posterior mean into Z·x̄ + (1 − Z)·μ. | Predict: where is the mean of the yellow curve? Z = n/(n + β) = 0.5 |
| 2:01 | BalanceBeam | A beam with weight β = 4 at μ and weight n at x̄. As n grows through 1, 4, 12, 36 and 100, the balance point slides toward x̄. | A weighted average is a balance point. As n → ∞, Z → 1 |
| 2:39 | WithinVsBetween | Year-to-year noise for one driver against the spread of λ across drivers; the law of total variance; their ratio is k = 4 = β. | Why β? Two kinds of variation. k = 0.5 / 0.125 = 4 = β |
| 3:15 | CredibilitySummary | The boxed credibility premium, Z and k, then the recall question and its answer. | Credibility premium = Z x̄ + (1 − Z) μ |

## Recall

With β = 4, how many years of claims give Z = 0.8? n/(n + 4) = 0.8, so n = 16.

## Notes

`scripts/check_video.py` flags three top margins: the PortfolioPrior caption at 0.37 units, and the exits of the WhereIsTheMean prompt and the WithinVsBetween title. They were accepted when this explainer was made.

## Render

Cloud: `scripts/render.sh final explainers/01-credibility`
PC: `.\render explainers\01-credibility\main.py -a -w`
