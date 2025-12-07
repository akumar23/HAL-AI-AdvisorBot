#!/bin/bash
# Build Tailwind CSS
# Requires: Tailwind CLI standalone binary
# Download from: https://github.com/tailwindlabs/tailwindcss/releases

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if tailwindcss binary exists
if ! command -v tailwindcss &> /dev/null; then
    echo "Tailwind CLI not found. Checking local binary..."
    if [ -f "./tailwindcss" ]; then
        TAILWIND="./tailwindcss"
    else
        echo ""
        echo "Please install Tailwind CLI standalone:"
        echo ""
        echo "  macOS (Apple Silicon):"
        echo "    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64"
        echo "    chmod +x tailwindcss-macos-arm64 && mv tailwindcss-macos-arm64 tailwindcss"
        echo ""
        echo "  macOS (Intel):"
        echo "    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64"
        echo "    chmod +x tailwindcss-macos-x64 && mv tailwindcss-macos-x64 tailwindcss"
        echo ""
        echo "  Linux:"
        echo "    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64"
        echo "    chmod +x tailwindcss-linux-x64 && mv tailwindcss-linux-x64 tailwindcss"
        echo ""
        exit 1
    fi
else
    TAILWIND="tailwindcss"
fi

MODE="${1:-build}"

case "$MODE" in
    build)
        echo "Building Tailwind CSS (production)..."
        $TAILWIND -i static/css/input.css -o static/css/output.css --minify
        echo "Done! Output: static/css/output.css"
        ;;
    watch)
        echo "Watching for changes..."
        $TAILWIND -i static/css/input.css -o static/css/output.css --watch
        ;;
    *)
        echo "Usage: $0 [build|watch]"
        echo "  build  - Build minified CSS for production (default)"
        echo "  watch  - Watch for changes and rebuild"
        exit 1
        ;;
esac
