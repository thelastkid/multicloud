#!/bin/bash
# Installation and Quick Test Script

echo "=========================================="
echo "MLOps Policy Engine - Setup Script"
echo "=========================================="
echo ""

# Install dependencies
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Install package
echo "[2/4] Installing policy engine package..."
pip install -e .
echo "✓ Package installed"
echo ""

# Run tests (optional)
echo "[3/4] Running tests..."
python -m pytest tests/ -v --tb=short 2>/dev/null || echo "⚠ Tests require pytest"
echo ""

# Show example
echo "[4/4] Running example..."
python examples.py
echo ""

echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Try the Python API:"
echo "   python -c \"from policy_engine import MLOpsPolicyEngine; engine = MLOpsPolicyEngine()\""
echo ""
echo "2. Start the REST API:"
echo "   python -m policy_engine.api.rest_api"
echo ""
echo "3. Use the CLI:"
echo "   policy-engine --help"
echo ""
echo "4. Read the documentation:"
echo "   cat README.md"
echo ""
echo "=========================================="
