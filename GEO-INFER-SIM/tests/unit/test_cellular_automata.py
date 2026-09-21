"""Unit tests for the CellularAutomata paradigm (M8-01).

Covers neighbor topology, the default Game-of-Life rule (blinker
oscillation), custom rules, shape validation and seeded determinism.
"""

import numpy as np
import pytest

from geo_infer_sim.paradigms.cellular_automata import CellularAutomata


class TestNeighborTopology:
    """get_neighbors returns in-grid coordinates only."""

    @pytest.fixture
    def automaton(self) -> CellularAutomata:
        grid = np.zeros((3, 3), dtype=int)
        return CellularAutomata((3, 3), initial_states=grid)

    def test_moore_interior_has_eight_neighbors(self, automaton) -> None:
        neighbors = automaton.get_neighbors(1, 1, "moore")
        assert sorted(neighbors) == [
            (0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2),
        ]

    def test_moore_corner_has_three_neighbors(self, automaton) -> None:
        assert sorted(automaton.get_neighbors(0, 0, "moore")) == [
            (0, 1), (1, 0), (1, 1)
        ]

    def test_von_neumann_excludes_diagonals(self, automaton) -> None:
        assert sorted(automaton.get_neighbors(1, 1, "von_neumann")) == [
            (0, 1), (1, 0), (1, 2), (2, 1)
        ]
        assert sorted(automaton.get_neighbors(0, 0, "von_neumann")) == [(0, 1), (1, 0)]

    def test_unknown_neighborhood_raises(self, automaton) -> None:
        with pytest.raises(ValueError, match="Unknown neighborhood"):
            automaton.get_neighbors(1, 1, "hexagonal")


class TestGridInitialization:
    """Initial states are copied; mismatched shapes are rejected."""

    def test_initial_states_are_copied(self) -> None:
        grid = np.zeros((2, 2), dtype=int)
        automaton = CellularAutomata((2, 2), initial_states=grid)
        grid[0, 0] = 7  # mutating the donor must not leak into the model
        assert automaton.grid[0, 0] == 0

    def test_shape_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="does not match grid shape"):
            CellularAutomata((3, 3), initial_states=np.zeros((2, 2), dtype=int))


class TestDefaultGameOfLifeRule:
    """step() without a rule applies Game of Life."""

    def test_blinker_oscillates(self) -> None:
        vertical_blinker = np.array(
            [[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=int
        )
        automaton = CellularAutomata((3, 3), initial_states=vertical_blinker)

        automaton.step()
        assert automaton.grid.tolist() == [[0, 0, 0], [1, 1, 1], [0, 0, 0]]
        assert automaton.time == 1.0

        automaton.step()
        assert automaton.grid.tolist() == vertical_blinker.tolist()
        assert automaton.time == 2.0

    def test_history_snapshots_every_ten_steps(self) -> None:
        automaton = CellularAutomata((3, 3), initial_states=np.zeros((3, 3), dtype=int))
        for _ in range(9):
            automaton.step()
        assert automaton.history == []
        automaton.step()  # 10th step
        assert len(automaton.history) == 1
        assert np.array_equal(automaton.history[0], automaton.grid)


class TestCustomRules:
    """apply_rule drives arbitrary transition rules."""

    def test_spread_rule_infects_neighbors(self) -> None:
        grid = np.zeros((3, 3), dtype=int)
        grid[1, 1] = 1  # single infected cell at the center
        automaton = CellularAutomata((3, 3), initial_states=grid)

        automaton.apply_rule(
            lambda current, neighbors: 1 if any(n == 1 for n in neighbors) else current
        )
        assert automaton.grid.sum() == 9  # everything is infected

    def test_rule_is_simultaneous_not_sequential(self) -> None:
        """All cells read the pre-step grid (center alive, rest copy center's
        old state only through their own neighbor views)."""
        grid = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=int)
        automaton = CellularAutomata((3, 3), initial_states=grid)

        # Majority rule: a cell adopts the most common neighbor state.
        automaton.apply_rule(
            lambda current, neighbors:
                1 if sum(n == 1 for n in neighbors) > len(neighbors) / 2 else current
        )
        # Every non-center cell sees exactly one alive neighbor → stays 0.
        assert automaton.grid.tolist() == grid.tolist()


class TestSeededDeterminism:
    """Random initialization is reproducible from the isolated Generator."""

    def test_same_seed_produces_identical_evolution(self) -> None:
        first = CellularAutomata((5, 5), random_seed=42)
        second = CellularAutomata((5, 5), random_seed=42)
        assert np.array_equal(first.grid, second.grid)

        for _ in range(6):
            first.step()
            second.step()
        assert np.array_equal(first.grid, second.grid)
        assert first.time == second.time == 6.0

    def test_different_seeds_diverge(self) -> None:
        first = CellularAutomata((5, 5), random_seed=42)
        second = CellularAutomata((5, 5), random_seed=7)
        assert not np.array_equal(first.grid, second.grid)

    def test_get_state_reports_state_counts(self) -> None:
        grid = np.array([[0, 1], [1, 1]], dtype=int)
        automaton = CellularAutomata((2, 2), initial_states=grid)
        state = automaton.get_state()

        assert state["time"] == 0.0
        assert state["grid_shape"] == (2, 2)
        assert state["num_states"] == 2
        assert state["state_counts"] == {0: 1, 1: 3}
