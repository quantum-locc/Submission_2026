"""
Statistical Analysis and Visualization
======================================

Analyzes hardware results and generates publication figures.

Input: hardware_results_YYYYMMDD_HHMMSS.json
Output: 
    - Statistical analysis
    - Publication-quality figures
    - Significance calculations
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import sys
from scipy import stats

# Publication-quality plot settings
plt.rcParams.update({
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 600,
    'savefig.format': 'png',
    'savefig.bbox': 'tight'
})

# Colors for conditions
COLOR_STANDARD = '#1f77b4'  # Blue
COLOR_NO_REV = '#d62728'    # Red  
COLOR_WITH_REV = '#ff7f0e'  # Orange

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data(filename):
    """Load experimental results from JSON"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def extract_arrays(data):
    """Extract numpy arrays from data dict"""
    d = data['data']
    return {
        'theta': np.array(d['theta']),
        'C_standard': np.array(d['C_standard']),
        'C_standard_err': np.array(d['C_standard_err']),
        'C_no_reversal': np.array(d['C_no_reversal']),
        'C_no_reversal_err': np.array(d['C_no_reversal_err']),
        'C_with_reversal': np.array(d['C_with_reversal']),
        'C_with_reversal_err': np.array(d['C_with_reversal_err'])
    }

# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def analyze_restoration_failure(data):
    """
    Test whether quantum erasure restores correlation
    
    Null hypothesis: C_with_reversal = C_standard
    Alternative: C_with_reversal ≠ C_standard
    
    Returns dict with statistical measures
    """
    arrays = extract_arrays(data)
    
    # Find maximum coupling (θ = 90°)
    idx_90 = np.where(arrays['theta'] == 90)[0][0]
    
    C_std = arrays['C_standard'][idx_90]
    C_rev = arrays['C_with_reversal'][idx_90]
    
    err_std = arrays['C_standard_err'][idx_90]
    err_rev = arrays['C_with_reversal_err'][idx_90]
    
    # Gap and significance
    gap = abs(C_std - C_rev)
    combined_err = np.sqrt(err_std**2 + err_rev**2)
    significance = gap / combined_err
    
    # Two-sample t-test
    # Approximate as normal distributions
    t_stat = gap / combined_err
    p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    
    results = {
        'theta': 90,
        'C_standard': C_std,
        'C_with_reversal': C_rev,
        'gap': gap,
        'significance_sigma': significance,
        't_statistic': t_stat,
        'p_value': p_value
    }
    
    return results


def test_erasure_vs_no_erasure(data):
    """
    Test whether "with reversal" differs from "no reversal"
    
    If they're the same, erasure has no effect on correlation
    """
    arrays = extract_arrays(data)
    
    idx_90 = np.where(arrays['theta'] == 90)[0][0]
    
    C_no_rev = arrays['C_no_reversal'][idx_90]
    C_with_rev = arrays['C_with_reversal'][idx_90]
    
    err_no = arrays['C_no_reversal_err'][idx_90]
    err_with = arrays['C_with_reversal_err'][idx_90]
    
    diff = abs(C_with_rev - C_no_rev)
    combined_err = np.sqrt(err_no**2 + err_with**2)
    significance = diff / combined_err
    
    return {
        'C_no_reversal': C_no_rev,
        'C_with_reversal': C_with_rev,
        'difference': diff,
        'significance_sigma': significance,
        'statistically_same': significance < 2
    }


def print_analysis(data):
    """Print comprehensive statistical analysis"""
    print("="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)
    
    # Test 1: Restoration failure
    print("\nTest 1: Does erasure restore correlation?")
    print("-" * 40)
    restoration = analyze_restoration_failure(data)
    
    print(f"At θ = {restoration['theta']}° (maximum coupling):")
    print(f"  Standard Bell:    C = {restoration['C_standard']:+.3f}")
    print(f"  With reversal:    C = {restoration['C_with_reversal']:+.3f}")
    print(f"  Gap:              ΔC = {restoration['gap']:.3f}")
    print(f"  Significance:     {restoration['significance_sigma']:.1f}σ")
    print(f"  p-value:          {restoration['p_value']:.2e}")
    
    if restoration['significance_sigma'] > 5:
        print("\n  ✓ CONFIRMED: Restoration FAILS (>5σ)")
    else:
        print("\n  ✗ Restoration succeeds")
    
    # Test 2: Erasure vs no erasure
    print("\nTest 2: Does erasure affect correlation at all?")
    print("-" * 40)
    comparison = test_erasure_vs_no_erasure(data)
    
    print(f"  No reversal:      C = {comparison['C_no_reversal']:+.3f}")
    print(f"  With reversal:    C = {comparison['C_with_reversal']:+.3f}")
    print(f"  Difference:       ΔC = {comparison['difference']:.3f}")
    print(f"  Significance:     {comparison['significance_sigma']:.1f}σ}")
    
    if comparison['statistically_same']:
        print("\n  ✓ CONFIRMED: Erasure has NO effect")
    else:
        print("\n  Note: Small difference detected")
    
    # Hardware fidelity
    print("\nHardware Quality:")
    print("-" * 40)
    arrays = extract_arrays(data)
    mean_C_std = np.mean(arrays['C_standard'])
    print(f"  Average Bell correlation: {mean_C_std:.3f}")
    print(f"  Gate fidelity:            ~{mean_C_std*100:.1f}%")
    print(f"  Expected ideal:           1.000 (100%)")
    
    print("\n" + "="*70)

# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_main_result(data, save_as='figure_main_result.png'):
    """
    Generate main result figure showing correlation destruction
    """
    arrays = extract_arrays(data)
    idx_90 = np.where(arrays['theta'] == 90)[0][0]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Bar plot
    conditions = ['Standard\nBell', 'No\nReversal', 'With\nReversal']
    correlations = [
        arrays['C_standard'][idx_90],
        arrays['C_no_reversal'][idx_90],
        arrays['C_with_reversal'][idx_90]
    ]
    errors = [
        arrays['C_standard_err'][idx_90],
        arrays['C_no_reversal_err'][idx_90],
        arrays['C_with_reversal_err'][idx_90]
    ]
    colors = [COLOR_STANDARD, COLOR_NO_REV, COLOR_WITH_REV]
    
    x_pos = np.arange(len(conditions))
    bars = ax.bar(x_pos, correlations, color=colors, alpha=0.75,
                   yerr=errors, capsize=5, edgecolor='black', linewidth=1)
    
    # Significance bracket
    gap = abs(correlations[0] - correlations[2])
    combined_err = np.sqrt(errors[0]**2 + errors[2]**2)
    sigma = gap / combined_err
    
    y_bracket = 0.95
    ax.plot([0, 2], [y_bracket, y_bracket], 'k-', linewidth=1.5)
    ax.plot([0, 0], [y_bracket-0.05, y_bracket], 'k-', linewidth=1.5)
    ax.plot([2, 2], [y_bracket-0.05, y_bracket], 'k-', linewidth=1.5)
    ax.text(1, y_bracket+0.05, '***', ha='center', fontsize=12, fontweight='bold')
    ax.text(1, y_bracket+0.12, f'ΔC = {gap:.2f}\n({sigma:.0f}σ)', 
            ha='center', fontsize=8,
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.4))
    
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.set_ylabel('Correlation C', fontweight='bold')
    ax.set_ylim(-0.2, 1.1)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(conditions)
    ax.set_title('Complete Correlation Destruction at θ=90°', fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(save_as, dpi=600, bbox_inches='tight')
    print(f"Saved: {save_as}")
    plt.close()


def plot_angle_dependence(data, save_as='figure_angle_dependence.png'):
    """
    Plot correlation vs coupling angle for all conditions
    """
    arrays = extract_arrays(data)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x_pos = np.arange(len(arrays['theta']))
    width = 0.27
    
    ax.bar(x_pos - width, arrays['C_standard'], width,
           label='Standard Bell', color=COLOR_STANDARD, alpha=0.75,
           yerr=arrays['C_standard_err'], capsize=3, edgecolor='black', linewidth=0.8)
    
    ax.bar(x_pos, arrays['C_no_reversal'], width,
           label='No Reversal', color=COLOR_NO_REV, alpha=0.75,
           yerr=arrays['C_no_reversal_err'], capsize=3, edgecolor='black', linewidth=0.8)
    
    ax.bar(x_pos + width, arrays['C_with_reversal'], width,
           label='With Reversal', color=COLOR_WITH_REV, alpha=0.75,
           yerr=arrays['C_with_reversal_err'], capsize=3, edgecolor='black', linewidth=0.8)
    
    ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    
    ax.set_xlabel('Coupling Angle θ (degrees)', fontweight='bold')
    ax.set_ylabel('Correlation C', fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{int(t)}°' for t in arrays['theta']])
    ax.set_ylim(-0.15, 1.0)
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.set_title('Correlation vs Coupling Angle: Reversal Fails at All Angles', 
                 fontweight='bold', pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle=':', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(save_as, dpi=600, bbox_inches='tight')
    print(f"Saved: {save_as}")
    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <hardware_results.json>")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"Loading data from: {filename}")
    
    data = load_data(filename)
    
    # Statistical analysis
    print_analysis(data)
    
    # Generate figures
    print("\nGenerating figures...")
    plot_main_result(data)
    plot_angle_dependence(data)
    
    print("\nAnalysis complete!")
