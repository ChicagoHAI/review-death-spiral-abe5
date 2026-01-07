#!/usr/bin/env python3
import numpy as np
from scipy import stats
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os

DEFAULT_PARAMS = {"alpha_q": 2.0, "beta_q": 5.0, "sigma0_sq": 0.3, "alpha_load": 0.5, "K": 0.5, "tau": 0.25, "V": 1.0, "c": 0.15}

def quality_cdf(q, alpha_q, beta_q):
    return stats.beta.cdf(q, alpha_q, beta_q)

def quality_ppf(p, alpha_q, beta_q):
    return stats.beta.ppf(p, alpha_q, beta_q)

def sigma_squared(S, sigma0_sq, alpha_load, K):
    return sigma0_sq * (1.0 + alpha_load * max(0.0, S / K - 1.0))

def acceptance_probability(q, S, params):
    sigma_sq = sigma_squared(S, params["sigma0_sq"], params["alpha_load"], params["K"])
    sigma = np.sqrt(sigma_sq)
    q_threshold = quality_ppf(1 - params["tau"], params["alpha_q"], params["beta_q"])
    if sigma < 1e-10:
        return 1.0 if q > q_threshold else 0.0
    return 1.0 - stats.norm.cdf((q_threshold - q) / sigma)

def submission_threshold(S, params):
    target_p = params["c"] / params["V"]
    p_at_0 = acceptance_probability(0.0, S, params)
    p_at_1 = acceptance_probability(1.0, S, params)
    if p_at_0 >= target_p:
        return 0.0
    if p_at_1 <= target_p:
        return 1.0
    try:
        return brentq(lambda q: acceptance_probability(q, S, params) - target_p, 0.0, 1.0, xtol=1e-8)
    except:
        return 0.5

def equilibrium_mapping(S, params):
    q_star = submission_threshold(S, params)
    return 1.0 - quality_cdf(q_star, params["alpha_q"], params["beta_q"])

def find_equilibrium(params, S_init=0.5, max_iter=1000, tol=1e-6):
    S = S_init
    for i in range(max_iter):
        S_new = equilibrium_mapping(S, params)
        if abs(S_new - S) < tol:
            return S_new, True
        S = 0.7 * S + 0.3 * S_new
    return S, False

def find_all_equilibria(params, n_init=30, tol=1e-5):
    equilibria = []
    for S_init in np.linspace(0.02, 0.98, n_init):
        S_eq, converged = find_equilibrium(params, S_init, tol=tol)
        if converged and 0.01 < S_eq < 0.99:
            if all(abs(S_eq - e) >= 0.02 for e in equilibria):
                equilibria.append(S_eq)
    return sorted(equilibria)

def check_stability(S_eq, params, delta=0.01):
    G_plus = equilibrium_mapping(min(S_eq + delta, 0.99), params)
    G_minus = equilibrium_mapping(max(S_eq - delta, 0.01), params)
    return (G_plus - G_minus) / (2 * delta) < 1


