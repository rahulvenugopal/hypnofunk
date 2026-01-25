"""
Core sleep analysis functions for hypnofunk package.

This module provides functions for calculating sleep macrostructure parameters
from hypnograms, including sleep efficiency, stage durations, and sleep cycles.
"""

from typing import List, Tuple, Union, Optional
import pandas as pd
import numpy as np
try:
    import antropy as ant
    HAS_ANTROPY = True
except ImportError:
    HAS_ANTROPY = False

from hypnofunk.utils import (
    STAGE_LABELS,
    DEFAULT_EPOCH_DURATION,
    DEFAULT_MAX_WAKE_EPOCHS,
    DEFAULT_MIN_NREM_EPOCHS,
    DEFAULT_MIN_REM_EPOCHS,
    Hypnogram,
    validate_hypnogram,
    rle_encode,
    epochs_to_minutes
)


def trim_terminal_wake(
    hypnogram: Hypnogram,
    max_wake_epochs: int = DEFAULT_MAX_WAKE_EPOCHS
) -> List[str]:
    """
    Trim excessive continuous wake epochs at the end of a hypnogram.
    
    This function removes trailing wake epochs beyond a specified threshold,
    which is useful for cleaning up hypnograms that have extended wake periods
    after the sleep session has effectively ended.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram sequence (e.g., ['W', 'N2', 'R', ...])
    max_wake_epochs : int, optional
        Maximum allowed continuous wake epochs at the end (default: 10)
        
    Returns
    -------
    list of str
        Trimmed hypnogram with the same type as input
        
    Examples
    --------
    >>> hyp = ["N2", "N2", "R", "W", "W", "W", "W", "W"]
    >>> trim_terminal_wake(hyp, max_wake_epochs=2)
    ["N2", "N2", "R", "W", "W"]
    """
    hyp = validate_hypnogram(hypnogram)
    
    # Count trailing wake epochs
    trailing_wake = 0
    for stage in reversed(hyp):
        if stage == 'W':
            trailing_wake += 1
        else:
            break
    
    # Trim if exceeds threshold
    if trailing_wake > max_wake_epochs:
        cut_idx = len(hyp) - (trailing_wake - max_wake_epochs)
        hyp = hyp[:cut_idx]
    
    return hyp


def find_nremstretches(
    sequence: Hypnogram,
    min_nrem_epochs: int = DEFAULT_MIN_NREM_EPOCHS
) -> Tuple[List[List[str]], List[Tuple[int, int]]]:
    """
    Identify NREM sleep stretches in a hypnogram.
    
    A NREM stretch is defined as a continuous sequence of at least min_nrem_epochs
    NREM epochs (N1, N2, N3) that starts with N2.
    
    Parameters
    ----------
    sequence : list, np.ndarray, or pd.Series
        Hypnogram sequence
    min_nrem_epochs : int, optional
        Minimum number of consecutive NREM epochs to qualify as a stretch (default: 30)
        
    Returns
    -------
    stretches : list of list
        List of NREM stretches, each as a list of stage labels
    indices : list of tuple
        List of (start_idx, end_idx) for each stretch
        
    Examples
    --------
    >>> hyp = ["W", "N2"] + ["N2"]*30 + ["R", "W"]
    >>> stretches, indices = find_nremstretches(hyp)
    >>> len(stretches)
    1
    """
    seq = validate_hypnogram(sequence)
    stretches = []
    indices = []
    n = len(seq)
    
    i = 0
    while i <= n - min_nrem_epochs:
        # Check if starts with N2 and next min_nrem_epochs are all NREM
        if seq[i] == 'N2' and all(s in ['N1', 'N2', 'N3'] for s in seq[i:i+min_nrem_epochs]):
            j = i + min_nrem_epochs
            # Extend as long as NREM continues
            while j < n and seq[j] in ['N1', 'N2', 'N3']:
                j += 1
            stretches.append(seq[i:j])
            indices.append((i, j - 1))
            i = j  # Move to end of current stretch
        else:
            i += 1
    
    return stretches, indices


