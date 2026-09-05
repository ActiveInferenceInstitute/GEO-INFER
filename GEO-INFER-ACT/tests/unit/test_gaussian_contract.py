"""Analytic Gaussian identities and rejection tests for continuous inference."""

import numpy as np
import pytest
from geo_infer_act.models.continuous_pomdp import ContinuousPOMDPActiveInference


def test_exact_posterior_free_energy_equals_negative_log_evidence():
    model = ContinuousPOMDPActiveInference(
        state_dim=1,
        obs_dim=1,
        action_dim=1,
        dt=0.5,
        prior_mean=np.array([1.0]),
        prior_cov=np.array([[2.0]]),
        process_noise_cov=np.array([[0.4]]),
        obs_noise_cov=np.array([[0.3]]),
    )
    mean, covariance = model.predict(np.array([0.2]))
    y = np.array([2.0])
    innovation_var = covariance[0, 0] + 0.3
    expected = 0.5 * (
        np.log(2 * np.pi * innovation_var) + (y[0] - mean[0]) ** 2 / innovation_var
    )
    _, _, evidence = model.update_beliefs(y, np.array([0.2]))
    result = model.compute_variational_free_energy()
    assert evidence == pytest.approx(expected)
    assert result.free_energy == pytest.approx(expected)
    assert result.free_energy == pytest.approx(result.complexity - result.accuracy)
    assert result.complexity >= 0
    assert result.entropy == pytest.approx(
        0.5 * np.log(2 * np.pi * np.e * model.sigma[0, 0])
    )


def test_rectangular_measurement_and_atomic_rejection():
    model = ContinuousPOMDPActiveInference(state_dim=3, obs_dim=2, action_dim=1)
    assert np.isfinite(model.compute_variational_free_energy().free_energy)
    previous = model.mu.copy()
    with pytest.raises(ValueError):
        model.update_beliefs(np.array([np.nan, 1.0]))
    np.testing.assert_array_equal(model.mu, previous)
    assert not model.history
    with pytest.raises(ValueError):
        model.set_system_matrices(A=np.eye(3), C=np.ones((3, 3)))
    np.testing.assert_array_equal(model.A, -0.1 * np.eye(3))


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(dt=0),
        dict(dt=np.nan),
        dict(state_dim=True),
        dict(obs_noise_cov=np.zeros((2, 2))),
        dict(prior_cov=np.array([[1.0, 2.0], [2.0, 1.0]])),
        dict(process_noise_cov=np.array([[1.0, 2.0], [0.0, 1.0]])),
    ],
)
def test_invalid_model_rejected(kwargs):
    with pytest.raises(ValueError):
        ContinuousPOMDPActiveInference(**kwargs)


def test_discrete_transition_is_not_euler_discretized_again():
    model = ContinuousPOMDPActiveInference(
        state_dim=1,
        obs_dim=1,
        action_dim=1,
        dt=2.0,
        time_domain="discrete",
        prior_mean=np.array([3.0]),
        process_noise_cov=np.array([[0.5]]),
    )
    model.set_system_matrices(A=np.array([[0.8]]), B=np.array([[2.0]]))
    mean, covariance = model.predict(np.array([1.0]))
    np.testing.assert_allclose(mean, [4.4])
    np.testing.assert_allclose(covariance, [[1.14]])


def test_information_gain_decreases_with_noise_at_fixed_state_uncertainty():
    def information(noise):
        model = ContinuousPOMDPActiveInference(obs_noise_cov=np.eye(2) * noise)
        return model.compute_expected_free_energy(
            np.zeros(2), return_breakdown=True
        ).epistemic_value

    assert information(0.01) > information(1.0) > information(100.0) >= 0


@pytest.mark.parametrize(
    "kwargs", [dict(horizon=0), dict(horizon=1.5), dict(epistemic_weight=np.nan)]
)
def test_invalid_policy_arguments(kwargs):
    with pytest.raises(ValueError):
        ContinuousPOMDPActiveInference().compute_expected_free_energy(
            np.zeros(2), **kwargs
        )


def test_candidate_actions_are_never_resized():
    model = ContinuousPOMDPActiveInference()
    with pytest.raises(ValueError):
        model.evaluate_actions(candidate_actions=[np.ones(1)])
    with pytest.raises(ValueError):
        model.evaluate_actions(candidate_actions=[])


def test_conditional_information_does_not_double_count_measurements():
    model = ContinuousPOMDPActiveInference(
        state_dim=1,
        obs_dim=1,
        action_dim=1,
        time_domain="discrete",
        process_noise_cov=np.zeros((1, 1)),
        obs_noise_cov=np.ones((1, 1)),
    )
    result = model.compute_expected_free_energy(
        np.zeros(1), horizon=3, return_breakdown=True
    )
    assert result.epistemic_value == pytest.approx(0.5 * np.log(4))
    assert result.pragmatic_value == pytest.approx(6)
