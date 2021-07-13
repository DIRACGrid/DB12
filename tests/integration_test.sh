#!/bin/bash
#This script is intended to compare results provided by DB12 when run on different python versions to make sure that 
#they are the same within a specified threshold.

list="$(find . -name 'result*')"

for file in $list
do
  for file2 in $list; 
  do 
    if [[ $file != $file2 ]]; then
      result1=$(cat $file)
      result2=$(cat $file2)

      threshold=0.2
      product=$(awk '{print $1*$2}' <<< "$result1 $threshold")

      difference1=$(awk '{print $1-$2}' <<< "$result1 $result2")

      if (( $(echo $difference1#- $product | awk '{if ($1 > $2) print 1;}') )); 
        then 
          echo "The results provided by $file and $file2 are not the same"
          exit 1
      else echo "The results provided by $file and $file2 are the same within the threshold"; 
      fi
    fi
   done
done
