#!/bin/bash

DATA_DIR=()
DATA_PREFIX="/data"
FIND=/usr/bin/find
RM=/bin/rm

init_dir()
{
	local path=""

	for ((i=1; i<=11; i++)); do
		path=$DATA_PREFIX"$i"

		if [ -d "$path" ]; then
			DATA_DIR[$i]=$path
		fi

	done
}

test_del_checksum()
{

	init_dir

	for dir in ${DATA_DIR[@]}; do
		#echo $dir
		cd $dir && \
		   $FIND . -name "*.checksum" |xargs $RM -f
	done

}

test_del_checksum
