#!/bin/bash

find . -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.qml" -o -name "*.txt" -o -name "*.js" \) | while read file
do
    sed -i.bak '/[ぁ-んァ-ン一-龥]/d' "$file"
done

echo "All Japanese comments removed."

