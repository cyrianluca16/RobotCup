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
