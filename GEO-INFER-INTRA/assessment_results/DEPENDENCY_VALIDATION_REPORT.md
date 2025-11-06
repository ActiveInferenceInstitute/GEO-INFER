# GEO-INFER Dependency Validation Report

**Generated**: Automated validation

## Overview

Validated 36 modules for dependency consistency, usage, and version compatibility.

## Summary Statistics

- **Modules with missing dependencies**: 27/36
- **Modules with potentially unused dependencies**: 27/36
- **Modules with dependency file inconsistencies**: 5/36
- **Potential version conflicts**: 0

## Module Details

### ACT

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 18
- **Actual Imports**: 23
- **Missing Dependencies**: 5
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `bayeux-mcmc`
- `core`
- `jax`
- `julia`
- `utils`


### AG

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 11
- **Actual Imports**: 12
- **Missing Dependencies**: 1
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `agricultural_api`


### AGENT

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 28
- **Actual Imports**: 10
- **Missing Dependencies**: 0
- **Potentially Unused**: 18
- **Inconsistencies**: 0


### AI

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 7
- **Actual Imports**: 5
- **Missing Dependencies**: 0
- **Potentially Unused**: 2
- **Inconsistencies**: 0

**Potentially Unused Dependencies** (may be false positives):
- `tensorflow`
- `torch`


### ANT

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 10
- **Actual Imports**: 22
- **Missing Dependencies**: 17
- **Potentially Unused**: 5
- **Inconsistencies**: 0

**Missing Dependencies**:
- `aco`
- `agent_base`
- `algorithms`
- `analysis`
- `applications`
- `config`
- `core`
- `digital_stigmergy`
- `disaster`
- `environmental`
- `metrics`
- `patterns`
- `population`
- `pso`
- `stigmergy`
- `urban`
- `utils`

**Potentially Unused Dependencies** (may be false positives):
- `asyncio-mqtt`
- `geopandas`
- `h3`
- `matplotlib`
- `networkx`


### API

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 10
- **Actual Imports**: 7
- **Missing Dependencies**: 4
- **Potentially Unused**: 7
- **Inconsistencies**: 0

**Missing Dependencies**:
- `exceptions`
- `middleware`
- `pydantic_settings`
- `starlette`

**Potentially Unused Dependencies** (may be false positives):
- `httpx`
- `pydantic-settings`
- `pytest`
- `pytest-cov`
- `python-dotenv`
- `python-multipart`
- `requests`


### APP

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 4
- **Actual Imports**: 2
- **Missing Dependencies**: 1
- **Potentially Unused**: 3
- **Inconsistencies**: 0

**Missing Dependencies**:
- `agent_interface`

**Potentially Unused Dependencies** (may be false positives):
- `fastapi`
- `pydantic`
- `uvicorn`


### ART

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 22
- **Actual Imports**: 14
- **Missing Dependencies**: 0
- **Potentially Unused**: 8
- **Inconsistencies**: 10

**Dependency File Inconsistencies**:
- `mayavi`: requirements.txt: >=4.7.0, setup.py: >=4.7.0",    # For 3D visualizations
- `seaborn`: requirements.txt: >=0.11.0, setup.py: >=0.11.0",  # For enhanced color palettes
- `cartopy`: requirements.txt: >=0.20.0, setup.py: >=0.20.0",  # For map projections
- `folium`: requirements.txt: >=0.12.0, setup.py: >=0.12.0",   # For web-based mapping
- `kaleido`: requirements.txt: >=0.2.0, setup.py: >=0.2.0",   # For plotly image export
- `imageio-ffmpeg`: requirements.txt: >=0.4.0, setup.py: >=0.4.0",  # For video export
- `imageio`: requirements.txt: >=2.9.0, setup.py: >=2.9.0",   # For animation support
- `psutil`: requirements.txt: >=5.8.0, setup.py: >=5.8.0",    # For system monitoring
- `plotly`: requirements.txt: >=5.0.0, setup.py: >=5.0.0",    # For interactive visualizations
- `bokeh`: requirements.txt: >=2.4.0, setup.py: >=2.4.0",     # For interactive plots

