#!/bin/bash

for i in {1..7}
do
  sed 's/$/\\n/' $i.py > x$i.txt
done