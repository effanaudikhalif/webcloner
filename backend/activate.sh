#!/bin/bash
# Script to activate the backend virtual environment

echo "Activating backend virtual environment..."
source backend/venv/bin/activate
echo "Virtual environment activated! Python version:"
python --version
echo ""
echo "To deactivate, run: deactivate" 