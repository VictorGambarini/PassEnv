#!/bin/bash
set -e

# Release script for PassEnv
# Usage: ./scripts/release.sh <version>

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.1"
    exit 1
fi

VERSION=$1

echo "Preparing release $VERSION..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: Must be on main branch to release. Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo "Error: Working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Update version in pyproject.toml
sed -i "1s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update version in __init__.py
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/passenv/__init__.py

# Run tests
echo "Running tests..."
make test

# Run linting
echo "Running linting..."
make lint

# Run type checking
echo "Running type checking..."
make type-check

# Build package
echo "Building package..."
make build

# Check package
echo "Checking package..."
twine check dist/*

# Commit version bump
git add pyproject.toml src/passenv/__init__.py
git commit -m "Bump version to $VERSION"

# Create tag
git tag -a "v$VERSION" -m "Release version $VERSION"

echo "Release $VERSION prepared successfully!"
echo "To complete the release:"
echo "1. Push the changes: git push origin main"
echo "2. Push the tag: git push origin v$VERSION"
echo "3. The GitHub Actions will automatically publish to PyPI"