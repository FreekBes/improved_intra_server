#!/bin/bash
./list.sh "ext_version" | grep "\"" | sed 's/^.*: //' | sort -n | uniq -c
