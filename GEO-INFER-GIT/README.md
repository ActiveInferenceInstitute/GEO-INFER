# GEO-INFER-GIT

**Geospatial Version Control & Repository Management**

## Overview

GEO-INFER-GIT is a specialized module within the GEO-INFER ecosystem designed to streamline the management, cloning, and synchronization of Git repositories, with a particular emphasis on those containing geospatial data, models, and aA. It provides robust tools for developers and researchers to efficiently access and maintain version-controlled geospatial resources and related software projects.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-git.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

The module facilitates the integration of external codebases, datasets, and pre-trained models into the GEO-INFER framework, ensuring that all components are version-aware and consistently managed. This is crucial for reproducibility, collaboration, and the systematic evolution of complex geospatial analysis workflows.

## Core Objectives

*   **Automated Repository Acquisition**: Simplify and automate the process of cloning and updating multiple Git repositories relevant to geospatial analysis and AI.
*   **Version Consistency**: Ensure that specific versions or branches of repositories are used, promoting stable and reproducible research and development environments.
*   **Selective Integration**: Allow fine-grained control over which repositories, users, or specific repository contents are cloned and integrated.
*   **Dependency Management**: Facilitate the tracking of external software dependencies that are managed via Git.
*   **Workflow Integration**: Provide a seamless bridge for other GEO-INFER modules to access and utilize code and data from version-controlled sources.

## Key Features

*   **Bulk Repository Cloning**:
    *   **Description**: Efficiently clone multiple repositories from platforms like GitHub, GitLab, or Bitbucket based on a configuration list.
    *   **Techniques**: Utilizes Git command-line interface or GitPython library for robust cloning operations.
    *   **Benefits**: Saves significant time and effort when setting up projects or integrating numerous external libraries.
*   **User-Specific Repository Cloning**:
    *   **Description**: Clone all or a filtered subset of repositories belonging to specific GitHub users or organizations.
    *   **Techniques**: Leverages GitHub API (or other platform APIs) to fetch user/organization repository lists.
    *   **Benefits**: Useful for tracking research groups, key contributors, or specific open-source ecosystems.
*   **Parallel Cloning Operations**:
    *   **Description**: Accelerate the cloning process by performing multiple clone operations concurrently.
    *   **Techniques**: Implements multi-threading or asynchronous operations.
    *   **Benefits**: Drastically reduces the time required for large-scale repository acquisition.
*   **Advanced Filtering and Selection**:
    *   **Description**: Include or exclude repositories based on names, topics, languages, or custom tags. Filter by branch, tag, or commit hash.
    *   **Techniques**: Regex pattern matching, API-based filtering, configuration-driven rules.
    *   **Benefits**: Ensures only relevant repositories and versions are integrated, optimizing storage and reducing noise.
*   **Configuration-Driven Management**:
    *   **Description**: Define cloning tasks, target repositories, user lists, and cloning parameters via human-readable YAML configuration files.
    *   **Techniques**: YAML parsing, structured configuration objects.
    *   **Benefits**: Easy to manage, version control, and share cloning setups without code changes.
*   **Comprehensive Reporting and Logging**:
    *   **Description**: Generate detailed reports on cloning successes, failures, and skipped repositories. Maintain logs for debugging and auditing.
    *   **Techniques**: Structured logging, report generation libraries (e.g., CSV, JSON, HTML).
    *   **Benefits**: Provides transparency and aids in troubleshooting integration issues.
*   **Authentication Support**:
    *   **Description**: Supports authenticated Git operations (e.g., using GitHub Personal Access Tokens) for accessing private repositories or avoiding rate limits.
    *   **Techniques**: Secure token management, integration with Git credential helpers.
    *   **Benefits**: Enables access to a wider range of repositories and improves reliability.

### Featured Repositories (Illustrative Examples)

GEO-INFER-GIT is pre-configured or can be easily configured to clone and integrate with several high-quality open-source projects relevant to the GEO-INFER ecosystem. These serve as examples of how the module can be used:

