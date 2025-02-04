#!/bin/bash

cd ../show_data

if [ -z "$1" ]; then
	echo >&2 "error: invalid parameters"
	exit
fi

filename=$(date +%s%N)

curl -s $1 -o "${filename}_r.jpg"

if [ $? != 0 ]; then
	echo >&2 "error: failed to download image"
	rm *.jpg
	exit
fi

convert "${filename}_r.jpg" -resize 750000@ "${filename}_c.jpg"

if [ $? != 0 ]; then
	echo >&2 "error: failed to convert image"
	rm *.jpg
	exit
fi

rm "${filename}_r.jpg"

hashed=$(md5sum "${filename}_c.jpg" | cut -f1 "-d ")

if [ ! -d images ]; then
	mkdir images
fi

mv "${filename}_c.jpg" ./images/${hashed}.jpg

rm *.jpg

echo ${hashed}.jpg
