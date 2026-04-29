#!/bin/bash
# Coverage reporting script for SABAC project

export PYTHONPATH=.

# Run tests with coverage
echo "Running tests with coverage..."
coverage run -m pytest ./tests

# Generate reports
echo "Generating coverage report..."
coverage report -m

# Optional: Generate XML for CI upload
coverage xml

echo "Coverage report generated."
echo "  Text report: Above"
echo "  XML report: coverage.xml"
