# Free Energy Principle in GEO-INFER-ACT

## Core Principle

The free energy principle states that any self-organizing system resists dispersion by minimizing the variational free energy of its internal states relative to its sensory inputs.

### Mathematical Formulation

Variational Free Energy:

\[ F(q) = \int q(\mathbf{s}) \ln \frac{q(\mathbf{s})}{p(\mathbf{s}, \mathbf{o})} d\mathbf{s} \]

Decomposed as:

\[ F = \text{Energy} - \text{Entropy} = D_{KL}[q(\mathbf{s}) || p(\mathbf{s}|\mathbf{o})] - \ln p(\mathbf{o}) \]

Where:
- \( D_{KL} \) is the Kullback-Leibler divergence (complexity term).
- \( -\ln p(\mathbf{o}) \) is the negative log evidence (inaccuracy term).

### Free Energy Decomposition Visualization

```mermaid
graph LR
    A[Variational Free Energy F] --> B[Complexity<br>D_KL[q||p]]
    A --> C[Inaccuracy<br>-ln p(o)]
    B --> D[Minimizes divergence<br>from true posterior]
    C --> E[Maximizes model evidence]
```

This diagram illustrates how free energy bounds surprise, with complexity penalizing deviations from priors and inaccuracy encouraging accurate predictions.

## Extensions to Geospatial Domains

In geospatial contexts, we extend the principle to include spatial and temporal dimensions:

### Spatial Free Energy

\[ F_{spatial} = \int q(\mathbf{s}(\mathbf{r})) \ln \frac{q(\mathbf{s}(\mathbf{r}))}{p(\mathbf{s}(\mathbf{r}), \mathbf{o}(\mathbf{r}))} d\mathbf{r} \]

Where \( \mathbf{r} \) is the spatial coordinate.

### Temporal Hierarchies

For multi-scale temporal dynamics:

\[ F = \sum_{k=1}^K F^{(k)} + \sum_{k=1}^{K-1} D_{KL}[q^{(k)}(\mathbf{s}^{(k)}) || p^{(k)}(\mathbf{s}^{(k)} | \mathbf{s}^{(k+1)})] \]

## Applications in GEO-INFER

- **Resource Allocation**: Minimize free energy in spatial resource distributions.
- **Path Planning**: Select trajectories that minimize expected free energy over space-time.
- **Uncertainty Reduction**: Active sensing in geospatial environments to resolve spatial ambiguities.

See [active_inference_overview.md] for implementation details. 