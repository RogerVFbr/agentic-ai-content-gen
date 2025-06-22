# Agentic AI MemeGen
*Not just another GenAI Meme Generator!* This project suggests a blueprint for integrating modern agentic AI implementations with software engineering best practices — ensuring maintainability, extensibility, portability, and scalability.

---

## Table of Contents
- [Business Case](#business-case)
- [Technical Features](#technical-features)
- [Solution Metrics](#solution-metrics)
- [Technology Stack](#technology-stack)
- [Architecture and Design Decisions](#architecture-and-design-decisions)
- [Project Structure](#project-structure)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Business Case
| Feature                           | Description                                                                                                                                                                                                                                                                                                    |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Industry                          | Content Creation, Marketing, Social Networks                                                                                                                                                                                                                                                                  |
| Persona                           | Content Marketers, Copywriters, Social Media Managers, Agencies                                                                                                                                                                                                                                               |
| Problem                           | Creating content at scale is time-consuming. Manual workflows limit throughput and consistency.                                                                                                                                                                                                              |
| Solution                          | This application uses AI agents to autonomously generate content. It orchestrates multiple LLM-powered tasks including research, validation, edition, and publishing.                                                                                                                                        |
| User Interface                    | Not applicable. Fully autonomous scheduled triggering.                                                                                                                                                                                                                                                        |
| LLM Models                        | OpenAI GPT-4o Mini, OpenAI DALL·E 3                                                                                                                                                                                                                                                                             |
| External Data Sources             | Google Trends, Web Search, Twitter (X)                                                                                                                                                                                                                                                                        |
| Key Features                      | 1. Researches funny trends on the internet.<br>2. Validates chosen topics for morality and ethics.<br>3. Designs a meme and other deliverables.<br>4. Publishes the results on social media.                                                                                                                 |
| Complexity                        | Medium — depends on API setup, agent configuration, and deployment requirements.                                                                                                                                                                                                                              |
| Value Proposition / Benefits      | - Reduces content creation time from hours to minutes.<br>- Enables scaling content production without growing headcount.                                                                                                   |

---

## Technical Features
- **Robust multi-environment configuration** - Enables seamless adaptation across local, development, testing, and production environments.
- **Modular architecture (Onion-inspired)** - Enforces strict responsibility boundaries for high reusability and maintainability.
- **Application lifecycle management** - Handles graceful shutdowns during cancellations or failures to ensure system integrity.
- **Dependency injection with automatic resolution** - Simplifies development and testing through clean, decoupled component management.
- **Fully asynchronous I/O architecture** - Improves performance and enables fast, reliable cancellation handling.
- **Comprehensive automated testing** - Includes both unit and integration tests to guarantee maintainability and safe extensibility.
- **Semantic in-memory caching** - Optimizes performance by reducing redundant LLM tool calls.
- **Tool quota management** - Controls and enforces agent nodes’ usage limits for external APIs, ensuring efficient and predictable resource consumption.
- **Flexible logging solution** - Provides developer-friendly logs formatting locally while structuring logs in JSON for production environments.
- **LLM and traditional observability integration** - Provides deep insights for troubleshooting, monitoring, and performance optimization.
- **Automated deployment pipeline** - Enables consistent, governed version releases without manual intervention.
- **Containerized deployment** - Ensures cross-environment portability and operational consistency.
- **Serverless cloud architecture** - Simplifies deployment with low-cost, low-maintenance infrastructure, accelerating time to market.

---

## Solution Metrics


| Metric                  | Value                     |
|-------------------------| ------------------------- |
| Latency *               | 2 minutes, 30 seconds     |
| Token Count * (Input)   | 30k                       |
| Token Count * (Output)  | 15k                       |
| Estimated Cost *        | US$ 0.07                  |
| Container Size          | 3GB                       |
| Deployment Time         | 5 minutes                 |
| Peak Memory Consumption | 3GB                       |
\* *(Avegage, per run)*

---

## Technology Stack
| Component                  | Technology/Tool                                              |
| -------------------------- | ------------------------------------------------------------ |
| Programming Language       | Python >= 3.11                                               |
| Package Management         | Astral UV                                                   |
| Containerization           | Docker                                                      |
| LLM                        | OpenAI GPT-4o Mini, OpenAI DALL·E 3                          |
| Agent Orchestration        | LangChain, LangGraph                                        |
| Agent Tooling              | MCP, Custom Implementations                                 |
| Agent Web Search           | Tavily, SerperDev                                           |
| Testing                    | Pytest, MagikMock                                           |
| CI/CD                      | GitHub, GitHub Actions                                      |
| Cloud Infrastructure       | AWS (Lambda, S3)                                            |
| Observability              | LangSmith, CloudWatch                                       |
| Infrastructure as Code     | Terraform                                                   |
| Similarity Search          | Levenshtein, Text Embeddings                                |

---

## Architecture and Design Decisions
*(W.I.P.)*

---

## Project Structure
```
├── README.md                              # Project documentation and usage instructions
└── app                                    # Main application directory
    ├── agents                             # Contains agent-related logic and workflows
    │   └── meme_gen                       # Specific implementation for the MemeGen agent
    │       ├── agent.py                   # MemeGen Agent entrypoint
    │       ├── graph.py                   # Workflow graph definition for MemeGen
    │       ├── nodes                      # Individual nodes in the workflow
    │       │   ├── node_00_initializer.py # Node for initializing the workflow
    │       │   ├── node_01_researcher.py  # Node for conducting research tasks
    │       │   ├── node_02_validator.py   # Node for validating research results
    │       │   ├── node_03_editor.py      # Node for editing and processing data
    │       │   ├── node_04_publisher.py   # Node for publishing the final output
    │       │   ├── node_05_failure.py     # Node for handling failure states
    │       │   ├── node_06_success.py     # Node for handling success states
    │       │   └── node_base.py           # Base class for all nodes
    │       ├── persistence                # Persistence-related files
    │       │   └── memegen_graph.png      # Visualization of the workflow graph
    │       ├── prompts.yml                # YAML file containing prompts for the agent
    │       └── state.py                   # State management for the MemeGen workflow
    ├── configs.json                       # Default configuration file
    ├── configs.local.json                 # Local configuration overrides
    ├── configurations                     # Configuration management module
    │   ├── configs.py                     # Configuration definitions
    │   ├── configs_parser.py              # Parser for configuration files
    │   ├── configuration_module.py        # Configuration module logic
    │   ├── di_container.py                # Dependency injection container
    │   └── di_services.py                 # Dependency injection services
    ├── controllers                        # Controllers for managing workflows
    │   ├── controller.py                  # Main controller logic
    │   └── worker.py                      # Handles application lifecycle and graceful shutdown
    ├── crosscutting                       # Cross-cutting concerns (e.g., logging, caching)
    │   ├── background_service.py          # Background service implementation
    │   ├── logging                        # Logging-related files
    │   │   ├── app_logger.py              # Custom logger implementation
    │   │   └── app_logger_config.py       # Logger configuration
    │   ├── memoize_method.py              # Memoization utility for methods
    │   └── semantic_cache.py              # Semantic caching implementation
    ├── handler_meme_gen.py                # Entry point for handling MemeGen agent tasks
    ├── infrastructure                     # Infrastructure-related clients and services
    │   ├── google_trends_client.py        # Client for Google Trends API
    │   ├── serper_dev_client.py           # Client for Serper.dev API
    │   └── tavily_client.py               # Client for Tavily API
    ├── logger_configs.json                # Default logger configuration
    ├── logger_configs.local.json          # Local logger configuration overrides
    └── repositories                       # Data access layer
        └── web_search_repository.py       # Repository for web search operations
```

---

## Limitations and Future Improvements
*(W.I.P)*

* Single instance run per time
* Lacks human in the loop
* Meme joke quality questionable
* Meme text on images might be defective
* Lack of prompt evals

---

## Installation
*(W.I.P)*

### Prerequisites
- Python 3.11 or higher

### No docker:
* Install UV
* Navigate to your default projects folder
* Clone repo
* Navigate to app folder
* Uv sync
* Run tests
* Run application

### Docker
* Install Docker
* Start docker
* Navigate to your default projects folder
* Clone Repo
* Navigate to app folder
* Build image
* Run image
* Ping image

---

## Usage
*(W.I.P)*

---

## Contributing
*(W.I.P)*

---

## License
*(W.I.P)*

---

## Contact
*(W.I.P)*




