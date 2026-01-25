"""
Example script: Polyman EDF Sleep Analysis

This script demonstrates how to use the hypnofunk package to analyze
sleep data from Polyman software EDF files with annotations.

It processes all EDF files in a directory, extracts hypnograms,
calculates sleep parameters, performs transition analysis, and
generates visualizations.

Author: Rahul Venugopal
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog

try:
    import mne
    import yasa
except ImportError:
    print("This example requires mne and yasa packages.")
    print("Install with: pip install mne yasa")
    raise

# Import hypnofunk modules
from hypnofunk import hypnoman, analyze_transitions
from hypnofunk.core import find_nremstretches, find_rem_stretches
from hypnofunk.visualization import plot_hypnogram_with_cycles


def extract_hypnogram_from_edf(edf_path: str, epoch_duration: int = 30) -> list:
    """
    Extract hypnogram from Polyman EDF annotation file.
    
    Parameters
    ----------
    edf_path : str
        Path to EDF file with sleep stage annotations
    epoch_duration : int
        Duration of each epoch in seconds (default: 30)
        
    Returns
    -------
    list of str
        Hypnogram as list of stage labels, or None if invalid
    """
    # Load annotations
    sleep_data = mne.read_annotations(edf_path)
    hypnogram_annot = sleep_data.to_data_frame()
    
    # Convert duration to epoch count
    hypnogram_annot['duration'] = hypnogram_annot['duration'] / epoch_duration
    
    # Extract time information
    timestamps = hypnogram_annot['onset'].dt.strftime("%m/%d/%Y, %H:%M:%S")
    
    only_time = []
    for entry in timestamps:
        time_part = entry.split()[1]
        only_time.append(time_part.split(':'))
    
    # Convert to epoch numbers
    epochs_start = []
    for time_components in only_time:
        hh = int(time_components[0]) * 120  # hours to epochs
        mm = int(time_components[1]) * 2    # minutes to epochs
        ss = int(time_components[2]) / 30   # seconds to epochs
        epochs_start.append(int(hh + mm + ss))
    
    hypnogram_annot['onset'] = epochs_start
    
    # Clean up stage labels
    just_labels = []
    for entry in hypnogram_annot['description']:
        # Extract stage label (assumes format like "Sleep stage N2")
        parts = entry.split()
        if len(parts) >= 3:
            just_labels.append(parts[2])
        else:
            just_labels.append(entry)
    
    hypnogram_annot['description'] = just_labels
    
    # Reconstruct hypnogram by repeating labels
    hypno_30s = []
    for idx in range(len(hypnogram_annot)):
        stage = hypnogram_annot['description'].iloc[idx]
        duration = int(hypnogram_annot['duration'].iloc[idx])
        hypno_30s.extend([stage] * duration)
    
    # Validate that only sleep stages are present
    valid_stages = {'N1', 'N2', 'N3', 'R', 'W'}
    if not set(np.unique(hypno_30s)).issubset(valid_stages):
        return None
    
    return hypno_30s


def main():
    """Main analysis workflow."""
    # Select directories
    print("Select directory containing EDF files...")
    data_dir = filedialog.askdirectory(title='Select directory with EDF files')
    
    print("Select directory to save results...")
    results_dir = filedialog.askdirectory(title='Select directory to save results')
    
    if not data_dir or not results_dir:
        print("Directory selection cancelled.")
        return
    
    # Find all EDF files
    os.chdir(data_dir)
    filelist = glob.glob(os.path.join(data_dir, "*.edf"), recursive=True)
    
    print(f"\nFound {len(filelist)} EDF files")
    
    # Initialize results list
    masterlist = []
    
    # Process each file
    for file_no, fname in enumerate(filelist, 1):
        print(f"\nProcessing {file_no}/{len(filelist)}: {os.path.basename(fname)}")
        
        try:
            # Extract hypnogram
            hypno_30s = extract_hypnogram_from_edf(fname, epoch_duration=30)
            
            if hypno_30s is None:
                print(f"  ⚠ Skipped: File contains non-sleep annotations")
                continue
            
            # Detect sleep cycles
            _, nrem_indices = find_nremstretches(hypno_30s)
            _, rem_indices = find_rem_stretches(hypno_30s)
            
            print(f"  ✓ Detected {len(nrem_indices)} NREM and {len(rem_indices)} REM cycles")
            
            # Create visualization
            base_name = os.path.basename(fname)[:-4]
            save_path = os.path.join(results_dir, f"{base_name}.png")
            
            plot_hypnogram_with_cycles(
                hypno_30s,
                epoch_duration=30,
                nrem_indices=nrem_indices,
                rem_indices=rem_indices,
                save_path=save_path,
                dpi=600
            )
            plt.close()
            
            print(f"  ✓ Saved hypnogram plot")
            
            # Save hypnogram as CSV
            csv_path = os.path.join(results_dir, f"{base_name}.csv")
            np.savetxt(csv_path, hypno_30s, delimiter=',', fmt='%s')
            
            # Calculate sleep parameters
            sleep_params = hypnoman(pd.Series(hypno_30s), epoch_duration=30)
            
            # Calculate transition parameters
            trans_df = analyze_transitions(hypno_30s)
            
            # Merge results
            merged = pd.concat([sleep_params, trans_df], axis=1)
            merged['fname'] = base_name
            masterlist.append(merged)
            
            print(f"  ✓ Calculated sleep parameters")
            
        except Exception as e:
            print(f"  ✗ Error processing file: {str(e)}")
            continue
    
    # Save master results
    if masterlist:
        df = pd.concat(masterlist, axis=0)
        df = df.reset_index(drop=True)
        
        output_path = os.path.join(results_dir, 'sleep_parameters_mastersheet.csv')
        df.to_csv(output_path, index=False)
        
        print(f"\n{'='*60}")
        print(f"✓ Analysis complete!")
        print(f"✓ Processed {len(masterlist)} files successfully")
        print(f"✓ Results saved to: {output_path}")
        print(f"{'='*60}")
    else:
        print("\n⚠ No files were processed successfully")


if __name__ == "__main__":
    main()
