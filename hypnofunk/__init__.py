"""
hypnofunk: A Python package for sleep analysis and hypnogram processing.

This package provides tools for analyzing sleep data, calculating sleep parameters,
and performing transition analysis on hypnograms.
"""

__version__ = "0.2.0"
__author__ = "Rahul Venugopal"

from hypnofunk.core import hypnoman, trim_terminal_wake, find_nremstretches, find_rem_stretches
from hypnofunk.transitions import analyze_transitions, compute_transition_matrix
from hypnofunk.io import read_edf_hypnogram
from hypnofunk import utils

__all__ = [
    "hypnoman",
    "trim_terminal_wake",
    "find_nremstretches",
    "find_rem_stretches",
    "analyze_transitions",
    "compute_transition_matrix",
    "read_edf_hypnogram",
    "utils",
]
