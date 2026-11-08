# A111 syllabus map

A111 follows the IFoA CS1 syllabus, and ActEd's CS1 Combined Materials Pack covers it. The areas and weights below are from the IFoA CS1 syllabus for the 2025 exams. The syllabus objectives printed in Sabelo's CMP are the authority on what's examinable.

| Area | Weight | Covers | Explainers |
|---|---|---|---|
| 1 Data analysis | 10% | the purpose of data analysis; exploratory data analysis, correlation, principal components | |
| 2 Random variables and distributions | 20% | common distributions and simulating from them; joint distributions; expectations and conditional expectations; generating functions; the central limit theorem; sampling distributions | |
| 3 Statistical inference | 25% | method of moments and maximum likelihood, and their properties; confidence and prediction intervals; hypothesis tests and goodness of fit | |
| 4 Regression | 30% | linear regression; generalised linear models | |
| 5 Bayesian statistics | 15% | priors and posteriors, Bayesian estimators, credibility theory | [01](explainers/01-credibility) |

## CMP chapters

To be filled in from the CMP's contents page the first time Claude reads it: each chapter's number, title, syllabus area and the explainers that cover it, in our own words.

| Chapter | Title | Area | Explainers |
|---|---|---|---|

## Explainer ideas

Places where a picture tends to do what the notes can't. A starting list, to check against the CMP.

| Area | Idea |
|---|---|
| 1 | Correlation: what r measures, and very different scatter plots with the same r |
| 1 | Principal components: turning the axes to the direction of greatest spread |
| 2 | Simulation by inverse transform: uniform numbers pushed through an inverse CDF |
| 2 | Why the MGF of a sum of independent variables is the product of their MGFs |
| 2 | Conditional expectation and the law of total variance |
| 2 | The central limit theorem: sums of a skewed variable turning normal |
| 2 | Why (n − 1)S²/σ² is chi-square on n − 1 degrees of freedom, and the t distribution's fatter tails |
| 3 | Maximum likelihood: the likelihood curve and its peak, and why the log changes nothing |
| 3 | Bias, variance and mean squared error: when a biased estimator wins |
| 3 | What "95% confidence" means: intervals from repeated samples covering the true mean |
| 3 | Size and power: two distributions, one critical value, and the trade-off between the errors |
| 3 | Chi-square goodness of fit: observed against expected, one cell at a time |
| 4 | Least squares: the line that makes the squared residuals smallest |
| 4 | Splitting the variation: total = regression + residual, and R² |
| 4 | Confidence and prediction intervals in regression: why the prediction band is wider |
| 4 | GLMs: the link function, and deviance as distance from the saturated model |
| 5 | Bayesian updating with a beta prior and binomial data |
| 5 | Loss functions: the posterior mean, median and mode as the best guesses under three losses |
| 5 | Empirical Bayes credibility: estimating k from many risks' data |
