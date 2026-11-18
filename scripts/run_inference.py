#!/usr/bin/env python3
"""
ATLAS-3B Local Inference & Tool Dispatcher
==========================================
Demonstrates running local inference using llama-cpp-python
and parsing structured JSON tool calls.
"""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Run ATLAS-3B Inference")
    parser.add_argument("--model", type=str, default="atlas-qwen-3b-q4_k_m.gguf", help="Path to GGUF model")
    parser.add_argument("--prompt", type=str, default="Atlas, wake up my PC and start Spotify", help="User prompt")
    parser.add_argument("--threads", type=int, default=4, help="CPU threads to use")
    args = parser.parse_args()

    try:
        from llama_cpp import Llama
    except ImportError:
        print("[!] Error: llama-cpp-python is not installed. Run: pip install llama-cpp-python")
        sys.exit(1)

    print(f"[*] Initializing ATLAS engine with {args.model}...")
    llm = Llama(
        model_path=args.model,
        n_ctx=2048,
        n_threads=args.threads,
        temperature=0.3,
        verbose=False
    )

    system_message = (
        "You are ATLAS, an ambient personal AI operating system. "
        "Reason step-by-step and output structured JSON tool calls when an action is required."
    )

    formatted_input = f"""<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{args.prompt}<|im_end|>
<|im_start|>assistant
"""

    print(f"[*] Query: {args.prompt}")
    print("[*] Generating response...")
    result = llm(formatted_input, max_tokens=150, stop=["<|im_end|>"])
    raw_text = result["choices"][0]["text"].strip()

    print("\n" + "=" * 50)
    print("RAW MODEL OUTPUT:")
    print("=" * 50)
    print(raw_text)

    try:
        parsed_action = json.loads(raw_text)
        print("\n" + "=" * 50)
        print("PARSED STRUCTURED ACTION:")
        print("=" * 50)
        print(f"Thought:   {parsed_action.get('thought')}")
        print(f"Tool:      {parsed_action.get('tool')}")
        print(f"Arguments: {json.dumps(parsed_action.get('arguments', {}), indent=2)}")
    except json.JSONDecodeError:
        print("\n[!] Output did not contain valid JSON.")

if __name__ == "__main__":
    main()
