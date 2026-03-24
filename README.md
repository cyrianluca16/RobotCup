# Sudriabotik - Autonomous Robot Simulator

This project is a mobile robot simulator developed in Python using **Pygame**. It visualizes robot movements on a standard competition table (3000x2000mm) and provides a sandbox to test real-time obstacle avoidance algorithms.

## Key Features
- **Realistic Physics**: Implementation of trapezoidal velocity profiles (smooth acceleration and deceleration).
- **Smart Obstacle Avoidance**: Dynamic braking system based on distance and field of view (FOV) relative to an opponent.
- **Command Interpreter**: Support for custom strategy files (`.txt`) using the `fdd.function_name` format.
- **Strategy Recording**: Tool to capture real-time mouse clicks and export them as valid robot trajectories.
- **Interactive UI**: Sidebar for real-time tuning of motion parameters (speed, acceleration, turning rates).

## Installation

1. Ensure you have Python 3.x installed.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Use
Launch the main simulation environment:
```bash
python main.py
```
-**Manual Navigation**: With recording OFF, click anywhere on the field to make the robot reach that point.
-**Strategy Execution**: Load a .txt file via the sidebar and press Start Strategy.
-**Recording**: Enable "Recording Mode", click points on the field, and save your custom path.

## Project Architecture
-**main.py**: Main application controller and event loop.
-**robot.py**: Core logic (FSM, physics, and collision avoidance).
-**setup.py**: Environment configuration and asset management.
-**read_strat_file.py**: Parser for the strategy command system.
-**side_bare.py**: UI components and input handling.
