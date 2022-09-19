#!/bin/bash

rm *-crop.pdf

for i in *.pdf; do
    pdfcrop $i
done

for i in *-crop.pdf; do
    convert -verbose -density 500 $i "${i%.*}.png"
done
