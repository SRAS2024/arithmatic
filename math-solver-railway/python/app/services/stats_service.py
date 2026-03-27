import numpy as np
from scipy import stats as scipy_stats
from typing import Any, Optional
import re
import math


class StatsService:
    """Statistics and probability computations."""

    def process(self, expression: str) -> dict:
        """Process a statistics/probability expression."""
        expr_lower = expression.lower().strip()

        # Try to extract data
        data = self._extract_data(expression)

        if "mean" in expr_lower or "average" in expr_lower:
            return self.compute_mean(data)
        elif "median" in expr_lower:
            return self.compute_median(data)
        elif "mode" in expr_lower:
            return self.compute_mode(data)
        elif "std" in expr_lower or "standard deviation" in expr_lower or "stdev" in expr_lower:
            return self.compute_std(data)
        elif "variance" in expr_lower or "var(" in expr_lower:
            return self.compute_variance(data)
        elif "correlation" in expr_lower or "corr" in expr_lower:
            return self.compute_correlation(expression)
        elif "regression" in expr_lower:
            return self.compute_regression(expression)
        elif "percentile" in expr_lower:
            return self.compute_percentile(expression, data)
        elif "z-score" in expr_lower or "z_score" in expr_lower or "zscore" in expr_lower:
            return self.compute_z_score(expression)
        elif "binomial" in expr_lower:
            return self.binomial_probability(expression)
        elif "poisson" in expr_lower:
            return self.poisson_probability(expression)
        elif "normal" in expr_lower or "gaussian" in expr_lower:
            return self.normal_probability(expression)
        elif "chi" in expr_lower and "square" in expr_lower:
            return self.chi_square(expression)
        elif "t-test" in expr_lower or "t_test" in expr_lower or "ttest" in expr_lower:
            return self.t_test(expression)
        elif "probability" in expr_lower:
            return self.basic_probability(expression)
        elif data is not None and len(data) > 0:
            return self.descriptive_stats(data)
        else:
            return {"answer": "Could not parse statistics problem", "steps": [], "latex": ""}

    def _extract_data(self, expression: str) -> Optional[list]:
        """Extract numerical data from expression."""
        # Find numbers in brackets, parens, or just listed
        patterns = [
            r"\[([^\]]+)\]",
            r"\(([^)]+)\)",
            r"data\s*[:=]\s*(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, expression)
            if match:
                nums_str = match.group(1)
                try:
                    nums = [float(x.strip()) for x in re.split(r"[,;\s]+", nums_str) if x.strip()]
                    if nums:
                        return nums
                except ValueError:
                    continue

        # Try extracting all numbers
        nums = re.findall(r"-?\d+\.?\d*", expression)
        if len(nums) >= 3:
            return [float(n) for n in nums]
        return None

    def descriptive_stats(self, data: list) -> dict:
        """Compute descriptive statistics for a dataset."""
        steps = []
        try:
            arr = np.array(data, dtype=float)
            n = len(arr)
            steps.append(f"Dataset: {data}")
            steps.append(f"Count: n = {n}")

            mean_val = np.mean(arr)
            steps.append(f"Mean: {mean_val:.6f}")

            median_val = np.median(arr)
            steps.append(f"Median: {median_val:.6f}")

            mode_result = scipy_stats.mode(arr, keepdims=True)
            mode_val = mode_result.mode[0]
            steps.append(f"Mode: {mode_val}")

            std_val = np.std(arr, ddof=1) if n > 1 else 0
            steps.append(f"Std Dev (sample): {std_val:.6f}")

            var_val = np.var(arr, ddof=1) if n > 1 else 0
            steps.append(f"Variance (sample): {var_val:.6f}")

            min_val = np.min(arr)
            max_val = np.max(arr)
            range_val = max_val - min_val
            steps.append(f"Min: {min_val}, Max: {max_val}, Range: {range_val}")

            q1 = np.percentile(arr, 25)
            q3 = np.percentile(arr, 75)
            iqr = q3 - q1
            steps.append(f"Q1: {q1:.6f}, Q3: {q3:.6f}, IQR: {iqr:.6f}")

            skew = scipy_stats.skew(arr) if n >= 3 else 0
            kurt = scipy_stats.kurtosis(arr) if n >= 4 else 0
            steps.append(f"Skewness: {skew:.6f}")
            steps.append(f"Kurtosis: {kurt:.6f}")

            answer = (
                f"n={n}, mean={mean_val:.4f}, median={median_val:.4f}, "
                f"std={std_val:.4f}, min={min_val}, max={max_val}"
            )

            return {
                "answer": answer,
                "steps": steps,
                "latex": f"\\bar{{x}} = {mean_val:.4f}, \\, s = {std_val:.4f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_mean(self, data: list) -> dict:
        steps = []
        try:
            if not data:
                return {"answer": "No data provided", "steps": [], "latex": ""}
            arr = np.array(data, dtype=float)
            steps.append(f"Data: {data}")
            steps.append(f"Sum: {np.sum(arr)}")
            steps.append(f"Count: {len(arr)}")
            result = np.mean(arr)
            steps.append(f"Mean = Sum / Count = {np.sum(arr)} / {len(arr)} = {result}")
            return {"answer": str(result), "steps": steps, "latex": f"\\bar{{x}} = {result:.6f}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_median(self, data: list) -> dict:
        steps = []
        try:
            if not data:
                return {"answer": "No data provided", "steps": [], "latex": ""}
            arr = np.sort(np.array(data, dtype=float))
            steps.append(f"Sorted data: {arr.tolist()}")
            result = np.median(arr)
            n = len(arr)
            if n % 2 == 1:
                steps.append(f"Odd count ({n}), median is middle value")
            else:
                steps.append(f"Even count ({n}), median is average of two middle values")
            steps.append(f"Median = {result}")
            return {"answer": str(result), "steps": steps, "latex": f"\\tilde{{x}} = {result}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_mode(self, data: list) -> dict:
        steps = []
        try:
            if not data:
                return {"answer": "No data provided", "steps": [], "latex": ""}
            arr = np.array(data, dtype=float)
            mode_result = scipy_stats.mode(arr, keepdims=True)
            mode_val = mode_result.mode[0]
            count = mode_result.count[0]
            steps.append(f"Data: {data}")
            steps.append(f"Mode: {mode_val} (appears {int(count)} times)")
            return {"answer": str(mode_val), "steps": steps, "latex": f"\\text{{mode}} = {mode_val}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_std(self, data: list) -> dict:
        steps = []
        try:
            if not data:
                return {"answer": "No data provided", "steps": [], "latex": ""}
            arr = np.array(data, dtype=float)
            mean = np.mean(arr)
            n = len(arr)
            steps.append(f"Data: {data}")
            steps.append(f"Mean: {mean}")
            deviations = arr - mean
            sq_devs = deviations ** 2
            steps.append(f"Squared deviations: {sq_devs.tolist()}")
            result = np.std(arr, ddof=1) if n > 1 else 0
            steps.append(f"Sample std dev = sqrt(sum of sq dev / (n-1)) = {result:.6f}")
            return {"answer": str(round(result, 6)), "steps": steps, "latex": f"s = {result:.6f}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_variance(self, data: list) -> dict:
        steps = []
        try:
            if not data:
                return {"answer": "No data provided", "steps": [], "latex": ""}
            arr = np.array(data, dtype=float)
            n = len(arr)
            result = np.var(arr, ddof=1) if n > 1 else 0
            steps.append(f"Data: {data}")
            steps.append(f"Sample variance = {result:.6f}")
            return {"answer": str(round(result, 6)), "steps": steps, "latex": f"s^2 = {result:.6f}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_percentile(self, expression: str, data: list) -> dict:
        steps = []
        try:
            if not data:
                return {"answer": "No data provided", "steps": [], "latex": ""}
            # Extract percentile value
            match = re.search(r"(\d+)\s*(?:th|st|nd|rd)?\s*percentile", expression, re.IGNORECASE)
            p = int(match.group(1)) if match else 50
            arr = np.array(data, dtype=float)
            result = np.percentile(arr, p)
            steps.append(f"Data: {data}")
            steps.append(f"{p}th percentile = {result}")
            return {"answer": str(result), "steps": steps, "latex": f"P_{{{p}}} = {result}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_z_score(self, expression: str) -> dict:
        steps = []
        try:
            nums = re.findall(r"-?\d+\.?\d*", expression)
            if len(nums) >= 3:
                x, mu, sigma = float(nums[0]), float(nums[1]), float(nums[2])
            elif len(nums) == 1:
                x = float(nums[0])
                mu, sigma = 0, 1
            else:
                return {"answer": "Provide x, mean, and std dev", "steps": [], "latex": ""}

            z = (x - mu) / sigma
            steps.append(f"x = {x}, mu = {mu}, sigma = {sigma}")
            steps.append(f"z = (x - mu) / sigma = ({x} - {mu}) / {sigma} = {z:.4f}")
            p_value = scipy_stats.norm.cdf(z)
            steps.append(f"P(Z <= {z:.4f}) = {p_value:.6f}")

            return {"answer": f"z = {z:.4f}", "steps": steps, "latex": f"z = {z:.4f}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_correlation(self, expression: str) -> dict:
        steps = []
        try:
            # Try to extract two datasets
            matches = re.findall(r"\[([^\]]+)\]", expression)
            if len(matches) >= 2:
                x = [float(n.strip()) for n in matches[0].split(",")]
                y = [float(n.strip()) for n in matches[1].split(",")]
            else:
                return {"answer": "Provide two datasets in [a,b,...] format", "steps": [], "latex": ""}

            r, p_value = scipy_stats.pearsonr(x, y)
            steps.append(f"X: {x}")
            steps.append(f"Y: {y}")
            steps.append(f"Pearson correlation: r = {r:.6f}")
            steps.append(f"P-value: {p_value:.6f}")

            return {"answer": f"r = {r:.6f}", "steps": steps, "latex": f"r = {r:.6f}"}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def compute_regression(self, expression: str) -> dict:
        steps = []
        try:
            matches = re.findall(r"\[([^\]]+)\]", expression)
            if len(matches) >= 2:
                x = np.array([float(n.strip()) for n in matches[0].split(",")])
                y = np.array([float(n.strip()) for n in matches[1].split(",")])
            else:
                return {"answer": "Provide two datasets", "steps": [], "latex": ""}

            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, y)
            steps.append(f"X: {x.tolist()}")
            steps.append(f"Y: {y.tolist()}")
            steps.append(f"Slope: {slope:.6f}")
            steps.append(f"Intercept: {intercept:.6f}")
            steps.append(f"R-squared: {r_value**2:.6f}")
            steps.append(f"P-value: {p_value:.6f}")

            return {
                "answer": f"y = {slope:.4f}x + {intercept:.4f} (R^2 = {r_value**2:.4f})",
                "steps": steps,
                "latex": f"y = {slope:.4f}x + {intercept:.4f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def binomial_probability(self, expression: str) -> dict:
        steps = []
        try:
            nums = re.findall(r"-?\d+\.?\d*", expression)
            if len(nums) >= 3:
                n, k, p = int(float(nums[0])), int(float(nums[1])), float(nums[2])
            else:
                return {"answer": "Provide n, k, p for binomial(n, k, p)", "steps": [], "latex": ""}

            prob = scipy_stats.binom.pmf(k, n, p)
            cum_prob = scipy_stats.binom.cdf(k, n, p)
            mean = n * p
            std = math.sqrt(n * p * (1 - p))

            steps.append(f"Binomial(n={n}, p={p})")
            steps.append(f"P(X = {k}) = C({n},{k}) * {p}^{k} * {1-p}^{n-k}")
            steps.append(f"P(X = {k}) = {prob:.6f}")
            steps.append(f"P(X <= {k}) = {cum_prob:.6f}")
            steps.append(f"Mean = np = {mean}")
            steps.append(f"Std Dev = sqrt(np(1-p)) = {std:.6f}")

            return {
                "answer": f"P(X={k}) = {prob:.6f}",
                "steps": steps,
                "latex": f"P(X = {k}) = {prob:.6f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def poisson_probability(self, expression: str) -> dict:
        steps = []
        try:
            nums = re.findall(r"-?\d+\.?\d*", expression)
            if len(nums) >= 2:
                lam, k = float(nums[0]), int(float(nums[1]))
            else:
                return {"answer": "Provide lambda and k for Poisson", "steps": [], "latex": ""}

            prob = scipy_stats.poisson.pmf(k, lam)
            cum_prob = scipy_stats.poisson.cdf(k, lam)

            steps.append(f"Poisson(lambda={lam})")
            steps.append(f"P(X = {k}) = e^(-{lam}) * {lam}^{k} / {k}!")
            steps.append(f"P(X = {k}) = {prob:.6f}")
            steps.append(f"P(X <= {k}) = {cum_prob:.6f}")

            return {
                "answer": f"P(X={k}) = {prob:.6f}",
                "steps": steps,
                "latex": f"P(X = {k}) = {prob:.6f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def normal_probability(self, expression: str) -> dict:
        steps = []
        try:
            nums = re.findall(r"-?\d+\.?\d*", expression)
            if len(nums) >= 3:
                x, mu, sigma = float(nums[0]), float(nums[1]), float(nums[2])
            elif len(nums) >= 1:
                x = float(nums[0])
                mu, sigma = 0, 1
            else:
                return {"answer": "Provide x, mean, sigma", "steps": [], "latex": ""}

            z = (x - mu) / sigma
            prob_less = scipy_stats.norm.cdf(x, mu, sigma)
            prob_greater = 1 - prob_less
            pdf_val = scipy_stats.norm.pdf(x, mu, sigma)

            steps.append(f"Normal(mu={mu}, sigma={sigma})")
            steps.append(f"x = {x}, z-score = {z:.4f}")
            steps.append(f"P(X < {x}) = {prob_less:.6f}")
            steps.append(f"P(X > {x}) = {prob_greater:.6f}")
            steps.append(f"f({x}) = {pdf_val:.6f}")

            return {
                "answer": f"P(X < {x}) = {prob_less:.6f}",
                "steps": steps,
                "latex": f"P(X < {x}) = {prob_less:.6f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def chi_square(self, expression: str) -> dict:
        steps = []
        try:
            matches = re.findall(r"\[([^\]]+)\]", expression)
            if len(matches) >= 2:
                observed = [float(n.strip()) for n in matches[0].split(",")]
                expected = [float(n.strip()) for n in matches[1].split(",")]
            else:
                return {"answer": "Provide observed and expected arrays", "steps": [], "latex": ""}

            chi2, p_value = scipy_stats.chisquare(observed, expected)
            steps.append(f"Observed: {observed}")
            steps.append(f"Expected: {expected}")
            steps.append(f"Chi-square statistic: {chi2:.6f}")
            steps.append(f"P-value: {p_value:.6f}")
            steps.append(f"Degrees of freedom: {len(observed) - 1}")

            return {
                "answer": f"chi^2 = {chi2:.6f}, p = {p_value:.6f}",
                "steps": steps,
                "latex": f"\\chi^2 = {chi2:.6f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def t_test(self, expression: str) -> dict:
        steps = []
        try:
            matches = re.findall(r"\[([^\]]+)\]", expression)
            if len(matches) >= 2:
                sample1 = [float(n.strip()) for n in matches[0].split(",")]
                sample2 = [float(n.strip()) for n in matches[1].split(",")]
                t_stat, p_value = scipy_stats.ttest_ind(sample1, sample2)
                steps.append(f"Sample 1: {sample1}")
                steps.append(f"Sample 2: {sample2}")
            elif len(matches) >= 1:
                sample1 = [float(n.strip()) for n in matches[0].split(",")]
                t_stat, p_value = scipy_stats.ttest_1samp(sample1, 0)
                steps.append(f"Sample: {sample1}")
                steps.append("One-sample t-test against mu=0")
            else:
                return {"answer": "Provide sample data in [a,b,...] format", "steps": [], "latex": ""}

            steps.append(f"t-statistic: {t_stat:.6f}")
            steps.append(f"P-value: {p_value:.6f}")
            sig = "significant" if p_value < 0.05 else "not significant"
            steps.append(f"Result at alpha=0.05: {sig}")

            return {
                "answer": f"t = {t_stat:.6f}, p = {p_value:.6f} ({sig})",
                "steps": steps,
                "latex": f"t = {t_stat:.6f}",
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def basic_probability(self, expression: str) -> dict:
        steps = []
        try:
            nums = re.findall(r"\d+", expression)
            if "of" in expression.lower() and len(nums) >= 2:
                favorable = int(nums[0])
                total = int(nums[1])
                prob = favorable / total
                steps.append(f"Favorable outcomes: {favorable}")
                steps.append(f"Total outcomes: {total}")
                steps.append(f"P = {favorable}/{total} = {prob:.6f}")
                return {
                    "answer": f"P = {favorable}/{total} = {prob:.6f}",
                    "steps": steps,
                    "latex": f"P = \\frac{{{favorable}}}{{{total}}} = {prob:.6f}",
                }
            return {"answer": "Could not parse probability problem", "steps": steps, "latex": ""}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}
