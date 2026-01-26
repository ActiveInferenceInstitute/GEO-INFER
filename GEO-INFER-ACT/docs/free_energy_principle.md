# The Free Energy Principle

## Introduction

The **Free Energy Principle (FEP)** is a theoretical framework proposing that all adaptive systems—from cells to societies—minimize variational free energy to maintain their existence and adapt to their environment.

## Historical Context

Developed by neuroscientist **Karl Friston** at University College London, the FEP emerged from efforts to understand brain function through the lens of Bayesian inference and statistical physics.

## Core Formulation

### Variational Free Energy

Free energy is defined as:

```
F = E_q[log q(s) - log p(o,s)]
     = E_q[log q(s)] - E_q[log p(o,s)]
     = -H[q(s)] + E_q[-log p(o,s)]
```

This can be rewritten as:

```
F = DKL[q(s) || p(s|o)] + (-log p(o))
```

Where:

- `DKL` - Kullback-Leibler divergence (a measure of difference between distributions)
- `q(s)` - Approximate posterior (recognition density)
- `p(s|o)` - True posterior
- `p(o)` - Model evidence (marginalized likelihood)

### Key Insight

Since `DKL ≥ 0`, free energy is an **upper bound on surprise**:

```
F ≥ -log p(o) = surprise
```

Minimizing F therefore minimizes surprise.

## Two Routes to Minimization

### 1. Perceptual Inference

Adjust beliefs `q(s)` to better explain observations:

```python
# Gradient descent on beliefs
dq/dt = -∂F/∂q
```

This is equivalent to Bayesian belief updating.

### 2. Active Inference

Select actions that change observations to match predictions:

```python
# Select action minimizing expected free energy
action = argmin_a E[F(o_future | a)]
```

## Mathematical Details

### Generative Model

The joint probability `p(o,s)` factorizes as:

```
p(o,s) = p(o|s) × p(s)
```

Where:

- `p(o|s)` - Likelihood (how states generate observations)
- `p(s)` - Prior (expected states)

### Belief Updating

Under Laplace approximation (Gaussian beliefs):

```
μ = μ + Δt × (∂F/∂μ)
```

Where `μ` is the mean of the approximate posterior.

## Connection to Other Frameworks

| Framework | Relationship |
|-----------|--------------|
| **Bayesian Inference** | FEP generalizes Bayesian updating |
| **Predictive Coding** | Perception as prediction error minimization |
| **Optimal Control** | Action selection with uncertainty |
| **Information Theory** | Free energy involves entropy and KL divergence |
| **Thermodynamics** | Analogy to free energy in physics |

## Implications

### For Neuroscience

- Brain as an inference machine
- Hierarchical predictive processing
- Unified theory of perception, action, learning

### For AI

- Principled approach to agent design
- Natural exploration-exploitation balance
- Robust to uncertainty

### For Geospatial AI

- Agents that actively seek information
- Spatial uncertainty quantification
- Adaptive environmental monitoring

## Further Reading

- [Active Inference Overview](./active_inference_overview.md)
- [Mathematical Framework](./mathematical_framework.md)

## References

Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.

---

**Last Updated**: 2026-01-26
