# Multi-Agent Application Proof of Concept

## Overview
This project is a proof of concept for a multi-agent application that demonstrates production-ready features. It showcases a modular architecture, an orchestration layer powered by `LangGraph`, and robust application lifecycle management using a `BackgroundService` implementation. The project also includes a custom dependency injection solution, unit testing, semantic caching, tool quota control, and a custom logging solution for local and remote structured logging.

---

## Features
- **Modular Architecture**: Each component of the application is encapsulated in separate modules for better maintainability and scalability.
- **Orchestration Layer**: Utilizes `LangGraph` to define and manage workflows with conditional transitions between states.
- **Application Lifecycle Management**: Implements a `BackgroundService` for managing the lifecycle of the application.
- **Custom Dependency Injection**: Provides a lightweight, custom-built dependency injection solution for managing dependencies.
- **Unit Testing**: Comprehensive unit tests ensure the reliability of individual components.
- **Semantic Caching**: Implements caching mechanisms to optimize performance and reduce redundant operations.
- **Tool Quota Control**: Manages and enforces quotas for external tools and APIs to ensure efficient resource usage.
- **Custom Logging Solution**: Provides structured logging for both local and remote environments, supporting JSON-based logs and integration with external logging services.

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

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/multi-agent-poc.git
   cd multi-agent-poc
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the tests to ensure everything is set up correctly:
   ```bash
   pytest
   ```

---

## Usage

### Building the Workflow
The `MultiAgentGraph` class defines the workflow. To build and visualize the graph:
```python
from app.agents.multi_agent.graph import MultiAgentGraph

# Initialize dependencies
graph = MultiAgentGraph(logger, initializer, researcher, validator, editor, publisher, failure, success)

# Build the graph
await graph.build()
```

### Running the Controller
The `MultiAgentController` manages the execution of the workflow:
```python
from app.controllers.controller import MultiAgentController

controller = MultiAgentController(agent=graph)
await controller.run({"input_key": "input_value"})
```

### Visualizing the Workflow
The workflow graph is saved as a PNG file in the `persistence` directory:
```
app/agents/multi_agent/persistence/multi_agent_graph.png
```

---

## Testing
Unit tests are provided for all major components. To run the tests:
```bash
pytest
```

---

## Key Components

### `MultiAgentGraph`
- **Purpose**: Defines the state-driven workflow for the multi-agent application.
- **Nodes**:
  - `Initializer`: Initializes the process.
  - `Researcher`: Conducts research tasks.
  - `Validator`: Validates research results.
  - `Editor`: Processes and edits data.
  - `Publisher`: Publishes the final output.
  - `Failure`: Handles failure states.
  - `Success`: Handles success states.

### `MultiAgentController`
- **Purpose**: Orchestrates the execution of the workflow.
- **Features**:
  - Handles input and output.
  - Manages logging and error handling.

### Logging
- **Implementation**: The custom logging solution includes:
  - **Local Logging**: Logs structured data to local files in JSON format.
  - **Remote Logging**: Integrates with external logging services for centralized log management.
  - **AppLogger**: Provides decorators like `@timeit` for measuring execution time.

---

## Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## Docker
   ```bash
      uv lock
   ```
   ```bash
      docker build -t memegen .
   ```
   ```bash
      docker run -p 9000:8080 memegen
   ```
   ```bash
      curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"payload":"hello world!"}'
   ```
   Docker local disk usage
   ```bash
      docker system df
   ```
   ```bash
      docker system prune -af
   ```

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments
- [LangGraph](https://github.com/langgraph) for the state graph framework.
- Contributors and maintainers of this project.



