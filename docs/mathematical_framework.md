"""
## Geocaching and Spatial Foraging Extension

Based on the paper "Synthetic Spatial Foraging With Active Inference in a Geocaching Task" (https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.809296/full), we extend the framework to include spatial navigation and foraging behaviors.

### Generative Model for Navigation

The generative model for position (global navigation) is defined as:

$$ p(o_t, \tilde{s}_t, \tilde{\pi}_t) = p(s_1) \prod_{t=1}^{T} p(\pi_t | s_t) p(o_t | s_t) p(s_{t+1} | s_t, \pi_t) $$

Where:
- $o_t$: Observation at time t (distance to target)
- $s_t$: Hidden state (position)
- $\pi_t$: Policy (direction of movement)

For local foraging, a separate model handles object detection within a visual field.

### Message Passing Inference

Belief updating uses variational message passing:

Posterior over states: $ q(s_t) \propto \exp(\mu_{s_t \rightarrow q(s_t)}) $

With messages computed from likelihood, transitions, and priors.

### Expected Free Energy for Geocaching

EFE includes terms for global navigation (distance minimization) and local foraging (object collection), balancing exploration and exploitation in spatial contexts.

## References (Updated)
4. Rao, D., et al. (2022). Synthetic Spatial Foraging With Active Inference in a Geocaching Task. Frontiers in Psychology.
""" 