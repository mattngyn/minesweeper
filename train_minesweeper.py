#!/usr/bin/env python3
"""
GRPO training script for Minesweeper environment with vLLM support.

To run on 2 GPUs (recommended):
1. GPU 0 for inference: CUDA_VISIBLE_DEVICES=0 vllm serve meta-llama/Llama-3.2-1B-Instruct --dtype auto --api-key token-abc123 --port 8000
2. GPU 1 for training: CUDA_VISIBLE_DEVICES=1 python train_minesweeper.py
"""

import os
import verifiers as vf

from datasets import load_from_disk, Dataset as VerifiersDataset

def main():
    env = vf.load_environment(
        env_id="hud-vf-gym",
        taskset="kizro/minesweeper_taskset",  
        config_path="./configs/minesweeper.yaml",
        num_tasks=4,
    )
    
    # 2. Load model and tokenizer
    model_name = "Qwen/Qwen2.5-3B-Instruct"
    model, tokenizer = vf.get_model_and_tokenizer(model_name)
    
    # 3. Configure training using grpo_defaults
    args = vf.grpo_defaults(
        run_name="minesweeper-grpo"
    )

    args.per_device_train_batch_size = 4
    args.gradient_accumulation_steps = 8
    args.max_steps = 100
    args.save_strategy = "steps"
    args.save_steps = 10
    args.logging_steps = 1
    
    args.mask_env_responses = True
    # 4. Train
    trainer = vf.GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        env=env,
        args=args,
    )
    
    # Start training
    print("Starting GRPO training for Minesweeper with vLLM...")
    print(f"Model: {model_name}")
    
    trainer.train()
    
    # Save the final model
    trainer.save_model()
    print(f"\nTraining completed! Model saved to {args.output_dir}")

if __name__ == "__main__":
    main()
