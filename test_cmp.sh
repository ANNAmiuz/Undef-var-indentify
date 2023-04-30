#!/bin/bash

proj1_path="/home/avery/cuhksz/csc4001/Proj1"
zcy_proj_path="/home/avery/cuhksz/csc4001/zcy_proj/cuhk-se-proj/src/submission"
input1_path="/home/avery/cuhksz/csc4001/Proj1/pretest1"
input2_path="/home/avery/cuhksz/csc4001/Proj1/pretest2"
output1_path="/home/avery/cuhksz/csc4001/test_result/test1"
output2_path="/home/avery/cuhksz/csc4001/test_result/test2"

# Create the output directory if it doesn't exist
mkdir -p "$output1_path"
mkdir -p "$output2_path"

echo "task 1"
for i in {1..10}; do
  # Run the Python program under Proj1 with redirect input
  /usr/bin/python3 "$proj1_path/1.py" < "$input1_path/x$i.txt" > "$output1_path/proj1_output_$i.txt"

  # Run the Python program under zcy_proj with redirect input
  /usr/bin/python3 "$zcy_proj_path/1.py" < "$input1_path/x$i.txt" > "$output1_path/zcy_proj_output_$i.txt"

  # Compare the output files
  diff -w  "$output1_path/proj1_output_$i.txt" "$output1_path/zcy_proj_output_$i.txt" > /dev/null
  if [ $? -eq 0 ]; then
    echo "Output files for x$i.txt are the same"
  else
    echo "Output files for x$i.txt are different"
  fi
done

echo "task 2"
for i in {1..11}; do
  # Run the Python program under Proj1 with redirect input
  /usr/bin/python3 "$proj1_path/2.py" < "$input2_path/x$i.txt" > "$output2_path/proj1_output_$i.txt"

  # Run the Python program under zcy_proj with redirect input
  /usr/bin/python3 "$zcy_proj_path/2.py" < "$input2_path/x$i.txt" > "$output2_path/zcy_proj_output_$i.txt"

  # Compare the output files
  diff -w  "$output2_path/proj1_output_$i.txt" "$output2_path/zcy_proj_output_$i.txt" > /dev/null
  if [ $? -eq 0 ]; then
    echo "Output files for x$i.txt are the same"
  else
    echo "Output files for x$i.txt are different"
  fi
done
