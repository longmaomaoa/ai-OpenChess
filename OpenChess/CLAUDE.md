# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese Chess (Xiangqi) Intelligent Assistant that combines computer vision and AI technology to provide real-time chess game analysis and move recommendations. The system identifies pieces, monitors opponent moves (top area), and provides strategic suggestions for the player (bottom area).

## Core Architecture

### Main Components

#### Core Modules (src/core/)
- **scanner/advanced_chess_scanner.py** - Enhanced scanner with template matching and color recognition
- **scanner/base_scanner.py** - Abstract base class for all scanners
- **ai_engine/chess_ai_assistant.py** - Core AI assistant for move analysis and recommendations
- **ai_engine/move_detector.py** - Move detection and chess rule validation engine
- **ai_engine/position_evaluator.py** - Multi-dimensional position evaluation and win rate calculation
- **vision/region_selector.py** - Interactive region selection tool for custom scanning areas
- **vision/image_utils.py** - Computer vision utilities and image processing functions

#### User Interface (src/ui/)
- **main_gui.py** - Unified GUI entry point
- **tkinter_gui/gui_chess_scanner.py** - Main GUI application with integrated AI assistant features

#### Utilities (src/utils/)
- **config.py** - Centralized configuration management
- **constants.py** - Project constants and definitions

#### Scripts (scripts/)
- **install_requirements.py** - Automated dependency installation and environment setup
- **run_chess_scanner.bat** - Enhanced Windows batch launcher

#### Tests (tests/)
- **test_chess_ai.py** - Comprehensive test suite for AI functionality
- **test_region_selection.py** - Multi-board region selection testing suite
- **simple_test.py** - Basic functionality tests

### Technical Stack

- **OpenCV** - Core computer vision library for image processing and template matching
- **PyAutoGUI** - Screen capture and automation
- **Pytesseract** - OCR text recognition for Chinese characters on chess pieces
- **NumPy** - Numerical computations for image arrays and AI calculations
- **Tkinter** - GUI framework for the visual interface with AI panels
- **PIL/Pillow** - Image processing utilities
- **AI Engine** - Custom chess analysis engine with position evaluation

### Chess Analysis System

The system uses a comprehensive multi-layered approach:

#### Visual Recognition
1. **Template Matching** - Compares chess pieces against stored templates
2. **OCR Recognition** - Identifies Chinese characters on pieces (帅/将, 仕/士, etc.)
3. **Color Detection** - HSV color space analysis to distinguish red/black pieces
4. **Board Detection** - Automatic chess board boundary detection with manual calibration fallback
5. **Custom Region Selection** - Interactive drag-to-select scanning areas for multiple boards

#### AI Analysis Engine  
1. **Move Detection** - Tracks board state changes and identifies opponent moves
2. **Position Evaluation** - Multi-dimensional analysis including material, position, king safety
3. **Move Generation** - Generates all legal moves with rule validation
4. **Win Rate Calculation** - Real-time probability assessment using evaluation functions
5. **Strategic Recommendations** - Provides best moves with reasoning and confidence scores

#### Region Selection Features
- **Interactive Selection** - Full-screen overlay with drag-to-select functionality
- **Multi-Board Support** - Save and switch between multiple board regions
- **Region Management** - Save, load, preview, and delete custom scanning areas
- **Configuration Persistence** - Automatic saving of region configurations to JSON files

## Development Commands

### Environment Setup
```bash
# Install all dependencies
python install_requirements.py

# Manual installation
pip install -r requirements.txt
```

### Running the Application

#### Quick Start
```bash
# Windows users - Double-click or run:
start.bat

# Or use the enhanced launcher:
scripts/run_chess_scanner.bat

# Direct Python execution:
python main.py
```

#### Advanced Usage
```bash
# GUI version (default)
python main.py --mode gui

# Console version
python main.py --mode console

# Region selection tool
python main.py --mode region-selector

# Debug mode
python main.py --debug

# Specify log level
python main.py --log-level DEBUG
```

### Region Selection Usage
```bash
# Test region selection functionality
python test_region_selection.py

# Use region selector programmatically
from region_selector import RegionSelector
selector = RegionSelector()
region = selector.select_region()  # Returns (x, y, width, height)
```

### Testing and Validation
```bash
# Test Python installation and dependencies
python -c "import cv2, pyautogui, pytesseract; print('Dependencies OK')"

# Validate Tesseract OCR installation
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## Configuration

### Tesseract OCR Setup
- Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki
- Ensure Chinese language pack is installed
- Update tesseract path in scanner files if needed:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```

