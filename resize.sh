#!/bin/bash

cd /var/services/homes/admin/show_data

if [ -z "$1" ]
then
	exit
fi

filename=`date +%s%N`

curl -s $1 -o "${filename}_r.jpg"

if [ $? != 0 ]
then
	exit
fi

magick "${filename}_r.jpg" -resize 750000@ "${filename}_c.jpg"

if [ $? != 0 ]
then
	exit
fi

rm "${filename}_r.jpg"

hashed=`md5sum "${filename}_c.jpg" | cut -f1 "-d "`

if [ ! -d images ]
then
	mkdir images
fi

mv "${filename}_c.jpg" ./images/${hashed}.jpg

echo ${hashed}.jpg
