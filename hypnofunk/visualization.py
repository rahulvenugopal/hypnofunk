"""
Visualization functions for hypnofunk package.

This module provides functions for plotting hypnograms and visualizing
sleep cycles and transitions.
"""

from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np

try:
    import yasa
    HAS_YASA = True
except ImportError:
    HAS_YASA = False

from hypnofunk.utils import Hypnogram, validate_hypnogram, epochs_to_minutes
from hypnofunk.core import find_nremstretches, find_rem_stretches


def plot_hypnogram_with_cycles(
    hypnogram: Hypnogram,
    epoch_duration: int = 30,
    nrem_indices: Optional[List[Tuple[int, int]]] = None,
    rem_indices: Optional[List[Tuple[int, int]]] = None,
    figsize: Tuple[float, float] = (25, 2.5),
    save_path: Optional[str] = None,
    dpi: int = 600
) -> plt.Figure:
    """
    Plot a hypnogram with NREM and REM cycle annotations.
    
    Parameters
    ----------
    hypnogram : list, np.ndarray, or pd.Series
        Hypnogram with sleep stage labels
    epoch_duration : int, optional
        Duration of each epoch in seconds (default: 30)
    nrem_indices : list of tuple, optional
        List of (start, end) indices for NREM periods. If None, automatically detected
    rem_indices : list of tuple, optional
        List of (start, end) indices for REM periods. If None, automatically detected
    figsize : tuple, optional
        Figure size (width, height) in inches (default: (25, 2.5))
    save_path : str, optional
        Path to save the figure. If None, figure is not saved
    dpi : int, optional
        Resolution for saved figure (default: 600)
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
        
    Raises
    ------
    ImportError
        If yasa is not installed
        
    Examples
    --------
    >>> hyp = ["W"]*10 + ["N2"]*50 + ["R"]*20
    >>> fig = plot_hypnogram_with_cycles(hyp, save_path="hypnogram.png")
    """
    if not HAS_YASA:
        raise ImportError("yasa package is required for plotting. Install with: pip install yasa")
    
    hyp = validate_hypnogram(hypnogram)
    
    # Auto-detect cycles if not provided
    if nrem_indices is None:
        _, nrem_indices = find_nremstretches(hyp)
    if rem_indices is None:
        _, rem_indices = find_rem_stretches(hyp)
    
    # Create hypnogram object
    hypno_obj = yasa.Hypnogram(hyp)
    
    # Create figure
    fig = plt.figure(figsize=figsize)
    yasa.plot_hypnogram(hypno_obj, fill_color="whitesmoke", lw=1)
    
    ax = plt.gca()
    ylim = ax.get_ylim()
    
    # Convert epoch indices to hours for plotting
    epochs_per_hour = 3600 / epoch_duration
    nrem_indices_hours = [(x / epochs_per_hour, y / epochs_per_hour) for (x, y) in nrem_indices]
    rem_indices_hours = [(x / epochs_per_hour, y / epochs_per_hour) for (x, y) in rem_indices]
    
    # Color palette for NREM cycles
    colors = [
        "#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a",
        "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"
    ] * 3  # Repeat to handle many cycles
    
    # Plot NREM cycles
    for i, (start, end) in enumerate(nrem_indices_hours):
        ax.hlines(
            y=ylim[1],
            xmin=start,
            xmax=end,
            colors=colors[i],
            linestyles='solid',
            linewidth=4,
            label=f'NREM {i+1}' if i < 5 else None
        )
    
    # Plot REM cycles
    for i, (start, end) in enumerate(rem_indices_hours):
        ax.hlines(
            y=ylim[1],
            xmin=start,
            xmax=end,
            colors='black',
            linestyles='solid',
            linewidth=4,
            label='REM' if i == 0 else None
        )
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    
    return fig


def plot_transition_matrix(
    transition_probs,
    title: str = "Sleep Stage Transition Probabilities",
    cmap: str = "YlOrRd",
    figsize: Tuple[float, float] = (8, 6),
    save_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Plot a heatmap of the transition probability matrix.
    
    Parameters
    ----------
    transition_probs : pd.DataFrame
        Transition probability matrix from compute_transition_matrix
    title : str, optional
        Plot title (default: "Sleep Stage Transition Probabilities")
    cmap : str, optional
        Matplotlib colormap name (default: "YlOrRd")
    figsize : tuple, optional
        Figure size (width, height) in inches (default: (8, 6))
    save_path : str, optional
        Path to save the figure. If None, figure is not saved
    dpi : int, optional
        Resolution for saved figure (default: 300)
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
        
    Examples
    --------
    >>> from hypnofunk.transitions import compute_transition_matrix
    >>> hyp = ["W", "N1", "N2", "N2", "R", "W"]
    >>> _, probs = compute_transition_matrix(hyp)
    >>> fig = plot_transition_matrix(probs)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(transition_probs, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(transition_probs.columns)))
    ax.set_yticks(np.arange(len(transition_probs.index)))
    ax.set_xticklabels(transition_probs.columns)
    ax.set_yticklabels(transition_probs.index)
    
    # Rotate the tick labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Probability', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(len(transition_probs.index)):
        for j in range(len(transition_probs.columns)):
            ax.text(j, i, f'{transition_probs.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=9)
    
    ax.set_xlabel('To Stage')
    ax.set_ylabel('From Stage')
    ax.set_title(title)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    
    return fig
