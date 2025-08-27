# Minesweeper GRPO Training Setup

This directory contains everything needed to train a model on Minesweeper using HUD and Verifiers GRPO.

## What's Been Set Up

1. **Dependencies**: Installed `hud-vf-gym`, `verifiers[train]`, and `flash-attn`
2. **Config File**: `configs/minesweeper.yaml` - Defines the environment, tools, and prompts
3. **Training Scripts**:
   - `train_minesweeper.py` - Full training with vLLM (requires 2 GPUs)
   - `train_minesweeper_simple.py` - Simple training without vLLM (single GPU)
4. **Taskset**: Created 30 minesweeper tasks with varying difficulty (5x5, 7x7, 9x9 boards)
5. **Helper Scripts**:
   - `create_taskset.py` - Generates the training dataset
   - `test_setup.py` - Verifies the environment is working

## Running Training

### Simple Training (Single GPU)

```bash
# Set environment variables (optional)
export OPENAI_API_KEY="your-key"  # For OpenAI models
export HUD_API_KEY="your-key"     # For telemetry (optional)

# Run training
uv run python train_minesweeper_simple.py
```

This will:
- Train for 1 epoch with 50 max steps (for testing)
- Use Llama-3.2-1B-Instruct model
- Save the model to `./minesweeper_grpo_model_test/`

### Full Training with vLLM (2 GPUs)

```bash
# Terminal 1: Start vLLM server on GPU 0
CUDA_VISIBLE_DEVICES=0 vllm serve meta-llama/Llama-3.2-1B-Instruct \
  --dtype auto --api-key token-abc123 --port 8000

# Terminal 2: Run training on GPU 1
CUDA_VISIBLE_DEVICES=1 uv run python train_minesweeper.py
```

## Configuration

The training uses:
- **Model**: meta-llama/Llama-3.2-1B-Instruct
- **GRPO Alpha**: 0.5 (group relative weight)
- **Learning Rate**: 5e-6
- **Batch Size**: 1-4 (depending on script)

Edit the training scripts to adjust these parameters.

## Taskset Structure

The taskset contains:
- 10 easy tasks (5x5 board, 3 mines)
- 10 medium tasks (7x7 board, 7 mines)  
- 10 hard tasks (9x9 board, 10 mines)

Each task has a different random seed for board generation.

## Monitoring Training

Training progress will be logged to the console. The trainer will show:
- Loss values
- Reward scores from the minesweeper environment
- Generation samples

## Next Steps

After training completes:
1. The model will be saved to the output directory
2. You can load and use it for inference
3. Consider pushing to HuggingFace Hub for sharing

## Troubleshooting

- If you see "API key is required" warnings, these are for telemetry and can be ignored
- For CUDA out of memory errors, reduce `per_device_train_batch_size` in the config
- Make sure the minesweeper Docker image is built (`docker build -t minesweeper:dev .`)
