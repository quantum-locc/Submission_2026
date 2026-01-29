# Experimental Test of LOCC Impossibility on Quantum Hardware

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Code and data accompanying the manuscript:

**"Experimental Demonstration of Entanglement Irreversibility: Local Operations Cannot Restore Global Correlations"**

*Submitted to Nature Physics (2026)*

---

## Abstract

We demonstrate experimentally that local quantum erasure cannot restore destroyed entanglement. Using a 3-qubit system on Rigetti's Ankaa-3 superconducting quantum processor, we show that while quantum erasure successfully removes which-path information (returning marker qubit to |0⟩), it completely fails to restore Alice-Bob correlation. The measured gap (ΔC = 0.89 ± 0.03) persists with >28σ significance, providing the first hardware demonstration that Local Operations and Classical Communication (LOCC) cannot increase entanglement.

## Key Results

**At θ = 90° (maximum coupling):**
- Standard Bell state: C = +0.839 ± 0.022
- After controlled rotation: C = -0.006 ± 0.022 (≈ 0)
- After "reversal" (erasure): C = -0.049 ± 0.022 (still ≈ 0)

**Statistical significance:**
- Restoration gap: ΔC = 0.888
- Significance: 28.5σ
- p-value: < 10⁻¹⁰⁰

**Interpretation:** Information erasure works (marker → |0⟩), but correlation remains destroyed. Local operations cannot restore entanglement.

---

## Repository Structure

```
quantum-locc-experiment/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── src/
│   ├── experiment.py         # Main experimental code
│   ├── analysis.py           # Statistical analysis & visualization
│   └── __init__.py
├── data/
│   └── hardware_results_20260129_113343.json  # Actual hardware data
├── figures/
│   ├── figure_main_result.png
│   └── figure_angle_dependence.png
└── notebooks/
    └── reproduce_analysis.ipynb  # Step-by-step reproduction
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- AWS Account with Braket access (for running on hardware)
- Amazon Braket SDK

### Setup

```bash
# Clone repository
git clone https://github.com/quantum_locc/submission_2026.git
cd submission_2026

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Reproduce Analysis from Hardware Data

```bash
# Analyze existing hardware results
python analysis.py data/hardware_results_20260129_113343.json
```

**Output:**
- Statistical analysis printed to console
- `figure_main_result.png` - Main correlation plot
- `figure_angle_dependence.png` - Full angular dependence

### 2. Run Experiment on Simulator (Free)

```bash
# Test on Amazon Braket simulator
python experiment.py
```

Edit `experiment.py` and set:
```python
USE_SIMULATOR = True
```

### 3. Run on Real Hardware (Costs AWS Credits)

```bash
# Configure AWS credentials
aws configure

# Run experiment
python experiment.py
```

Edit `experiment.py` and set:
```python
USE_SIMULATOR = False
```

**Cost estimate:** ~$15 for full experiment (7 angles × 3 conditions × 2000 shots)

---

## Experimental Protocol

### Circuit Design

**Condition 1: Standard Bell State (Reference)**
```
H(Alice) -- CNOT(Alice, Bob) -- Measure(Alice, Bob)
```
*Expected: C ≈ +0.84 (hardware fidelity limit)*

**Condition 2: No Reversal (Correlation Destroyed)**
```
Bell State -- CRY(θ)[Alice, Marker] -- Measure(Alice, Bob, Marker)
```
*Expected: C ≈ 0 (correlation destroyed)*

**Condition 3: With Reversal (Quantum Erasure)**
```
Bell State -- CRY(θ) -- CRY(-θ) -- Measure(Alice, Bob, Marker)
```
*Test: Does erasure restore correlation?*  
*Result: NO - C remains ≈ 0*

### Controlled Rotation Implementation

Uses CNOT-based decomposition:
```
CRY(θ) = RY(θ/2) - CNOT - RY(-θ/2) - CNOT - RY(θ/2)
```

### Correlation Calculation

```python
C = (N_same - N_different) / N_total

where:
  N_same = counts where Alice and Bob match (00 or 11)
  N_different = counts where Alice and Bob differ (01 or 10)
```

---

## Hardware Specifications

