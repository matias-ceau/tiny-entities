#!/bin/bash

# Create directory structure
mkdir -p src/{world,creatures,emergence,simulation}
mkdir -p config examples tests
mkdir -p .github/workflows

# Create __init__.py files
touch src/__init__.py
touch src/world/__init__.py
touch src/creatures/__init__.py
touch src/emergence/__init__.py
touch src/simulation/__init__.py
touch config/__init__.py
touch tests/__init__.py

echo "Directory structure created!"