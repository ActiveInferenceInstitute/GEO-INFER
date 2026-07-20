# Categorical inference contract

The standard single-state categorical APIs use a predict-then-update filter:

1. Predict the next state with `B @ beliefs`, where `B` is column-stochastic and
   `B[next_state, current_state] = P(next_state | current_state)`.
2. Update that prior with the observation model `A`, where
   `A[observation, state] = P(observation | state)`.

Categorical likelihoods are evaluated in log space. Observation vectors may be
non-negative hard counts or soft counts, including totals large enough that a
linear-space likelihood product would underflow. Every successful update returns
finite, non-negative beliefs that sum to one. Invalid shapes, negative values,
zero-mass priors, and observations with no posterior support raise `ValueError`.

`GenerativeModel` uses one `B` matrix for a single-level model. A hierarchical
`GenerativeModel` accepts a mapping such as
`{"level_0": B0, "level_1": B1}`; a single matrix may be broadcast only when
all levels have the same state dimension. If no `B` is supplied, the categorical
default is the identity transition, preserving state continuity.

The categorical model retains its row-stochastic matrix orientation:
`transition_matrix[current_state, next_state]`.
It applies `transition_matrix.T @ beliefs` before each observation update.
`BayesianBeliefUpdate.update_categorical` shares the same stable log-space
normalization helper but remains a pure Bayes update over the prior supplied by
the caller.

## Validation

Run the focused regression suite from the repository root:

```bash
PYTHONPATH=GEO-INFER-ACT/src uv run pytest \
  GEO-INFER-ACT/tests/unit/test_categorical_regressions.py -q
```

Then run the ACT unit suite and the repository contract checks:

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
```