def experiment1_multiple_equilibria():
    print("=" * 60)
    print("Experiment 1: Multiple Equilibria Detection")
    print("=" * 60)
    sigma0_range = np.linspace(0.1, 0.8, 15)
    alpha_range = np.linspace(0.1, 1.5, 15)
    results = {"sigma0_range": sigma0_range.tolist(), "alpha_range": alpha_range.tolist(), "n_equilibria": [], "equilibria_details": []}
    n_eq_matrix = np.zeros((len(alpha_range), len(sigma0_range)))
    for i, alpha in enumerate(alpha_range):
        row_details = []
        for j, sigma0 in enumerate(sigma0_range):
            params = DEFAULT_PARAMS.copy()
            params["sigma0_sq"] = sigma0
            params["alpha_load"] = alpha
            eqs = find_all_equilibria(params)
            n_eq_matrix[i, j] = len(eqs)
            row_details.append({"sigma0": sigma0, "alpha": alpha, "equilibria": eqs})
        results["equilibria_details"].append(row_details)
    results["n_equilibria"] = n_eq_matrix.tolist()
    n_single = np.sum(n_eq_matrix == 1)
    n_multi = np.sum(n_eq_matrix >= 2)
    n_none = np.sum(n_eq_matrix == 0)
    print(f"Parameter space: {len(sigma0_range)}x{len(alpha_range)} grid")
    print(f"  Single equilibrium: {n_single}")
    print(f"  Multiple equilibria: {n_multi}")
    print(f"  No equilibrium: {n_none}")
    multi_eq_example = None
    for i, alpha in enumerate(alpha_range):
        for j, sigma0 in enumerate(sigma0_range):
            if n_eq_matrix[i, j] >= 2:
                params = DEFAULT_PARAMS.copy()
                params["sigma0_sq"] = sigma0
                params["alpha_load"] = alpha
                eqs = find_all_equilibria(params)
                multi_eq_example = {"sigma0_sq": sigma0, "alpha_load": alpha, "equilibria": eqs, "stable": [check_stability(e, params) for e in eqs]}
                break
        if multi_eq_example:
            break
    if multi_eq_example:
        print(f"Multiple equilibria example: sigma0_sq={multi_eq_example[\"sigma0_sq\"]:.3f}, alpha={multi_eq_example[\"alpha_load\"]:.3f}")
        for eq, stable in zip(multi_eq_example["equilibria"], multi_eq_example["stable"]):
            print(f"  S* = {eq:.4f} ({\"stable\" if stable else \"unstable\"})")
        results["multi_eq_example"] = multi_eq_example
    plt.figure(figsize=(10, 8))
    plt.imshow(n_eq_matrix, origin="lower", aspect="auto", extent=[sigma0_range[0], sigma0_range[-1], alpha_range[0], alpha_range[-1]], cmap="RdYlBu_r")
    plt.colorbar(label="Number of Equilibria")
    plt.xlabel("Baseline Noise sigma_0^2")
    plt.ylabel("Load Sensitivity alpha")
    plt.title("Phase Diagram: Number of Equilibria")
    plt.savefig("results/phase_diagram_equilibria.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: results/phase_diagram_equilibria.png")
    return results


def experiment2_phase_transitions():
    print("\\n" + "=" * 60)
    print("Experiment 2: Phase Transitions from Cost Reduction")
    print("=" * 60)
    cost_range = np.linspace(0.3, 0.02, 50)
    results = {"cost_range": cost_range.tolist(), "equilibria_trajectory": [], "noise_at_eq": [], "threshold_at_eq": []}
    for c in cost_range:
        params = DEFAULT_PARAMS.copy()
        params["c"] = c
        eqs = find_all_equilibria(params)
        if len(eqs) == 0:
            S_eq, _ = find_equilibrium(params, 0.5)
            eqs = [S_eq]
        results["equilibria_trajectory"].append(eqs)
        S_high = max(eqs)
        sigma_sq = sigma_squared(S_high, params["sigma0_sq"], params["alpha_load"], params["K"])
        q_star = submission_threshold(S_high, params)
        results["noise_at_eq"].append(sigma_sq)
        results["threshold_at_eq"].append(q_star)
    for i, (c, eqs) in enumerate(zip(cost_range, results["equilibria_trajectory"])):
        if max(eqs) > 0.8:
            results["critical_cost"] = float(c)
            results["critical_index"] = i
            print(f"Critical cost: c = {c:.3f}, S* = {max(eqs):.3f}")
            break
    print(f"Cost range: {cost_range[0]:.2f} -> {cost_range[-1]:.2f}")
    print(f"Final equilibria: {results[\"equilibria_trajectory\"][-1]}")
    print(f"Final noise: sigma^2 = {results[\"noise_at_eq\"][-1]:.3f}")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    ax1 = axes[0]
    for i, eqs in enumerate(results["equilibria_trajectory"]):
        for eq in eqs:
            ax1.scatter(cost_range[i], eq, c="blue", s=10, alpha=0.6)
    ax1.set_xlabel("Submission Cost c")
    ax1.set_ylabel("Equilibrium S*")
    ax1.set_title("Equilibrium vs Cost")
    ax1.invert_xaxis()
    ax1.axhline(y=DEFAULT_PARAMS["K"], color="red", linestyle="--", label=f"K={DEFAULT_PARAMS[\"K\"]}")
    ax1.legend()
    ax2 = axes[1]
    ax2.plot(cost_range, results["noise_at_eq"], "r-", linewidth=2)
    ax2.axhline(y=DEFAULT_PARAMS["sigma0_sq"], color="gray", linestyle="--")
    ax2.set_xlabel("Submission Cost c")
    ax2.set_ylabel("Review Noise sigma^2")
    ax2.set_title("Noise at Equilibrium")
    ax2.invert_xaxis()
    ax3 = axes[2]
    ax3.plot(cost_range, results["threshold_at_eq"], "g-", linewidth=2)
    ax3.set_xlabel("Submission Cost c")
    ax3.set_ylabel("Quality Threshold q*")
    ax3.set_title("Threshold at Equilibrium")
    ax3.invert_xaxis()
    plt.tight_layout()
    plt.savefig("results/phase_transition_cost.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: results/phase_transition_cost.png")
    return results


