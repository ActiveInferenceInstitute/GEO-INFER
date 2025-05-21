# GEO-INFER-TIME

**Temporal Methods for Dynamic Geospatial Data**

## Overview

GEO-INFER-TIME is a specialized module within the GEO-INFER framework focused on providing robust **temporal methods for timeline expression, analysis, and fusion of dynamic geospatial data**. Time is a critical dimension in understanding most ecological, civic, and environmental phenomena, from tracking climate change impacts and urban growth to monitoring species migration and real-time incident response. This module equips the GEO-INFER ecosystem with the tools to handle various forms of time-series data, perform sophisticated temporal analysis, model dynamic processes, and integrate real-time data streams for timely decision-making.

## Core Concepts

-   **Time Series:** A sequence of data points indexed in time order. In geospatial contexts, this often means observations of a variable at a specific location or for a specific spatial feature over time.
-   **Temporal Dynamics:** The patterns of change, trends, seasonality, and events that characterize how systems evolve over time.
-   **Temporal Resolution & Granularity:** The level of detail at which time is measured or represented (e.g., seconds, days, years).
-   **Real-time Processing:** The ability to ingest, analyze, and react to data as it is generated or received, with minimal delay.
-   **Temporal Databases:** Database systems optimized for storing and querying time-stamped data (e.g., TimescaleDB).

## Key Features

-   **Comprehensive Time-Series Geospatial Dataset Integration:** Tools for ingesting, aligning, and managing time-series data from various sources (e.g., satellite image archives, sensor networks, historical records) associated with geospatial features.
    -   Support for standard formats and protocols (e.g., STAC for spatio-temporal assets).
-   **Advanced Predictive Modeling of Temporal Trends:** Implementation of statistical and machine learning models (e.g., ARIMA, Prophet, LSTMs, Temporal Convolutional Networks) to forecast future values and trends in ecological, civic, and environmental systems.
-   **Real-time Data Ingestion & Updates:** Capabilities for handling high-velocity data streams, including WebSocket integration for pushing real-time updates to applications and other modules.
-   **Temporal Interpolation & Gap-Filling Methods:** Algorithms to estimate missing data points in time series, crucial for creating complete datasets for analysis (e.g., linear interpolation, spline interpolation, kriging for spatio-temporal data).
-   **Event Detection & Timeline Expression:** Methods for identifying significant events, anomalies, or change points within time series and constructing structured timelines of these occurrences.
-   **Temporal Aggregation & Resampling:** Tools to change the temporal resolution of time series data (e.g., aggregating daily data to monthly, or downsampling high-frequency sensor data).

## Temporal Data Processing & Analysis Workflow (Conceptual)

```mermaid
graph TD
    subgraph Data_Ingestion_Preparation as "Data Ingestion & Preparation"
        DS[Data Sources (Sensors, Satellites, APIs, Databases)] --> RAW[Raw Time-Series Data]
        RAW --> PRE[Preprocessing (Cleaning, Validation)]
        PRE --> ALIGN[Temporal Alignment & Synchronization]
        ALIGN --> GAP[Gap Filling & Interpolation]
        GAP --> AGG[Aggregation / Resampling (Optional)]
        AGG --> TDS[Prepared Time-Series Datasets]
    end

    subgraph Temporal_Analysis_Modeling as "Temporal Analysis & Modeling"
        TDS --> EDA[Exploratory Data Analysis (Decomposition, Autocorrelation)]
        EDA --> FEAT[Feature Engineering (Lags, Rolling Stats)]
        FEAT --> MODEL[Temporal Modeling (ARIMA, LSTM, Prophet)]
        MODEL --> EVAL[Model Evaluation & Validation]
        EVAL --> FORECAST[Forecasting & Prediction]
        EVAL --> INSIGHTS[Insights & Anomaly Detection]
    end

    subgraph Realtime_Processing as "Real-time Stream Processing (Optional)"
        STREAM_IN[Incoming Real-time Data (e.g., WebSockets)] --> RT_PROC[Real-time Analysis & Event Detection]
        RT_PROC --> RT_ALERT[Real-time Alerts / Updates]
        RT_PROC --> TDS %% Can update datasets
    end

    subgraph Output_Integration as "Output & Integration"
        FORECAST --> APP[Applications / Dashboards]
        INSIGHTS --> APP
        RT_ALERT --> APP
        FORECAST --> OTHER_MODULES[Other GEO-INFER Modules]
        INSIGHTS --> OTHER_MODULES
        TDS --> OTHER_MODULES
    end
    
    classDef timeprocess fill:#d2f8d2,stroke:#27ae60,stroke-width:2px;
    class Data_Ingestion_Preparation,Temporal_Analysis_Modeling,Realtime_Processing timeprocess;
```

## Directory Structure
```
GEO-INFER-TIME/
├── config/              # Configuration files for data sources, models
├── docs/                # Detailed documentation, tutorials
├── examples/            # Example scripts and notebooks for time-series analysis
├── src/                 # Source code
│   └── geo_infer_time/  # Main Python package
│       ├── api/         # API endpoints for temporal services
│       ├── core/        # Core temporal analysis algorithms, model implementations
│       ├── models/      # Data structures for time series, events
│       ├── io/          # Data ingestion and output utilities
│       └── utils/       # Helper functions, date/time utilities
└── tests/               # Unit and integration tests for temporal functions
```

## Getting Started

