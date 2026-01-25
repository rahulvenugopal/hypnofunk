"""
Sleep stage transition analysis for hypnofunk package.

This module provides functions for analyzing transitions between sleep stages,
calculating transition probabilities, and computing sleep fragmentation metrics.
"""

from typing import List, Tuple, Optional
import numpy as np
import pandas as pd

from hypnofunk.utils import (
    STAGE_LABELS,
    STAGE_CODES,
    Hypnogram,
    validate_hypnogram,
    convert_to_numeric
)


def compute_transition_matrix(
    hypnogram: Hypnogram,
    stages: Optional[List[int]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute transition count and probability matrices from a hypnogram.
    
    This function calculates how frequently each sleep stage transitions to
    every other stage, providing both raw counts and normalized probabilities.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels (e.g., "W", "N1", "R")
    stages : list of int, optional
        Specific stage codes to include. If None, uses all stages present
        in the hypnogram (default: None)
        
    Returns
    -------
    transition_counts : pd.DataFrame
        Matrix of transition counts (rows = from stage, columns = to stage)
    transition_probs : pd.DataFrame
        Matrix of transition probabilities (row-normalized)
        
    Examples
    --------
    >>> hyp = ["W", "N1", "N2", "N2", "R", "W"]
    >>> counts, probs = compute_transition_matrix(hyp)
    >>> probs.loc["N2", "R"]  # Probability of N2 -> R transition
    0.5
    
    Notes
    -----
    The transition probability matrix is row-normalized, meaning each row
    sums to 1.0 (or 0 if that stage never occurred).
    """
    # Convert to numeric codes
    hyp_numeric = convert_to_numeric(hypnogram)
    
    # Initialize transition count matrix with all possible stages
    transition_counts = pd.DataFrame(
        0, index=STAGE_CODES, columns=STAGE_CODES, dtype=int
    )
    
    # Count transitions
    for from_stage, to_stage in zip(hyp_numeric[:-1], hyp_numeric[1:]):
        transition_counts.loc[from_stage, to_stage] += 1
    
    # Convert counts to probabilities (row-normalized)
    row_sums = transition_counts.sum(axis=1).replace(0, np.nan)
    transition_probs = transition_counts.div(row_sums, axis=0).fillna(0)
    
    # Rename indices and columns with stage labels
    transition_counts.index = transition_counts.columns = STAGE_LABELS
    transition_probs.index = transition_probs.columns = STAGE_LABELS
    
    return transition_counts, transition_probs


def compute_transition_counts(hypnogram: Hypnogram) -> int:
    """
    Calculate the total number of stage transitions in a hypnogram.
    
    This counts how many times the sleep stage changes from one epoch to
    the next, which is an indicator of sleep fragmentation.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels
        
    Returns
    -------
    int
        Total number of stage transitions
        
    Examples
    --------
    >>> hyp = ["W", "W", "N2", "N2", "R", "W"]
    >>> compute_transition_counts(hyp)
    3
    
    Notes
    -----
    Higher values indicate more fragmented sleep with frequent stage changes.
    """
    hyp_numeric = convert_to_numeric(hypnogram)
    return sum(1 for i in range(1, len(hyp_numeric)) if hyp_numeric[i] != hyp_numeric[i - 1])


def compute_transition_to_wake_index(hypnogram: Hypnogram) -> float:
    """
    Calculate the proportion of transitions that end in wake.
    
    This metric reflects sleep fragility by measuring what fraction of all
    stage transitions result in awakening.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels
        
    Returns
    -------
    float
        Proportion of transitions to wake (0.0 to 1.0)
        
    Examples
    --------
    >>> hyp = ["N2", "N2", "R", "W", "N1", "W"]
    >>> compute_transition_to_wake_index(hyp)
    0.5
    
    Notes
    -----
    Higher values indicate more awakenings relative to total stage changes.
    Only counts transitions FROM sleep stages TO wake, not wake-to-wake.
    """
    hyp_numeric = convert_to_numeric(hypnogram)
    total_transitions = compute_transition_counts(hypnogram)
    
    if total_transitions == 0:
        return 0.0
    
    # Count transitions from sleep to wake (wake code = 0)
    to_wake_transitions = 0
    for i in range(1, len(hyp_numeric)):
        from_stage, to_stage = hyp_numeric[i - 1], hyp_numeric[i]
        if from_stage != 0 and to_stage == 0:
            to_wake_transitions += 1
    
    return to_wake_transitions / total_transitions


def compute_stage_persistence_probs(transition_probs: pd.DataFrame) -> List[float]:
    """
    Extract stage persistence probabilities from transition matrix.
    
    Persistence probability is the likelihood of remaining in the same stage
    from one epoch to the next (diagonal of transition matrix).
    
    Parameters
    ----------
    transition_probs : pd.DataFrame
        Transition probability matrix from compute_transition_matrix
        
    Returns
    -------
    list of float
        Persistence probabilities for each stage [W, N1, N2, N3, R]
        
    Examples
    --------
    >>> _, probs = compute_transition_matrix(["N2"]*10 + ["R"]*5)
    >>> persistence = compute_stage_persistence_probs(probs)
    >>> persistence[2]  # N2 persistence
    0.9
    
    Notes
    -----
    N3 typically has the highest persistence (most stable stage).
    N1 often has low persistence (transient stage).
    """
    return np.diag(transition_probs).tolist()


def compute_awakening_probs(transition_probs: pd.DataFrame) -> List[float]:
    """
    Extract awakening probabilities from transition matrix.
    
    Awakening probability is the likelihood of transitioning to wake from
    each sleep stage.
    
    Parameters
    ----------
    transition_probs : pd.DataFrame
        Transition probability matrix from compute_transition_matrix
        
    Returns
    -------
    list of float
        Awakening probabilities for each stage [W, N1, N2, N3, R]
        
    Examples
    --------
    >>> _, probs = compute_transition_matrix(["N2", "N2", "W", "N1", "W"])
    >>> awaken_probs = compute_awakening_probs(probs)
    >>> awaken_probs[2]  # Probability of N2 -> W
    0.5
    """
    return transition_probs["W"].tolist()


def compute_sleep_compactness(transition_probs: pd.DataFrame) -> float:
    """
    Calculate sleep compactness as mean persistence of sleep stages.
    
    Sleep compactness is the average self-transition probability across
    all non-wake stages (N1, N2, N3, R). Higher values indicate more
    consolidated, less fragmented sleep.
    
    Parameters
    ----------
    transition_probs : pd.DataFrame
        Transition probability matrix from compute_transition_matrix
        
    Returns
    -------
    float
        Mean persistence probability across sleep stages
        
    Examples
    --------
    >>> _, probs = compute_transition_matrix(["N2"]*20 + ["R"]*10)
    >>> compute_sleep_compactness(probs)
    0.95
    
    Notes
    -----
    High compactness (>0.9) suggests deep, consolidated sleep cycles.
    Low compactness (<0.7) suggests fragmented, unstable sleep.
    """
    persistence = compute_stage_persistence_probs(transition_probs)
    # Exclude wake (index 0) and compute mean of sleep stages
    sleep_persistence = [p for i, p in enumerate(persistence) if STAGE_LABELS[i] != "W"]
    return np.mean(sleep_persistence)


def analyze_transitions(hypnogram: Hypnogram) -> pd.DataFrame:
    """
    Comprehensive transition analysis of a hypnogram.
    
    This is the main function for extracting all transition-related metrics,
    including:
    - Total number of transitions
    - Probability of transitions to wake
    - Sleep compactness
    - Stage persistence probabilities
    - Awakening probabilities from each stage
    - Full Markov transition probability matrix
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels
        
    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with all transition metrics
        
    Examples
    --------
    >>> hyp = ["W"]*5 + ["N2"]*30 + ["R"]*15 + ["W"]*5
    >>> results = analyze_transitions(hyp)
    >>> results['Total_Transitions'].values[0]
    3
    >>> results['Sleep_Compactness'].values[0]
    0.96...
    
    Notes
    -----
    The returned DataFrame contains:
    - Total_Transitions: Count of stage changes
    - Prob_Wake_Transition: Fraction of transitions ending in wake
    - Sleep_Compactness: Mean persistence of sleep stages
    - Persistence_{Stage}: Self-transition probability for each stage
    - Prob_{Stage}_to_W: Awakening probability from each stage
    - P_{from}_to_{to}: Full transition probability matrix (25 values)
    """
    # Validate input
    hyp = validate_hypnogram(hypnogram)
    
    # Compute transition matrices
    trans_counts, trans_probs = compute_transition_matrix(hyp)
    
    # Compute summary metrics
    total_transitions = compute_transition_counts(hyp)
    tw_prob = compute_transition_to_wake_index(hyp)
    persistence_probs = compute_stage_persistence_probs(trans_probs)
    awakening_probs = compute_awakening_probs(trans_probs)
    compactness = compute_sleep_compactness(trans_probs)
    
    # Build results dictionary
    flat_results = {
        "Total_Transitions": total_transitions,
        "Prob_Wake_Transition": tw_prob,
        "Sleep_Compactness": compactness
    }
    
    # Add persistence probabilities
    for stage, prob in zip(STAGE_LABELS, persistence_probs):
        flat_results[f"Persistence_{stage}"] = prob
    
    # Add awakening probabilities (probability any stage → W)
    for stage, prob in zip(STAGE_LABELS, awakening_probs):
        flat_results[f"Prob_{stage}_to_W"] = prob
    
    # Add full transition probability matrix
    for from_stage in STAGE_LABELS:
        for to_stage in STAGE_LABELS:
            flat_results[f"P_{from_stage}_to_{to_stage}"] = trans_probs.loc[from_stage, to_stage]
    
    return pd.DataFrame([flat_results])
