nohup timeout 10h python annotate_amazon.py \
    --output_path data/amazon_annotated_openrouter.jsonl \
    --model qwen/qwen3.6-flash \
    --num_examples 50000 \
    --batch_size 2 \
    --concurrency 1 \
    --max_tokens 2048 \
    --temperature 0.7 \
    --split train \
    --skip 0 \
    --use_openrouter &> amazon_annotated_openrouter.log &
echo "amazon-annotate-openrouter PID: $!"
