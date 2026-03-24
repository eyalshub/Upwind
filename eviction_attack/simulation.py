# Simulation of the Upwind scheme
from typing import List, Optional, Dict
from eviction_attack.policies import EvictionPolicy


class MemorySimulator:
    """
    Simulates a Direct-Mapped physical memory system.
    Eviction decisions are delegated to an EvictionPolicy.
    """

    def __init__(
        self,
        num_frames: int,
        num_pages: int,
        eviction_policy: EvictionPolicy,
    ):
        self.num_frames = num_frames
        self.num_pages = num_pages
        self.frames: List[Optional[int]] = [None] * num_frames

        self.hits = 0
        self.misses = 0

        self.eviction_policy = eviction_policy

    def access(self, page_id: int) -> Dict:
        """
        Simulate access to a virtual page.
        """
        # --- HIT ---
        if page_id in self.frames:
            self.hits += 1
            frame_index = self.frames.index(page_id)
            return {
                "result": "HIT",
                "page": page_id,
                "frame_index": frame_index,
                "evicted": None,
                "ram_state": self.dump_state(),
            }

        # --- MISS ---
        self.misses += 1

        # Free frame available
        if None in self.frames:
            frame_index = self.frames.index(None)
            self.frames[frame_index] = page_id
            return {
                "result": "MISS_NO_EVICTION",
                "page": page_id,
                "frame_index": frame_index,
                "evicted": None,
                "ram_state": self.dump_state(),
            }

        # --- MISS WITH EVICTION ---
        victim_index = self.eviction_policy.select_victim(
            ram_pages=self.frames,
            incoming_page=page_id,
            num_pages=self.num_pages,
        )

        evicted_page = self.frames[victim_index]
        self.frames[victim_index] = page_id

        return {
            "result": "MISS_EVICTION",
            "page": page_id,
            "frame_index": victim_index,
            "evicted": evicted_page,
            "ram_state": self.dump_state(),
        }

    def dump_state(self) -> List[Optional[int]]:
        """
        Return a copy of the current RAM state.
        """
        return self.frames.copy()

    def stats(self) -> Dict:
        """
        Return hit/miss statistics.
        """
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_accesses": self.hits + self.misses,
            "page_fault_rate": (
                self.misses / (self.hits + self.misses)
                if (self.hits + self.misses) > 0 else 0.0
            ),
        }
