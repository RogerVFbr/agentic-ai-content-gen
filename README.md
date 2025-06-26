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


| Metric                  | Value                                    |
|-------------------------|------------------------------------------|
| Latency *               | P50: 77.03s, P99: 189.96s                |
| Token Count * (Input)   | 10k                                      |
| Token Count * (Output)  | 5k                                       |
| Estimated Cost *        | US$ 0.03                                 |
| Container Size          | 4.5 GB (Uncompressed), 3 GB (Compressed) |
| Deployment Time         | 6 minutes                                | 
| Peak Memory Consumption | 3 GB                                     |

\* *(Average or percentile if specified, per run)*

---

## Technology Stack
| Component                  | Technology/Tool                         |
| -------------------------- |-----------------------------------------|
| Programming Language       | Python >= 3.13                          |
| Package Management         | Astral UV                               |
| Containerization           | Docker                                  |
| LLM                        | OpenAI GPT-4o Mini, OpenAI DALL·E 3     |
| Agent Orchestration        | LangChain, LangGraph                    |
| Agent Tooling              | MCP, Custom Implementations             |
| Agent Web Search           | Tavily, SerperDev                       |
| Testing                    | Pytest, MagikMock                       |
| CI/CD                      | GitHub, GitHub Actions                  |
| Cloud Infrastructure       | AWS - Eventbridge, IAM, Lambda, S3, ECR |
| Observability              | LangSmith, CloudWatch                   |
| Infrastructure as Code     | Terraform                               |
| Similarity Search          | Levenshtein, Text Embeddings            |

---

## Architecture and Design Decisions
*(W.I.P.)*

---

## Project Structure
```
├── app
│   ├── agents
│   │   └── meme_gen
│   │       ├── deliverables
│   │       │   └── image_generation_disabled.png  # Placeholder image for when image generation is disabled
│   │       ├── nodes                              # Contains individual processing nodes for the meme generation agent
│   │       │   ├── node_00_initializer.py         # Initializes the meme generation process
│   │       │   ├── node_01_researcher.py          # Researches trending topics for meme creation
│   │       │   ├── node_02_validator.py           # Validates topics for ethical and moral compliance
│   │       │   ├── node_03_editor.py              # Edits and prepares the meme content
│   │       │   ├── node_04_publisher.py           # Publishes the generated meme to social media
│   │       │   ├── node_05_failure.py             # Handles failure scenarios in the process
│   │       │   ├── node_06_success.py             # Handles successful completion of the process
│   │       │   ├── node_07_terminate.py           # Terminates the process and cleans up resources
│   │       │   └── node_base.py                   # Base class for all nodes in the meme generation process
│   │       ├── persistence                        # Stores persistent data for the meme generation agent
│   │       │   ├── memegen_graph.png              # Visual representation of the meme generation process
│   │       │   ├── used_topics_cache.pkl          # Cache of previously used topics
│   │       │   └── web_search_cache.pkl           # Cache of web search results
│   │       ├── agent.py                           # Main agent logic for meme generation
│   │       ├── graph.py                           # Defines the graph structure for the agent's workflow
│   │       ├── prompts.yml                        # YAML file containing prompts for the LLM
│   │       └── state.py                           # Manages the state of the meme generation process
│   ├── configurations                             # Configuration management for the application
│   │   ├── configs.py                             # Core configuration definitions
│   │   ├── configs_parser.py                      # Parses configuration files
│   │   ├── configuration_module.py                # Module for managing configurations
│   │   └── di_services.py                         # Dependency injection services
│   ├── controllers                                # Application controllers for managing workflows
│   │   ├── controller.py                          # Main application controller
│   │   ├── web_ui.py                              # Controller for the web user interface
│   │   └── worker.py                              # Background worker for asynchronous tasks
│   ├── crosscutting                               # Cross-cutting concerns shared across the application
│   │   ├── background_service
│   │   │   ├── cancellation_token.py              # Handles task cancellation tokens
│   │   │   ├── multi_shot_background_service.py   # Background service for multi-shot tasks
│   │   │   └── one_shot_background_service.py     # Background service for one-shot tasks
│   │   ├── logging
│   │   │   ├── app_logger.py                      # Application logging utility
│   │   │   └── app_logger_config.py               # Configuration for application logging
│   │   ├── semantic_cache.py                      # In-memory caching for semantic data
│   │   └── service_provider.py                    # Provides services for dependency injection
│   ├── infrastructure                             # Infrastructure-related clients and utilities
│   │   ├── google_trends_client.py                # Client for interacting with Google Trends
│   │   ├── serper_dev_client.py                   # Client for interacting with SerperDev
│   │   └── tavily_client.py                       # Client for interacting with Tavily
│   ├── mcp_servers                                # Manages connections to external MCP servers
│   │   └── social_networks.py                     # Handles interactions with social networks
│   ├── repositories                               # Data repositories for accessing and managing data
│   │   ├── image_repository.py                    # Repository for managing image data
│   │   ├── social_networks_repository.py          # Repository for social network data
│   │   ├── used_topics_repository.py              # Repository for used topics
│   │   ├── web_search_repository.py               # Repository for web search data
│   │   └── web_trends_repository.py               # Repository for web trends data
│   ├── tests                                      # Automated tests for the application
│   │   ├── integration                            # Integration tests for end-to-end workflows
│   │   └── unit                                   # Unit tests for individual components
│   ├── Dockerfile                                 # Dockerfile for containerizing the application
│   ├── configs.json                               # Default configuration file
│   ├── configs.local.json                         # Local environment configuration
│   ├── configs.tests.json                         # Test environment configuration
│   ├── configs_logger.json                        # Default logger configuration
│   ├── configs_logger.local.json                  # Local logger configuration
│   ├── configs_logger.tests.json                  # Test logger configuration
│   ├── configs_mcp.json                           # MCP-specific configuration
│   ├── handler_lambda.py                          # Lambda function handler
│   ├── handler_web_ui.py                          # Web UI handler
│   ├── pyproject.toml                             # Python project configuration
│   └── pytest.ini                                 # Pytest configuration
├── infra                                          # Terraform infrastructure as code.
└── README.md                                      # Project documentation

```

---

## Limitations and Future Improvements
*(W.I.P)*

* Single instance run per time
* Lacks human in the loop
* Meme joke quality questionable
* Meme text on images might be defective
* Lack of prompt evals
* Infra networking - VPC, Subnets, Security Groups, etc.

---

## Installation
*(W.I.P)*

### Prerequisites
- Python 3.13 or higher
- OpenAI account and API Key with organization validation
- Twitter (X) Developer account and API Key

### No docker:
* Install UV
* Navigate to your default projects folder
* Clone repo
* Navigate to app folder
* Create virtual environment
* Activate virtual environment
* Uv sync
* Create and populate .env file
* Run tests
* Run application

### Docker
* Install Docker & CURL
* Start Docker Desktop
* Open terminal
```bash
    # Navigate to your default projects folder
    cd ~/projects
    
    # Clone Repo
    git clone https://github.com/RogerVFbr/agentic-ai-content-gen.git
    
    # Navigate to app folder
    cd app
    
    # Create and populate .env file
    touch .env
    
    # Build image
    docker build --no-cache -t memegen . 
    
    # Run image
    docker run -p 9000:8080 memegen
    
    # Ping image
    curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

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




