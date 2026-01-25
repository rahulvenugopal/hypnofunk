"""
Shared utilities and constants for the hypnofunk package.
"""

from typing import List, Union, Tuple
import numpy as np
import pandas as pd

# Constants
STAGE_LABELS = ["W", "N1", "N2", "N3", "R"]
STAGE_CODES = [0, 1, 2, 3, 4]
STAGE_LABEL_TO_CODE = {
    "W": 0,
    "N1": 1,
    "N2": 2,
    "N3": 3,
    "R": 4
}
STAGE_CODE_TO_LABEL = {v: k for k, v in STAGE_LABEL_TO_CODE.items()}

# Default parameters
DEFAULT_EPOCH_DURATION = 30  # seconds
DEFAULT_MAX_WAKE_EPOCHS = 10
DEFAULT_MIN_NREM_EPOCHS = 30
DEFAULT_MIN_REM_EPOCHS = 10

# Type aliases
Hypnogram = Union[List[str], np.ndarray, pd.Series]
HypnogramNumeric = Union[List[int], np.ndarray]


def validate_hypnogram(hypnogram: Hypnogram) -> List[str]:
    """
    Validate and convert hypnogram to a list of stage labels.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels (e.g., "W", "N1", "N2", "N3", "R")
        
    Returns
    -------
    list of str
        Validated hypnogram as a list of stage labels
        
    Raises
    ------
    ValueError
        If hypnogram is empty or contains invalid stage labels
    """
    if isinstance(hypnogram, pd.Series):
        hyp_list = hypnogram.tolist()
    elif isinstance(hypnogram, np.ndarray):
        hyp_list = hypnogram.tolist()
    else:
        hyp_list = list(hypnogram)
    
    if len(hyp_list) == 0:
        raise ValueError("Hypnogram cannot be empty")
    
    # Check for invalid stages
    invalid_stages = set(hyp_list) - set(STAGE_LABELS)
    if invalid_stages:
        raise ValueError(f"Invalid stage labels found: {invalid_stages}. "
                        f"Valid labels are: {STAGE_LABELS}")
    
    return hyp_list


def convert_to_numeric(hypnogram: Hypnogram) -> List[int]:
    """
    Convert a hypnogram with stage labels to numeric codes.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Sleep stages as strings (e.g., "W", "N1", "R")
        
    Returns
    -------
    list of int
        Numeric hypnogram (W=0, N1=1, N2=2, N3=3, R=4)
        
    Examples
    --------
    >>> convert_to_numeric(["W", "N1", "N2", "R"])
    [0, 1, 2, 4]
    """
    hyp_list = validate_hypnogram(hypnogram)
    return [STAGE_LABEL_TO_CODE[label] for label in hyp_list]


def convert_to_labels(hypnogram_numeric: HypnogramNumeric) -> List[str]:
    """
    Convert a numeric hypnogram to stage labels.
    
    Parameters
    ----------
    hypnogram_numeric : list or np.ndarray
        Numeric hypnogram (W=0, N1=1, N2=2, N3=3, R=4)
        
    Returns
    -------
    list of str
        Hypnogram with stage labels
        
    Examples
    --------
    >>> convert_to_labels([0, 1, 2, 4])
    ["W", "N1", "N2", "R"]
    """
    if isinstance(hypnogram_numeric, np.ndarray):
        hyp_list = hypnogram_numeric.tolist()
    else:
        hyp_list = list(hypnogram_numeric)
    
    return [STAGE_CODE_TO_LABEL[code] for code in hyp_list]


def rle_encode(sequence: List) -> Tuple[List, List[int]]:
    """
    Run-length encoding of a sequence.
    
    Parameters
    ----------
    sequence : list
        Input sequence to encode
        
    Returns
    -------
    symbols : list
        Unique symbols in order of appearance
    lengths : list of int
        Length of each run
        
    Examples
    --------
    >>> rle_encode(["W", "W", "N2", "N2", "N2", "R"])
    (["W", "N2", "R"], [2, 3, 1])
    """
    if len(sequence) == 0:
        return [], []
    
    symbols = []
    lengths = []
    
    current_symbol = sequence[0]
    current_count = 1
    
    for symbol in sequence[1:]:
        if symbol == current_symbol:
            current_count += 1
        else:
            symbols.append(current_symbol)
            lengths.append(current_count)
            current_symbol = symbol
            current_count = 1
    
    # Store the last symbol and its count
    symbols.append(current_symbol)
    lengths.append(current_count)
    
    return symbols, lengths


def epochs_to_minutes(epochs: Union[int, float], epoch_duration: int = DEFAULT_EPOCH_DURATION) -> float:
    """
    Convert number of epochs to minutes.
    
    Parameters
    ----------
    epochs : int or float
        Number of epochs
    epoch_duration : int, optional
        Duration of each epoch in seconds (default: 30)
        
    Returns
    -------
    float
        Duration in minutes
    """
    return (epochs * epoch_duration) / 60


def minutes_to_epochs(minutes: float, epoch_duration: int = DEFAULT_EPOCH_DURATION) -> int:
    """
    Convert minutes to number of epochs.
    
    Parameters
    ----------
    minutes : float
        Duration in minutes
    epoch_duration : int, optional
        Duration of each epoch in seconds (default: 30)
        
    Returns
    -------
    int
        Number of epochs
    """
    return int((minutes * 60) / epoch_duration)
