# Presentation Visualization System

A comprehensive tool for automatically generating professional visualizations for robotics presentations, including kinematic diagrams, workspace analysis, ROS communication graphs, state machine diagrams, keyframe sequences, and data plots.

## Features

- **Kinematic Diagrams**: Generate robot skeleton diagrams with joint annotations
- **Workspace Analysis**: Visualize and compare reachable workspace with/without rail extension
- **ROS Communication Graphs**: Create clear system architecture diagrams
- **State Machine Visualization**: Generate FSM flow diagrams
- **Keyframe Extraction**: Automatically capture simulation keyframes
- **Data Plotting**: Generate professional time-series plots from CSV data

## Installation

### Prerequisites

- Python 3.10 or higher
- ROS2 Humble (for data collection features)
- Gazebo Fortress (for keyframe extraction)

### Install from source

```bash
# Clone the repository (if not already in workspace)
cd /path/to/workspace

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Linux-specific dependencies

For screenshot functionality on Linux:

```bash
pip install python-xlib
```

## Quick Start

### 1. Create a configuration file

Copy the template configuration:

```bash
cp presentation_viz/config_template.yaml config.yaml
```

Edit `config.yaml` to customize your visualization settings.

### 2. Generate visualizations

```python
from presentation_viz import ConfigManager, setup_logger

# Set up logging
logger = setup_logger()

# Load configuration
config = ConfigManager("config.yaml")

# Get configuration for specific modules
style = config.get_style()
output_config = config.get_output_config()

logger.info(f"Output directory: {output_config['directory']}")
logger.info(f"DPI: {style['dpi']}")
```

### 3. Run batch generation (coming soon)

```bash
presentation-viz --config config.yaml --batch
```

## Configuration

The system uses YAML configuration files. See `presentation_viz/config_template.yaml` for all available options.

### Key configuration sections:

- **style**: Global visual styling (colors, fonts, DPI)
- **data_sources**: ROS topics and file paths
- **output**: Output directory and format settings
- **module-specific**: Configuration for each visualization module

## Project Structure

```
presentation_viz/
├── __init__.py              # Package initialization
├── config_manager.py        # Configuration management
├── logger.py                # Logging system
├── config_template.yaml     # Configuration template
├── data_collector.py        # ROS2 data collection (coming soon)
├── kinematic_diagram.py     # Kinematic diagram generator (coming soon)
├── workspace_analyzer.py    # Workspace analysis (coming soon)
├── ros_graph.py             # ROS graph generator (coming soon)
├── fsm_visualizer.py        # FSM visualization (coming soon)
├── keyframe_extractor.py    # Keyframe extraction (coming soon)
├── plot_generator.py        # Data plotting (coming soon)
└── export_manager.py        # Output management (coming soon)
```

## Development

### Running tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=presentation_viz
```

### Code formatting

```bash
# Format code
black presentation_viz/

# Check style
flake8 presentation_viz/
```

## Requirements

This system addresses the following requirements:
- **Requirement 9.1**: YAML configuration file support
- **Requirement 9.5**: Default configuration fallback

## License

MIT License

## Authors

Dog2 Robotics Team
