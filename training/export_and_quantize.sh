#!/bin/bash
# ==============================================================================
# ATLAS-3B: Weight Merging & GGUF Quantization Script
# ==============================================================================

set -e

MERGED_DIR="atlas_qwen_3b_merged"
FP16_GGUF="atlas_qwen_3b_f16.gguf"
OUTPUT_GGUF="atlas-qwen-3b-q4_k_m.gguf"
LLAMA_DIR="$HOME/llama.cpp"

if [ ! -d "$LLAMA_DIR" ] && [ -d "llama.cpp" ]; then
    LLAMA_DIR="llama.cpp"
fi

QUANTIZE_BIN="$LLAMA_DIR/build/bin/llama-quantize"
if [ ! -f "$QUANTIZE_BIN" ]; then
    QUANTIZE_BIN="$LLAMA_DIR/llama-quantize"
fi

echo "[*] Step 1: Converting merged PyTorch weights to FP16 GGUF..."
python3 "$LLAMA_DIR/convert_hf_to_gguf.py" "$MERGED_DIR" --outfile "$FP16_GGUF" --outtype f16

echo "[*] Step 2: Quantizing to 4-bit Q4_K_M..."
"$QUANTIZE_BIN" "$FP16_GGUF" "$OUTPUT_GGUF" Q4_K_M

echo "[*] Step 3: Removing temporary FP16 GGUF..."
rm -f "$FP16_GGUF"

echo "[+] SUCCESS: Quantized model ready at $OUTPUT_GGUF"
ls -lh "$OUTPUT_GGUF"
