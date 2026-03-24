# eviction_attack/benchmark.py

import random
import statistics

from eviction_attack.simulation import MemorySimulator
from eviction_attack.policies import (
    DeterministicMaxDistancePolicy,
    TopKRandomPolicy,
    SoftmaxDistancePolicy,
    EpsilonGreedyPolicy,
    NoisePerturbedPolicy,
)


def run_benchmark(eviction_policy, access_trace: list[int]) -> float:
    """
    Run a single benchmark for a given eviction policy
    over a fixed access trace.
    """
    simulator = MemorySimulator(
        num_frames=10,
        num_pages=100,
        eviction_policy=eviction_policy,
    )

    for page in access_trace:
        simulator.access(page)

    stats = simulator.stats()
    return stats["page_fault_rate"]


def main():
    NUM_ACCESSES = 1000
    SEEDS = [5, 6, 7, 8, 9, 10]

    # Factory for all eviction policies
    policies_factory = {
        "Deterministic": lambda seed: DeterministicMaxDistancePolicy(),
        "TopK (k=3)": lambda seed: TopKRandomPolicy(k=3, seed=seed),
        "Softmax (T=1.0)": lambda seed: SoftmaxDistancePolicy(temperature=1.0, seed=seed),
        "Epsilon-Greedy (ε=0.05)": lambda seed: EpsilonGreedyPolicy(epsilon=0.05, seed=seed),
        "Noise-Perturbed (σ=0.1)": lambda seed: NoisePerturbedPolicy(noise_scale=0.1, seed=seed),
    }

    # Store results per policy
    results: dict[str, list[float]] = {name: [] for name in policies_factory}

    print("\n=== Multi-Seed Benchmark (1000 accesses each) ===")

    for seed in SEEDS:
        random.seed(seed)
        access_trace = [random.randint(0, 99) for _ in range(NUM_ACCESSES)]

        print(f"\nSeed {seed}:")

        for name, policy_fn in policies_factory.items():
            policy = policy_fn(seed)
            rate = run_benchmark(policy, access_trace)
            results[name].append(rate)

            print(f"  {name:25s} Page Fault Rate = {rate:.3f}")

    # -----------------------
    # Summary table
    # -----------------------
    print("\n=== Summary: All Eviction Policies ===")
    print(f"{'Policy':25s} {'Mean PFR':>12s} {'Std':>10s}")

    for name, rates in results.items():
        mean = statistics.mean(rates)
        std = statistics.stdev(rates)
        print(f"{name:25s} {mean:12.4f} {std:10.4f}")


if __name__ == "__main__":
    main()