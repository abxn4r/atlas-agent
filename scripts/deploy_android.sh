#!/bin/bash
# ==============================================================================
# ATLAS-3B: Automated Android (Termux) Deployment Script
# Targets: ARM64 Snapdragon / MediaTek / Exynos processors
# ==============================================================================

set -e

echo "=== [1/4] Updating Termux environment ==="
pkg update -y && pkg install -y git clang cmake wget tar libomp

WORK_DIR="$HOME/atlas-engine"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "=== [2/4] Downloading ATLAS-3B GGUF Model ==="
MODEL_FILE="atlas-qwen-3b-q4_k_m.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    wget -c "https://huggingface.co/abxn4r/Atlas-Qwen2.5-3B-Instruct-GGUF/resolve/main/atlas-qwen-3b-q4_k_m.gguf" -O "$MODEL_FILE"
else
    echo "Model file already exists. Skipping download."
fi

echo "=== [3/4] Setting up llama.cpp runtime ==="
if [ ! -f "llama-server" ]; then
    echo "Cloning and building llama.cpp..."
    git clone --depth 1 https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    mkdir build && cd build
    cmake .. -DGGML_OPENMP=OFF
    cmake --build . --config Release -j 4
    cp bin/llama-server "$WORK_DIR/"
    cd "$WORK_DIR"
fi

echo "=== [4/4] Launching ATLAS OpenAI-Compatible REST Server ==="
echo "Access endpoint at: http://127.0.0.1:8088"
./llama-server \
    -m "$MODEL_FILE" \
    --port 8088 \
    --ctx-size 2048 \
    --threads 4 \
    --cont-batching
