# policies.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import random
import math


def cyclical_distance(p_in: int, p_resident: int, num_pages: int) -> int:
    """
    Computes cyclical distance on a ring of size num_pages.
    """
    diff = abs(p_in - p_resident)
    return min(diff, num_pages - diff)


class EvictionPolicy(ABC):
    """
    Abstract base class for eviction policies.
    """

    @abstractmethod
    def select_victim(
        self,
        ram_pages: List[int],
        incoming_page: int,
        num_pages: int
    ) -> int:
        """
        Returns the frame index to evict.
        """
        raise NotImplementedError


#Policy 1 — Original Deterministic (Baseline)
class DeterministicMaxDistancePolicy(EvictionPolicy):
    """
    Evicts the page with the maximal cyclical distance.
    Ties are broken by smallest frame index.
    """

    def select_victim(self, ram_pages, incoming_page, num_pages):
        distances = [
            cyclical_distance(incoming_page, page, num_pages)
            for page in ram_pages
        ]
        max_distance = max(distances)

        for idx, dist in enumerate(distances):
            if dist == max_distance:
                return idx



#Policy 2 — Top-K Randomized
class TopKRandomPolicy(EvictionPolicy):
    """
    Randomly selects a victim among the top-K pages
    with the largest cyclical distance.
    """

    def __init__(self, k: int = 3, seed: int | None = None):
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k = k
        self._rng = random.Random(seed)

    def select_victim(self, ram_pages, incoming_page, num_pages):
        distances = [
            cyclical_distance(incoming_page, page, num_pages)
            for page in ram_pages
        ]

        indexed = list(enumerate(distances))
        indexed.sort(key=lambda x: x[1], reverse=True)

        top_k = indexed[:self.k]
        victim_idx, _ = self._rng.choice(top_k)
        return victim_idx



#Policy 3 — Probabilistic Distance-Based
class SoftmaxDistancePolicy(EvictionPolicy):
    """
    Selects a victim probabilistically using a softmax
    over cyclical distances.
    """

    def __init__(self, temperature: float = 1.0, seed: int | None = None):
        if temperature <= 0:
            raise ValueError("temperature must be > 0")
        self.temperature = temperature
        self._rng = random.Random(seed)

    def select_victim(self, ram_pages, incoming_page, num_pages):
        distances = [
            cyclical_distance(incoming_page, page, num_pages)
            for page in ram_pages
        ]

        # numerically stable softmax
        scaled = [d / self.temperature for d in distances]
        max_val = max(scaled)
        exp_scores = [math.exp(s - max_val) for s in scaled]

        total = sum(exp_scores)
        probs = [s / total for s in exp_scores]

        return self._rng.choices(range(len(ram_pages)), weights=probs, k=1)[0]



#Policy 4 — ε-Greedy Eviction
class EpsilonGreedyPolicy(EvictionPolicy):
    """
    With probability (1 - epsilon), behaves deterministically.
    With probability epsilon, evicts a random page.
    """

    def __init__(self, epsilon: float = 0.05, seed: int | None = None):
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be in [0, 1]")
        self.epsilon = epsilon
        self._rng = random.Random(seed)

    def select_victim(self, ram_pages, incoming_page, num_pages):
        if self._rng.random() < self.epsilon:
            return self._rng.randrange(len(ram_pages))

        distances = [
            cyclical_distance(incoming_page, page, num_pages)
            for page in ram_pages
        ]
        max_distance = max(distances)
        return distances.index(max_distance)


#Policy 5 — Rank-Based Randomized Eviction
class NoisePerturbedPolicy(EvictionPolicy):
    """
    Adds small hidden noise to the distance ranking.
    The noise seed is private and unknown to the attacker.
    """

    def __init__(self, noise_scale: float = 0.1, seed: int | None = None):
        if noise_scale < 0:
            raise ValueError("noise_scale must be >= 0")
        self.noise_scale = noise_scale
        self._rng = random.Random(seed)

    def select_victim(self, ram_pages, incoming_page, num_pages):
        scores = []
        for page in ram_pages:
            d = cyclical_distance(incoming_page, page, num_pages)
            noise = self._rng.uniform(-self.noise_scale, self.noise_scale)
            scores.append(d + noise)

        return scores.index(max(scores))
