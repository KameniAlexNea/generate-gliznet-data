nohup timeout 15h python annotate_amazon.py \
    --output_path data/amazon_annotated.jsonl \
    --model gliznet-data \
    --api_base http://localhost:8000/v1 \
    --num_examples 50000 \
    --batch_size 32 \
    --max_tokens 2048 \
    --temperature 0.7 \
    --split train \
    --skip 3000 &> amazon_annotated.log &
echo "amazon-annotate PID: $!"
