#eviction_attack/test_simulation.py
"""
Tests for MemorySimulator
Part 1.1 – System Modeling Validation (with debug prints)
"""

from eviction_attack.simulation import MemorySimulator
from eviction_attack.policies import DeterministicMaxDistancePolicy


def test_hit():
    print("\n=== test_hit ===")
    sim = MemorySimulator(num_frames=4, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    print("Accessing page 10 (expect MISS)")
    sim.access(10)

    print("Accessing page 10 again (expect HIT)")
    response = sim.access(10)

    print("Response:", response)
    print("RAM:", sim.dump_state())

    assert response["result"] == "HIT"
    assert response["evicted"] is None
    assert response["frame_index"] == 0


def test_miss_with_free_frame():
    print("\n=== test_miss_with_free_frame ===")
    sim = MemorySimulator(num_frames=4, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    print("Initial RAM:", sim.dump_state())
    response = sim.access(42)

    print("Accessing page 42")
    print("Response:", response)
    print("RAM after access:", sim.dump_state())

    assert response["result"] == "MISS_NO_EVICTION"
    assert response["evicted"] is None
    assert response["ram_state"][0] == 42


def test_ram_fills_in_order():
    print("\n=== test_ram_fills_in_order ===")
    sim = MemorySimulator(num_frames=3, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    for p in [1, 2, 3]:
        print(f"Accessing page {p}")
        sim.access(p)
        print("RAM:", sim.dump_state())

    assert sim.dump_state() == [1, 2, 3]


def test_eviction_occurs_when_ram_full():
    print("\n=== test_eviction_occurs_when_ram_full ===")
    sim = MemorySimulator(num_frames=3, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    for p in [10, 20, 30]:
        sim.access(p)

    print("RAM before eviction:", sim.dump_state())
    response = sim.access(90)

    print("Accessing page 90 (RAM full)")
    print("Response:", response)
    print("RAM after eviction:", sim.dump_state())

    assert response["result"] == "MISS_EVICTION"
    assert response["evicted"] in [10, 20, 30]
    assert 90 in sim.dump_state()


def test_cyclical_distance_logic():
    print("\n=== test_cyclical_distance_logic ===")
    sim = MemorySimulator(num_frames=3, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    for p in [10, 20, 30]:
        sim.access(p)

    print("Initial RAM:", sim.dump_state())
    print("Accessing page 90")

    response = sim.access(90)

    print("Response:", response)
    print("Expected eviction: page 30 (max cyclical distance)")
    print("RAM after eviction:", sim.dump_state())

    assert response["evicted"] == 30
    assert response["frame_index"] == 2


def test_tie_breaking_by_frame_index():
    print("\n=== test_tie_breaking_by_frame_index ===")
    sim = MemorySimulator(num_frames=2, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    sim.access(10)
    sim.access(90)

    print("Initial RAM:", sim.dump_state())
    print("Accessing page 50 (equal distance to both)")

    response = sim.access(50)

    print("Response:", response)
    print("Expected eviction: page 10 (smallest frame index)")
    print("RAM after eviction:", sim.dump_state())

    assert response["evicted"] == 10
    assert response["frame_index"] == 0


def test_determinism():
    print("\n=== test_determinism ===")
    sim1 = MemorySimulator(num_frames=3, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)
    sim2 = MemorySimulator(num_frames=3, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    sequence = [5, 15, 25, 85]
    print("Access sequence:", sequence)

    for p in sequence:
        r1 = sim1.access(p)
        r2 = sim2.access(p)

        print(f"\nAccessing page {p}")
        print("Sim1 RAM:", r1["ram_state"])
        print("Sim2 RAM:", r2["ram_state"])
        print("Evicted Sim1:", r1["evicted"], "| Evicted Sim2:", r2["evicted"])

        assert r1["ram_state"] == r2["ram_state"]
        assert r1["evicted"] == r2["evicted"]


def test_stats_tracking():
    print("\n=== test_stats_tracking ===")
    sim = MemorySimulator(num_frames=2, num_pages=100,eviction_policy=DeterministicMaxDistancePolicy(),)

    sim.access(1)   # miss
    sim.access(1)   # hit
    sim.access(2)   # miss
    sim.access(3)   # miss + eviction

    stats = sim.stats()

    print("Final RAM:", sim.dump_state())
    print("Stats:", stats)

    assert stats["hits"] == 1
    assert stats["misses"] == 3
