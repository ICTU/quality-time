# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "matplotlib>=3.10.8",
# ]
# ///
"""Simulate code bases to translate SIG-TUV tiers for unit size to Quality-time metric target.

Developed with use of Claude Sonnet 4.5.
"""

import random

import matplotlib.pyplot as plt


def generate_codebase() -> list[int]:
    """Generate a simulated codebase with hopefully realistic unit size distribution.

    Returns a list of integers representing the size (in lines of code) of each unit
    (function, method, procedure) in the codebase.

    The simulation uses log-normal distributions based on empirical observations that
    real-world code metrics tend to follow log-normal patterns, where most units are
    small (10-20 lines) with a long tail of larger units.

    Number of units:
        Generated from log-normal(μ=6.5, σ=1.0), producing a codebase with:
        - Mode around 250 lines
        - Median about 670 lines
        - Mean about 1100 lines

    Unit sizes:
        Generated from log-normal(μ=2.7, σ=0.7), producing unit sizes with:
        - Mode about 9 lines
        - Median around 15 lines
        - Mean around 19 lines

    Returns:
        List of integers, where each integer represents the size of one unit in lines of code.
    """
    number_of_units = round(random.lognormvariate(mu=6.5, sigma=1.0))
    return [max(1, round(random.lognormvariate(mu=2.7, sigma=0.7))) for _ in range(number_of_units)]


def generate_codebases(number: int) -> list[list[int]]:
    """Generate code bases."""
    return [generate_codebase() for _ in range(number)]


def unit_size_4_star(codebase: list[int]) -> bool:
    """Evaluate whether the code base is eligible for 4 stars."""
    codebase_size = sum(codebase)
    return sum(unit for unit in codebase if unit > 15) / codebase_size <= 0.471 and \
        sum(unit for unit in codebase if unit > 30) / codebase_size <= 0.231 and \
        sum(unit for unit in codebase if unit > 60) / codebase_size <= 0.083


def fraction_units_too_long(codebase: list[int], max_unit_size: int = 20) -> int:
    """Calculate the fraction of units that is too long as would be reported by SonarQube."""
    return round(len([unit for unit in codebase if unit > max_unit_size]) / len(codebase) * 100)


ok = {}
not_ok = {}
for codebase in generate_codebases(100_000):
    fraction = fraction_units_too_long(codebase)
    star = unit_size_4_star(codebase)
    for target in range(100):
        prediction = not_ok if fraction <= target and not star else ok
        prediction[target] = prediction.get(target, 0) + 1

targets = sorted(ok.keys())
precision = [round(ok[t] / (ok[t] + not_ok.get(t, 0)) * 100) for t in targets]

plt.figure(figsize=(10, 6))
plt.plot(targets, precision, linewidth=2, color='#3266ad')
plt.fill_between(targets, precision, alpha=0.1, color='#3266ad')
plt.xlabel('Quality-time target (max % units > 20 lines)', fontsize=12)
plt.ylabel('Precision (%)', fontsize=12)
plt.title('Precision of Quality-time metric for predicting SIG TÜV 4-star certification', fontsize=13)
plt.grid(True, alpha=0.3)
plt.xlim(0, 100)
plt.ylim(0, 105)
plt.tight_layout()
plt.savefig('sigsim_results.png', dpi=150, bbox_inches='tight')
print(f"Plot saved to sigsim_results.png")
plt.show()
