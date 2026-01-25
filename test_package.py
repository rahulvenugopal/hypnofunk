"""
Simple test script to verify hypnofunk package structure and basic functionality.

This script tests the package without requiring installation.
"""

import sys
import os

# Add parent directory to path to import hypnofunk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing hypnofunk package structure")
print("=" * 60)

# Test 1: Import main modules
print("\n1. Testing imports...")
try:
    from hypnofunk import hypnoman, analyze_transitions
    from hypnofunk.core import find_nremstretches, find_rem_stretches
    from hypnofunk.transitions import compute_transition_matrix
    from hypnofunk.utils import validate_hypnogram, convert_to_numeric
    print("   ✓ All imports successful")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create a simple hypnogram
print("\n2. Creating test hypnogram...")
test_hypnogram = ["W"] * 10 + ["N2"] * 50 + ["N3"] * 30 + ["R"] * 20 + ["W"] * 5
print(f"   ✓ Created hypnogram with {len(test_hypnogram)} epochs")

# Test 3: Validate hypnogram
print("\n3. Testing hypnogram validation...")
try:
    validated = validate_hypnogram(test_hypnogram)
    print(f"   ✓ Validation successful")
except Exception as e:
    print(f"   ✗ Validation failed: {e}")
    sys.exit(1)

# Test 4: Calculate sleep parameters
print("\n4. Testing sleep parameter calculation...")
try:
    sleep_params = hypnoman(test_hypnogram, epoch_duration=30)
    print(f"   ✓ Sleep parameters calculated")
    print(f"      - Total Sleep Time: {sleep_params['TST'].values[0]:.1f} minutes")
    print(f"      - Sleep Efficiency: {sleep_params['Sleep_efficiency'].values[0]:.1f}%")
    print(f"      - Sleep Onset Latency: {sleep_params['SOL'].values[0]:.1f} minutes")
except Exception as e:
    print(f"   ✗ Sleep parameter calculation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Analyze transitions
print("\n5. Testing transition analysis...")
try:
    transitions = analyze_transitions(test_hypnogram)
    print(f"   ✓ Transition analysis complete")
    print(f"      - Total Transitions: {transitions['Total_Transitions'].values[0]}")
    print(f"      - Sleep Compactness: {transitions['Sleep_Compactness'].values[0]:.3f}")
    print(f"      - Prob Wake Transition: {transitions['Prob_Wake_Transition'].values[0]:.3f}")
except Exception as e:
    print(f"   ✗ Transition analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Detect sleep cycles
print("\n6. Testing sleep cycle detection...")
try:
    nrem_stretches, nrem_indices = find_nremstretches(test_hypnogram)
    rem_stretches, rem_indices = find_rem_stretches(test_hypnogram)
    print(f"   ✓ Sleep cycle detection complete")
    print(f"      - NREM cycles detected: {len(nrem_indices)}")
    print(f"      - REM cycles detected: {len(rem_indices)}")
except Exception as e:
    print(f"   ✗ Sleep cycle detection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Compute transition matrix
print("\n7. Testing transition matrix computation...")
try:
    counts, probs = compute_transition_matrix(test_hypnogram)
    print(f"   ✓ Transition matrix computed")
    print(f"      - Matrix shape: {probs.shape}")
    print(f"      - N2 persistence: {probs.loc['N2', 'N2']:.3f}")
except Exception as e:
    print(f"   ✗ Transition matrix computation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed successfully!")
print("=" * 60)
print("\nPackage structure is correct and all core functions work.")
print("\nTo install the package, run:")
print("  python -m pip install -e .")
print("\nOr to install with full dependencies:")
print("  python -m pip install -e .[full]")
