nohup timeout 7h python annotate_amazon.py \
    --output_path data/amazon_annotated.jsonl \
    --model Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled \
    --api_base http://localhost:8000/v1 \
    --num_examples 50000 \
    --batch_size 16 \
    --max_tokens 2048 \
    --temperature 0.7 \
    --split train \
    --skip 0 \
    --seed 42 &> amazon_annotated.log &
echo "amazon-annotate PID: $!"
