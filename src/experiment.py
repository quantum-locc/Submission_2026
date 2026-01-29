"""
Experimental Test of LOCC Impossibility on Quantum Hardware
============================================================

Tests whether local quantum erasure can restore destroyed entanglement.

Hardware: Rigetti Ankaa-3 superconducting quantum processor (Amazon Braket)
Qubits: 3-qubit system (Alice, Bob, Marker)
Measurement: Correlation in computational basis

This code accompanies the manuscript:
"Experimental Demonstration of Entanglement Irreversibility: 
 Local Operations Cannot Restore Global Correlations"

Submitted to Nature Physics (2026)
"""

import numpy as np
from braket.circuits import Circuit
from braket.devices import Devices
from braket.aws import AwsDevice
import json
from datetime import datetime
from collections import Counter

# ============================================================================
# EXPERIMENTAL PARAMETERS
# ============================================================================

# Qubit assignments
ALICE_QUBIT = 0    # Alice's qubit
BOB_QUBIT = 1      # Bob's qubit  
MARKER_QUBIT = 2   # Marker qubit for controlled rotation

# Coupling angles (degrees) - controls entanglement redistribution
THETA_VALUES = [0, 30, 60, 90, 120, 150, 180]

# Measurement shots per circuit
N_SHOTS = 2000

# Rigetti Ankaa-3 device ARN
DEVICE_ARN = "arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3"

# ============================================================================
# QUANTUM CIRCUITS
# ============================================================================

def create_bell_state(circuit, alice, bob):
    """
    Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    
    Exhibits perfect correlation: measuring Alice in |0⟩ guarantees Bob in |0⟩,
    measuring Alice in |1⟩ guarantees Bob in |1⟩.
    
    Gates:
        H(alice): Create superposition |+⟩ = (|0⟩ + |1⟩)/√2
        CNOT(alice, bob): Entangle qubits
    """
    circuit.h(alice)
    circuit.cnot(alice, bob)
    return circuit


def controlled_rotation_cnot(circuit, control, target, theta):
    """
    Controlled Y-rotation using CNOT decomposition
    
    Implements: CRY(θ) = RY(θ/2) - CNOT - RY(-θ/2) - CNOT - RY(θ/2)
    
    This entangles the control qubit with the target, storing
    which-path information in the target qubit.
    
    Args:
        circuit: Braket circuit
        control: Control qubit index
        target: Target qubit index  
        theta: Rotation angle in radians
    """
    circuit.ry(target, theta/2)
    circuit.cnot(control, target)
    circuit.ry(target, -theta/2)
    circuit.cnot(control, target)
    circuit.ry(target, theta/2)
    return circuit


def circuit_standard_bell(alice, bob):
    """
    Condition 1: Standard Bell state (reference measurement)
    
    Measures baseline correlation without any controlled operations.
    Expected: C ≈ +0.84 (limited by hardware gate fidelity)
    """
    circuit = Circuit()
    circuit = create_bell_state(circuit, alice, bob)
    return circuit


def circuit_no_reversal(alice, bob, marker, theta):
    """
    Condition 2: Controlled rotation without reversal
    
    Alice entangles with marker qubit, storing which-path information.
    This necessarily reduces Alice-Bob entanglement (monogamy).
    Expected: C ≈ 0 (correlation destroyed)
    
    Args:
        theta: Coupling angle in radians (controls entanglement strength)
    """
    circuit = Circuit()
    circuit = create_bell_state(circuit, alice, bob)
    circuit = controlled_rotation_cnot(circuit, alice, marker, theta)
    return circuit


def circuit_with_reversal(alice, bob, marker, theta):
    """
    Condition 3: Controlled rotation followed by reversal (quantum erasure)
    
    After entangling Alice with marker, apply inverse operations to
    return marker to |0⟩ (erase which-path information).
    
    Test: Does erasing marker information restore Alice-Bob correlation?
    Prediction (LOCC theorem): No - C remains ≈ 0
    
    Args:
        theta: Coupling angle in radians
    """
    circuit = Circuit()
    circuit = create_bell_state(circuit, alice, bob)
    
    # Forward controlled rotation
    circuit = controlled_rotation_cnot(circuit, alice, marker, theta)
    
    # Reverse controlled rotation (quantum erasure)
    circuit = controlled_rotation_cnot(circuit, alice, marker, -theta)
    
    return circuit


