# hypnofunk 🌙

A comprehensive Python package for sleep analysis and hypnogram processing.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**hypnofunk** provides a complete toolkit for analyzing sleep data from hypnograms (sleep stage sequences). It calculates comprehensive sleep macrostructure parameters, performs transition analysis, and generates publication-quality visualizations.

### Key Features

- 📊 **Comprehensive Sleep Metrics**: Calculate 40+ sleep parameters including TST, sleep efficiency, stage durations, and more
- 🔄 **Transition Analysis**: Markov chain analysis of sleep stage transitions with fragmentation metrics
- 📈 **Visualization**: Generate hypnogram plots with automatic sleep cycle detection
- 🎯 **Type-Safe**: Full type hints throughout the codebase
- 📚 **Well-Documented**: Comprehensive docstrings with examples for all functions
- 🔧 **Flexible**: Works with lists, numpy arrays, or pandas Series

## Installation

### Basic Installation

```bash
pip install hypnofunk
```

### Full Installation (with optional dependencies)

For complete functionality including Lempel-Ziv complexity and advanced plotting:

```bash
pip install hypnofunk[full]
```

### Development Installation

```bash
git clone https://github.com/yourusername/hypnofunk.git
cd hypnofunk
pip install -e .[dev]
```

## Quick Start

```python
from hypnofunk import hypnoman, analyze_transitions

# Your hypnogram (sleep stages per epoch)
hypnogram = ["W"]*10 + ["N2"]*50 + ["N3"]*30 + ["R"]*20 + ["W"]*5

# Calculate sleep parameters
sleep_params = hypnoman(hypnogram, epoch_duration=30)
print(f"Total Sleep Time: {sleep_params['TST'].values[0]:.1f} minutes")
print(f"Sleep Efficiency: {sleep_params['Sleep_efficiency'].values[0]:.1f}%")

# Analyze transitions
transitions = analyze_transitions(hypnogram)
print(f"Sleep Compactness: {transitions['Sleep_Compactness'].values[0]:.3f}")
print(f"Total Transitions: {transitions['Total_Transitions'].values[0]}")
```

## Core Functionality

### Sleep Macrostructure Analysis

The `hypnoman()` function calculates comprehensive sleep parameters:

**Time Metrics:**

- Total Recording Time (TRT)
- Total Sleep Time (TST)
- Sleep Period Time (SPT)
- Wake After Sleep Onset (WASO)
- Sleep Onset Latency (SOL)

**Efficiency Metrics:**

- Sleep Efficiency (SE)
- Sleep Maintenance Efficiency (SME)

**Stage Metrics:**

- Duration and percentage for each stage (W, N1, N2, N3, R)
- Onset latencies
- Longest, mean, and median streak lengths

**Complexity:**

- Lempel-Ziv complexity (requires `antropy`)

### Transition Analysis

The `analyze_transitions()` function provides:

**Fragmentation Metrics:**

- Total number of transitions
- Probability of transitions to wake
- Sleep compactness index

**Markov Analysis:**

- Full transition probability matrix (5×5)
- Stage persistence probabilities
- Awakening probabilities from each stage

### Sleep Cycle Detection

Automatically detect NREM and REM sleep cycles:

```python
from hypnofunk.core import find_nremstretches, find_rem_stretches

# Detect NREM cycles (≥30 consecutive NREM epochs starting with N2)
nrem_stretches, nrem_indices = find_nremstretches(hypnogram)

# Detect REM cycles (first REM of any length, subsequent ≥10 epochs)
rem_stretches, rem_indices = find_rem_stretches(hypnogram)
```

### Visualization

Create publication-quality hypnogram plots:

```python
from hypnofunk.visualization import plot_hypnogram_with_cycles

# Plot hypnogram with automatic cycle detection
fig = plot_hypnogram_with_cycles(
    hypnogram,
    epoch_duration=30,
    save_path="hypnogram.png",
    dpi=600
)
```

## Example: Polyman EDF Analysis

See [`examples/polyman_analysis.py`](examples/polyman_analysis.py) for a complete workflow that:

1. Loads EDF files with sleep stage annotations
2. Extracts hypnograms
3. Calculates all sleep parameters
4. Generates visualizations
5. Exports results to CSV

Run the example:

```bash
python examples/polyman_analysis.py
```

## API Reference

### Core Module (`hypnofunk.core`)

- `hypnoman(hypnogram, epoch_duration=30)` - Calculate all sleep parameters
- `trim_terminal_wake(hypnogram, max_wake_epochs=10)` - Remove excessive terminal wake
- `find_nremstretches(sequence, min_nrem_epochs=30)` - Detect NREM cycles
- `find_rem_stretches(sequence, min_rem_epochs=10)` - Detect REM cycles

### Transitions Module (`hypnofunk.transitions`)

- `analyze_transitions(hypnogram)` - Complete transition analysis
- `compute_transition_matrix(hypnogram)` - Calculate transition counts and probabilities
- `compute_sleep_compactness(transition_probs)` - Calculate compactness index

### Utilities Module (`hypnofunk.utils`)

- `validate_hypnogram(hypnogram)` - Validate and convert hypnogram format
- `convert_to_numeric(hypnogram)` - Convert labels to numeric codes
- `convert_to_labels(hypnogram_numeric)` - Convert numeric codes to labels
- `rle_encode(sequence)` - Run-length encoding
- `epochs_to_minutes(epochs, epoch_duration)` - Convert epochs to minutes

### Visualization Module (`hypnofunk.visualization`)

- `plot_hypnogram_with_cycles(hypnogram, ...)` - Plot hypnogram with cycles
- `plot_transition_matrix(transition_probs, ...)` - Plot transition heatmap

## Data Format

Hypnograms should use standard sleep stage labels:

- `W` - Wake
- `N1` - NREM Stage 1
- `N2` - NREM Stage 2
- `N3` - NREM Stage 3 (slow-wave sleep)
- `R` - REM sleep

Accepted input formats:

- Python list: `["W", "N2", "N2", "R"]`
- NumPy array: `np.array(["W", "N2", "N2", "R"])`
- Pandas Series: `pd.Series(["W", "N2", "N2", "R"])`

## Dependencies

**Core:**

- numpy ≥ 1.20.0
- pandas ≥ 1.3.0
- matplotlib ≥ 3.3.0

**Optional (for full functionality):**

- antropy ≥ 0.1.4 (Lempel-Ziv complexity)
- yasa ≥ 0.6.0 (hypnogram plotting)
- mne ≥ 1.0.0 (EDF file reading)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use hypnofunk in your research, please cite:

```
@software{hypnofunk2026,
  author = {Venugopal, Rahul},
  title = {hypnofunk: A Python package for sleep analysis},
  year = {2026},
  url = {https://github.com/rahulvenugopal/hypnofunk}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Rahul Venugopal**

## Acknowledgments

- Built with inspiration from YASA and other sleep analysis tools
- Sleep cycle detection based on standard polysomnography criteria
