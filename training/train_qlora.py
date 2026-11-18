#!/usr/bin/env python3
"""
ATLAS-3B QLoRA Fine-Tuning Pipeline
===================================
Fine-tunes Qwen 2.5 3B Instruct on structured tool-calling data using
Hugging Face PEFT / TRL and BitsAndBytes 4-bit NF4 quantization.
"""

import sys
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer

def train():
    model_name = "Qwen/Qwen2.5-3B-Instruct"
    dataset_name = "abxn4r/atlas-edge-tool-calling-10k"
    output_dir = "atlas_qwen_3b_lora"

    print(f"[*] Loading dataset: {dataset_name}...")
    dataset = load_dataset(dataset_name)

    print(f"[*] Initializing tokenizer for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("[*] Loading base model with 4-bit NF4 quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    print("[*] Configuring LoRA adapters...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=50,
        max_steps=1000,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy="steps",
        save_steps=250,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        peft_config=peft_config,
        max_seq_length=2048,
        args=training_args,
    )

    print("[*] Starting QLoRA training run...")
    trainer.train()
    print(f"[+] Training complete. Saving LoRA adapter to {output_dir}...")
    trainer.save_model(output_dir)

if __name__ == "__main__":
    train()
