#!/bin/bash
# Rebuild the oversize PDFs (>50MB) from their committed split parts.
# Run this once after cloning the repo. Originals are restored next to their parts.
#
# Each oversize file F was stored as:  F.zip.part-00, F.zip.part-01, ...
# (a single stored/zip archive of F, split into 45MB chunks).
set -e
cd "$(dirname "$0")"
count=0
while IFS= read -r -d '' p0; do
  dir=$(dirname "$p0")
  base=$(basename "$p0"); base=${base%.zip.part-00}   # original filename
  echo "Rebuilding: ${dir#./}/$base"
  cat "$dir/$base.zip.part-"* > "$dir/.__rebuild.zip"
  unzip -o -j -q "$dir/.__rebuild.zip" -d "$dir"
  rm -f "$dir/.__rebuild.zip"
  count=$((count+1))
done < <(find . -name '*.zip.part-00' -print0)
echo "Done — reassembled $count file(s)."
echo "(Optional) remove the parts afterwards with:  find . -name '*.zip.part-*' -delete"