### Chess Piece Definitions
The scanners recognize these Chinese chess pieces:
- Red pieces: 帅(King), 仕(Advisor), 相(Elephant), 马(Horse), 车(Chariot), 炮(Cannon), 兵(Pawn)
- Black pieces: 将(King), 士(Advisor), 象(Elephant), 马(Horse), 车(Chariot), 炮(Cannon), 卒(Pawn)

### Board Calibration
All scanners support:
- Automatic board detection using edge detection and contour analysis
- Manual calibration by clicking board corners
- Template creation for custom chess sets
- Real-time scanning with configurable intervals

## Code Organization

### Scanner Classes
- `ChineseChessScanner` (basic) - Core scanning functionality
- `AdvancedChessScanner` - Enhanced with template matching and color analysis
- `ChessScannerGUI` - Tkinter-based visual interface

### Key Methods
- `scan_board()` - Main scanning logic
- `detect_board_area()` - Chess board boundary detection
- `identify_piece()` - Multi-modal piece recognition
- `check_game_state()` - Win/loss condition evaluation
- `calibrate_board()` - Manual position calibration

### Image Processing Pipeline
1. Screen capture using PyAutoGUI
2. Preprocessing (grayscale, edge detection, binary threshold)
3. Board area extraction and grid mapping
4. Individual piece extraction and analysis
5. Multi-algorithm fusion for piece identification

## Development Notes

### Performance Considerations
- Scanning interval is configurable (default: 2 seconds)
- Board area restriction to optimize processing
- Template caching for faster matching
- Incremental updates to reduce computation

### Common Workflows
1. **First-time setup**: Run install script → calibrate board → create templates
2. **Single board scanning**: Launch scanner → verify calibration → start monitoring
3. **Multi-board setup**: Launch GUI → select custom regions → save configurations
4. **Region management**: Load saved regions → preview areas → switch between boards
5. **Troubleshooting**: Check dependencies → recalibrate board → adjust parameters

### Debugging
- Enable detailed logging in scanner classes
- Save debug images using `cv2.imwrite()`
- Use GUI version for visual feedback during development
- Template matching confidence thresholds can be adjusted for different chess sets
- Region selection: Check `scan_regions.json` for saved configurations
- Multi-board issues: Use test script to validate region boundaries
- Preview functionality helps verify correct area selection

## AI Team Configuration (autogenerated by team-configurator, 2025-01-03)

**Important: YOU MUST USE subagents when available for the task.**

### Detected Technology Stack

- **Backend Framework**: Pure Python with custom chess engine
- **Computer Vision**: OpenCV 4.5+ for image processing and template matching
- **GUI Framework**: Tkinter for native desktop interface
- **OCR Engine**: Pytesseract for Chinese character recognition
- **Image Processing**: PIL/Pillow for advanced image manipulation
- **Automation**: PyAutoGUI for screen capture and interaction
- **Numerical Computing**: NumPy for array operations and calculations
- **AI/ML**: Custom chess analysis algorithms with position evaluation
- **Configuration**: Python config files and JSON for persistence
- **Testing**: Custom test suites for AI and region selection functionality

### Specialist Team Assignments

| Task | Agent | Notes |
|------|-------|-------|
| Computer Vision & Image Processing | `computer-vision-specialist` | OpenCV, template matching, OCR optimization |
| GUI Development & User Interface | `gui-developer` | Tkinter enhancements, UX improvements |
| AI Algorithm Development | `ai-ml-engineer` | Chess engine optimization, move evaluation |
| Performance & Optimization | `performance-optimizer` | Image processing speed, memory usage |
| Code Quality & Review | `code-reviewer` | Code structure, best practices, refactoring |
| Python Architecture & Design | `python-architect` | Module organization, design patterns |
| Testing & Quality Assurance | `test-engineer` | Unit tests, integration tests, edge cases |
| Documentation & User Guides | `technical-writer` | API docs, user manuals, setup guides |
| Configuration & Deployment | `devops-specialist` | Environment setup, dependency management |
| Game Logic & Chess Rules | `algorithm-specialist` | Chess rule validation, move generation |
| Desktop Application Development | `desktop-app-developer` | Cross-platform compatibility, packaging |
| Data Processing & Analytics | `data-engineer` | Position analysis, statistics, logging |

