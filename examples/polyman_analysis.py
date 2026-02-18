# =============================================================================
# Polyman EDF Sleep Analysis — Example Script
# =============================================================================
#
# What this script does:
#   1. Asks you to pick a folder containing EDF annotation files
#   2. Asks you to pick a folder where results will be saved
#   3. For every EDF file it finds, it:
#       a. Reads the sleep stage annotations and builds a hypnogram
#       b. Detects NREM and REM sleep cycles
#       c. Saves a hypnogram plot as a PNG image
#       d. Saves the raw hypnogram as a CSV file
#       e. Calculates sleep macrostructure parameters (TST, efficiency, etc.)
#       f. Calculates sleep stage transition metrics
#   4. Combines all results into one master CSV spreadsheet
#
# Requirements:
#   pip install hypnofunk[full]   (installs mne and yasa as well)
#
# How to run:
#   python examples/polyman_analysis.py
#
# =============================================================================

import os
import glob

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")           # Use non-interactive backend — safe for scripts
import matplotlib.pyplot as plt
from tkinter import filedialog
import tkinter as tk

# Check that mne and yasa are available before doing anything else.
# Both are optional dependencies — install with: pip install hypnofunk[full]
try:
    import mne
    import yasa
except ImportError:
    print("This script requires mne and yasa.")
    print("Install them with: pip install hypnofunk[full]")
    raise

# Import the functions we need from hypnofunk.
# read_edf_hypnogram  — reads a Polyman EDF file and returns a hypnogram list
# hypnoman            — calculates sleep macrostructure parameters (TST, SE, etc.)
# analyze_transitions — calculates transition probabilities between sleep stages
# find_nremstretches  — detects NREM sleep cycles in the hypnogram
# find_rem_stretches  — detects REM sleep cycles in the hypnogram
# plot_hypnogram_with_cycles — draws and saves a hypnogram figure
from hypnofunk import hypnoman, analyze_transitions, read_edf_hypnogram
from hypnofunk.core import find_nremstretches, find_rem_stretches
from hypnofunk.visualization import plot_hypnogram_with_cycles


# =============================================================================
# Step 1: Select input and output directories via a folder picker dialog
# =============================================================================

# Hide the blank Tkinter root window that appears behind the dialog
root = tk.Tk()
root.withdraw()

print("Please select the folder that contains your EDF files...")
data_dir = filedialog.askdirectory(title="Select folder with EDF files")

print("Please select the folder where results should be saved...")
results_dir = filedialog.askdirectory(title="Select folder to save results")

# If the user closed the dialog without selecting, exit gracefully
if not data_dir or not results_dir:
    print("No folder selected. Exiting.")
    raise SystemExit


# =============================================================================
# Step 2: Find all EDF files in the selected input folder
# =============================================================================

# glob.glob searches for files matching a pattern.
# "*.edf" matches any file whose name ends with .edf
filelist = glob.glob(os.path.join(data_dir, "*.edf"))

print(f"\nFound {len(filelist)} EDF file(s) in: {data_dir}")

if len(filelist) == 0:
    print("No EDF files found. Check that the correct folder was selected.")
    raise SystemExit


# =============================================================================
# Step 3: Process each EDF file one by one
# =============================================================================

# masterlist will collect one result row per file.
# At the end we concatenate them into a single spreadsheet.
masterlist = []

