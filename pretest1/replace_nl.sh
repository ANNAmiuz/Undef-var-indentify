#!/bin/bash

for i in {1..8}
do
  sed 's/$/\\n/' $i.py > x$i.txt
done