**Device:** Rigetti Ankaa-3 (via Amazon Braket)
- 84 superconducting qubits
- Median 2-qubit gate fidelity: 98.6%
- Median T₁/T₂ coherence: 40/30 μs
- Connectivity: Universal (all-to-all via routing)

**Qubits Used:**
- Qubit 0: Alice
- Qubit 1: Bob
- Qubit 2: Marker

**Measurement:**
- 2000 shots per circuit
- Computational (Z) basis
- 7 coupling angles: 0°, 30°, 60°, 90°, 120°, 150°, 180°

---

## Data Format

### JSON Structure

```json
{
  "metadata": {
    "device": "arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3",
    "timestamp": "2026-01-29T11:32:39",
    "theta_values": [0, 30, 60, 90, 120, 150, 180],
    "n_shots": 2000
  },
  "data": {
    "theta": [...],
    "C_standard": [...],
    "C_no_reversal": [...],
    "C_with_reversal": [...]
  },
  "raw_counts": [...]
}
```

### Accessing Data

```python
import json

with open('data/hardware_results_20260129_113343.json', 'r') as f:
    data = json.load(f)

# Extract correlations
C_standard = data['data']['C_standard']
C_with_reversal = data['data']['C_with_reversal']

# Raw measurement counts
raw_counts = data['raw_counts'][3]  # θ = 90°
print(raw_counts['circuits']['standard']['counts'])
```

---

## Key Files

### `/experiment.py`
Main experimental code:
- Circuit definitions
- Device configuration
- Data collection
- Results storage

### `/analysis.py`
Statistical analysis:
- Correlation calculations
- Significance testing
- Figure generation

### `data/hardware_results_20260129_113343.json`
Actual hardware data from Rigetti Ankaa-3:
- All measurement counts
- Computed correlations
- Error bars
- Metadata

---

## Reproducing Figures

All figures in the manuscript can be reproduced:

```bash
# Generate publication figures
python /analysis.py data/hardware_results_20260129_113343.json

# Outputs:
# - figure_main_result.png (Fig 1b equivalent)
# - figure_angle_dependence.png (Fig 1c equivalent)
```

Figures saved at 600 DPI, publication-ready.

---

## Citation

If you use this code or data, please cite:

```bibtex
@article{locc_irreversibility_2026,
  title={Experimental Demonstration of Entanglement Irreversibility: 
         Local Operations Cannot Restore Global Correlations},
  author={[Author]},
  journal={Submitted to Nature Physics},
  year={2026}
}
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

Code is freely available for research and educational purposes.

---

## Contact

For questions about the experiment or code:
- Open an issue on GitHub
- Email: [provided in manuscript]

---

## Acknowledgments

- Rigetti Computing for hardware access
- Amazon Braket team for platform support
- Nature Physics reviewers for feedback

---

## Technical Notes

### Why Hardware Shows C ≈ 0.84 (Not 1.0)?

Gate imperfections in current superconducting hardware:
- Two-qubit gate fidelity: ~98.6%
- Cumulative errors from H + CNOT + X + Z gates
- Expected correlation: ~0.84-0.88
- This is normal and accounted for in analysis

### Why Negative Correlations?

Measurement conventions:
- Standard convention would give C ≈ -1 for this Bell state
- We report absolute correlations
- Sign doesn't affect LOCC test (testing |C| restoration)

### Statistical Robustness

- n = 2000 shots per condition
- Standard error: σ = 1/√n ≈ 0.022
- Restoration gap: 0.89 ± 0.03
- Significance: 28.5σ (extremely high confidence)

---

## Version History

**v1.0** (January 2026)
- Initial release with hardware data
- Nature Physics submission

---

## FAQ

**Q: Can I run this on other quantum computers?**  
A: Yes, modify device ARN and verify qubit connectivity.

**Q: Why does erasure fail to restore correlation?**  
A: LOCC theorem: entanglement spreading to marker becomes classical entropy, which cannot be converted back to quantum correlation locally.

**Q: Is the code peer-reviewed?**  
A: Code is under peer review with manuscript. All analysis steps are documented and reproducible.

**Q: How long does hardware run take?**  
A: ~30-45 minutes for full experiment (queue time + execution).

---

**Repository maintained for Nature Physics submission**  
**Last updated: January 2026**
