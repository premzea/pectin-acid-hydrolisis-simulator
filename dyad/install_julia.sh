#!/usr/bin/env bash
set -euo pipefail

echo "======================================================"
echo "Installing Juliaup & Julia (LTS / 1.10+) in WSL"
echo "======================================================"

if command -v julia &> /dev/null; then
    echo "Julia is already installed: $(julia --version)"
    exit 0
fi

if ! command -v juliaup &> /dev/null; then
    echo "Installing juliaup..."
    curl -fsSL https://install.julialang.org | sh -s -- -y
    # Source environment
    export PATH="$HOME/.juliaup/bin:$PATH"
fi

echo "Julia installation complete: $(julia --version)"
echo "To initialize the PectinDyad environment, run:"
echo "  julia --project=dyad -e 'using Pkg; Pkg.instantiate(); Pkg.test()'"
