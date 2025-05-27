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
app/
├── agents/
│   └── multi_agent/
│       ├── graph.py                # Defines the workflow using LangGraph
│       ├── nodes/                  # Contains individual node implementations
│       │   ├── node_00_initializer.py
│       │   ├── node_01_researcher.py
│       │   ├── node_02_validator.py
│       │   ├── node_03_editor.py
│       │   ├── node_04_publisher.py
│       │   ├── node_05_failure.py
│       │   └── node_06_success.py
│       ├── state.py                # Defines the application state class
│       └── persistence/            # Stores SQLite database and workflow images
├── controllers/
│   └── controller.py               # Orchestration layer for managing workflows
├── crosscutting/
│   ├── logging/
│   │   └── app_logger.py           # Custom logger implementation
│   └── semantic_cache.py           # Semantic caching implementation
├── services/
│   └── background_service.py       # BackgroundService implementation
├── config/
│   ├── settings.py                 # Application configuration settings
│   └── logging_config.py           # Logging configuration settings
├── tests/
│   ├── unit/
│   │   ├── agents/
│   │   │   └── multi_agent/
│   │   │       └── test_graph.py   # Unit tests for the workflow
│   │   ├── controllers/
│   │   │   └── test_controller.py  # Unit tests for the orchestration layer
│   │   └── crosscutting/
│   │       ├── test_logging.py     # Unit tests for logging
│   │       └── test_caching.py     # Unit tests for caching
│   └── integration/
│       └── test_end_to_end.py      # End-to-end integration tests
└── main.py                         # Entry point for the application
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

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments
- [LangGraph](https://github.com/langgraph) for the state graph framework.
- Contributors and maintainers of this project.
