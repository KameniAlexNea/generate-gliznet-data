#!/usr/bin/env bash
# Run this in a dedicated terminal / tmux pane.
# The server must be up before starting main.py.

MODEL="Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled"

nohup timeout 11h vllm serve "$MODEL" \
    --tensor-parallel-size 2 \
    --port 8000 \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --enable-prefix-caching &> vllm_serve.log &
echo "vllm PID: $!"