for file_no, fname in enumerate(filelist, start=1):

    base_name = os.path.splitext(os.path.basename(fname))[0]
    print(f"\n[{file_no}/{len(filelist)}] Processing: {base_name}")

    try:
        # -----------------------------------------------------------------
        # 3a. Read the EDF annotation file and extract the hypnogram
        # -----------------------------------------------------------------
        # read_edf_hypnogram() is part of hypnofunk.
        # It reads the sleep stage annotations embedded in the EDF file and
        # returns a flat Python list like ["W", "W", "N2", "N2", "R", ...],
        # one label per 30-second epoch.
        # It returns None if the file contains non-sleep annotations.
        hypnogram = read_edf_hypnogram(fname, epoch_duration=30)

        if hypnogram is None:
            print(f"  [WARNING] Skipped: file contains non-sleep stage labels")
            continue

        print(f"  Hypnogram loaded: {len(hypnogram)} epochs "
              f"({len(hypnogram) * 30 / 3600:.1f} hours)")

        # -----------------------------------------------------------------
        # 3b. Detect NREM and REM sleep cycles
        # -----------------------------------------------------------------
        # find_nremstretches returns:
        #   nrem_stretches — list of stage-label lists, one per NREM cycle
        #   nrem_indices   — list of (start_epoch, end_epoch) tuples
        # A NREM cycle requires at least 30 consecutive NREM epochs (15 min)
        # starting with N2.
        _, nrem_indices = find_nremstretches(hypnogram)

        # find_rem_stretches works similarly.
        # The first REM period can be any length; subsequent ones need >= 10
        # consecutive REM epochs (5 min).
        _, rem_indices = find_rem_stretches(hypnogram)

        print(f"  Detected {len(nrem_indices)} NREM cycle(s) "
              f"and {len(rem_indices)} REM cycle(s)")

        # -----------------------------------------------------------------
        # 3c. Save a hypnogram plot as a PNG image
        # -----------------------------------------------------------------
        # The plot shows the sleep stages over time with coloured bars
        # marking each NREM and REM cycle.
        plot_path = os.path.join(results_dir, f"{base_name}.png")

        plot_hypnogram_with_cycles(
            hypnogram,
            epoch_duration=30,
            nrem_indices=nrem_indices,
            rem_indices=rem_indices,
            save_path=plot_path,
            dpi=600           # high resolution for publications
        )
        plt.close()           # free memory — important when processing many files
        print(f"  Hypnogram plot saved: {plot_path}")

        # -----------------------------------------------------------------
        # 3d. Save the raw hypnogram as a CSV file
        # -----------------------------------------------------------------
        # One stage label per row, e.g.:
        #   W
        #   W
        #   N2
        #   ...
        csv_path = os.path.join(results_dir, f"{base_name}.csv")
        np.savetxt(csv_path, hypnogram, delimiter=",", fmt="%s")
        print(f"  Raw hypnogram saved: {csv_path}")

        # -----------------------------------------------------------------
        # 3e. Calculate sleep macrostructure parameters
        # -----------------------------------------------------------------
        # hypnoman() returns a single-row DataFrame with 40+ sleep metrics:
        #   TST  — Total Sleep Time
        #   TRT  — Total Recording Time
        #   SPT  — Sleep Period Time
        #   SOL  — Sleep Onset Latency
        #   WASO — Wake After Sleep Onset
        #   Sleep_efficiency, Sleep_Maintenance_Efficiency
        #   N1/N2/N3/R duration, percentage, onset, streak statistics
        #   LZc  — Lempel-Ziv complexity (if antropy is installed)
        sleep_params = hypnoman(hypnogram, epoch_duration=30)

        # -----------------------------------------------------------------
        # 3f. Calculate sleep stage transition metrics
        # -----------------------------------------------------------------
        # analyze_transitions() returns a single-row DataFrame with:
        #   Total_Transitions    — how many times the stage changed
        #   Prob_Wake_Transition — fraction of transitions that ended in wake
        #   Sleep_Compactness    — mean self-transition probability (0–1)
        #   Persistence_{stage}  — probability of staying in the same stage
        #   P_{from}_to_{to}     — full 5x5 transition probability matrix
        trans_params = analyze_transitions(hypnogram)

        # Merge both DataFrames side-by-side and tag with the filename
        merged = pd.concat([sleep_params, trans_params], axis=1)
        merged["fname"] = base_name
        masterlist.append(merged)

        print(f"  Sleep parameters calculated")

    except Exception as e:
        # If anything goes wrong with one file, print the error and move on
        # so the rest of the batch still runs.
        print(f"  [ERROR] Could not process file: {e}")
        continue


# =============================================================================
# Step 4: Save the combined results to a master spreadsheet
# =============================================================================

if masterlist:
    # Stack all per-file result rows into one DataFrame
    master_df = pd.concat(masterlist, axis=0)
    master_df = master_df.reset_index(drop=True)

    # Move the filename column to the front for readability
    cols = ["fname"] + [c for c in master_df.columns if c != "fname"]
    master_df = master_df[cols]

    output_path = os.path.join(results_dir, "sleep_parameters_mastersheet.csv")
    master_df.to_csv(output_path, index=False)

    print(f"\n{'='*60}")
    print(f"Analysis complete!")
    print(f"Processed {len(masterlist)} of {len(filelist)} file(s) successfully")
    print(f"Master results saved to: {output_path}")
    print(f"{'='*60}")

else:
    print("\n[WARNING] No files were processed successfully.")
    print("Check the error messages above for details.")
