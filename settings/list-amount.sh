#!/bin/bash

if [[ $# -eq 0 ]]; then
	echo "This script requires one argument: the key to look for in the settings"
	exit 1
fi
./list.sh "${1}" | sed 's/^.*: //' | sort -n | uniq -c
