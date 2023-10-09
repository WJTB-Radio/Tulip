#!/bin/bash

cd /var/services/homes/admin/show_data

if [ -z "$1" ]
then
	>&2 echo "error: invalid parameters"
	exit
fi

filename=`date +%s%N`

curl -s $1 -o "${filename}_r.jpg"

if [ $? != 0 ]
then
	>&2 echo "error: failed to download image"
	rm /var/services/homes/admin/show_data/*.jpg
	exit
fi

convert "${filename}_r.jpg" -resize 750000@ "${filename}_c.jpg"

if [ $? != 0 ]
then
	>&2 echo "error: failed to convert image"
	rm /var/services/homes/admin/show_data/*.jpg
	exit
fi

rm "${filename}_r.jpg"

hashed=`md5sum "${filename}_c.jpg" | cut -f1 "-d "`

if [ ! -d images ]
then
	mkdir images
fi

mv "${filename}_c.jpg" ./images/${hashed}.jpg

rm /var/services/homes/admin/show_data/*.jpg

echo ${hashed}.jpg