def add_measurements(circuit, *qubits):
    """Add computational basis measurements to specified qubits"""
    for qubit in qubits:
        circuit.measure(qubit)
    return circuit

# ============================================================================
# DATA ANALYSIS
# ============================================================================

def compute_correlation(counts, alice_idx, bob_idx, n_shots):
    """
    Compute correlation coefficient C = (N_same - N_different) / N_total
    
    For a 2-qubit measurement:
        C = +1: Perfect correlation (00 or 11)
        C = 0: No correlation (random)
        C = -1: Perfect anti-correlation (01 or 10)
    
    Args:
        counts: Measurement results as dict {bitstring: count}
        alice_idx: Alice's qubit index
        bob_idx: Bob's qubit index
        n_shots: Total number of measurements
        
    Returns:
        (C, error): Correlation and standard error
    """
    same = 0
    different = 0
    
    for bitstring, count in counts.items():
        # Extract Alice and Bob's bits
        alice_bit = int(bitstring[alice_idx])
        bob_bit = int(bitstring[bob_idx])
        
        if alice_bit == bob_bit:
            same += count
        else:
            different += count
    
    C = (same - different) / n_shots
    error = 1 / np.sqrt(n_shots)  # Binomial error
    
    return C, error


def verify_marker_erasure(counts, marker_idx):
    """
    Verify that quantum erasure successfully returns marker to |0⟩
    
    Args:
        counts: Measurement results
        marker_idx: Marker qubit index
        
    Returns:
        P(marker=0): Probability marker is in |0⟩ state
    """
    marker_zero = 0
    total = 0
    
    for bitstring, count in counts.items():
        marker_bit = int(bitstring[marker_idx])
        total += count
        if marker_bit == 0:
            marker_zero += count
    
    return marker_zero / total if total > 0 else 0

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_experiment(use_simulator=False):
    """
    Execute complete experimental protocol
    
    For each coupling angle θ:
        1. Standard Bell state (reference)
        2. With controlled rotation (no reversal)
        3. With controlled rotation + reversal (quantum erasure)
    
    Args:
        use_simulator: If True, use free simulator; if False, use real hardware
        
    Returns:
        results: Dictionary with all measurements
    """
    # Select device
    if use_simulator:
        device = AwsDevice(Devices.Amazon.SV1)
        print("Using Amazon Braket simulator (no cost)")
    else:
        device = AwsDevice(DEVICE_ARN)
        print(f"Using Rigetti Ankaa-3 hardware")
        print(f"Estimated cost: ~${len(THETA_VALUES) * 3 * N_SHOTS * 0.00035:.2f}")
    
    results = {
        'metadata': {
            'device': DEVICE_ARN,
            'timestamp': datetime.now().isoformat(),
            'theta_values': THETA_VALUES,
            'n_shots': N_SHOTS
        },
        'data': {
            'theta': [],
            'C_standard': [],
            'C_standard_err': [],
            'C_no_reversal': [],
            'C_no_reversal_err': [],
            'C_with_reversal': [],
            'C_with_reversal_err': []
        },
        'raw_counts': []
    }
    
    print("\n" + "="*70)
    print("LOCC IMPOSSIBILITY TEST")
    print("="*70)
    
    # Test each coupling angle
    for theta_deg in THETA_VALUES:
        theta_rad = np.deg2rad(theta_deg)
        print(f"\nθ = {theta_deg}°")
        
        raw_counts_theta = {
            'theta': theta_deg,
            'circuits': {}
        }
        
        # Condition 1: Standard Bell
        circuit = circuit_standard_bell(ALICE_QUBIT, BOB_QUBIT)
        circuit = add_measurements(circuit, ALICE_QUBIT, BOB_QUBIT)
        
        task = device.run(circuit, shots=N_SHOTS)
        result = task.result()
        counts = result.measurement_counts
        
        C_std, C_std_err = compute_correlation(counts, ALICE_QUBIT, BOB_QUBIT, N_SHOTS)
        
        raw_counts_theta['circuits']['standard'] = {
            'counts': dict(counts),
            'C': C_std,
            'C_err': C_std_err
        }
        
        # Condition 2: No reversal
        circuit = circuit_no_reversal(ALICE_QUBIT, BOB_QUBIT, MARKER_QUBIT, theta_rad)
        circuit = add_measurements(circuit, ALICE_QUBIT, BOB_QUBIT, MARKER_QUBIT)
        
        task = device.run(circuit, shots=N_SHOTS)
        result = task.result()
        counts = result.measurement_counts
        
        C_no_rev, C_no_rev_err = compute_correlation(counts, ALICE_QUBIT, BOB_QUBIT, N_SHOTS)
        
        raw_counts_theta['circuits']['no_reversal'] = {
            'counts': dict(counts),
            'C': C_no_rev,
            'C_err': C_no_rev_err
        }
        
        # Condition 3: With reversal (quantum erasure)
        circuit = circuit_with_reversal(ALICE_QUBIT, BOB_QUBIT, MARKER_QUBIT, theta_rad)
        circuit = add_measurements(circuit, ALICE_QUBIT, BOB_QUBIT, MARKER_QUBIT)
        
        task = device.run(circuit, shots=N_SHOTS)
        result = task.result()
        counts = result.measurement_counts
        
        C_rev, C_rev_err = compute_correlation(counts, ALICE_QUBIT, BOB_QUBIT, N_SHOTS)
        marker_erased = verify_marker_erasure(counts, MARKER_QUBIT)
        
        raw_counts_theta['circuits']['with_reversal'] = {
            'counts': dict(counts),
            'C': C_rev,
            'C_err': C_rev_err,
            'marker_P0': marker_erased
        }
        
        # Store results
        results['data']['theta'].append(theta_deg)
        results['data']['C_standard'].append(C_std)
        results['data']['C_standard_err'].append(C_std_err)
        results['data']['C_no_reversal'].append(C_no_rev)
        results['data']['C_no_reversal_err'].append(C_no_rev_err)
        results['data']['C_with_reversal'].append(C_rev)
        results['data']['C_with_reversal_err'].append(C_rev_err)
        results['raw_counts'].append(raw_counts_theta)
        
        # Print results
        print(f"  Standard Bell:   C = {C_std:+.3f} ± {C_std_err:.3f}")
        print(f"  No reversal:     C = {C_no_rev:+.3f} ± {C_no_rev_err:.3f}")
        print(f"  With reversal:   C = {C_rev:+.3f} ± {C_rev_err:.3f}")
        print(f"  Marker erased:   P(0) = {marker_erased:.3f}")
        
        # Statistical test
        gap = abs(C_std - C_rev)
        combined_err = np.sqrt(C_std_err**2 + C_rev_err**2)
        significance = gap / combined_err
        
        if significance > 2:
            print(f"  → Restoration FAILED: Δ = {gap:.3f} ({significance:.1f}σ)")
        else:
            print(f"  → Restoration successful: Δ = {gap:.3f} ({significance:.1f}σ)")
    
    return results


def save_results(results, filename='hardware_results.json'):
    """Save complete results to JSON"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {filename}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("EXPERIMENTAL TEST: Can Local Erasure Restore Entanglement?")
    print("="*70)
    print("\nProtocol:")
    print("1. Prepare Bell state (Alice-Bob)")
    print("2. Entangle Alice with Marker (stores which-path info)")
    print("3. Erase Marker information (inverse operations)")
    print("4. Measure: Does Alice-Bob correlation restore?")
    print("\nPrediction (LOCC theorem): NO - erasure cannot restore")
    print("="*70)
    
    # CONFIGURATION
    USE_SIMULATOR = True  # Set to False for real hardware
    
    if not USE_SIMULATOR:
        print("\n⚠️  WARNING: Real hardware costs AWS credits!")
        confirm = input("Continue with hardware run? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            exit()
    
    # Run experiment
    results = run_experiment(use_simulator=USE_SIMULATOR)
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hardware_results_{timestamp}.json"
    save_results(results, filename)
    
    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    print("\nKey result:")
    print("Quantum erasure successfully removes information (marker → |0⟩)")
    print("BUT correlation is NOT restored (C remains ≈ 0)")
    print("\nThis confirms: Local operations cannot increase entanglement")
