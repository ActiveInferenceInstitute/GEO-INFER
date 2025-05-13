# GEO-INFER-ACT Mathematical Framework

## Overview

This document describes the mathematical foundations of active inference as implemented in the GEO-INFER-ACT module. Active inference is a framework that unifies perception, learning, and decision-making under a single theoretical construct based on free energy minimization.

## Free Energy Principle

The free energy principle posits that all adaptive systems (biological or artificial) resist a natural tendency to disorder by minimizing their variational free energy. In information-theoretic terms, this is equivalent to maximizing the evidence for their model of the world.

The variational free energy is defined as:

$F = \mathbb{E}_{q(s)} \left[ \ln q(s) - \ln p(s, o) \right]$

Where:
- $q(s)$ is the approximate posterior distribution over hidden states
- $p(s, o)$ is the generative model of states $s$ and observations $o$

This can be decomposed into:

$F = \underbrace{D_{KL}[q(s) \parallel p(s|o)]}_{\text{Divergence}} - \underbrace{\ln p(o)}_{\text{Evidence}}$

## Belief Updating

In active inference, perception corresponds to updating beliefs about hidden states based on observations. This happens by minimizing free energy with respect to the approximate posterior $q(s)$.

For categorical distributions, belief updating follows Bayes' rule:

$q(s) \propto p(o|s) \cdot p(s)$

For Gaussian distributions, belief updating follows the Kalman filter equations:

$\mu_t = \mu_{t-1} + K_t(o_t - g(\mu_{t-1}))$

$\Sigma_t = (I - K_t \nabla g)\Sigma_{t-1}$

Where $K_t$ is the Kalman gain and $g(\cdot)$ is the observation mapping function.

## Expected Free Energy

For policy selection, active inference uses the expected free energy, defined as:

$G(\pi) = \sum_{\tau} G(\pi, \tau)$

$G(\pi, \tau) = \underbrace{\mathbb{E}_{q(o_\tau, s_\tau|\pi)} \left[ \ln q(s_\tau|\pi) - \ln p(s_\tau|o_\tau, \pi) \right]}_{\text{Information gain}} + \underbrace{\mathbb{E}_{q(o_\tau|\pi)} \left[ \ln q(o_\tau|\pi) - \ln p(o_\tau) \right]}_{\text{Preference divergence}}$

The first term represents the expected information gain or reduction in uncertainty about hidden states. The second term represents the divergence between predicted and preferred observations.

## Policy Selection

Policies (action sequences) are selected according to a softmax function of their expected free energy:

$p(\pi) = \sigma(-\gamma \cdot G(\pi))$

Where $\gamma$ is the precision parameter that governs the randomness of policy selection.

## Mathematical Components in GEO-INFER-ACT

### Generative Models

The GEO-INFER-ACT module implements generative models as:

1. **Categorical models**: Discrete state and observation spaces represented as categorical probability distributions.
2. **Gaussian models**: Continuous state and observation spaces represented as multivariate Gaussian distributions.

### Variational Inference

For categorical models, the module implements exact Bayesian inference. For Gaussian models, it implements variational Laplace (Gaussian approximation) methods.

### Markov Decision Processes

The dynamics of the environment are modeled as Markov Decision Processes (MDPs), where:

- $p(s_{t+1}|s_t, a_t)$ represents state transitions
- $p(o_t|s_t)$ represents the observation model
- $p(s_0)$ represents prior beliefs about initial states

### Dynamic Causal Models

For continuous-time dynamics, Dynamic Causal Models are used, described by stochastic differential equations:

$\dot{x} = f(x, v, \theta) + w$

$y = g(x, v, \theta) + z$

Where $x$ are hidden states, $v$ are inputs, $\theta$ are parameters, and $w, z$ are random fluctuations.

## Applications

The mathematical framework of active inference is applied in the GEO-INFER-ACT module to model various ecological and civic systems:

1. **Ecological niche modeling**: Modeling how species adapt to and modify their environments
2. **Urban planning**: Multi-agent active inference for urban development
3. **Climate adaptation**: Policy optimization under uncertainty
4. **Resource allocation**: Balancing exploration and exploitation

## References

1. Friston, K. (2010). The free-energy principle: a unified brain theory? Nature Reviews Neuroscience, 11(2), 127-138.
2. Friston, K., et al. (2017). Active inference: a process theory. Neural Computation, 29(1), 1-49.
3. Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. Biological Cybernetics, 113(5), 495-513. 