"""
Tests for hypnofunk package core functionality.
Run with: pytest tests/ -v
"""

import pytest
import numpy as np
import pandas as pd

from hypnofunk import hypnoman, analyze_transitions
from hypnofunk.core import find_nremstretches, find_rem_stretches
from hypnofunk.transitions import compute_transition_matrix
from hypnofunk.utils import validate_hypnogram, convert_to_numeric


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_hypnogram():
    """A minimal but realistic hypnogram for testing."""
    return ["W"] * 10 + ["N2"] * 50 + ["N3"] * 30 + ["R"] * 20 + ["W"] * 5


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_validate_hypnogram_list(simple_hypnogram):
    result = validate_hypnogram(simple_hypnogram)
    assert isinstance(result, list)
    assert len(result) == len(simple_hypnogram)


def test_validate_hypnogram_numpy(simple_hypnogram):
    arr = np.array(simple_hypnogram)
    result = validate_hypnogram(arr)
    assert isinstance(result, list)


def test_validate_hypnogram_series(simple_hypnogram):
    s = pd.Series(simple_hypnogram)
    result = validate_hypnogram(s)
    assert isinstance(result, list)


def test_validate_hypnogram_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_hypnogram([])


def test_validate_hypnogram_invalid_stage():
    with pytest.raises(ValueError, match="Invalid stage labels"):
        validate_hypnogram(["W", "N2", "UNKNOWN"])


# ---------------------------------------------------------------------------
# Numeric conversion
# ---------------------------------------------------------------------------

def test_convert_to_numeric():
    result = convert_to_numeric(["W", "N1", "N2", "N3", "R"])
    assert result == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# Sleep parameters (hypnoman)
# ---------------------------------------------------------------------------

def test_hypnoman_returns_dataframe(simple_hypnogram):
    result = hypnoman(simple_hypnogram, epoch_duration=30)
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 1


def test_hypnoman_tst(simple_hypnogram):
    result = hypnoman(simple_hypnogram, epoch_duration=30)
    # TST = (N2 + N3 + R) epochs * 30s / 60 = 100 * 0.5 = 50 min
    assert result["TST"].values[0] == pytest.approx(50.0, abs=0.1)


def test_hypnoman_sleep_efficiency(simple_hypnogram):
    result = hypnoman(simple_hypnogram, epoch_duration=30)
    assert 0 < result["Sleep_efficiency"].values[0] <= 100


def test_hypnoman_sol(simple_hypnogram):
    result = hypnoman(simple_hypnogram, epoch_duration=30)
    # SOL = 10 wake epochs * 30s / 60 = 5 min
    assert result["SOL"].values[0] == pytest.approx(5.0, abs=0.1)


def test_hypnoman_no_sleep():
    """All-wake hypnogram should not crash."""
    hyp = ["W"] * 20
    result = hypnoman(hyp, epoch_duration=30)
    assert result["TST"].values[0] == pytest.approx(0.0, abs=0.01)


# ---------------------------------------------------------------------------
# Sleep cycle detection
# ---------------------------------------------------------------------------

def test_find_nremstretches(simple_hypnogram):
    stretches, indices = find_nremstretches(simple_hypnogram)
    assert isinstance(stretches, list)
    assert isinstance(indices, list)
    assert len(stretches) == len(indices)


def test_find_rem_stretches(simple_hypnogram):
    stretches, indices = find_rem_stretches(simple_hypnogram)
    assert len(stretches) >= 1
    assert all(len(s) > 0 for s in stretches)


# ---------------------------------------------------------------------------
# Transition analysis
# ---------------------------------------------------------------------------

def test_compute_transition_matrix(simple_hypnogram):
    counts, probs = compute_transition_matrix(simple_hypnogram)
    assert counts.shape == (5, 5)
    assert probs.shape == (5, 5)
    # Row sums of probs should be 0 or 1
    row_sums = probs.sum(axis=1)
    for s in row_sums:
        assert s == pytest.approx(0.0, abs=1e-9) or s == pytest.approx(1.0, abs=1e-9)


def test_analyze_transitions_returns_dataframe(simple_hypnogram):
    result = analyze_transitions(simple_hypnogram)
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 1
    assert "Total_Transitions" in result.columns
    assert "Sleep_Compactness" in result.columns


def test_analyze_transitions_total(simple_hypnogram):
    result = analyze_transitions(simple_hypnogram)
    # W->N2, N2->N3, N3->R, R->W = 4 transitions
    assert result["Total_Transitions"].values[0] == 4
