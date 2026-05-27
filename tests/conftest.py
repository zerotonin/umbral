# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — conftest                                               ║
# ║  « module »                                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝


"""Shared fixtures. A deterministic dice source for reproducible tests."""
from __future__ import annotations

import pytest


class SequenceRandom:
    """A random.Random stand-in that yields a fixed sequence from randint."""

    def __init__(self, values):
        self.values = list(values)
        self.i = 0

    def randint(self, a, b):
        v = self.values[self.i]
        self.i += 1
        return v


@pytest.fixture
def make_rng():
    return lambda values: SequenceRandom(values)
