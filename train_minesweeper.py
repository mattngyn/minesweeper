#!/usr/bin/env python3

"""
Training Script for Minesweeper (2 GPUs)

Terminal 1 - Start vLLM server:

  CUDA_VISIBLE_DEVICES=0 vf-vllm \
      --model Qwen/Qwen2.5-3B-Instruct \
      --enforce-eager \
      --disable-log-requests

  Terminal 2 - Run training:

  CUDA_VISIBLE_DEVICES=1 uv run train_minesweeper.py

rm -rf ~/.triton ~/.cache/torch/inductor ~/.cache/torch/extension_cache
"""
import verifiers as vf

def main():
    env = vf.load_environment(
        env_id="hud-vf-gym",
        taskset="kizro/minesweeper_taskset",  
        config_path="./configs/minesweeper.yaml",
    )
    
    # 2. Load model and tokenizer
    model_name = "Qwen/Qwen2.5-3B-Instruct"
    model, tokenizer = vf.get_model_and_tokenizer(model_name)
    
    # 3. Configure training using grpo_defaults
    args = vf.grpo_defaults(
        run_name="minesweeper-grpo"
    )

    args.max_steps = 100
    args.save_strategy = "steps"
    args.save_steps = 10
    args.logging_steps = 1
    args.mask_env_responses = True
    
    args.per_device_train_batch_size = 5
    args.num_generations = 5
    args.gradient_accumulation_steps = 1

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