**Potentially Unused Dependencies** (may be false positives):
- `bokeh`
- `cartopy`
- `colour`
- `imageio`
- `imageio-ffmpeg`
- `kaleido`
- `scikit-image`
- `seaborn`


### BAYES

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 14
- **Actual Imports**: 38
- **Missing Dependencies**: 28
- **Potentially Unused**: 4
- **Inconsistencies**: 11

**Missing Dependencies**:
- `base`
- `bayesian_network`
- `bayesian_timeseries`
- `core`
- `data_processing`
- `diagnostics`
- `dirichlet_process`
- `dynamic_spatial`
- `hierarchical`
- `hmc`
- `inference`
- `likelihoods`
- `mcmc`
- `model_comparison`
- `models`
- `multilevel`
- `posterior`
- `priors`
- `pymc_interface`
- `smc`
- `spatial_causal`
- `spatial_clustering`
- `spatial_gp`
- `spatiotemporal_gp`
- `stan_interface`
- `tfp_interface`
- `variational`
- `visualization`

**Dependency File Inconsistencies**:
- `tensorflow-probability`: requirements.txt: >=0.18.0, setup.py: unspecified
- `numpy`: requirements.txt: >=1.20.0, setup.py: unspecified
- `pymc`: requirements.txt: >=4.0.0, setup.py: unspecified
- `xarray`: requirements.txt: >=0.19.0, setup.py: unspecified
- `arviz`: requirements.txt: >=0.11.0, setup.py: unspecified
- `geopandas`: requirements.txt: >=0.10.0, setup.py: unspecified
- `rasterio`: requirements.txt: >=1.2.0, setup.py: unspecified
- `cmdstanpy`: requirements.txt: >=1.0.0, setup.py: unspecified
- `scipy`: requirements.txt: >=1.7.0, setup.py: unspecified
- `pandas`: requirements.txt: >=1.3.0, setup.py: unspecified
- `matplotlib`: requirements.txt: >=3.4.0, setup.py: unspecified

**Potentially Unused Dependencies** (may be false positives):
- `cmdstanpy`
- `geopandas`
- `rasterio`
- `tensorflow-probability`


### BIO

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 29
- **Actual Imports**: 18
- **Missing Dependencies**: 4
- **Potentially Unused**: 15
- **Inconsistencies**: 0

**Missing Dependencies**:
- `api`
- `core`
- `models`
- `utils`


### CIV

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 3
- **Actual Imports**: 0
- **Missing Dependencies**: 0
- **Potentially Unused**: 3
- **Inconsistencies**: 0

**Potentially Unused Dependencies** (may be false positives):
- `geopandas`
- `numpy`
- `pandas`


### COG

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 2
- **Actual Imports**: 25
- **Missing Dependencies**: 24
- **Potentially Unused**: 1
- **Inconsistencies**: 0

**Missing Dependencies**:
- `adapters`
- `api`
- `cognitive_engine`
- `cognitive_models`
- `core`
- `decision`
- `flask`
- `flask-cors`
- `helpers`
- `matplotlib`
- `models`
- `networkx`
- `processor`
- `pyyaml`
- `seaborn`
- `spatial_language`
- `spatial_memory`
- `spatial_perception`
- `spatial_reasoning`
- `support`
- `user_profiles`
- `utils`
- `validation`
- `visualization`

**Potentially Unused Dependencies** (may be false positives):
- `pandas`


### COMMS

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 4
- **Actual Imports**: 5
- **Missing Dependencies**: 1
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `smtplib`


### DATA

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 39
- **Actual Imports**: 36
- **Missing Dependencies**: 22
- **Potentially Unused**: 25
- **Inconsistencies**: 0

**Missing Dependencies**:
- `aiohttp`
- `api`
- `cloud`
- `core`
- `database`
- `file`
- `h5py`
- `ingestion`
- `lzma`
- `models`
- `pipeline`
- `psutil`
- `pymongo`
- `rest_api`
- `schemas`
- `service`
- `storage`
- `stream`
- `urllib3`
- `utils`
- `validation`
- `xarray`


