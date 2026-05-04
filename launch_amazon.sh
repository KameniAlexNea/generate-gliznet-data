nohup timeout 10h python annotate_amazon.py \
    --output_path data/amazon_annotated.jsonl \
    --model deepseek-v4-pro \
    --api_base https://api.deepseek.com \
    --num_examples 50000 \
    --batch_size 16 \
    --max_tokens 2048 \
    --temperature 0.7 \
    --split train \
    --skip 0 &> amazon_annotated.log &
echo "amazon-annotate PID: $!"
