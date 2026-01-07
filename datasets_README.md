# Datasets for Peer Review Research

## Primary Datasets

### 1. PeerRead
- Source: github.com/allenai/PeerRead
- Size: ~15,000 paper-review pairs
- Format: JSON
- Download: git clone https://github.com/allenai/PeerRead.git

### 2. OpenReview ICLR Data
- Source: openreview.net API
- Size: ~5K submissions/year
- Install: pip install openreview-py

### 3. NeurIPS Consistency Experiment
- Source: arXiv:2011.01469
- Key Data: σ² ≈ 0.3-0.5 noise measurement

## Synthetic Data Generation

```python
import numpy as np
from scipy.stats import beta

# Quality distribution
qualities = beta.rvs(2, 5, size=10000)

# Noise model
def sigma(S, K, sigma0=0.3, alpha=0.5):
    return sigma0 * np.sqrt(1 + alpha * max(0, S/K - 1))
```

## Parameter Calibration
- σ₀² ≈ 0.3 (baseline noise)
- α ≈ 0.5 (noise growth)
- τ ≈ 0.25 (acceptance rate)
- Quality: Beta(2,5)