def find_rem_stretches(
    sequence: Hypnogram,
    min_rem_epochs: int = DEFAULT_MIN_REM_EPOCHS
) -> Tuple[List[List[str]], List[Tuple[int, int]]]:
    """
    Identify REM sleep stretches in a hypnogram.
    
    The first REM period can be of any length, but subsequent REM periods
    must have at least min_rem_epochs consecutive REM epochs.
    
    Parameters
    ----------
    sequence : list, np.ndarray, or pd.Series
        Hypnogram sequence
    min_rem_epochs : int, optional
        Minimum number of consecutive REM epochs for non-first periods (default: 10)
        
    Returns
    -------
    stretches : list of list
        List of REM stretches, each as a list of stage labels
    indices : list of tuple
        List of (start_idx, end_idx) for each stretch
        
    Examples
    --------
    >>> hyp = ["N2"]*30 + ["R"]*5 + ["N2"]*10 + ["R"]*12
    >>> stretches, indices = find_rem_stretches(hyp)
    >>> len(stretches)
    2
    """
    seq = validate_hypnogram(sequence)
    r_stretches = []
    indices = []
    n = len(seq)
    
    first_r_found = False
    i = 0
    
    while i < n:
        if seq[i] == 'R':
            if not first_r_found:
                # First REM period: any length is acceptable
                first_r_found = True
                j = i + 1
                while j < n and seq[j] == 'R':
                    j += 1
                r_stretches.append(seq[i:j])
                indices.append((i, j - 1))
                i = j
            elif i + min_rem_epochs <= n and all(s == 'R' for s in seq[i:i+min_rem_epochs]):
                # Subsequent REM periods: must meet minimum length
                j = i + min_rem_epochs
                while j < n and seq[j] == 'R':
                    j += 1
                r_stretches.append(seq[i:j])
                indices.append((i, j - 1))
                i = j
            else:
                i += 1
        else:
            i += 1
    
    return r_stretches, indices