def experiment3_ai_interventions():
    print("\\n" + "=" * 60)
    print("Experiment 3: AI Intervention Comparative Statics")
    print("=" * 60)
    interventions = {
        "baseline": {},
        "cost_-25%": {"c": DEFAULT_PARAMS["c"] * 0.75},
        "cost_-50%": {"c": DEFAULT_PARAMS["c"] * 0.50},
        "capacity_+50%": {"K": DEFAULT_PARAMS["K"] * 1.5},
        "capacity_+100%": {"K": DEFAULT_PARAMS["K"] * 2.0},
        "precision_+25%": {"sigma0_sq": DEFAULT_PARAMS["sigma0_sq"] * 0.75},
        "precision_+50%": {"sigma0_sq": DEFAULT_PARAMS["sigma0_sq"] * 0.50},
        "combined_moderate": {"c": DEFAULT_PARAMS["c"] * 0.75, "K": DEFAULT_PARAMS["K"] * 1.5, "sigma0_sq": DEFAULT_PARAMS["sigma0_sq"] * 0.75},
        "combined_aggressive": {"c": DEFAULT_PARAMS["c"] * 0.50, "K": DEFAULT_PARAMS["K"] * 2.0, "sigma0_sq": DEFAULT_PARAMS["sigma0_sq"] * 0.50}
    }
    results = {"interventions": {}}
    for name, changes in interventions.items():
        params = DEFAULT_PARAMS.copy()
        params.update(changes)
        eqs = find_all_equilibria(params)
        if len(eqs) == 0:
            S_eq, _ = find_equilibrium(params, 0.5)
            eqs = [S_eq]
        S_high = max(eqs)
        sigma_sq = sigma_squared(S_high, params["sigma0_sq"], params["alpha_load"], params["K"])
        q_star = submission_threshold(S_high, params)
        result = {"equilibria": eqs, "S_high": S_high, "sigma_sq": sigma_sq, "q_star": q_star, "overload": S_high > params["K"], "n_equilibria": len(eqs)}
        results["interventions"][name] = result
        status = "OVERLOAD" if result["overload"] else "OK"
        print(f"{name:25s}: S*={S_high:.3f}, sigma^2={sigma_sq:.3f}, q*={q_star:.3f} [{status}]")
    names = list(interventions.keys())
    S_values = [results["interventions"][n]["S_high"] for n in names]
    sigma_values = [results["interventions"][n]["sigma_sq"] for n in names]
    q_values = [results["interventions"][n]["q_star"] for n in names]
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    colors = ["gray" if not results["interventions"][n]["overload"] else "red" for n in names]
    ax1 = axes[0]
    ax1.barh(names, S_values, color=colors, alpha=0.7)
    ax1.axvline(x=DEFAULT_PARAMS["K"], color="red", linestyle="--", label="Capacity K")
    ax1.set_xlabel("Equilibrium S*")
    ax1.set_title("Submission Volume")
    ax1.legend()
    ax2 = axes[1]
    ax2.barh(names, sigma_values, color="orange", alpha=0.7)
    ax2.axvline(x=DEFAULT_PARAMS["sigma0_sq"], color="gray", linestyle="--")
    ax2.set_xlabel("Review Noise sigma^2")
    ax2.set_title("Review Noise")
    ax3 = axes[2]
    ax3.barh(names, q_values, color="green", alpha=0.7)
    ax3.set_xlabel("Quality Threshold q*")
    ax3.set_title("Submission Threshold")
    plt.tight_layout()
    plt.savefig("results/ai_interventions_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: results/ai_interventions_comparison.png")
    return results


