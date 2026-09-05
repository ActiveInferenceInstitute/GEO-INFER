"""Basic risk assessment example using GEO-INFER-RISK.

This example actually computes risk numbers end to end:
1. Simulates a reproducible earthquake event set with a seeded
   catastrophe model.
2. Converts events into an event loss table.
3. Computes annual average loss (AAL), the 25-year PML, and an annual
   aggregate exceedance probability curve with ``geo_infer_risk.utils.risk_metrics``.

Run from the repository root:
    uv run --no-sync python GEO-INFER-RISK/examples/basic_risk_assessment.py
"""

import pandas as pd

from geo_infer_risk.core.catastrophe_models import (
    CatastropheConfig,
    EnhancedEarthquakeModel,
)
from geo_infer_risk.utils.risk_metrics import (
    calculate_aal,
    calculate_annual_aggregate_exceedance_probability,
    calculate_pml,
)

EXPOSURE_YEARS = 50.0


def build_loss_table(model: EnhancedEarthquakeModel, n_events: int) -> pd.DataFrame:
    """Simulate events and derive one loss per event.

    Loss per event uses an ILLUSTRATIVE fragility: 2% of exposure value per
    unit of magnitude above M5 (the event's intensity measure). Swap in a
    real vulnerability curve for production use.
    """
    events = model.simulate_events(n_events)
    exposure_value = 1_000_000.0
    rows = [
        {
            "event_id": event["event_id"],
            "hazard_type": "earthquake",
            "loss": exposure_value * 0.02 * max(0.0, event["magnitude"] - 5.0),
        }
        for event in events
    ]
    return pd.DataFrame(rows)


def main() -> None:
    """Run the basic risk assessment example."""
    print("=" * 60)
    print("GEO-INFER-RISK: Basic Risk Assessment Example")
    print("=" * 60)

    # Step 1: reproducible catastrophe simulation. The seed lives on the
    # config, so this run replays exactly.
    config = CatastropheConfig(
        simulation_years=int(EXPOSURE_YEARS),
        spatial_correlation=False,
        random_seed=7,
    )
    model = EnhancedEarthquakeModel(config=config)
    model.model_parameters = {"mean_depth": 15.0}
    events = model.simulate_events(200)
    print(f"\nStep 1: simulated {len(events)} earthquake events (seed=7)")

    # Step 2: event loss table
    losses = build_loss_table(model, 200)
    print(f"Step 2: loss table with {len(losses)} events")
    print(f"   Total simulated loss: ${losses['loss'].sum():,.0f}")

    # Step 3: risk metrics over a 50-year exposure window
    aal = calculate_aal(losses, exposure_years=EXPOSURE_YEARS)["total"]
    pml_25 = calculate_pml(losses, return_period=25, exposure_years=EXPOSURE_YEARS)
    aep = calculate_annual_aggregate_exceedance_probability(
        losses,
        threshold=25_000,
        num_years=20_000,
        random_seed=7,
        exposure_years=EXPOSURE_YEARS,
    )

    print(f"Step 3: risk metrics over a {EXPOSURE_YEARS:.0f}-year exposure window")
    print(f"   AAL (annual average loss):     ${aal:,.0f}")
    print(f"   25-year PML:                   ${pml_25:,.0f}")
    print(f"   P(aggregate loss > $25k/yr):   {aep:.4f}")

    print("\nExample complete. All numbers derive from the simulated event set.")


if __name__ == "__main__":
    main()
