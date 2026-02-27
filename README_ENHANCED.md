# AI-WantEngine Enhanced

AI-Powered Endogenous Scarcity-Driven Engine with improved configuration, logging, error handling, and OpenClaw integration.

## Features

- **Psychological State Simulation**: Models boredom, curiosity, energy, and fatigue
- **Autonomous Task Generation**: Creates tasks based on psychological states
- **Energy Management**: Prevents burnout with rest periods and fatigue tracking
- **OpenClaw Integration**: Execute tasks via OpenClaw CLI
- **Configurable**: JSON-based configuration system
- **Logging**: Comprehensive logging with file and console output
- **Type Hints**: Full type annotation support
- **Error Handling**: Robust error handling throughout

## Installation

```bash
git clone https://github.com/wuyunfa/AI-WantEngine.git
cd AI-WantEngine
pip install -r requirements.txt  # if any dependencies
```

## Quick Start

### Basic Usage

```python
from want_engine_enhanced import WantEngine, WantEngineConfig

# Use default configuration
engine = WantEngine()

# Run a cycle
result = engine.run_cycle()
print(result)
```

### With Custom Configuration

```python
from want_engine_enhanced import WantEngine, WantEngineConfig

# Create custom config
config = WantEngineConfig(
    enable_openclaw_call=True,
    openclaw_cli_path="/usr/local/bin/openclaw",
    energy_warning_line=30,
    log_level="DEBUG",
    log_file="~/.wantengine.log"
)

# Save config for future use
config.to_file("~/.wantengine_config.json")

# Load config from file
config = WantEngineConfig.from_file("~/.wantengine_config.json")
engine = WantEngine(config)
```

### Configuration File

Create `~/.wantengine_config.json`:

```json
{
  "speed_factor": 10,
  "enable_openclaw_call": false,
  "openclaw_cli_path": "openclaw",
  "boredom_threshold": 60,
  "curiosity_threshold": 60,
  "energy_warning_line": 25,
  "energy_recovery_line": 60,
  "energy_safe_line": 40,
  "energy_healthy_line": 70,
  "fatigue_growth_per_tick": 1,
  "fatigue_warning_line": 10,
  "fatigue_critical_line": 20,
  "consecutive_low_energy_limit": 15,
  "force_rest_recovery_line": 80,
  "max_history": 8,
  "exploration_chance": 0.2,
  "log_level": "INFO",
  "log_file": "~/.wantengine.log"
}
```

## API Reference

### WantEngine

Main engine class for task generation and execution.

#### Methods

- `check_environment()`: Check Python version and OpenClaw availability
- `update_state()`: Update psychological state (boredom, curiosity, fatigue)
- `generate_task()`: Generate a task based on current state
- `execute_task(task)`: Execute a task via OpenClaw CLI
- `rest(deep=False)`: Enter rest mode to recover energy
- `get_status()`: Get current engine status
- `run_cycle()`: Run one complete cycle

### WantEngineConfig

Configuration dataclass.

#### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_openclaw_call` | bool | false | Enable OpenClaw CLI execution |
| `openclaw_cli_path` | str | "openclaw" | Path to OpenClaw CLI |
| `energy_warning_line` | int | 25 | Energy threshold for warnings |
| `boredom_threshold` | int | 60 | Boredom threshold for task switching |
| `curiosity_threshold` | int | 60 | Curiosity threshold for exploration |
| `log_level` | str | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `log_file` | str | null | Log file path (null for console only) |

## Domain Library

The engine includes predefined domains:

- **sports**: running, yoga, fitness, swimming, etc.
- **food**: cooking, baking, coffee making, etc.
- **art**: drawing, design, handicrafts, etc.
- **media**: photography, video editing, music, etc.
- **tech**: programming, AI, open-source, etc.

## Task Types

- **hobby**: Interest-based activities
- **skill**: Skill development tasks
- **knowledge**: Learning and research
- **content**: Content creation
- **project**: Project-based tasks

## State Management

### Energy System

- Energy decreases with task execution
- Rest recovers energy
- Force rest when energy is critically low

### Fatigue System

- Fatigue accumulates over time
- Rest reduces fatigue
- High fatigue affects task quality

### Boredom & Curiosity

- Boredom increases with repetitive tasks
- Curiosity drives exploration
- Both affect domain/task selection

## Examples

### Running Continuous Cycles

```python
import time
from want_engine_enhanced import WantEngine

engine = WantEngine()

while True:
    result = engine.run_cycle()
    
    if result['task'] is None:
        print("Resting...")
        engine.rest(deep=True)
    else:
        print(f"Task: {result['task']['description']}")
    
    time.sleep(60)  # Wait 1 minute between cycles
```

### Custom Domain

```python
from want_engine_enhanced import WantEngine, DOMAIN_LIBRARY

# Add custom domain
DOMAIN_LIBRARY["gaming"] = {
    "hobby": ["RPG", "strategy", "puzzle", "action"],
    "skill": ["game design", "level editing", "modding"],
    "knowledge": ["game theory", "mechanics design"],
    "content": ["reviews", "tutorials", "streams"]
}

engine = WantEngine()
```

## Logging

Logs are written to console by default. Enable file logging:

```python
config = WantEngineConfig(
    log_level="DEBUG",
    log_file="~/.wantengine.log"
)
```

## License

MIT License

## Contributing

Pull requests welcome! Please ensure:
- Code follows PEP 8
- Type hints are included
- Tests pass (if applicable)
