# Literature Review: Peer Review Equilibrium Modeling under AI-Driven Scale

## Research Area Overview

This review examines peer review mechanism design, game theory, and AI impacts on scientific publishing, focusing on equilibrium dynamics and potential system collapse.

## Key Papers

### 1. How Noisy Is Peer Review? (NeurIPS Experiment, 2021)
- **arXiv**: 2011.01469
- **Key Finding**: ~50% of accepted papers would be rejected with different reviewers
- **Noise Estimate**: σ² ≈ 0.3-0.5
- **Relevance**: CRITICAL for calibrating noise model σ²(S)

### 2. Strategyproof Peer Selection (Xu et al., 2018)
- **arXiv**: 1806.06266
- **Authors**: Yichong Xu, Han Zhao, Xiaofei Shi, Nihar Shah
- **Key Finding**: Conditions for multiple equilibria in peer review
- **Relevance**: Models strategic author behavior driving submission volume S

### 3. Mechanism Design for Peer Review (Shah et al.)
- **Source**: Multiple venues (AAAI, WWW, EC)
- **Key Contribution**: Incentive-compatible peer review mechanisms
- **Relevance**: Foundation for understanding incentive structures

### 4. Incentivizing Quality Review (de Clippel et al., 2019)
- **Source**: Theoretical Economics
- **Key Contribution**: Mechanism design for reviewer effort
- **Relevance**: Endogenous noise σ²(S) and capacity constraints

### 5. Can LLMs Provide Useful Feedback? (Liang et al., 2023)
- **arXiv**: 2310.01783
- **Key Finding**: LLMs provide surface feedback, struggle with deep evaluation
- **Relevance**: Models AI intervention parameters (Δc, ΔK, Δσ²)

### 6. PeerReview4All (Stelmakh et al., 2019)
- **arXiv**: 1905.01989
- **Key Contribution**: Optimal reviewer-paper matching under constraints
- **Relevance**: Informs capacity constraint K

## Common Methodologies

1. **Game-Theoretic Analysis**: Nash equilibrium, mechanism design
2. **Empirical Measurement**: Large-scale experiments, inter-reviewer agreement
3. **Simulation**: Agent-based models, Monte Carlo

## Key Model Components

### Quality Distribution F(q)
- Standard: Beta(α,β) with α<β (right-skewed)
- Typical: Beta(2,5)

### Submission Decision
- Authors submit if V·P_acc(q;S) ≥ c
- Induces threshold q*(S)

### Review Noise Model
- σ²(S) = σ₀²·(1 + α·max(0, S/K - 1))
- Noise increases with load relative to capacity

### Equilibrium
- Fixed point: S = 1 - F(q*(S))
- Multiple equilibria possible

## Gaps and Opportunities

1. **Dynamic Analysis**: Most work is static
2. **Multiple Equilibria Validation**: Limited empirical evidence
3. **AI Impact Modeling**: Needs rigorous treatment
4. **Intervention Design**: Limited policy analysis

## Recommendations

### Datasets
- Synthetic data for equilibrium simulation
- OpenReview for empirical validation

### Baselines
1. Fixed-noise model (σ² constant)
2. No-endogeneity model
3. Capacity-only / precision-only variants

### Key Parameters
- σ₀² ≈ 0.3 (baseline noise)
- α ≈ 0.5 (noise growth rate)
- τ ≈ 0.25 (acceptance rate)
- Quality: Beta(2,5)

### AI Interventions
1. Δc: Submission cost reduction (AI writing)
2. ΔK: Review capacity increase (AI reviewing)
3. Δσ²: Review precision improvement

## References
1. Shah et al. - Mechanism Design for Peer Review
2. NeurIPS 2021 - Peer Review Consistency
3. Xu et al. 2018 - Strategyproof Peer Selection
4. de Clippel et al. 2019 - Incentivizing Quality
5. Liang et al. 2023 - LLMs for Review
6. Stelmakh et al. 2019 - PeerReview4All
7. Kang et al. 2018 - PeerRead Dataset

---
*Last updated: 2026-01-06*
