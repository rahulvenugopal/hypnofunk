# Changelog

All notable changes to the hypnofunk project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-18

### Added

- Initial production-ready release of hypnofunk package
- New `hypnofunk.io` module for EDF+ annotation parsing
- Integrated Markov-chain transition analysis with persistence metrics
- Automated PyPI publishing via GitHub Actions (Trusted Publishing)
- Publication-quality visualizations with sleep cycle overlays
- Comprehensive macrostructure analysis (40+ parameters)
- Lempel-Ziv complexity support
- Beginner-friendly analysis workflow example

### Earlier Development (0.1.x)

- Initial release of hypnofunk package
- Core sleep analysis functions (`hypnoman`)
- Sleep stage transition analysis (`analyze_transitions`)
- Comprehensive sleep parameter calculation:
  - Total sleep time (TST), sleep efficiency, sleep onset latency
  - Stage durations and percentages
  - Sleep cycle detection (NREM and REM)
  - Streak statistics (longest, mean, median)
  - Lempel-Ziv complexity
- Transition metrics:
  - Transition probability matrices
  - Stage persistence probabilities
  - Awakening probabilities
  - Sleep compactness index
- Visualization functions:
  - Hypnogram plotting with cycle annotations
  - Transition matrix heatmaps
- Utility functions for data validation and conversion
- Type hints throughout the codebase
- Comprehensive docstrings with examples
- Example script for Polyman EDF file analysis

### Fixed

- Data type inconsistencies between list, numpy array, and pandas Series
- Redundant code across modules
- Missing input validation

### Changed

- Refactored code into modular structure
- Improved error handling
- Standardized function signatures
- Made epoch duration configurable throughout

### New in 0.1.0 (Pre-release Refinements)

- Added `hypnofunk.io` module with `read_edf_hypnogram` for robust EDF loading
- Rewrote `examples/polyman_analysis.py` as a beginner-friendly flat script
- Added `assets/logo.png` to the repository
- Exposed `read_edf_hypnogram` in the top-level package API