#### Geospatial & Climate
*   **[kraina-ai/srai](https://github.com/kraina-ai/srai)**: Spatial Representations for Artificial Intelligence - a library to extract, process, and transform spatial data into ML-ready representations.
*   **[koito19960406/ZenSVI](https://github.com/koito19960406/ZenSVI)**: Zero-code framework for downloading, processing, and analyzing street view imagery.
*   **[os-climate](https://github.com/os-climate)**: Open-source climate analytics and tools for climate risk assessment and alignment with the Paris Agreement.

#### Agent Systems
*   **[SamuelSchmidgall/AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)**: A research platform for developing, testing, and evaluating multi-agent systems.
*   **[Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)**: An experimental open-source attempt to make GPT-4 fully autonomous.

#### Bayesian & Active Inference
*   **[biaslab/ForneyLab.jl](https://github.com/biaslab/ForneyLab.jl)**: A Julia package for factor graph modeling and automated inference.
*   **[ReactiveBayes/ReactiveMP.jl](https://github.com/ReactiveBayes/ReactiveMP.jl)**: A message passing-based Bayesian inference framework for reactive systems in Julia.

## Module Architecture

The GEO-INFER-GIT module is designed with a clear separation of concerns, facilitating maintainability and extensibility.

```mermaid
graph TD
    A[Configuration Files (YAML)] --> B{Git Operation Core};
    B --> C[Cloning Engine];
    B --> D[Update/Sync Engine];
    B --> E[Filtering & Selection Logic];
    F[GEO-INFER Modules] --> G{Git API Facade};
    G --> B;
    C --> H[Parallel Execution Manager];
    H --> I[Individual Git Clone Tasks];
    E --> C;
    E --> D;
    B --> J[Logging & Reporting];

    subgraph Input
        A
    end

    subgraph Core Logic
        B
        C
        D
        E
        H
        I
    end

    subgraph Output & Integration
        F
        G
        J
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#ccf,stroke:#333,stroke-width:2px
    style J fill:#9cf,stroke:#333,stroke-width:2px
```

**Components**:

1.  **Configuration Files (YAML)**: Define target repositories, users, cloning parameters, and authentication details.
2.  **Git API Facade**: Provides a simplified interface for other GEO-INFER modules to request repository data or trigger Git operations.
3.  **Git Operation Core**: Manages the overall workflow, parses configurations, and orchestrates different engines.
4.  **Cloning Engine**: Responsible for executing the `git clone` operations.
5.  **Update/Sync Engine**: Handles `git pull` or other synchronization tasks for already cloned repositories.
6.  **Filtering & Selection Logic**: Applies rules to determine which repositories or branches to process.
7.  **Parallel Execution Manager**: Manages concurrent Git operations to improve performance.
8.  **Logging & Reporting**: Captures detailed logs of all operations and generates summary reports.

## Integration with other GEO-INFER Modules

GEO-INFER-GIT plays a crucial role in the broader GEO-INFER ecosystem:

*   **GEO-INFER-DATA**: Can use GIT to clone repositories containing datasets or scripts for data acquisition and preprocessing.
*   **GEO-INFER-AI / GEO-INFER-ML**: Leverages GIT to fetch specific versions of machine learning models, libraries, or research codebases.
*   **GEO-INFER-AGENT**: May clone agent frameworks or supporting libraries required for multi-agent simulations.
*   **GEO-INFER-OPS**: Could utilize GIT to manage infrastructure-as-code repositories or deployment scripts.
*   **Reproducibility**: By pinning specific commit hashes or tags, GEO-INFER-GIT ensures that experiments and analyses across the GEO-INFER platform are reproducible.

Other modules can interact with GEO-INFER-GIT programmatically via its API or by relying on a shared directory structure where cloned repositories are stored.

## Getting Started

### Prerequisites

*   Python 3.8 or higher
*   Git command-line tools installed and accessible in the system PATH.
*   Access to the internet for cloning remote repositories.

### Installation

1.  **Ensure GEO-INFER-GIT is part of your GEO-INFER installation.**
    If installed as a submodule or component of the main GEO-INFER project, it should be readily available.

2.  **Install dependencies**:
    Navigate to the `GEO-INFER-GIT` module directory:
    ```bash
    cd path/to/GEO-INFER/GEO-INFER-GIT
    ```
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Basic Usage

The primary interaction with GEO-INFER-GIT is often through its command-line interface or by invoking its core functions from other scripts.

To clone repositories based on the default configuration:
```bash
python clone_repos.py
```
(Assuming `clone_repos.py` is the main executable script for this module).

### Configuration

The module behavior is primarily controlled by YAML configuration files typically located in the `config/` directory within the `GEO-INFER-GIT` module.

*   **`target_repos.yaml`**: Defines a list of specific repositories to clone, including their owner, repository name, and optionally, branch, tag, or commit.
    ```yaml
    repositories:
      - owner: kraina-ai
        repo: srai
        branch: main
        tags: ["geospatial", "ml", "library"]
      - owner: os-climate
        repo: physrisk
        # Clones default branch if not specified
    ```

*   **`target_users.yaml`**: Specifies GitHub users (or organizations) whose repositories should be cloned. Supports filtering within user repositories.
    ```yaml
    users:
      - username: Significant-Gravitas
        include_repos:
          - AutoGPT
        exclude_repos:
          - "*-docs"  # Wildcards might be supported
        max_repos: 5 # Limit the number of repos cloned per user
        tags: ["ai", "agent"]
    ```

*   **`clone_config.yaml`**: Contains general cloning settings, such as the output directory for cloned repositories, parallel execution settings, and default authentication details.
    ```yaml
    clone_settings:
      output_directory: "../cloned_repositories" # Relative to GEO-INFER-GIT root
      parallel_cloning: true
      max_workers: 4 # Number of parallel processes/threads
      default_branch: "main"
      # github_token: "YOUR_GITHUB_PAT" # Alternatively, use command-line or environment variables
    ```

### Command-line Options (Illustrative)

A typical command-line interface might offer:
```bash
python clone_repos.py --help
```

Possible options:
*   `--config-dir <path>`: Specify a custom directory for configuration files.
*   `--output-dir <path>`: Override the output directory for cloned repositories.
*   `--clone-repos`: Flag to specifically clone repositories from `target_repos.yaml`.
*   `--clone-users`: Flag to clone repositories from users defined in `target_users.yaml`.
*   `--github-token <token>`: Provide a GitHub API token for authentication, overriding config or environment variables.
*   `--parallel / --no-parallel`: Enable or disable parallel cloning.
*   `--max-workers <num>`: Set the maximum number of parallel workers.
*   `--verbose`: Enable more detailed logging output.
*   `--generate-report`: Create a summary report of the cloning operations.
*   `--update-existing`: Pull changes for already cloned repositories.

## GitHub Authentication

For accessing private repositories or to avoid API rate limits when dealing with many repositories, using a GitHub Personal Access Token (PAT) is recommended.

1.  **Generate a PAT** from your GitHub account settings (Developer settings -> Personal access tokens). Grant appropriate scopes (e.g., `repo`).
2.  **Provide the token**:
    *   Via `clone_config.yaml` (less secure for shared configs).
    *   Via the `--github-token` command-line argument.
    *   Via an environment variable (e.g., `GITHUB_TOKEN`), which the script can be designed to read.

Example using command-line:
```bash
python clone_repos.py --github-token YOUR_PERSONAL_ACCESS_TOKEN
```

## Directory Structure

A typical directory structure for the `GEO-INFER-GIT` module:

```
GEO-INFER-GIT/
├── config/                   # Configuration files
│   ├── clone_config.yaml       # General cloning configuration
│   ├── target_repos.yaml       # Specific repositories to clone
│   └── target_users.yaml       # Users/organizations whose repositories to clone
├── src/                      # Source code for the module
│   └── geo_infer_git/          # Main Python package
│       ├── api/                # API for programmatic access (optional)
│       ├── core/               # Core cloning, updating, and management logic
│       ├── models/             # Data models for configuration, reports
│       └── utils/              # Utility functions (e.g., YAML parsing, logging setup)
├── tests/                    # Unit and integration tests
│   ├── core/
│   └── utils/
├── clone_repos.py            # Main executable script (example)
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules for this module
└── README.md                 # This file
```

## Future Development

*   **Support for other Git Platforms**: Extend functionality to clone from GitLab, Bitbucket, and other self-hosted Git instances.
*   **Enhanced Synchronization Strategies**: Implement more sophisticated update mechanisms (e.g., rebase, merge strategies).
*   **Git LFS (Large File Storage) Support**: Add specific handling for repositories using Git LFS.
*   **Sparse Checkout**: Allow cloning only specific subdirectories within large repositories.
*   **GUI / Web Interface**: A simple interface for managing configurations and viewing cloning status (potentially integrated with GEO-INFER-APP).
*   **Direct Integration with GEO-INFER-DATA's ETL pipelines**: Trigger cloning as a preliminary step in data ingestion workflows.
*   **Security Enhancements**: More robust handling of secrets and credentials.

## Contributing

Contributions to GEO-INFER-GIT are highly encouraged! Whether it's improving documentation, adding new features, fixing bugs, or suggesting new ideas, your input is valuable. Please refer to the main `CONTRIBUTING.md` in the GEO-INFER root directory for general guidelines.

1.  Fork the repository.
2.  Create a new branch for your feature or fix.
3.  Develop and test your changes.
4.  Ensure your code adheres to the project's coding standards.
5.  Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License - see the `LICENSE` file in the GEO-INFER root directory for details. 