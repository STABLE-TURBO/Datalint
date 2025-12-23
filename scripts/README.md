# Diagram Generation Scripts

This directory contains scripts for automatically generating UML diagrams from the datalint codebase and updating the README.md documentation.

## Files

- `generate_diagrams.py` - Main Python script that analyzes the codebase and generates diagrams
- `generate_diagrams.bat` - Windows batch script wrapper for easy execution
- `README.md` - This documentation file

## Generated Diagrams

The system generates comprehensive UML diagrams that are automatically embedded in the README:

### Structural Diagrams (Static Views)
- **Component Diagram**: Shows high-level software components and their relationships
- **Deployment Diagram**: Illustrates how the system is deployed
- **Class Diagram**: Displays class hierarchies (requires Graphviz for PNG generation)

### Behavioral Diagrams (Dynamic Flow)
- **Sequence Diagram**: Shows the validation workflow sequence
- **Activity Diagram**: Displays the validation pipeline activities
- **Use Case Diagram**: Illustrates user interactions with the system

## Usage

### Automatic (Recommended)
The system runs automatically as a pre-commit hook when you commit changes to Python files in the `datalint/` directory.

### Manual Execution

#### On Windows:
```batch
scripts/generate_diagrams.bat
```

#### On Linux/Mac:
```bash
python scripts/generate_diagrams.py
```

## How It Works

1. **Code Analysis**: Uses Python AST to analyze classes, functions, and imports
2. **Diagram Generation**: Creates PlantUML files for each diagram type
3. **README Integration**: Embeds PlantUML code blocks directly in README.md
4. **Git Integration**: Pre-commit hooks ensure documentation stays current

## Dependencies

- Python 3.8+
- pylint (for pyreverse class diagrams)
- plantuml (optional, for PNG generation)
- graphviz (optional, for pyreverse PNG output)

## Git Hooks

The system includes both Unix shell scripts and Windows batch files for maximum compatibility:

- `.git/hooks/pre-commit` - Unix shell script
- `.git/hooks/pre-commit.bat` - Windows batch script

Git on Windows automatically prefers `.bat` files, ensuring reliable operation across platforms.
