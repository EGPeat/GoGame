#!/bin/bash

# Run tests with coverage
coverage run -m pytest

# Generate HTML coverage report
coverage html

# Navigate to the HTML coverage directory
cd htmlcov/

# Open the coverage report in Firefox
firefox index.html
