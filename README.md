# hypnofunk 🌙

<p align="center">
  <img src="https://github.com/rahulvenugopal/PyKumbogram/blob/main/Logo.png" width="400" alt="hypnofunk logo">
</p>


[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/1142052114.svg)](https://doi.org/10.5281/zenodo.18713864)

**hypnofunk** is a high-performance toolkit for sleep researchers. It calculates 40+ macrostructure parameters, performs first-order **Markov-chain transition analysis**, and detects sleep cycles—all from simple hypnogram sequences.

---

## Installation

```bash
# Core package
pip install hypnofunk

# Full installation — includes Lempel-Ziv complexity, plotting, and EDF support
pip install hypnofunk[full]
```

---

## Supported Input Formats

### Hypnogram data (in-memory)

hypnofunk accepts standard AASM sleep stage labels (`W`, `N1`, `N2`, `N3`, `R`) as:
- **Python lists**, **NumPy arrays**, or **Pandas Series**.

### File formats (via example workflow)

The included [`polyman_analysis.py`](examples/polyman_analysis.py) provides a turnkey solution for:
- **EDF / EDF+**: Reads Polyman-style annotations directly.
- **CSV**: Processes exported spreadsheets with epoch-by-epoch scoring.

---

## Standard Analysis Parameters

hypnofunk uses industry-standard defaults, all of which are configurable via function arguments:

| Parameter | Default | Logic |
|---|---|---|
| `epoch_duration` | `30s` | The standard temporal resolution for clinical sleep scoring. |
| `max_wake_epochs` | `10` | Keeps 5 mins of wake after final sleep before trimming terminal wake. |
| `min_nrem_epochs` | `30` | Defines a NREM cycle as ≥15 mins of continuous NREM starting with N2. |
| `min_rem_epochs` | `10` | Subsequent REM cycles must be ≥5 mins (1st REM cycle can be any length). |

---

## Sleep Cycle Detection Logic

Our detection algorithms follow standard clinical research criteria to ensure consistency across datasets:

### NREM Cycles 🌙
A sequence is identified as a NREM cycle if:
1.  It **starts with N2** sleep.
2.  It contains at least **15 minutes** (30 epochs) of continuous NREM (N1, N2, or N3).
3.  This prevents short "transitional" light sleep from being miscounted as a full cycle.

### REM Cycles ⚡
REM detection handles the unique nature of early-night sleep:
1.  **First REM Cycle**: Accepted at any length (standard research practice).
2.  **Subsequent REM Cycles**: Must be at least **5 minutes** (10 epochs) long.
3.  This ensures that REM "fragments" commonly found in fragmented sleep don't artificially inflate cycle counts.

---

## Markov-Chain Transition Analysis 🔄

hypnofunk provides a robust framework for quantifying sleep stability and fragmentation using first-order Markov chains:

- **Full Transition Matrix**: A 5×5 matrix of probabilities for transitions between every sleep stage (W, N1, N2, N3, R).
- **Stage Persistence**: The probability of remaining in a specific stage (diagonal nodes of the Markov chain).
- **Awakening Probabilities**: The specific likelihood of transitioning to Wake from each individual sleep stage.
- **Sleep Compactness**: A global consolidation index calculated as the mean persistence across all sleep stages.
- **Fragility Metrics**: Proportion of all transitions that result in awakening.

---

## Quick Start

```python
from hypnofunk import hypnoman, analyze_transitions

# 10 epochs Wake, 50 N2, 30 N3, 20 REM, 5 Wake
hypnogram = ["W"]*10 + ["N2"]*50 + ["N3"]*30 + ["R"]*20 + ["W"]*5

# Get 40+ parameters in one line (Macrostructure)
params = hypnoman(hypnogram, epoch_duration=30)
print(f"TST: {params['TST'].values[0]:.1f} min | SE: {params['Sleep_efficiency'].values[0]:.1f}%")

# Analyze stage transitions & Markov chain dynamics
trans = analyze_transitions(hypnogram)
print(f"Sleep Compactness: {trans['Sleep_Compactness'].values[0]:.3f}")
print(f"Prob. N2 Persistence: {trans['Persistence_N2'].values[0]:.3f}")
```

---

## Core Functionality

### Sleep Macrostructure — `hypnoman()`
Returns a single-row `pd.DataFrame` containing:
- **Time metrics:** TRT, TST, SPT, WASO, SOL.
- **Efficiency:** Sleep Efficiency (SE), Sleep Maintenance Efficiency (SME).
- **Stage statistics:** Duration, percentage, and onset latency for all stages.
- **Streak analysis:** Longest, mean, and median "runs" (streaks) for every stage.
- **Information Theory:** **Lempel-Ziv complexity (LZc)** — a non-linear measure of sleep stage variety (requires `antropy`).

### Transition Analysis — `analyze_transitions()`
Performs the Markov-chain analysis described above, returning:
- Total transitions (fragmentation count).
- Probability of awakening.
- Sleep compactness index.
- Per-stage persistence and awakening probabilities.
- Complete transition matrix (25 probability values).

---

## API Reference

### `hypnofunk.io`
- `read_edf_hypnogram()`: Standardized loader for Polyman EDF and EDF+ files.

### `hypnofunk.core`
- `hypnoman()`: The main entry point for macrostructure metrics.
- `find_nremstretches()` & `find_rem_stretches()`: Cycle detection engines.
- `trim_terminal_wake()`: Utility to clean extended wake at the end of recordings.

### `hypnofunk.transitions`
- `analyze_transitions()`: Main entry point for fragmentation and Markov metrics.
- `compute_transition_matrix()`: Raw transition probability calculations.
- `compute_sleep_compactness()`: Statistical consolidated sleep index.

### `hypnofunk.visualization`
- `plot_hypnogram_with_cycles()`: Clean hypnograms with cycle-overlay bars.
- `plot_transition_matrix()`: Heatmap visualization of stage dynamics (Markov matrix).

---

## Citation

```bibtex
@software{hypnofunk2026,
  author = {Venugopal, Rahul},
  title  = {hypnofunk: A Python package for sleep analysis},
  year   = {2026},
  url    = {https://github.com/rahulvenugopal/hypnofunk}
}
```

## License
MIT — see [LICENSE](LICENSE) for details. Developed by **Rahul Venugopal**.
