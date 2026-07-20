# Limitations and Next Steps {#sec:limitations_next_steps}

## Current Limitations

- Repository inventory counts measure implementation and verification surfaces;
  they do not establish domain validity, predictive accuracy, calibration, or
  causal efficacy.
- The generated figures summarize file-backed evidence surfaces and should not
  be read as benchmark results.
- A verification record is only as complete as the commands requested during
  generation; this build reports `{{VERIFICATION_STATUS}}` and exposes the
  command-level record for audit.
- External scientific claims require resolved entries in `references.bib` and
  should be expanded with domain-specific datasets and preregistered analyses.

## Next Steps

1. Run the full validation pipeline with fixed data seeds and archive
   `research_verification.json`, `research_inventory.json`, and the figure
   registry alongside rendered outputs.
2. Extend the inventory with domain datasets and benchmark results only when
   their producers emit machine-readable provenance and uncertainty.
3. Add preregistered comparisons for the Active Inference, Bayesian, and RISK
   research spine without replacing real model outputs with file-count proxies.
4. Render PDF/HTML through the publication template and inspect figure
   legibility, alt text, references, and caption fidelity at publication size.

## Boundary Note

Changing values must enter the manuscript through the generator. The tracked
source contains tokens; resolved output is disposable and must never be edited
by hand.
