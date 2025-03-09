#!/bin/bash

sudo systemctl restart icecast2

if [ $? -eq 0 ]; then
	echo ok
fi
