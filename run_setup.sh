#!/bin/bash

# Make scripts executable
chmod +x setup_structure.sh
chmod +x setup_uv.sh

# Run structure setup
./setup_structure.sh

echo "Project structure created! Now run ./setup_uv.sh to set up the environment."