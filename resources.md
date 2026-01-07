# Resources Catalog

## Summary
Resources for "The Review Death Spiral: Equilibrium Modeling of Peer Review under AI-Driven Scale"

## Papers

| Title | arXiv | Authors | Key Finding |
|-------|-------|---------|-------------|
| NeurIPS Noise Experiment | 2011.01469 | NeurIPS | σ²≈0.3-0.5, 50% inconsistency |
| Strategyproof Selection | 1806.06266 | Xu et al. | Strategic behavior models |
| LLM Peer Review | 2310.01783 | Liang et al. | AI review capabilities |
| PeerReview4All | 1905.01989 | Stelmakh et al. | Assignment algorithms |
| Statistical Discrimination | 2103.03591 | Shah et al. | Heterogeneous effects |
| Calibration Methods | 1909.00784 | Wang et al. | Noise reduction |

### Download Commands
```bash
mkdir -p papers && cd papers
wget https://arxiv.org/pdf/2011.01469.pdf -O neurips_noise.pdf
wget https://arxiv.org/pdf/1806.06266.pdf -O strategyproof.pdf
wget https://arxiv.org/pdf/2310.01783.pdf -O llm_review.pdf
wget https://arxiv.org/pdf/1905.01989.pdf -O peerreview4all.pdf
```

## Datasets

| Name | Source | Size | Purpose |
|------|--------|------|---------|
| PeerRead | github.com/allenai/PeerRead | 15K reviews | Baseline data |
| OpenReview | openreview.net API | ~5K/year | ICLR/NeurIPS |
| NeurIPS Experiment | arXiv paper | Noise calibration | σ² measurement |
| Synthetic | Generated | Configurable | Equilibrium simulation |

### Download
```bash
git clone https://github.com/allenai/PeerRead.git datasets/PeerRead
pip install openreview-py
```

## Code Repositories

| Repository | Purpose | URL |
|------------|---------|-----|
| PeerReview4All | Assignment | github.com/niharshah/PeerReview4All |
| openreview-py | API client | github.com/openreview/openreview-py |
| PeerRead | Baselines | github.com/allenai/PeerRead |

## Recommendations

### For Simulation
- Use synthetic data with Beta(2,5) quality distribution
- Calibrate σ₀² = 0.3 from NeurIPS experiment
- Model equilibrium as fixed point: S = 1 - F(q*(S))

### Baselines
1. Fixed noise model (σ² constant)
2. No-endogeneity model
3. Capacity-only / precision-only variants

### Key Parameters
- σ₀² = 0.3, α = 0.5, τ = 0.25
- Quality: Beta(2,5)

### AI Interventions
1. Δc: Submission cost reduction
2. ΔK: Review capacity increase
3. Δσ²: Review precision improvement
