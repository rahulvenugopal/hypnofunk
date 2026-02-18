"""
I/O utilities for hypnofunk package.

This module provides functions for reading hypnograms from common
polysomnography (PSG) file formats, such as EDF annotation files
produced by Polyman and other PSG software.
"""

from datetime import datetime
from typing import Optional

import numpy as np

from hypnofunk.utils import STAGE_LABELS

# mne is an optional dependency — only needed for EDF reading.
# If not installed, the function will raise a clear ImportError at call time.
try:
    import mne
    HAS_MNE = True
except ImportError:
    HAS_MNE = False


def read_edf_hypnogram(
    edf_path: str,
    epoch_duration: int = 30
) -> Optional[list]:
    """
    Read a hypnogram from a Polyman-style EDF annotation file.

    EDF (European Data Format) is the standard file format used by most
    polysomnography (PSG) systems. Polyman exports sleep stage annotations
    as EDF+ files where each annotation entry looks like::

        "Sleep stage N2"   duration=30s   onset=00:05:00

    This function reads those annotations, converts them to a flat list of
    per-epoch stage labels (one label per epoch), and validates that only
    recognised AASM stage labels are present.

    Parameters
    ----------
    edf_path : str
        Full path to the EDF annotation file (e.g. ``"C:/data/subject01.edf"``)
    epoch_duration : int, optional
        Duration of each scoring epoch in seconds. Default is 30 s, which is
        the standard used in clinical PSG.

    Returns
    -------
    list of str or None
        Flat list of stage labels, one per epoch — e.g.
        ``["W", "W", "N2", "N2", "N3", "R", ...]``.
        Returns ``None`` if the file contains annotation labels that are not
        valid AASM sleep stages (e.g. artefact markers or movement labels).

    Raises
    ------
    ImportError
        If the ``mne`` package is not installed.
        Install it with: ``pip install hypnofunk[full]``
    FileNotFoundError
        If ``edf_path`` does not point to an existing file.

    Examples
    --------
    >>> hypnogram = read_edf_hypnogram("subject01.edf", epoch_duration=30)
    >>> if hypnogram is not None:
    ...     print(f"Recording has {len(hypnogram)} epochs")

    Notes
    -----
    The annotation description is expected to contain the stage label as the
    third word, e.g. ``"Sleep stage N2"`` → ``"N2"``. Single-word descriptions
    are used as-is. This matches the Polyman export convention.
    """
    if not HAS_MNE:
        raise ImportError(
            "mne is required to read EDF files. "
            "Install it with: pip install hypnofunk[full]"
        )

    # --- Step 1: Load annotations from the EDF file ---
    # mne.read_annotations reads the annotation track embedded in the EDF+
    # file. Each row has an onset time, a duration, and a description string.
    annotations = mne.read_annotations(edf_path)
    annot_df = annotations.to_data_frame()

    # --- Step 2: Convert annotation duration to epoch count ---
    # Each annotation covers one or more consecutive epochs of the same stage.
    # Dividing the duration (seconds) by epoch_duration gives the number of
    # epochs that annotation spans.
    annot_df["duration"] = annot_df["duration"] / epoch_duration

    # --- Step 3: Convert onset timestamps to epoch index numbers ---
    # The onset column holds the absolute clock time of each annotation.
    # We convert it to an integer epoch index (0-based from recording start).
    epoch_indices = []
    for onset in annot_df["onset"]:
        t = datetime.strptime(onset.strftime("%H:%M:%S"), "%H:%M:%S")
        total_seconds = t.hour * 3600 + t.minute * 60 + t.second
        epoch_indices.append(int(total_seconds / epoch_duration))
    annot_df["onset"] = epoch_indices

    # --- Step 4: Extract the stage label from the description string ---
    # Polyman writes descriptions like "Sleep stage N2". We take the third
    # word (index 2). If the description is a single word, we use it as-is.
    stage_labels = []
    for description in annot_df["description"]:
        parts = description.split()
        stage_labels.append(parts[2] if len(parts) >= 3 else parts[0])
    annot_df["description"] = stage_labels

    # --- Step 5: Reconstruct the per-epoch hypnogram ---
    # Each annotation row represents a run of identical epochs. We expand it
    # by repeating the stage label for the number of epochs it covers.
    hypnogram = []
    for _, row in annot_df.iterrows():
        stage = row["description"]
        n_epochs = int(row["duration"])
        hypnogram.extend([stage] * n_epochs)

    # --- Step 6: Validate that only AASM sleep stages are present ---
    # If the file contains non-sleep annotations (e.g. "Movement", "Arousal"),
    # we return None so the caller can skip this file gracefully.
    valid_stages = set(STAGE_LABELS)  # {"W", "N1", "N2", "N3", "R"}
    found_stages = set(np.unique(hypnogram))
    if not found_stages.issubset(valid_stages):
        unexpected = found_stages - valid_stages
        return None

    return hypnogram
