#!/usr/bin/env bash
# Run this in a dedicated terminal / tmux pane.
# The server must be up before starting main.py.

MODEL="google/gemma-4-E4B-it"

nohup timeout 16h vllm serve "$MODEL" \
    --served-model-name gliznet-data \
    --tensor-parallel-size 2 \
    --port 8000 \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --enable-prefix-caching &> vllm_serve.log &
echo "vllm PID: $!"
