# eviction_attack/attack_demo.py
from eviction_attack.simulation import MemorySimulator
from eviction_attack.policies import (
    DeterministicMaxDistancePolicy,
    TopKRandomPolicy,
)


def generate_attack_page_analytical(target_page: int, num_pages: int) -> int:
    """
    Analytical attack:
    Select the page opposite to the target on the virtual address ring.
    """
    return (target_page + num_pages // 2) % num_pages


def setup_victim_system(
    num_frames: int,
    num_pages: int,
    target_page: int,
    eviction_policy,
) -> MemorySimulator:
    """
    Initialize a simulator with RAM fully occupied and the target page resident.
    """
    simulator = MemorySimulator(
        num_frames=num_frames,
        num_pages=num_pages,
        eviction_policy=eviction_policy,
    )

    initial_pages = [45, 46, 47, 48, 49, 50, 51, 52, 53, 54]
    assert target_page in initial_pages

    for page in initial_pages:
        simulator.access(page)

    return simulator


def run_single_attack(simulator: MemorySimulator, attack_page: int) -> int | None:
    """
    Execute a single attack attempt and return the evicted page (if any).
    """
    response = simulator.access(attack_page)
    return response["evicted"]


def run_attack_experiment(
    eviction_policy,
    policy_name: str,
    num_runs: int = 50,
):
    """
    Run repeated attacks and measure success rate.
    """
    NUM_FRAMES = 10
    NUM_PAGES = 100
    TARGET_PAGE = 50

    success_count = 0

    for _ in range(num_runs):
        simulator = setup_victim_system(
            num_frames=NUM_FRAMES,
            num_pages=NUM_PAGES,
            target_page=TARGET_PAGE,
            eviction_policy=eviction_policy,
        )

        attack_page = generate_attack_page_analytical(TARGET_PAGE, NUM_PAGES)
        evicted = run_single_attack(simulator, attack_page)

        if evicted == TARGET_PAGE:
            success_count += 1

    print("\n======================================")
    print(f"Eviction Policy: {policy_name}")
    print(f"Attack success rate: {success_count}/{num_runs}")
    print("======================================")


def run_demo():
    """
    Demonstrate attack on vulnerable and patched systems.
    """
    print("\n=== Part 1.2 – Vulnerable System (Deterministic) ===")
    run_attack_experiment(
        eviction_policy=DeterministicMaxDistancePolicy(),
        policy_name="DeterministicMaxDistance",
    )

    print("\n=== Part 1.3 – Patched System (Top-K Randomized) ===")
    run_attack_experiment(
        eviction_policy=TopKRandomPolicy(k=3, seed=42),
        policy_name="TopKRandom (k=3)",
    )


if __name__ == "__main__":
    run_demo()
