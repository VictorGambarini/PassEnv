#!/bin/bash
set -e

echo "Setting up PassEnv development environment..."

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Not in a virtual environment. Consider creating one:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo ""
fi

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev]"

# Check if pass is installed
if ! command -v pass &> /dev/null; then
    echo "Warning: 'pass' command not found."
    echo "Please install pass for full functionality:"
    echo "  # Ubuntu/Debian:"
    echo "  sudo apt install pass"
    echo "  # macOS:"
    echo "  brew install pass"
    echo "  # Arch Linux:"
    echo "  sudo pacman -S pass"
    echo ""
fi

# Check if pass is initialized
if command -v pass &> /dev/null; then
    if ! pass ls &> /dev/null; then
        echo "Warning: Pass store not initialized."
        echo "Initialize with: pass init <your-gpg-key-id>"
        echo ""
    fi
fi

# Set up pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "Setting up pre-commit hooks..."
    pre-commit install
fi

# Run initial tests
echo "Running initial test suite..."
pytest

echo "Development environment setup complete!"
echo ""
echo "Available make commands:"
make help