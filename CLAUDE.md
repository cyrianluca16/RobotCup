# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a robotics simulation application built with pygame for visualizing and controlling robot movement on a 3000x2000mm playing field. The application provides both manual control and automated strategy execution capabilities.

## Core Architecture

The application follows a modular structure:

- **main.py** - Main application loop handling pygame events, UI interactions, and coordinating between modules
- **robot.py** - Core Robot class with movement physics (trapezoidal velocity profiles), coordinate transformations, and control functions (avancer, reculer, orienter, cibler, rejoindre)
- **setup.py** - Initialization and configuration (screen setup, image loading, theme management)
- **side_bare.py** - UI sidebar with robot parameter controls, strategy file selection, and recording functionality
- **read_strat_file.py** - Strategy file parser for executing FDD commands from text files
- **rec_strat.py** - Recording functionality to save robot movements as FDD commands

## Key Components

### Robot Control System
- Implements trapezoidal velocity profiles for smooth acceleration/deceleration
- Coordinate system: 3000x2000mm field mapped to 900x600px display
- Movement functions: avancer(distance, ratio_vitesse), reculer(), orienter(angle), cibler(x,y), rejoindre(x,y,face,speed)
- Real-time position tracking and graphical updates

### Strategy System
- FDD command format: `fdd.function_name("arg1", "arg2", ...)`
- Supports sequential execution of movement commands from text files
- Recording mode captures mouse clicks as rejoindre commands

### UI System
- Sidebar with parameter entry fields for position (x,y,o) and motion parameters (max_speed, acceleration, turning_speed)
- Real-time mouse coordinate display in mm
- Strategy file selection and execution controls

## Common Commands

### Running the Application
```bash
python main.py
```

### Building Executable
```bash
pyinstaller main.spec
```

### Strategy File Format
Strategy files (*.txt) contain FDD commands:
```
fdd.rejoindre("1500", "1000", "0", "100", ser)
fdd.orienter("90", "100", ser)
fdd.avancer("500", "100", ser)
```

## Configuration

- Field dimensions: 3000x2000mm (TABLE_WIDTH_MM, TABLE_HEIGHT_MM in setup.py)
- Robot dimensions: 320x290mm (ROBOT_WIDTH_MM, ROBOT_HEIGHT_MM in robot.py)
- Display: 1200x600px with 900x600px field area
- Default strategy file: test_V2.txt
- Default recording file: rec.txt

## File Structure Notes

- Strategy files are stored as .txt files in the root directory
- botikplaymat.jpg serves as the field background image
- theme.json is auto-generated for pygame_gui styling
- build/ directory contains PyInstaller build artifacts