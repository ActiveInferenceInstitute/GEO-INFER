# GEO-INFER-BIO 🧬

**Bioinformatics and Biological Data Analysis with Geospatial Context**

[![License: CC BY-ND-SA 4.0](https://img.shields.io/badge/License-CC%20BY--ND--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nd-sa/4.0/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Documentation Status](https://img.shields.io/badge/docs-in%20progress-orange.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

## Overview 📋

GEO-INFER-BIO is a specialized module within the GEO-INFER framework that uniquely **bridges the domains of bioinformatics, biological data science, and geospatial analysis**. It provides a powerful suite of tools for processing, analyzing, and visualizing diverse biological datasets (e.g., genomic, transcriptomic, proteomic, ecological) by explicitly incorporating their spatial and temporal contexts. This module enables researchers to explore biological systems from molecular to ecosystem scales, understanding how geographic location, environmental factors, and spatial relationships influence biological processes, distributions, and interactions. GEO-INFER-BIO aims to unlock new insights in fields like spatial omics, landscape genetics/genomics, phylogeography, epidemiology, and microbial ecology by providing an integrated analytical environment.

## Core Objectives

-   **Integrate Spatial Context into Bioinformatics:** Systematically incorporate geographic coordinates, environmental data, and spatial relationships into the analysis of biological data.
-   **Enable Spatial Omics Analysis:** Provide tools for analyzing spatially resolved omics data (e.g., spatial transcriptomics, metabolomics) to understand tissue architecture, cellular heterogeneity, and micro-environmental interactions.
-   **Support Landscape Genetics/Genomics & Phylogeography:** Facilitate the analysis of how landscape features and geographic distance influence genetic variation, population structure, gene flow, and evolutionary history.
-   **Facilitate Spatio-Temporal Ecological Modeling:** Model population dynamics, species distributions, habitat suitability, and ecological network interactions considering both spatial and temporal dimensions.
-   **Enhance Epidemiological Analysis:** Support the spatial tracking of pathogens, analysis of disease outbreaks by linking pathogen genomics with host locations and environmental factors (complementing GEO-INFER-HEALTH).
-   **Advance Microbial Ecology Research:** Enable the study of microbial community composition and function in relation to their geographic distribution and environmental niches.

## Key Features 🌟

### 1. Multi-Omics Integration with Spatial Dimensions
-   **Description:** Tools for processing, analyzing, and integrating various types of omics data (genomics, transcriptomics, epigenomics, proteomics, metabolomics) with their associated spatial information.
-   **Techniques/Examples:**
    -   Mapping gene expression patterns onto tissue sections (Spatial Transcriptomics).
    -   Analyzing genomic variation (SNPs, structural variants) across geographic landscapes.
    -   Correlating epigenetic modifications or proteomic profiles with environmental gradients or sample locations.
    -   Visualizing metabolic pathway activity in different spatial contexts or microenvironments.
-   **Benefits:** Uncovers spatial patterns in molecular data, links molecular mechanisms to geographical or environmental factors, provides insights into tissue organization and spatially regulated biological processes.

### 2. Biological Network Analysis in a Spatial Context
-   **Description:** Construction, analysis, and visualization of biological networks (e.g., protein-protein interaction, gene regulatory, metabolic, ecological food webs, microbial co-occurrence) where nodes or interactions have spatial attributes.
-   **Techniques/Examples:**
    -   Identifying geographically localized modules in interaction networks.
    -   Analyzing how network topology changes across different environments or locations.
    -   Overlaying network data on maps to visualize spatial distribution of interactions.
    -   Modeling flows (e.g., gene flow, nutrient flow) through spatially explicit networks.
-   **Benefits:** Reveals how spatial organization influences biological interactions and system properties, helps understand the resilience and function of ecological or molecular networks in different locations.

### 3. Advanced Spatial-Temporal Analysis for Biological Systems
-   **Description:** A suite of methods for analyzing biological data that varies across both space and time.
-   **Techniques/Examples:**
    -   Modeling species distribution changes in response to climate change (integrating GEO-INFER-TIME and GEO-INFER-SPACE).
    -   Tracking the spread of invasive species or pathogens using phylogeographic and spatial data.
    -   Analyzing spatio-temporal patterns in population abundance or genetic diversity.
    -   Visualizing developmental processes where gene expression changes occur in specific spatial locations over time.
-   **Benefits:** Provides a dynamic understanding of biological systems, enables forecasting of future states, and helps identify drivers of spatio-temporal change.

### 4. Geospatial Machine Learning & Statistics for Biology
-   **Description:** Application of machine learning and advanced statistical methods to biological data, explicitly incorporating spatial features and dependencies.
-   **Techniques/Examples:**
    -   Using geographically weighted regression (GWR) to model species abundance based on local environmental factors.
    -   Applying spatial clustering algorithms to identify distinct ecological zones or genetic populations.
    -   Training machine learning models (e.g., Random Forests, CNNs via GEO-INFER-AI) to predict habitat suitability or disease risk using both biological and geospatial predictors.
    -   Bayesian inference for population assignment or estimating migration rates (integrating GEO-INFER-BAYES).
-   **Benefits:** Improves predictive accuracy of biological models, helps uncover complex non-linear relationships between biology and geography, provides robust statistical inference in the presence of spatial autocorrelation.

## Module Architecture (Conceptual)

```mermaid
graph TD
    subgraph BIO_Core as "GEO-INFER-BIO Core Engine"
        API_BIO[API Layer (REST, GraphQL)]
        SERVICE_BIO[Service Layer (Workflow Orchestration)]
        OMICS_PROCESSOR[Omics Data Processor]
        NETWORK_BUILDER[Biological Network Engine]
        SPATIAL_BIO_ANALYZER[Spatial Bio-Analytics Toolkit]
        DATA_ADAPTERS_BIO[Data Adapters (Bio-DBs, GEO-INFER-DATA)]
    end

    subgraph Bio_Tools_Libs as "Bioinformatics Tools & Libraries (Interfaces)"
        SEQ_ANALYSIS_TOOLS[Sequence Analysis (e.g., BLAST, Aligners)]
        PHYLO_TOOLS[Phylogenetic Analysis (e.g., RAxML, BEAST wrappers)]
        POPGEN_TOOLS[Population Genetics Tools (e.g., VCFtools, Adegenet interfaces)]
        NETWORKX_BIO[NetworkX/igraph for Biological Networks]
        BIOPYTHON_INT[BioPython Integration]
    end

    subgraph External_Integrations_BIO as "External Systems & GEO-INFER Modules"
        BIO_DATABASES[(NCBI, Ensembl, UniProt, Public Omics Repos)]
        DATA_MOD_GI[GEO-INFER-DATA (Environmental Layers, Base Maps)]
        SPACE_MOD_GI[GEO-INFER-SPACE (Spatial Operations, Distance Matrices)]
        TIME_MOD_GI[GEO-INFER-TIME (Temporal Dynamics Modeling)]
        AI_MOD_GI[GEO-INFER-AI (ML Models for Bio-Pattern Recognition)]
        MATH_MOD_GI[GEO-INFER-MATH (Statistics, Graph Algorithms)]
        HEALTH_MOD_GI[GEO-INFER-HEALTH (Epidemiological Context)]
        APP_MOD_GI[GEO-INFER-APP (Visualization of Bio-Geo Data)]
    end

    %% Core Engine Connections
    API_BIO --> SERVICE_BIO
    SERVICE_BIO --> OMICS_PROCESSOR; SERVICE_BIO --> NETWORK_BUILDER; SERVICE_BIO --> SPATIAL_BIO_ANALYZER
    SERVICE_BIO --> DATA_ADAPTERS_BIO
    DATA_ADAPTERS_BIO --> BIO_DATABASES; DATA_ADAPTERS_BIO --> DATA_MOD_GI

    %% Core Components use Bio Tools & GI Modules
    OMICS_PROCESSOR --> SEQ_ANALYSIS_TOOLS; OMICS_PROCESSOR --> BIOPYTHON_INT
    NETWORK_BUILDER --> NETWORKX_BIO; NETWORK_BUILDER --> MATH_MOD_GI
    SPATIAL_BIO_ANALYZER --> POPGEN_TOOLS; SPATIAL_BIO_ANALYZER --> PHYLO_TOOLS
    SPATIAL_BIO_ANALYZER --> SPACE_MOD_GI; SPATIAL_BIO_ANALYZER --> TIME_MOD_GI; SPATIAL_BIO_ANALYZER --> AI_MOD_GI
    SPATIAL_BIO_ANALYZER --> HEALTH_MOD_GI

    %% Visualization
    SERVICE_BIO --> APP_MOD_GI

    classDef biomodule fill:#e0f2f1,stroke:#00796b,stroke-width:2px;
    class BIO_Core,Bio_Tools_Libs biomodule;
```

-   **Core Engine:** Manages APIs, orchestrates complex bio-geospatial workflows, and integrates various processing units.
-   **Bioinformatics Tools & Libraries (Interfaces):** Provides wrappers or direct interfaces to common bioinformatics software and libraries for tasks like sequence alignment, phylogenetic tree construction, and population genetics analysis.
-   **Processing Units:** Specialized components for omics data, network construction, and spatial bio-analytics.
-   **Data Adapters:** Handles connections to biological databases and integrates with `GEO-INFER-DATA` for environmental/geospatial context.

## Integration with other GEO-INFER Modules 🔄

-   **GEO-INFER-SPACE:** Essential for all spatial calculations, such as distances between samples, defining geographic regions, overlaying biological data with environmental layers, and creating spatial grids for analysis.
-   **GEO-INFER-TIME:** Crucial for analyzing time-series biological data, such as monitoring changes in species distribution, tracking epidemic spread over time, or studying developmental biology with temporal gene expression.
-   **GEO-INFER-DATA:** Provides access to contextual geospatial data (elevation, climate, land cover, administrative boundaries) and can store derived biological-geospatial datasets.
-   **GEO-INFER-AI:** Leveraged for applying machine learning techniques to predict species occurrences, classify cell types in spatial omics, or identify genetic markers associated with environmental adaptation, using combined bio-geo features.
-   **GEO-INFER-MATH:** Supplies statistical methods (e.g., for spatial statistics on genetic data), graph theory algorithms for network analysis, and optimization routines.
-   **GEO-INFER-SIM:** Can be used to simulate population dynamics, gene flow, or disease spread based on models parameterized or validated using GEO-INFER-BIO analyses.
-   **GEO-INFER-HEALTH:** Complements HEALTH by providing deeper biological/genomic insights into pathogens or host genetics relevant to epidemiological studies managed by HEALTH.
-   **GEO-INFER-APP:** Facilitates visualization of results, such as interactive maps of genetic diversity, spatial transcriptomic atlases, or dashboards showing species distribution model outputs.

## Use Cases 🔍

### 1. Spatial Transcriptomics & Multi-Omics Atlas
-   **Analysis:** Mapping gene, protein, or metabolite expression directly onto tissue images or 3D models of organs/organisms.
-   **Insight:** Understanding cellular heterogeneity, cell-cell interactions, and the spatial organization of biological processes within tissues in healthy and diseased states.

### 2. Landscape Genomics & Adaptation Studies
-   **Analysis:** Correlating genetic variation (e.g., SNPs from whole-genome sequencing) with environmental variables across a species' range.
-   **Insight:** Identifying genes and genomic regions under selection due to local environmental pressures, predicting how populations might respond to climate change.

### 3. Phylogeography & Pathogen Tracking
-   **Analysis:** Reconstructing the evolutionary history and geographic spread of species or pathogens using genetic/genomic data and sample locations.
-   **Insight:** Understanding historical migration routes, origins of outbreaks, and pathways of pathogen transmission.

### 4. Microbial Biogeography & Community Ecology
-   **Analysis:** Analyzing microbial community composition (e.g., from 16S rRNA or metagenomic sequencing) in relation to geographic location, soil type, host organism, or pollutant levels.
-   **Insight:** Understanding what drives microbial diversity and function in different environments, identifying hotspots of beneficial or pathogenic microbes.

### 5. Species Distribution Modeling (SDM) with Genetic Data
-   **Analysis:** Integrating occurrence data, environmental layers, and population genetic information to model current and future habitat suitability for species.
-   **Insight:** More accurate predictions of species ranges, identification of conservation priorities, understanding the role of genetic diversity in adaptability.

## Getting Started 🚀

### Prerequisites
-   Python 3.9+
-   Core GEO-INFER framework.
-   Standard bioinformatics libraries: Biopython, Pandas, NumPy, Scipy.
-   Potentially, command-line bioinformatics tools (e.g., BLAST+, SAMtools, BCFtools, common sequence aligners, phylogenetic software like RAxML or IQ-TREE) accessible in the system PATH or via Conda environments managed by the module.
-   Geospatial libraries: GeoPandas, Rasterio, Shapely.

### Installation
```bash
# Ensure the main GEO-INFER repository is cloned
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER

pip install -e ./GEO-INFER-BIO
# Or if managed by a broader project build system.
# Consider using Conda for managing complex bioinformatics dependencies.
```

### Configuration
-   Paths to reference genomes, gene annotations, biological databases.
-   Configuration for external bioinformatics tools (if applicable).
-   API keys for online biological databases (e.g., NCBI Entrez).
-   Typically managed in YAML files (e.g., `GEO-INFER-BIO/config/bio_config.yaml`).

### Quick Start Example (Illustrative: Landscape Genetics)
```python
import geopandas as gpd
# Assuming conceptual classes from geo_infer_bio
# from geo_infer_bio.analysis import LandscapeGeneticsAnalyzer
# from geo_infer_bio.utils import load_genetic_data_vcf, load_sample_locations_csv, load_environmental_raster

# --- 1. Load Data ---
# vcf_file = "path/to/population_snps.vcf.gz"
# sample_locations_file = "path/to/sample_coords_env.csv" # With sampleID, lat, lon, env_variable1
# environmental_raster_file = "path/to/temperature_bio1.tif"

# genetic_data = load_genetic_data_vcf(vcf_file)
# samples_gdf = load_sample_locations_csv(sample_locations_file)
# temperature_raster = load_environmental_raster(environmental_raster_file)

# --- 2. Initialize Analyzer ---
# landscape_gen_analyzer = LandscapeGeneticsAnalyzer(config_path="GEO-INFER-BIO/config/default.yaml")

# --- 3. Calculate Genetic Differentiation & Correlate with Geography/Environment ---
# Pairwise Fst, Isolation by Distance (IBD)
# results_ibd = landscape_gen_analyzer.analyze_isolation_by_distance(
#    genetic_data=genetic_data,
#    samples_locations=samples_gdf
# )
# results_ibd.plot_ibd(output_path="outputs/ibd_plot.png")

# Genotype-Environment Association (GEA) - e.g., using RDA or LFMM
# gea_results = landscape_gen_analyzer.run_gea_analysis(
#    genetic_data=genetic_data,
#    samples_env_data=samples_gdf, # Assuming env data is in the GeoDataFrame
#    environmental_layers={"temperature": temperature_raster} 
# )
# gea_results.plot_manhattan_candidate_snps(output_path="outputs/gea_manhattan.png")

# --- 4. Visualize Results (e.g., map of genetic clusters or adaptive allele frequencies) ---
# Not shown here, but would use GEO-INFER-APP adapters.
```

## Directory Structure 📁

(Adjusted to better fit a Python module with bioinformatics focus)
```
GEO-INFER-BIO/
├── config/                 # Configuration files (db paths, tool params)
├── data/                   # Example small datasets, reference files for tests
├── docs/                   # Detailed documentation, methodology for bio-geo analyses
├── examples/               # Jupyter notebooks or scripts for use cases
│   └── sequence_analysis_example.py
├── src/
│   └── geo_infer_bio/
│       ├── __init__.py
│       ├── analysis/       # High-level analytical workflows (e.g., landscape_genetics, spatial_omics)
│       │   ├── __init__.py
│       │   ├── sequence_analysis.py # (Broader than just core, might be workflow level)
│       │   └── network_analysis.py  # (Workflow level)
│       ├── core/           # Fundamental algorithms & processing steps
│       │   ├── __init__.py
│       │   ├── alignment.py  # Wrappers for aligners
│       │   ├── phylogenetics.py # Tree building logic
│       │   └── population_genetics.py # Basic calculations (allele freqs, heterozygosity)
│       ├── io/             # Data input/output for bio formats (VCF, FASTA, GFF, Newick)
│       ├── models/         # Data structures for biological entities (genes, proteins, populations with spatial attributes)
│       ├── services/       # Interfaces to external bioinformatics tools or databases
│       ├── utils/          # Utility functions (bioinformatics string manipulation, stats helpers)
│       │   ├── __init__.py
│       │   ├── validation.py
│       │   └── visualization.py # Adapters for GEO-INFER-APP or specific bio-visuals
│       └── api/            # REST/GraphQL APIs for accessing GEO-INFER-BIO functionalities
│           ├── __init__.py
│           ├── rest_api.py
│           └── graphql_api.py
├── tests/                  # Unit and integration tests
│   └── test_sequence_analysis.py
├── Dockerfile              # For containerizing the module with its dependencies
└── docker-compose.yml      # For multi-container setups if needed
```

## Future Development

-   Direct integration with cloud-based bioinformatics platforms (e.g., Terra, DNAnexus).
-   Support for single-cell spatial omics data formats and advanced analytical pipelines.
-   Development of AI-driven tools for de novo discovery of bio-geospatial patterns.
-   Integration of epidemiological models with pathogen genomic surveillance.
-   Tools for modeling gene drive dynamics in spatial contexts.

## Contributing 🤝

We welcome contributions! This includes adding new bioinformatics tools or analysis pipelines, developing interfaces to more biological databases, creating new use case examples, improving documentation, or enhancing the integration between biological and geospatial methods. Please see our main [CONTRIBUTING.md](https://github.com/activeinference/GEO-INFER/blob/main/CONTRIBUTING.md) and any specific guidelines in `GEO-INFER-BIO/docs/CONTRIBUTING_BIO.md` (to be created).

## License 📄

This module, as part of the GEO-INFER framework, is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details.

## Citation 📚

If you use GEO-INFER-BIO in your research, please cite the GEO-INFER framework and this module:
```bibtex
@software{geo_infer_framework_2024,
  title = {{GEO-INFER: A Comprehensive Geospatial Inference Framework}},
  author = {{GEO-INFER Collaborative Team}},
  year = {2024},
  publisher = {Active Inference Institute},
  url = {https://github.com/activeinference/GEO-INFER}
}
@software{geo_infer_bio_2024,
  title = {{GEO-INFER-BIO: Bioinformatics and Biological Data Analysis with Geospatial Context}},
  author = {{GEO-INFER BIO Module Contributors}},
  year = {2024},
  publisher = {Active Inference Institute},
  url = {https://github.com/activeinference/GEO-INFER/tree/main/GEO-INFER-BIO}
}
``` 