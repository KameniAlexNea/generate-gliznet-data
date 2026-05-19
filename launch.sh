nohup timeout 4h python main.py \
    --output_path data/wikipedia_synthetic.jsonl \
    --model gliznet-data \
    --api_base http://localhost:8000/v1 \
    --free-labels \
    --num_examples 100000 \
    --batch_size 48 \
    --max_tokens 4096 \
    --temperature 0.7 \
    --skip 1050000 \
    --seed 164 \
    --shuffle_buffer 50000 &> wikipedia_synthetic.log &
echo "ds-gen PID: $!"