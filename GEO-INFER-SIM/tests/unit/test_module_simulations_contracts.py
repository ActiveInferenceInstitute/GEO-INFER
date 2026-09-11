"""Contract tests for ModuleSimulations free-energy/posterior approximations.

These pin the documented contracts in ``module_simulations.py``:
``simulate_act`` reports the surprisal (negative entropy) of the categorical
state belief as "free energy" (not the ACT expected free energy), and
``simulate_bayes`` reports a fixed 50/50 prior/sample moment blend as the
"posterior" (not the exact Normal conjugate posterior).
"""

import numpy as np
import pytest

from geo_infer_sim.module_simulations import ModuleSimulationConfig, ModuleSimulations


@pytest.fixture
def sims() -> ModuleSimulations:
    """Deterministic, short-horizon simulation harness."""
    return ModuleSimulations(ModuleSimulationConfig(time_horizon=5.0, time_step=1.0))


class TestSimulateActContract:
    """Pin the surprisal-as-free-energy contract."""

    def test_free_energy_is_negative_entropy_of_state_belief(
        self, sims: ModuleSimulations
    ) -> None:
        """Every reported free energy equals -sum(b * log(b + eps))."""
        beliefs = {
            "state_belief": np.array([0.2, 0.5, 0.3]),
            "observation_belief": np.array([0.6, 0.4]),
            "precision": 1.0,
        }
        observations = np.zeros((4, 3))

        result = sims.simulate_act(
            observations=observations,
            beliefs=beliefs,
            policies=[{"id": 0}],
        )

        assert result["module"] == "ACT"
        assert len(result["free_energy_history"]) == len(result["belief_history"])
        for fe, b in zip(result["free_energy_history"], result["belief_history"]):
            expected = -np.sum(b * np.log(b + 1e-10))
            assert fe == pytest.approx(expected)

    def test_final_free_energy_matches_final_beliefs(
        self, sims: ModuleSimulations
    ) -> None:
        """Trailing free energy is computed from the trailing belief state."""
        result = sims.simulate_act(observations=np.ones((3, 3)))
        b = np.asarray(result["final_beliefs"]["state_belief"])
        expected = -np.sum(b * np.log(b + 1e-10))
        assert result["free_energy_history"][-1] == pytest.approx(expected)


class TestSimulateBayesContract:
    """Pin the 50/50 prior/sample moment-blend contract."""

    def test_posterior_is_prior_sample_blend_not_conjugate(
        self, sims: ModuleSimulations
    ) -> None:
        """Final posterior mean/std match the documented blend formulas."""
        observations = np.array([1.0, 2.0, 3.0, 4.0])
        prior = {"mean": -2.0, "std": 1.5}

        result = sims.simulate_bayes(observations=observations, prior_params=prior)

        sample_mean = float(np.mean(observations))
        sample_std = float(np.std(observations))
        expected_mean = (prior["mean"] + sample_mean) / 2
        expected_std = float(np.sqrt((prior["std"] ** 2 + sample_std**2) / 2))

        assert result["module"] == "BAYES"
        assert result["final_posterior"]["mean"] == pytest.approx(expected_mean)
        assert result["final_posterior"]["std"] == pytest.approx(expected_std)

    def test_posterior_is_not_exact_conjugate_mean(
        self, sims: ModuleSimulations
    ) -> None:
        """Guard the honesty of the contract: the blend differs from the
        exact Normal conjugate posterior for a known prior mean."""
        observations = np.array([10.0, 11.0, 12.0])
        prior = {"mean": 0.0, "std": 1.0}

        result = sims.simulate_bayes(observations=observations, prior_params=prior)

        exact_conjugate_mean = 11.0  # known-variance Normal posterior mean
        assert result["final_posterior"]["mean"] == pytest.approx(5.5)
        assert result["final_posterior"]["mean"] != pytest.approx(exact_conjugate_mean)