### ECON

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 3
- **Actual Imports**: 41
- **Missing Dependencies**: 38
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `api`
- `behavioral_economics`
- `bioregional`
- `bioregional_governance`
- `bioregional_markets`
- `circular_economy`
- `consumer_theory`
- `core`
- `data_loader`
- `ecological_economics`
- `econometrics_engine`
- `economic_api`
- `ecosystem_services`
- `fastapi`
- `game_theory`
- `geopandas`
- `growth_models`
- `indicators`
- `macroeconomics`
- `market_structure`
- `matplotlib`
- `microeconomics`
- `modeling_engine`
- `natural_capital`
- `networkx`
- `policy_engine`
- `producer_theory`
- `pydantic`
- `pyyaml`
- `requests`
- `scikit-learn`
- `seaborn`
- `spatial_ecology`
- `statsmodels`
- `sustainability_metrics`
- `utils`
- `validator`
- `visualizer`


### EXAMPLES

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 12
- **Actual Imports**: 5
- **Missing Dependencies**: 4
- **Potentially Unused**: 11
- **Inconsistencies**: 2

**Missing Dependencies**:
- `integration_models`
- `models`
- `monitoring`
- `utils`

**Dependency File Inconsistencies**:
- `pandas`: requirements.txt: >=1.3.0, setup.py: >=1.4.0",         # Data manipulation for examples
- `matplotlib`: requirements.txt: >=3.4.0, setup.py: >=3.5.0",     # Basic plotting for demonstrations


### GIT

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 18
- **Actual Imports**: 14
- **Missing Dependencies**: 5
- **Potentially Unused**: 9
- **Inconsistencies**: 0

**Missing Dependencies**:
- `core`
- `git`
- `github_api`
- `urllib3`
- `utils`

**Potentially Unused Dependencies** (may be false positives):
- `GitPython`
- `black`
- `colorlog`
- `flake8`
- `isort`
- `mypy`
- `pytest`
- `pytest-cov`
- `radon`


### HEALTH

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 44
- **Actual Imports**: 18
- **Missing Dependencies**: 11
- **Potentially Unused**: 37
- **Inconsistencies**: 0

**Missing Dependencies**:
- `advanced_geospatial`
- `api`
- `config`
- `core`
- `data_models`
- `disease_surveillance`
- `environmental_health`
- `geospatial_utils`
- `healthcare_accessibility`
- `models`
- `utils`


### INTRA

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 13
- **Actual Imports**: 2
- **Missing Dependencies**: 0
- **Potentially Unused**: 11
- **Inconsistencies**: 0


### IOT

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 23
- **Actual Imports**: 15
- **Missing Dependencies**: 2
- **Potentially Unused**: 10
- **Inconsistencies**: 0

**Missing Dependencies**:
- `networkx`
- `registry`

**Potentially Unused Dependencies** (may be false positives):
- `aiocoap`
- `confluent-kafka`
- `geopandas`
- `influxdb-client`
- `pyproj`
- `pyserial`
- `python-dotenv`
- `rich`
- `scikit-learn`
- `websockets`


### LOG

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 2
- **Actual Imports**: 18
- **Missing Dependencies**: 16
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `contextily`
- `delivery`
- `fastapi`
- `folium`
- `matplotlib`
- `networkx`
- `numpy`
- `ortools`
- `prometheus-client`
- `pulp`
- `pydantic`
- `routing`
- `shapely`
- `structlog`
- `supply_chain`
- `transport`


### MATH

- **Requirements.txt**: ❌
- **Setup.py**: ❌
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 0
- **Actual Imports**: 13
- **Missing Dependencies**: 13
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `core`
- `cupy`
- `flask`
- `numpy`
- `pandas`
- `psutil`
- `scikit-learn`
- `scipy`
- `symengine`
- `sympy`
- `tensorflow`
- `torch`
- `werkzeug`


### METAGOV

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 3
- **Actual Imports**: 0
- **Missing Dependencies**: 0
- **Potentially Unused**: 3
- **Inconsistencies**: 0

