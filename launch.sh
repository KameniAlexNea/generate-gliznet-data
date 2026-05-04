nohup timeout 7h python main.py \
    --output_path data/wikipedia_synthetic.jsonl \
    --model Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled \
    --api_base http://localhost:8000/v1 \
    --num_examples 64000 \
    --batch_size 16 \
    --max_tokens 4096 \
    --temperature 0.9 \
    --skip 47500 \
    --seed 164 \
    --shuffle_buffer 50000 &> wikipedia_synthetic.log &
echo "ds-gen PID: $!"