def experiment4_capacity_precision_heatmap():
    print("\\n" + "=" * 60)
    print("Experiment 4: Capacity-Precision Heatmap")
    print("=" * 60)
    K_range = np.linspace(0.3, 1.5, 20)
    sigma_range = np.linspace(0.1, 0.6, 20)
    S_matrix = np.zeros((len(sigma_range), len(K_range)))
    noise_matrix = np.zeros((len(sigma_range), len(K_range)))
    overload_matrix = np.zeros((len(sigma_range), len(K_range)))
    for i, sigma0 in enumerate(sigma_range):
        for j, K in enumerate(K_range):
            params = DEFAULT_PARAMS.copy()
            params["sigma0_sq"] = sigma0
            params["K"] = K
            params["c"] = 0.08
            eqs = find_all_equilibria(params)
            if len(eqs) == 0:
                S_eq, _ = find_equilibrium(params, 0.5)
                eqs = [S_eq]
            S_high = max(eqs)
            S_matrix[i, j] = S_high
            noise_matrix[i, j] = sigma_squared(S_high, params["sigma0_sq"], params["alpha_load"], params["K"])
            overload_matrix[i, j] = 1 if S_high > K else 0
    print(f"Overloaded: {int(np.sum(overload_matrix))} / {len(K_range)*len(sigma_range)}")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    ax1 = axes[0]
    im1 = ax1.imshow(S_matrix, origin="lower", aspect="auto", extent=[K_range[0], K_range[-1], sigma_range[0], sigma_range[-1]], cmap="viridis")
    plt.colorbar(im1, ax=ax1, label="S*")
    ax1.set_xlabel("Capacity K")
    ax1.set_ylabel("Baseline Noise sigma_0^2")
    ax1.set_title("Equilibrium Volume")
    ax2 = axes[1]
    im2 = ax2.imshow(noise_matrix, origin="lower", aspect="auto", extent=[K_range[0], K_range[-1], sigma_range[0], sigma_range[-1]], cmap="Reds")
    plt.colorbar(im2, ax=ax2, label="sigma^2(S*)")
    ax2.set_xlabel("Capacity K")
    ax2.set_ylabel("Baseline Noise sigma_0^2")
    ax2.set_title("Realized Noise")
    ax3 = axes[2]
    im3 = ax3.imshow(overload_matrix, origin="lower", aspect="auto", extent=[K_range[0], K_range[-1], sigma_range[0], sigma_range[-1]], cmap="RdYlGn_r")
    plt.colorbar(im3, ax=ax3, label="Overload")
    ax3.set_xlabel("Capacity K")
    ax3.set_ylabel("Baseline Noise sigma_0^2")
    ax3.set_title("Overload Status")
    plt.tight_layout()
    plt.savefig("results/capacity_precision_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: results/capacity_precision_heatmap.png")
    return {"K_range": K_range.tolist(), "sigma_range": sigma_range.tolist(), "S_matrix": S_matrix.tolist(), "overload_fraction": float(np.mean(overload_matrix))}


def main():
    print("=" * 60)
    print("PEER REVIEW EQUILIBRIUM SIMULATION")
    print("=" * 60)
    print(f"Parameters: {DEFAULT_PARAMS}")
    os.makedirs("results", exist_ok=True)
    all_results = {}
    all_results["experiment1"] = experiment1_multiple_equilibria()
    all_results["experiment2"] = experiment2_phase_transitions()
    all_results["experiment3"] = experiment3_ai_interventions()
    all_results["experiment4"] = experiment4_capacity_precision_heatmap()
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        return obj
    with open("results/results.json", "w") as f:
        json.dump(convert(all_results), f, indent=2)
    print("\\n" + "=" * 60)
    print("ALL EXPERIMENTS COMPLETED")
    print("=" * 60)
    print("Output: results/results.json, results/*.png")
    return all_results

if __name__ == "__main__":
    main()