**Potentially Unused Dependencies** (may be false positives):
- `numpy`
- `pyyaml`
- `typing_extensions`


### NORMS

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 6
- **Actual Imports**: 20
- **Missing Dependencies**: 14
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `compliance_status`
- `compliance_tracking`
- `core`
- `fastapi`
- `legal_entity`
- `legal_frameworks`
- `models`
- `normative_inference`
- `policy`
- `policy_impact`
- `pydantic`
- `regulation`
- `zoning`
- `zoning_analysis`


### OPS

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 16
- **Actual Imports**: 16
- **Missing Dependencies**: 8
- **Potentially Unused**: 8
- **Inconsistencies**: 5

**Missing Dependencies**:
- `config`
- `cryptography`
- `logger`
- `monitoring`
- `prometheus_fastapi_instrumentator`
- `psutil`
- `pyjwt`
- `redis`

**Dependency File Inconsistencies**:
- `pytest-cov`: requirements.txt: >=4.1.0, setup.py: >=2.12.0
- `prometheus-client`: requirements.txt: >=0.16.0, setup.py: >=0.12.0
- `pytest`: requirements.txt: >=7.3.1, setup.py: >=6.0.0
- `fastapi`: requirements.txt: >=0.100.0, setup.py: >=0.68.0
- `structlog`: requirements.txt: >=23.1.0, setup.py: >=21.1.0

**Potentially Unused Dependencies** (may be false positives):
- `black`
- `docker`
- `flake8`
- `isort`
- `pre-commit`
- `prometheus-fastapi-instrumentator`
- `pytest-cov`
- `pytest-timeout`


### ORG

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 1
- **Actual Imports**: 0
- **Missing Dependencies**: 0
- **Potentially Unused**: 1
- **Inconsistencies**: 0

**Potentially Unused Dependencies** (may be false positives):
- `pandas`


### PEP

- **Requirements.txt**: ✅
- **Setup.py**: ❌
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 6
- **Actual Imports**: 31
- **Missing Dependencies**: 26
- **Potentially Unused**: 1
- **Inconsistencies**: 0

**Missing Dependencies**:
- `core`
- `crm`
- `crm_endpoints`
- `crm_models`
- `crm_reports`
- `crm_visuals`
- `generic_report_generator`
- `hr`
- `hr_endpoints`
- `hr_models`
- `hr_reports`
- `hr_visuals`
- `importer`
- `methods`
- `models`
- `orchestrator`
- `pep_engine`
- `reporting`
- `talent`
- `talent_endpoints`
- `talent_models`
- `talent_reports`
- `talent_visuals`
- `transformer`
- `validator`
- `visualizations`

**Potentially Unused Dependencies** (may be false positives):
- `uvicorn`


### PLACE

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 25
- **Actual Imports**: 23
- **Missing Dependencies**: 12
- **Potentially Unused**: 14
- **Inconsistencies**: 0

**Missing Dependencies**:
- `base_module`
- `branca`
- `coastal_resilience_analyzer`
- `core`
- `county_boundary_loader`
- `data_sources`
- `fire_risk_assessor`
- `forest_health_monitor`
- `locations`
- `unified_backend`
- `utils`
- `visualization_engine`


### REQ

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 1
- **Actual Imports**: 0
- **Missing Dependencies**: 0
- **Potentially Unused**: 1
- **Inconsistencies**: 0

**Potentially Unused Dependencies** (may be false positives):
- `pydantic`


### RISK

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 3
- **Actual Imports**: 28
- **Missing Dependencies**: 25
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `catastrophe_models`
- `claim_models`
- `claims_processing`
- `core`
- `geopandas`
- `hazard_model`
- `insurance_models`
- `jsonschema`
- `models`
- `policy_management`
- `policy_models`
- `portfolio_management`
- `portfolio_models`
- `pricing_engine`
- `pyyaml`
- `requests`
- `risk_assessment`
- `risk_engine`
- `risk_models`
- `shapely`
- `underwriting_models`
- `underwriting_rules`
- `utils`
- `validation`
- `vulnerability_model`


