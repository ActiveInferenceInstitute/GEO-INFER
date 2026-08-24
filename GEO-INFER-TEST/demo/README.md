# Crescent City civic-intel end-to-end consumer demo

This runnable example shows GEO-INFER importing the sibling
`crescent-city-intel` contract (`crescent-city-geo-intel/v1`) and driving the
RISK, BAYES and ACT modules together on the SAME bundled seed, in one place.

There is a per-module civic-intel ingestion surface
(`geo_infer_risk.civic_intel`, `geo_infer_bayes.civic_intel`,
`geo_infer_act.core.civic_intel`) and a cross-module integration test, but no
single consumer that ties them together. This demo closes that gap:

1. loads the bundled seed (the RISK / BAYES / PLACE copies are byte-identical)
   via `load_bundled_contract()`;
2. feeds that one contract to all three ingestors;
3. prints a compact human-readable summary — Crescent City anchor, the four
   hazard domains, the RISK hazard weights, the BAYES categorical prior, the
   ACT deterministic policy decision, and a geo-view parity block;
4. skips a module gracefully (clear message) when its civic-intel helper
   cannot be imported.

## Geo-view parity

`build_geo_parity(contract)` (alias `build_iso_geo_parity`) is a pure,
deterministic, JSON-safe digest that proves all three modules lower the same
contract into agreeing geo views. It compares, field-wise, the raw contract
against each importable module's parsed view across six dimensions:

- the contract schema id;
- the per-module view schema each module validates against;
- the WGS84 bounds;
- the municipal anchor (name / county / state / latitude / longitude);
- the nominal hazard-domain points (the four domain ids + names);
- the hazard-weighted municipal-code section references per domain
  (`get_sections` refs, flattened from the contract's nested hazard topics).

The digest reports `sighted` (modules that imported), `skipped` (modules whose
helper is absent), per-dimension `*Agreement` booleans, and a single `match`.
`geo_views_agree(contract)` collapses that into a boolean (and raises
`RuntimeError` only when no module is importable).

## Files

- `crescent_city_civic_intel_demo.py` — the runnable example. The pure
  `build_summary(contract)` / `build_geo_parity(contract)` functions are the
  deterministic, testable digest; `main()` loads the seed and renders it.
- `test_crescent_city_civic_intel_demo.py` — pins `build_summary` and
  `build_geo_parity` output to the bundled seed (real modules, no stand-ins).
- `__init__.py` — package marker so pytest can import the demo beside its test.

`build_summary` / `build_geo_parity` resolve the seed via
`CRESCENT_CITY_INTEL_CONTRACT_PATH` when set, otherwise the first existing
RISK/BAYES/PLACE bundled copy. They perform no network access and never search
sibling checkouts.

## Run

```bash
uv run python GEO-INFER-TEST/demo/crescent_city_civic_intel_demo.py
```

Expected output tail (module outputs are real and deterministic for the seed):

```
  RISK      : hazard weights  climate adaptation 0.833 | erosion 0.667 | flood zone 1.000 | ...
  BAYES     : prior probabilities  climate-environment 0.300 | emergency-management 0.200 | ...
  ACT       : policy prior over 9 hazard states
              dominant hazard: tsunami
              selected action: maintain_baseline_ops (p=0.257, EFE=1.153)
  geo view parity : 3 modules sighted
    modules       : risk bayes act
    schema        : contract=crescent-city-geo-intel/v1, agrees=yes
    bounds        : {'west': -124.408, 'south': 41.458, 'east': -123.536, 'north': 42.006}, agrees=yes
    anchor        : Crescent City · Del Norte County, California [41.76, -124.2], agrees=yes
    sections      : 4 domain points, agrees=yes
    match         : yes
```

## Verify

```bash
uv run python -m pytest GEO-INFER-TEST/demo/test_crescent_city_civic_intel_demo.py -q
uv run --with 'ruff>=0.3.0' ruff check \
  GEO-INFER-TEST/demo/crescent_city_civic_intel_demo.py \
  GEO-INFER-TEST/demo/test_crescent_city_civic_intel_demo.py \
  --select F821,F823,E721,E722
uv run python -m py_compile \
  GEO-INFER-TEST/demo/crescent_city_civic_intel_demo.py \
  GEO-INFER-TEST/demo/test_crescent_city_civic_intel_demo.py
```

No production modules are modified by this example; the files above are the
only additions.