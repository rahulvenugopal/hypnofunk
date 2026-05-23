# hypnofunk 🌙 🕺💤

A Python package for hypnogram analysis. `hypnofunk` provides a streamlined, open-source toolkit to extract structural and continuous data from sleep stages, evaluate Markov-chain stage transitions, and analyze polysomnography (PSG) macro-architecture.

<p align="center">
  <img src="https://github.com/rahulvenugopal/PyKumbogram/blob/main/Logo.png" width="400" alt="hypnofunk logo">
</p>

# In next release (June 2026)
1. Use edf reader instead of heavy mne to read edf annotations
2. Better handling of transitions.py function to report sleep compactness correctly even when say N1 stage is not present
3. Better documentation for onset (for example R onset is calculated from onset of a sleep stage and not from the start of the hypnogram)
4. Improve annotation reading and autofixes when there are non sleep annotations like movements, ?s, other labels like leg movement or apnea

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

## Hypnogram Macrostructure Parameters

hypnofunk uses industry-standard defaults, all of which are configurable via function arguments:

| Parameter | Default | Logic |
|---|---|---|
| `epoch_duration` | `30s` | The standard temporal resolution for clinical sleep scoring. |
| `max_wake_epochs` | `10` | Keeps 5 mins of wake after final sleep before trimming terminal wake. |
| `min_nrem_epochs` | `30` | Defines a NREM cycle as ≥15 mins of continuous NREM starting with N2. |
| `min_rem_epochs` | `10` | Subsequent REM cycles must be ≥5 mins (1st REM cycle can be any length). |

### 🕒 Global Sleep Durations
* **TIB (Time In Bed):** `Total number of epochs × epoch_length`
    * *What it conveys:* The absolute total recording duration from "lights out" to "lights on."
* **SPT (Sleep Period Time):** `(Epoch of final sleep awakening - Epoch of initial sleep onset) × epoch_length`
    * *What it conveys:* The boundary-to-boundary time elapsed from the very first moment of sleep to the final awakening.
* **TST (Total Sleep Time):** `Sum of all sleep epochs (N1 + N2 + N3 + REM) × epoch_length`
    * *What it conveys:* The true total time spent asleep during the entire recording.
* **WT (Wake Time):** `Sum of all Wake epochs × epoch_length`
    * *What it conveys:* The total cumulative time spent awake while in bed.

### ⏱️ Latencies & Continuity
* **SOL (Sleep Onset Latency):** `(Index of first sleep epoch - Index of lights out) × epoch_length`
    * *What it conveys:* The time it takes to initially transition from wakefulness into any stage of sleep.
* **LPS (Latency to Persistent Sleep):** `(Index of first epoch of 10 consecutive minutes of sleep - Index of lights out) × epoch_length`
    * *What it conveys:* The time required to achieve a stable, sustained, and uninterrupted block of sleep.
* **REML (REM Latency):** `(Index of first REM epoch - Index of first sleep epoch) × epoch_length`
    * *What it conveys:* The duration from initial sleep onset until the brain enters its first cycle of Rapid Eye Movement sleep.
* **WASO (Wake After Sleep Onset):** `Sum of Wake epochs strictly bounded between the first and last sleep epochs × epoch_length`
    * *What it conveys:* The total amount of awake time that fragments and disrupts the main sleep period.

### 📈 Efficiency Indices
* **SE (Sleep Efficiency):** `(TST / TIB) × 100`
    * *What it conveys:* The overall percentage of Time in Bed successfully spent asleep, acting as a primary marker of sleep quality.
* **SME (Sleep Maintenance Efficiency):** `(TST / SPT) × 100`
    * *What it conveys:* The efficiency of sleep continuity, isolating the ability to stay asleep by ignoring initial sleep latency.

### 🧠 Stage-Specific Durations
* **W (Wake Duration):** `Count of Wake epochs × epoch_length`
    * *What it conveys:* Total volume of wakefulness.
* **N1 (Stage 1 Duration):** `Count of N1 epochs × epoch_length`
    * *What it conveys:* Total volume of transitional, light sleep.
* **N2 (Stage 2 Duration):** `Count of N2 epochs × epoch_length`
    * *What it conveys:* Total volume of intermediate, stable sleep (typically the majority of the night).
* **N3 (Stage 3 / SWS Duration):** `Count of N3 epochs × epoch_length`
    * *What it conveys:* Total volume of deep, physically restorative slow-wave sleep.
* **REM (REM Duration):** `Count of REM epochs × epoch_length`
    * *What it conveys:* Total volume of dream-state, cognitively restorative sleep.

### 📊 Stage Percentages (Relative to TST and SPT)
* **%N1, %N2, %N3, %REM (Percentage of TST):** `(Stage Duration / TST) × 100`
    * *What it conveys:* The internal architecture and proportion of the total sleep spent in each specific stage.
* **%W_SPT, %N1_SPT, %N2_SPT, %N3_SPT, %REM_SPT (Percentage of SPT):** `(Stage Duration / SPT) × 100`
    * *What it conveys:* The composition of the sleep period, factoring in the WASO (Wake After Sleep Onset) as part of the denominator.

### 🔀 Fragmentation & Markov-Chain Transitions
* **Num_Awak (Number of Awakenings):** `Count of transitions where previous stage ∈ [N1, N2, N3, REM] and current stage = W`
    * *What it conveys:* The absolute number of times the subject woke up after initially falling asleep.
* **Awak_Index (Awakening Index):** `Num_Awak / (TST in hours)`
    * *What it conveys:* The frequency of awakenings normalized per hour of sleep.
* **Num_Shifts (Number of Stage Shifts):** `Count of transitions where Stage(t) ≠ Stage(t-1)`
    * *What it conveys:* A gross measure of general sleep instability and macro-architectural fragmentation.
* **Shift_Index:** `Num_Shifts / (TST in hours)`
    * *What it conveys:* The frequency of moving between any two sleep stages normalized per hour of sleep.
* **Transition Matrix (First-Order Markov Probabilities):** `Count of transitions (Stage X → Stage Y) / Total outbound transitions from Stage X`
    * *What it conveys:* The mathematical probability (from 0 to 1) of moving directly from one specific physiological state to another.
* **Transition Counts:** `Absolute frequency of (Stage X → Stage Y)`
    * *What it conveys:* The raw count of specific state changes, useful for mapping specific pathological patterns (e.g., REM → Wake).

### 📏 Bout Dynamics
* **Bout_Count (per stage):** `Number of continuous, uninterrupted blocks of a specific stage`
    * *What it conveys:* How intensely fragmented a specific stage is (higher count for same duration = more fragmented).
* **Mean_Bout_Duration (per stage):** `Total Stage Duration / Bout_Count for that stage`
    * *What it conveys:* The average length of time the subject can sustain a specific sleep stage before shifting.
* **Max_Bout_Duration (per stage):** `Max(duration of all individual continuous bouts for that stage)`
    * *What it conveys:* The longest single continuous stretch of a given sleep stage achieved during the recording.

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
