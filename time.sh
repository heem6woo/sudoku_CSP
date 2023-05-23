#!/bin/bash

total_time=0
input1="hard"
input2="BFC"

for ((i=1; i<=1; i++)); do
  execution_time=$( { time (echo -e "$input1\n$input2" | python3 main.py >/dev/null); } 2>&1 | awk 'user {print $2}')
  total_time=$(echo "$total_time + $execution_time" | bc -l)
done

average_time=$(echo "$total_time / 50" | bc -l)
echo "Average time: $average_time"