### SEC

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 13
- **Actual Imports**: 22
- **Missing Dependencies**: 12
- **Potentially Unused**: 3
- **Inconsistencies**: 1

**Missing Dependencies**:
- `access_control`
- `cognitive_security`
- `core`
- `digital_security`
- `hmac`
- `joblib`
- `models`
- `physical_security`
- `requests`
- `scikit-learn`
- `secrets`
- `utils`

**Dependency File Inconsistencies**:
- `h3`: requirements.txt: >=4.0.0, setup.py: >=3.7.0

**Potentially Unused Dependencies** (may be false positives):
- `bcrypt`
- `pydantic`
- `sqlalchemy`


### SIM

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 3
- **Actual Imports**: 2
- **Missing Dependencies**: 0
- **Potentially Unused**: 1
- **Inconsistencies**: 0

**Potentially Unused Dependencies** (may be false positives):
- `scipy`


### SPACE

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 17
- **Actual Imports**: 80
- **Missing Dependencies**: 66
- **Potentially Unused**: 3
- **Inconsistencies**: 0

**Missing Dependencies**:
- `aggregation`
- `analytics`
- `backends`
- `boundaries`
- `boundary_manager`
- `branca`
- `config_models`
- `core`
- `data_models`
- `datasets`
- `detector`
- `dispatcher`
- `flow_analysis`
- `folium`
- `format_handlers`
- `geojson_pydantic`
- `geometric_operations`
- `geostatistics`
- `git`
- `glob`
- `h3_backend`
- `h3_utils`
- `hierarchy`
- `hierarchy_metrics`
- `laspy`
- `lumping`
- `main`
- `matplotlib`
- `message_broker`
- `messaging`
- `ml_integration`
- `nested_grid`
- `network`
- `operations`
- `osc_geo`
- `osc_simple_status`
- `osmnx`
- `pattern_detection`
- `performance_metrics`
- `place_analyzer`
- `plotly`
- `point_cloud`
- `point_cloud_io`
- `protocols`
- `psutil`
- `raster`
- `raster_io`
- `repos`
- `requests`
- `rest`
- `rest_api`
- `routing`
- `schemas`
- `seaborn`
- `spatial_indexing`
- `spatial_utils`
- `splitting`
- `srai`
- `srai_backend`
- `src`
- `status`
- `utils`
- `vector`
- `vector_io`
- `visualization`
- `webbrowser`

**Potentially Unused Dependencies** (may be false positives):
- `fiona`
- `geojson-pydantic`
- `python-multipart`


### SPM

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 10
- **Actual Imports**: 36
- **Missing Dependencies**: 26
- **Potentially Unused**: 0
- **Inconsistencies**: 0

**Missing Dependencies**:
- `api`
- `bayesian`
- `contrasts`
- `core`
- `data_io`
- `data_models`
- `diagnostics`
- `endpoints`
- `glm`
- `helpers`
- `interactive`
- `maps`
- `mixed_effects`
- `model_validation`
- `models`
- `nonparametric`
- `preprocessing`
- `pymc`
- `rft`
- `ruptures`
- `spatial_analysis`
- `spatial_regression`
- `statsmodels`
- `temporal_analysis`
- `utils`
- `validation`


### TEST

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 25
- **Actual Imports**: 11
- **Missing Dependencies**: 8
- **Potentially Unused**: 22
- **Inconsistencies**: 0

**Missing Dependencies**:
- `h3`
- `log_integration`
- `module_health`
- `performance_monitor`
- `scipy`
- `test_discoverer`
- `test_orchestrator`
- `test_runner`


### TIME

- **Requirements.txt**: ✅
- **Setup.py**: ✅
- **Pyproject.toml**: ✅
- **Declared Dependencies**: 5
- **Actual Imports**: 5
- **Missing Dependencies**: 1
- **Potentially Unused**: 1
- **Inconsistencies**: 0

**Missing Dependencies**:
- `models`

**Potentially Unused Dependencies** (may be false positives):
- `scipy`