def hypnoman(
    hypnogram: Hypnogram,
    epoch_duration: int = DEFAULT_EPOCH_DURATION,
    trim_wake: bool = True,
    max_wake_epochs: int = DEFAULT_MAX_WAKE_EPOCHS
) -> pd.DataFrame:
    """
    Calculate comprehensive sleep macrostructure parameters from a hypnogram.
    
    This is the main function for extracting sleep metrics including:
    - Total recording time (TRT), total sleep time (TST), sleep period time (SPT)
    - Sleep efficiency and sleep maintenance efficiency
    - Stage durations and percentages
    - Sleep onset latencies for each stage
    - Stage streak statistics (longest, mean, median)
    - Lempel-Ziv complexity (if antropy is installed)
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels per epoch
    epoch_duration : int, optional
        Duration of each epoch in seconds (default: 30)
    trim_wake : bool, optional
        Whether to trim excessive terminal wake epochs (default: True)
    max_wake_epochs : int, optional
        Maximum wake epochs to keep at end if trim_wake=True (default: 10)
        
    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with all calculated sleep parameters
        
    Examples
    --------
    >>> hyp = ["W"]*10 + ["N2"]*50 + ["R"]*20 + ["W"]*5
    >>> params = hypnoman(hyp, epoch_duration=30)
    >>> params['TST'].values[0]  # Total sleep time in minutes
    35.0
    
    Notes
    -----
    All time-based outputs are in minutes unless otherwise specified.
    Percentages are calculated relative to Sleep Period Time (SPT).
    """
    # Validate and optionally trim hypnogram
    hyp = validate_hypnogram(hypnogram)
    if trim_wake:
        hyp = trim_terminal_wake(hyp, max_wake_epochs=max_wake_epochs)
    
    hyp_series = pd.Series(hyp)
    
    # Run-length encoding for streak analysis
    symbols, lengths = rle_encode(hyp)
    rle_df = pd.DataFrame({'Symbol': symbols, 'values': lengths})
    
    # Initialize results DataFrame
    sleep_data = pd.DataFrame({
        'TRT': [np.nan],  # Total Recording Time
        'TST': [np.nan],  # Total Sleep Time
        'SPT': [np.nan],  # Sleep Period Time
        'WASO': [np.nan],  # Wake After Sleep Onset
        'SOL': [np.nan],  # Sleep Onset Latency
        'Sleep_efficiency': [np.nan],
        'Sleep_Maintenance_Efficiency': [np.nan],
        'W_duration': [np.nan],
        'N1_duration': [np.nan],
        'N2_duration': [np.nan],
        'N3_duration': [np.nan],
        'R_duration': [np.nan],
        'NREM_duration': [np.nan],
        'N1_percentage': [np.nan],
        'N2_percentage': [np.nan],
        'N3_percentage': [np.nan],
        'R_percentage': [np.nan],
        'W_onset': [np.nan],
        'N1_onset': [np.nan],
        'N2_onset': [np.nan],
        'N3_onset': [np.nan],
        'R_onset': [np.nan],
        'W_longest_streak': [np.nan],
        'N1_longest_streak': [np.nan],
        'N2_longest_streak': [np.nan],
        'N3_longest_streak': [np.nan],
        'R_longest_streak': [np.nan],
        'W_mean_length_of_streak': [np.nan],
        'N1_mean_length_of_streak': [np.nan],
        'N2_mean_length_of_streak': [np.nan],
        'N3_mean_length_of_streak': [np.nan],
        'R_mean_length_of_streak': [np.nan],
        'W_median_length_of_streak': [np.nan],
        'N1_median_length_of_streak': [np.nan],
        'N2_median_length_of_streak': [np.nan],
        'N3_median_length_of_streak': [np.nan],
        'R_median_length_of_streak': [np.nan],
        'LZc': [np.nan]
    })
    
    # Total Recording Time (minutes)
    sleep_data['TRT'] = epochs_to_minutes(len(hyp_series), epoch_duration)
    
    # Stage onset times (minutes from start)
    for stage in STAGE_LABELS:
        if hyp_series.isin([stage]).any():
            onset = epochs_to_minutes(
                np.where(hyp_series == stage)[0].min(),
                epoch_duration
            )
        else:
            onset = np.nan
        sleep_data[f'{stage}_onset'] = onset
    
    # Sleep Onset Latency (to any sleep stage)
    sleep_indices = np.where(hyp_series != "W")[0]
    if len(sleep_indices) > 0:
        sleep_data['SOL'] = epochs_to_minutes(sleep_indices[0], epoch_duration)
    else:
        sleep_data['SOL'] = sleep_data['TRT']  # No sleep occurred
    
    # Sleep Period Time (from sleep onset to end)
    sleep_data['SPT'] = sleep_data['TRT'] - sleep_data['SOL']
    
    # Correct REM latency (relative to sleep onset, not recording start)
    if not pd.isna(sleep_data['R_onset'].values[0]):
        sleep_data['R_onset'] = sleep_data['R_onset'] - sleep_data['SOL']
    
    # Stage durations (minutes)
    stage_durations = hyp_series.value_counts() * epoch_duration / 60
    for stage in STAGE_LABELS:
        if hyp_series.isin([stage]).any():
            duration = stage_durations[stage]
        else:
            duration = 0.0
        sleep_data[f'{stage}_duration'] = duration
    
    # NREM duration
    sleep_data['NREM_duration'] = (
        sleep_data['N1_duration'].fillna(0) +
        sleep_data['N2_duration'].fillna(0) +
        sleep_data['N3_duration'].fillna(0)
    )
    
    # Total Sleep Time
    sleep_data['TST'] = sleep_data['NREM_duration'] + sleep_data['R_duration'].fillna(0)
    
    # Sleep Maintenance Efficiency
    if sleep_data['SPT'].values[0] > 0:
        sleep_data['Sleep_Maintenance_Efficiency'] = (
            sleep_data['TST'].values[0] / sleep_data['SPT'].values[0]
        ) * 100
    
    # Stage percentages (relative to SPT)
    if sleep_data['SPT'].values[0] > 0:
        for stage in STAGE_LABELS:
            if stage != 'W' and hyp_series.isin([stage]).any():
                perc = (stage_durations[stage] / sleep_data['SPT'].values[0]) * 100
                sleep_data[f'{stage}_percentage'] = round(perc, 2)
    
    # Sleep Efficiency
    sleep_data['Sleep_efficiency'] = (sleep_data['TST'] / sleep_data['TRT']) * 100
    
    # WASO (Wake After Sleep Onset)
    sleep_data['WASO'] = sleep_data['SPT'] - sleep_data['TST']
    
    # Streak statistics
    # Mean streak lengths
    mean_run_lengths = rle_df.groupby('Symbol').agg({'values': 'mean'})
    for stage in STAGE_LABELS:
        if hyp_series.isin([stage]).any() and stage in mean_run_lengths.index:
            mean_runs = epochs_to_minutes(
                mean_run_lengths.loc[stage, 'values'],
                epoch_duration
            )
        else:
            mean_runs = np.nan
        sleep_data[f'{stage}_mean_length_of_streak'] = mean_runs
    
    # Median streak lengths
    median_run_lengths = rle_df.groupby('Symbol').agg({'values': 'median'})
    for stage in STAGE_LABELS:
        if hyp_series.isin([stage]).any() and stage in median_run_lengths.index:
            med_runs = epochs_to_minutes(
                median_run_lengths.loc[stage, 'values'],
                epoch_duration
            )
        else:
            med_runs = np.nan
        sleep_data[f'{stage}_median_length_of_streak'] = med_runs
    
    # Longest streak lengths
    longest_run_lengths = rle_df.groupby('Symbol').agg({'values': 'max'})
    for stage in STAGE_LABELS:
        if hyp_series.isin([stage]).any() and stage in longest_run_lengths.index:
            long_runs = epochs_to_minutes(
                longest_run_lengths.loc[stage, 'values'],
                epoch_duration
            )
        else:
            long_runs = np.nan
        sleep_data[f'{stage}_longest_streak'] = long_runs
    
    # Lempel-Ziv complexity (if antropy is available)
    if HAS_ANTROPY:
        sleep_data['LZc'] = ant.lziv_complexity(hyp_series.to_numpy(), normalize=True)
    else:
        sleep_data['LZc'] = np.nan
    
    return sleep_data