### Prerequisites
- Python 3.9+
- Pandas, NumPy, SciPy
- Statsmodels, Scikit-learn
- Optionally, libraries like Prophet, PyTorch/TensorFlow for advanced forecasting.
- Access to time-series databases (e.g., TimescaleDB, InfluxDB) might be required for certain use cases.

### Installation
```bash
# Clone the GEO-INFER repository if you haven't already
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER/GEO-INFER-TIME

pip install -e .
# or poetry install if pyproject.toml is configured
```

### Configuration
Module configuration (e.g., database connection strings, API keys for data services, default model parameters) can be managed via YAML files in `config/` or through environment variables.
```bash
# cp config/example_timescaledb_config.yaml config/local_timescaledb_config.yaml
# Edit local_timescaledb_config.yaml
```

### Running Tests
```bash
pytest tests/
```

## Temporal Analysis Capabilities

GEO-INFER-TIME provides a rich set of tools for understanding temporal patterns:

-   **Time Series Decomposition:** Breaking down a time series into trend, seasonal, and residual components (e.g., using moving averages, STL decomposition).
-   **Temporal Autocorrelation Analysis:** Measuring the correlation of a time series with lagged versions of itself (ACF and PACF plots) to identify seasonality and inform model selection.
-   **Change Point Detection:** Identifying abrupt changes or structural breaks in time series data.
-   **Seasonal Pattern Identification & Adjustment:** Detecting and quantifying regular seasonal variations, and methods for seasonal adjustment.
-   **Temporal Clustering:** Grouping similar time series based on their patterns or features.
-   **Anomaly Detection in Time Series:** Identifying unusual data points or subsequences that deviate from normal behavior (e.g., using statistical methods, isolation forests).
-   **Frequency Domain Analysis:** Techniques like Fourier transforms to analyze periodic components in time series.

## Data Handling

The module is designed to handle diverse temporal data characteristics:

-   **Regular Time Series:** Data points collected at fixed, consistent intervals (e.g., daily temperature readings).
-   **Irregular Time Series:** Data points collected at variable or non-uniform intervals (e.g., event timestamps, sensor readings triggered by thresholds).
-   **Event-Based Data:** Timestamps marking specific occurrences or events.
-   **Cyclical/Periodic Data:** Data exhibiting recurring patterns that are not necessarily tied to standard calendar seasons (e.g., economic cycles).
-   **Multi-Resolution Temporal Data:** Integrating and analyzing data collected at different time scales.
-   **Time-Stamped Geospatial Features:** Handling vector or raster data where each feature or pixel has an associated time series of attributes.

## Integration with Other Modules

GEO-INFER-TIME plays a crucial role in the broader GEO-INFER ecosystem:

-   **GEO-INFER-SPACE:** Essential for spatio-temporal analysis, where TIME provides the temporal dimension to spatial data managed by SPACE. This enables tracking changes in spatial patterns over time, spatio-temporal interpolation, and modeling of moving objects or spreading phenomena.
-   **GEO-INFER-DATA:** TIME relies on DATA for accessing and managing underlying storage of time-series datasets, whether from files, databases, or APIs. DATA may also handle archival of processed temporal data.
-   **GEO-INFER-ACT:** Dynamic active inference models in ACT require robust temporal representations of the environment and agent states. TIME provides the tools to model these temporal dynamics and feed them into agent generative models.
-   **GEO-INFER-AI:** Many AI techniques, particularly those for forecasting (LSTMs, TCNs) or sequence analysis, are applied to time-series data. TIME provides the preprocessed temporal data and features for these AI models.
-   **GEO-INFER-SIM:** Simulations often evolve over time. TIME can be used to analyze simulation outputs, compare simulated time series with real-world data, or provide temporal drivers (e.g., historical weather patterns) for simulations.
-   **GEO-INFER-APP:** Applications often need to display time-varying data, dashboards with temporal trends, or real-time updates. TIME provides the backend services for these frontend components.

## Use Cases

-   **Environmental Monitoring:** Analyzing trends in air/water quality, deforestation rates from satellite imagery time series, tracking glacial melt.
-   **Urban Mobility Pattern Analysis:** Understanding daily, weekly, and seasonal traffic flows, public transport usage, and pedestrian movement from location-based service data or sensor networks.
-   **Ecological Phenology Tracking:** Monitoring the timing of seasonal biological events (e.g., plant flowering, bird migration) and their shifts due to climate change.
-   **Temporal Impact Assessment:** Evaluating the changes in environmental or social indicators before and after an intervention or event (e.g., impact of a new policy, effect of a natural disaster over time).
-   **Real-time Sensor Network Data Integration & Alerting:** Processing streams from IoT sensors (e.g., weather stations, flood sensors, air quality monitors) for immediate insights and automated alerts.
-   **Agricultural Crop Growth Monitoring & Yield Prediction:** Analyzing time series of vegetation indices (e.g., NDVI) to track crop development and forecast yields.
-   **Public Health Surveillance:** Tracking the temporal spread of diseases or health-related incidents.

## Contributing

Contributions are welcome in areas such as:
-   Implementation of new time-series analysis or forecasting algorithms.
-   Optimizations for real-time data processing.
-   Integration with additional time-series databases or data formats.
-   Development of novel temporal visualization techniques.
-   Adding more example use cases and tutorials.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md` in the root repository) and any specific guidelines in `GEO-INFER-TIME/docs/CONTRIBUTING_TIME.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 